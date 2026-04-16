"""
Step 5: Assemble generated clips into the final remix video.

Usage: python scripts/assemble.py [--with-audio] [--crossfade <seconds>]
"""

import argparse
import json
import shutil
import subprocess
from pathlib import Path

from config import (
    CLIPS_DIR,
    OUTPUT_DIR,
    WORK_DIR,
    ensure_dirs,
    load_manifest,
    write_state,
)


def probe_duration(path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_format", str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(json.loads(result.stdout)["format"]["duration"])


def sorted_clips() -> list[Path]:
    clips = sorted(CLIPS_DIR.glob("shot_*.mp4"))
    return [c for c in clips if c.stat().st_size > 0]


def assemble_simple(clips: list[Path], output: Path):
    """Concatenate clips using the concat demuxer. Clips must share codec + resolution."""
    concat_file = WORK_DIR / "concat.txt"
    concat_file.write_text(
        "\n".join(f"file '{c.resolve()}'" for c in clips) + "\n"
    )
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-an", str(output),
    ]
    subprocess.run(cmd, check=True)


def assemble_with_crossfade(clips: list[Path], output: Path, fade: float):
    """Chain the xfade filter across N clips, computing cumulative offsets."""
    if len(clips) < 2:
        assemble_simple(clips, output)
        return

    durations = [probe_duration(c) for c in clips]
    inputs: list[str] = []
    for c in clips:
        inputs += ["-i", str(c)]

    filter_parts: list[str] = []
    offset = durations[0] - fade

    if len(clips) == 2:
        filter_parts.append(
            f"[0:v][1:v]xfade=transition=fade:duration={fade}:offset={offset:.3f}[v]"
        )
    else:
        filter_parts.append(
            f"[0:v][1:v]xfade=transition=fade:duration={fade}:offset={offset:.3f}[xf0]"
        )
        for i in range(2, len(clips)):
            offset += durations[i - 1] - fade
            prev = f"[xf{i - 2}]"
            label = "[v]" if i == len(clips) - 1 else f"[xf{i - 1}]"
            filter_parts.append(
                f"{prev}[{i}:v]xfade=transition=fade:duration={fade}:offset={offset:.3f}{label}"
            )

    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        *inputs,
        "-filter_complex", ";".join(filter_parts),
        "-map", "[v]",
        "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-an", str(output),
    ]
    subprocess.run(cmd, check=True)


def mix_audio(video_path: Path, audio_path: Path, output_path: Path):
    """Overlay the source audio track on the assembled video.

    Uses `-shortest` so the output ends at whichever stream finishes first —
    typically the video, because Veo clips are time-quantised and the summed
    length may differ from the source audio.
    """
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(video_path), "-i", str(audio_path),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        str(output_path),
    ]
    subprocess.run(cmd, check=True)


def parse_args():
    parser = argparse.ArgumentParser(description="Assemble remix clips")
    parser.add_argument("--with-audio", action="store_true",
                        help="overlay original audio onto the final video")
    parser.add_argument("--crossfade", type=float, default=0.3,
                        help="crossfade duration in seconds (0 disables)")
    return parser.parse_args()


def main():
    args = parse_args()
    ensure_dirs()

    clips = sorted_clips()
    if not clips:
        raise SystemExit(f"ERROR: no clips found in {CLIPS_DIR}")

    print(f"Assembling {len(clips)} clips (crossfade: {args.crossfade}s)")

    video_only = OUTPUT_DIR / "remix_video_only.mp4"
    final_output = OUTPUT_DIR / "remix_final.mp4"
    if final_output.exists():
        final_output.unlink()

    if args.crossfade > 0 and len(clips) > 1:
        assemble_with_crossfade(clips, video_only, args.crossfade)
    else:
        assemble_simple(clips, video_only)

    if args.with_audio:
        manifest = load_manifest()
        audio_path = manifest.get("audio_path")
        if audio_path and Path(audio_path).exists():
            print("Mixing original audio")
            mix_audio(video_only, Path(audio_path), final_output)
            video_only.unlink(missing_ok=True)
        else:
            print("WARNING: --with-audio requested but no audio track available")
            shutil.move(str(video_only), final_output)
    else:
        shutil.move(str(video_only), final_output)

    duration = probe_duration(final_output)
    write_state("STATE_ASSEMBLE_COMPLETE")
    print(f"\nDone: {final_output} ({duration:.1f}s)")


if __name__ == "__main__":
    main()
