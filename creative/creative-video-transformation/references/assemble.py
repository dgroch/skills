"""
video-remix/scripts/assemble.py
Assemble generated clips into final remix video.

Usage: python scripts/assemble.py [--with-audio] [--crossfade 0.3]
"""

import sys
import json
import subprocess
from pathlib import Path

from config import (
    CLIPS_DIR, AUDIO_DIR, OUTPUT_DIR, WORK_DIR,
    ensure_dirs, load_manifest, write_state,
)


def get_sorted_clips() -> list[Path]:
    clips = sorted(CLIPS_DIR.glob("shot_*.mp4"))
    return [c for c in clips if c.stat().st_size > 0]


def assemble_simple(clips: list[Path], output: Path):
    """Concatenate clips without transitions."""
    concat_file = WORK_DIR / "concat.txt"
    with open(concat_file, "w") as f:
        for clip in clips:
            f.write(f"file '{clip.resolve()}'\n")

    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output),
    ]
    subprocess.run(cmd, check=True)


def assemble_with_crossfade(clips: list[Path], output: Path, fade_duration: float = 0.3):
    """Concatenate clips with crossfade transitions using FFmpeg xfade filter."""
    if len(clips) < 2:
        return assemble_simple(clips, output)

    # Get durations for offset calculation
    durations = []
    for clip in clips:
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", str(clip),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        d = float(json.loads(result.stdout)["format"]["duration"])
        durations.append(d)

    # Build xfade filter chain
    inputs = []
    for clip in clips:
        inputs.extend(["-i", str(clip)])

    # Calculate offsets and build filter
    filter_parts = []
    current_offset = durations[0] - fade_duration

    if len(clips) == 2:
        filter_parts.append(
            f"[0:v][1:v]xfade=transition=fade:duration={fade_duration}:offset={current_offset}[v]"
        )
    else:
        # First pair
        filter_parts.append(
            f"[0:v][1:v]xfade=transition=fade:duration={fade_duration}:offset={current_offset}[xf0]"
        )
        for i in range(2, len(clips)):
            current_offset += durations[i - 1] - fade_duration
            prev = f"[xf{i - 2}]"
            if i == len(clips) - 1:
                filter_parts.append(
                    f"{prev}[{i}:v]xfade=transition=fade:duration={fade_duration}:offset={current_offset}[v]"
                )
            else:
                filter_parts.append(
                    f"{prev}[{i}:v]xfade=transition=fade:duration={fade_duration}:offset={current_offset}[xf{i - 1}]"
                )

    filter_complex = ";".join(filter_parts)

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output),
    ]
    subprocess.run(cmd, check=True)


def mix_audio(video_path: Path, audio_path: Path, output_path: Path):
    """Overlay original audio onto assembled video."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(output_path),
    ]
    subprocess.run(cmd, check=True)


def main():
    ensure_dirs()
    args = sys.argv[1:]
    with_audio = "--with-audio" in args
    crossfade = 0.3
    if "--crossfade" in args:
        idx = args.index("--crossfade")
        crossfade = float(args[idx + 1])

    clips = get_sorted_clips()
    if not clips:
        print("ERROR: No valid clips found in work/clips/")
        sys.exit(1)

    print(f"Assembling {len(clips)} clips (crossfade: {crossfade}s)...")

    # Assemble video
    video_only = OUTPUT_DIR / "remix_video_only.mp4"
    final_output = OUTPUT_DIR / "remix_final.mp4"

    if crossfade > 0 and len(clips) > 1:
        assemble_with_crossfade(clips, video_only, crossfade)
    else:
        assemble_simple(clips, video_only)

    # Mix audio if requested and available
    if with_audio:
        manifest = load_manifest()
        audio_path = manifest.get("audio_path")
        if audio_path and Path(audio_path).exists():
            print("Mixing original audio...")
            mix_audio(video_only, Path(audio_path), final_output)
        else:
            print("WARNING: --with-audio specified but no audio track found")
            final_output = video_only
    else:
        # Just rename
        video_only.rename(final_output)

    # Validate
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", str(final_output),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    probe = json.loads(result.stdout)
    duration = float(probe["format"]["duration"])

    write_state("STATE_ASSEMBLE_COMPLETE")
    print(f"\nDone: {final_output} ({duration:.1f}s)")


if __name__ == "__main__":
    main()
