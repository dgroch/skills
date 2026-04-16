"""
video-remix/scripts/decompose.py
Decompose source video into shots with keyframe extraction.

Usage: python scripts/decompose.py <source_video>
"""

import sys
import json
import subprocess
from pathlib import Path
from scenedetect import open_video, SceneManager, ContentDetector

from config import (
    WORK_DIR, KEYFRAMES_DIR, AUDIO_DIR,
    ensure_dirs, save_manifest, write_state,
)


def get_video_info(video_path: str) -> dict:
    """Get video dimensions and duration via FFprobe."""
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_streams", "-show_format", video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    probe = json.loads(result.stdout)
    video_stream = next(
        s for s in probe["streams"] if s["codec_type"] == "video"
    )
    return {
        "width": int(video_stream["width"]),
        "height": int(video_stream["height"]),
        "duration": float(probe["format"]["duration"]),
        "fps": eval(video_stream.get("r_frame_rate", "24/1")),
    }


def detect_shots(video_path: str, threshold: float = 27.0) -> list[tuple]:
    """Run PySceneDetect and return list of (start, end) FrameTimecode pairs."""
    video = open_video(video_path)
    manager = SceneManager()
    manager.add_detector(ContentDetector(threshold=threshold))
    manager.detect_scenes(video)
    return manager.get_scene_list()


def extract_keyframe(video_path: str, timestamp: float, output_path: str):
    """Extract a single frame at the given timestamp."""
    cmd = [
        "ffmpeg", "-y", "-ss", str(timestamp),
        "-i", video_path, "-frames:v", "1",
        "-q:v", "2", output_path,
    ]
    subprocess.run(cmd, capture_output=True, check=True)


def extract_audio(video_path: str, output_path: str):
    """Extract audio track as WAV."""
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "44100", output_path,
    ]
    subprocess.run(cmd, capture_output=True, check=True)


def validate_keyframe(path: str) -> bool:
    """Check keyframe is not corrupt (> 10KB)."""
    return Path(path).stat().st_size > 10_000


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/decompose.py <source_video>")
        sys.exit(1)

    video_path = sys.argv[1]
    ensure_dirs()

    # Get source video info
    info = get_video_info(video_path)
    print(f"Source: {info['width']}x{info['height']}, {info['duration']:.1f}s, {info['fps']:.1f}fps")

    # Detect shots
    scenes = detect_shots(video_path, threshold=27.0)

    # Retry with lower threshold if no shots found
    if len(scenes) == 0:
        print("No shots detected at threshold 27.0, retrying at 20.0...")
        scenes = detect_shots(video_path, threshold=20.0)

    if len(scenes) == 0:
        print("ERROR: No shots detected. Video may be single-shot.")
        print("Provide manual timestamps or treat entire video as one shot.")
        # Fallback: treat whole video as one shot
        scenes = [(0.0, info["duration"])]

    print(f"Detected {len(scenes)} shots")

    # Extract keyframes
    shots = []
    for i, scene in enumerate(scenes):
        shot_id = f"shot_{i:03d}"

        # Handle both FrameTimecode objects and raw floats
        if hasattr(scene[0], "get_seconds"):
            start_sec = scene[0].get_seconds()
            end_sec = scene[1].get_seconds()
        else:
            start_sec = float(scene[0])
            end_sec = float(scene[1])

        duration = end_sec - start_sec

        # Extract at 30% into shot (avoid transition artifacts)
        keyframe_time = start_sec + (duration * 0.3)
        keyframe_path = str(KEYFRAMES_DIR / f"{shot_id}.png")

        extract_keyframe(video_path, keyframe_time, keyframe_path)

        # Validate keyframe
        if not validate_keyframe(keyframe_path):
            print(f"  {shot_id}: keyframe corrupt at 30%, retrying at 50%...")
            keyframe_time = start_sec + (duration * 0.5)
            extract_keyframe(video_path, keyframe_time, keyframe_path)
            if not validate_keyframe(keyframe_path):
                print(f"  {shot_id}: WARNING — keyframe still corrupt, skipping")
                continue

        shots.append({
            "shot_id": shot_id,
            "start": start_sec,
            "end": end_sec,
            "duration": round(duration, 2),
            "keyframe_path": keyframe_path,
        })
        print(f"  {shot_id}: {start_sec:.2f}s - {end_sec:.2f}s ({duration:.2f}s)")

    # Extract audio
    audio_path = str(AUDIO_DIR / "source_audio.wav")
    try:
        extract_audio(video_path, audio_path)
        has_audio = True
    except subprocess.CalledProcessError:
        print("WARNING: No audio track found")
        has_audio = False
        audio_path = None

    # Write manifest
    manifest = {
        "source_video": video_path,
        "video_info": info,
        "shots": shots,
        "audio_path": audio_path,
        "has_audio": has_audio,
    }
    save_manifest(manifest)
    write_state("STATE_DECOMPOSE_COMPLETE")

    print(f"\nDecomposition complete: {len(shots)} shots extracted")
    print(f"Manifest: {WORK_DIR / 'shots_manifest.json'}")


if __name__ == "__main__":
    main()
