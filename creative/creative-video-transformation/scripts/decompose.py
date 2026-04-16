"""
Step 1: Decompose a source video into shots with keyframes and audio.

Usage: python scripts/decompose.py <source_video>
"""

import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

from scenedetect import ContentDetector, SceneManager, open_video

from config import (
    AUDIO_DIR,
    KEYFRAMES_DIR,
    WORK_DIR,
    aspect_ratio_from_info,
    ensure_dirs,
    save_manifest,
    write_state,
)


def parse_fps(rate: str) -> float:
    try:
        return float(Fraction(rate))
    except (ValueError, ZeroDivisionError):
        return 24.0


def get_video_info(video_path: str) -> dict:
    """Probe video dimensions, duration, and fps via FFprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_streams", "-show_format", video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    probe = json.loads(result.stdout)
    video_stream = next(
        (s for s in probe["streams"] if s["codec_type"] == "video"), None
    )
    if not video_stream:
        raise SystemExit(f"ERROR: no video stream found in {video_path}")
    has_audio = any(s["codec_type"] == "audio" for s in probe["streams"])
    return {
        "width": int(video_stream["width"]),
        "height": int(video_stream["height"]),
        "duration": float(probe["format"]["duration"]),
        "fps": parse_fps(video_stream.get("r_frame_rate", "24/1")),
        "has_audio_stream": has_audio,
    }


def detect_shots(video_path: str, threshold: float = 27.0) -> list[tuple]:
    """Run PySceneDetect with ContentDetector and return (start, end) pairs."""
    video = open_video(video_path)
    manager = SceneManager()
    manager.add_detector(ContentDetector(threshold=threshold))
    manager.detect_scenes(video)
    return manager.get_scene_list()


def extract_keyframe(video_path: str, timestamp: float, output_path: str):
    """Extract a single PNG frame at the given timestamp.

    `-ss` after `-i` is frame-accurate (slower than input-level seek but
    necessary for short shots).
    """
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", video_path, "-ss", f"{timestamp:.3f}",
        "-frames:v", "1", "-q:v", "2", output_path,
    ]
    subprocess.run(cmd, check=True)


def extract_audio(video_path: str, output_path: str) -> bool:
    """Extract audio as WAV. Returns False if the source has no audio stream."""
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", video_path, "-vn", "-acodec", "pcm_s16le",
        "-ar", "44100", output_path,
    ]
    try:
        subprocess.run(cmd, check=True)
        return Path(output_path).exists() and Path(output_path).stat().st_size > 0
    except subprocess.CalledProcessError:
        return False


def valid_keyframe(path: str) -> bool:
    p = Path(path)
    return p.exists() and p.stat().st_size > 10_000


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/decompose.py <source_video>")
        sys.exit(1)

    video_path = sys.argv[1]
    if not Path(video_path).exists():
        raise SystemExit(f"ERROR: source video not found: {video_path}")

    ensure_dirs()

    info = get_video_info(video_path)
    aspect = aspect_ratio_from_info(info)
    print(
        f"Source: {info['width']}x{info['height']} ({aspect}), "
        f"{info['duration']:.1f}s, {info['fps']:.1f}fps"
    )

    scenes = detect_shots(video_path, threshold=27.0)
    if not scenes:
        print("No shots at threshold 27.0, retrying at 20.0...")
        scenes = detect_shots(video_path, threshold=20.0)
    if not scenes:
        print("WARNING: no shots detected. Treating whole video as a single shot.")
        scenes = [(0.0, info["duration"])]

    print(f"Detected {len(scenes)} shots")

    shots = []
    for i, scene in enumerate(scenes):
        shot_id = f"shot_{i:03d}"

        # PySceneDetect returns FrameTimecode; the single-shot fallback is raw floats.
        if hasattr(scene[0], "get_seconds"):
            start_sec = scene[0].get_seconds()
            end_sec = scene[1].get_seconds()
        else:
            start_sec = float(scene[0])
            end_sec = float(scene[1])
        duration = end_sec - start_sec

        keyframe_time = start_sec + duration * 0.3
        keyframe_path = str(KEYFRAMES_DIR / f"{shot_id}.png")

        extract_keyframe(video_path, keyframe_time, keyframe_path)

        if not valid_keyframe(keyframe_path):
            print(f"  {shot_id}: corrupt at 30%, retrying at 50%")
            keyframe_time = start_sec + duration * 0.5
            extract_keyframe(video_path, keyframe_time, keyframe_path)
            if not valid_keyframe(keyframe_path):
                print(f"  {shot_id}: WARNING still corrupt, skipping")
                continue

        shots.append({
            "shot_id": shot_id,
            "start": round(start_sec, 3),
            "end": round(end_sec, 3),
            "duration": round(duration, 3),
            "keyframe_path": keyframe_path,
        })
        print(f"  {shot_id}: {start_sec:.2f}s – {end_sec:.2f}s ({duration:.2f}s)")

    if not shots:
        raise SystemExit("ERROR: no usable keyframes extracted")

    audio_path = str(AUDIO_DIR / "source_audio.wav")
    has_audio = False
    if info["has_audio_stream"]:
        has_audio = extract_audio(video_path, audio_path)
        if not has_audio:
            print("WARNING: audio extraction failed")
    else:
        print("No audio stream in source")
    if not has_audio:
        audio_path = None

    manifest = {
        "source_video": str(Path(video_path).resolve()),
        "video_info": info,
        "aspect_ratio": aspect,
        "shots": shots,
        "audio_path": audio_path,
        "has_audio": has_audio,
    }
    save_manifest(manifest)
    write_state("STATE_DECOMPOSE_COMPLETE")

    print(f"\nDecomposition complete: {len(shots)} shots")
    print(f"Manifest: {WORK_DIR / 'shots_manifest.json'}")


if __name__ == "__main__":
    main()
