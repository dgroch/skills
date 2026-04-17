"""
Step 4: Generate video clips from regenerated keyframes via Veo 3.1 I2V.

Usage: python scripts/generate_video.py
"""

import json
import subprocess
import sys
import time
from pathlib import Path

import higgsfield_client
import requests

from config import (
    CLIPS_DIR,
    REGEN_DIR,
    VIDEO_I2V_MODEL,
    VIDEO_RESOLUTION,
    ensure_dirs,
    have_higgsfield_creds,
    load_manifest,
    load_remix_plan,
    write_state,
)

MAX_ATTEMPTS = 3
SHOT_DELAY_SECONDS = 5
BACKOFF_BASE_SECONDS = 30
DOWNLOAD_TIMEOUT = 300


def _queue_logger(shot_id: str):
    def _on(status):
        name = type(status).__name__
        print(f"    [{shot_id}] {name}")
    return _on


def _extract_video_url(result: dict) -> str | None:
    if not isinstance(result, dict):
        return None
    video = result.get("video")
    if isinstance(video, dict) and video.get("url"):
        return video["url"]
    if result.get("video_url"):
        return result["video_url"]
    if result.get("url"):
        return result["url"]
    videos = result.get("videos")
    if isinstance(videos, list) and videos:
        first = videos[0]
        if isinstance(first, dict) and first.get("url"):
            return first["url"]
    output = result.get("output")
    if isinstance(output, dict) and output.get("url"):
        return output["url"]
    return None


def validate_clip(path: str, expected_duration: int | None = None) -> bool:
    """Probe the clip with FFprobe. Confirm it's playable and roughly the right length."""
    try:
        cmd = [
            "ffprobe", "-v", "error", "-print_format", "json",
            "-show_format", "-show_streams", path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        probe = json.loads(result.stdout)
        duration = float(probe["format"].get("duration", 0))
        if duration < 0.5:
            return False
        has_video = any(s["codec_type"] == "video" for s in probe.get("streams", []))
        if not has_video:
            return False
        if expected_duration is not None and abs(duration - expected_duration) > 1.5:
            print(f"    WARNING: duration {duration:.1f}s off target {expected_duration}s")
        return True
    except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError):
        return False


def generate_once(
    keyframe_path: str,
    prompt: str,
    duration: int,
    aspect_ratio: str,
    output_path: str,
    shot_id: str,
) -> bool:
    try:
        image_url = higgsfield_client.upload_file(keyframe_path)
    except higgsfield_client.CredentialsMissedError:
        raise
    except Exception as e:
        print(f"    upload failed: {e}")
        return False

    try:
        result = higgsfield_client.subscribe(
            VIDEO_I2V_MODEL,
            arguments={
                "image_url": image_url,
                "prompt": prompt,
                "duration": duration,
                "resolution": VIDEO_RESOLUTION,
                "aspect_ratio": aspect_ratio,
            },
            on_queue_update=_queue_logger(shot_id),
        )
    except higgsfield_client.CredentialsMissedError:
        raise
    except higgsfield_client.HiggsfieldClientError as e:
        print(f"    SDK error: {e}")
        return False
    except Exception as e:
        print(f"    unexpected error: {e}")
        return False

    if isinstance(result, higgsfield_client.NSFW):
        print("    content filter rejected the prompt")
        return False
    if isinstance(result, (higgsfield_client.Failed, higgsfield_client.Cancelled)):
        print(f"    terminal non-success: {type(result).__name__}")
        return False

    payload = result
    if isinstance(result, higgsfield_client.Completed):
        payload = getattr(result, "result", None) or getattr(result, "data", None) or {}

    video_url = _extract_video_url(payload)
    if not video_url:
        keys = list(payload.keys()) if isinstance(payload, dict) else type(payload).__name__
        print(f"    no video URL in result ({keys})")
        return False

    try:
        r = requests.get(video_url, timeout=DOWNLOAD_TIMEOUT)
        r.raise_for_status()
        Path(output_path).write_bytes(r.content)
    except requests.RequestException as e:
        print(f"    download failed: {e}")
        return False

    if not validate_clip(output_path, expected_duration=duration):
        print("    downloaded file is not a valid clip")
        return False

    return True


def generate_shot(
    shot: dict,
    aspect_ratio: str,
    output_path: str,
) -> bool:
    shot_id = shot["shot_index"]
    keyframe_path = str(REGEN_DIR / f"{shot_id}.png")
    if not Path(keyframe_path).exists():
        print(f"    missing regenerated keyframe {keyframe_path}")
        return False

    prompt = shot["veo_prompt"]
    duration = shot["duration_seconds"]

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"    attempt {attempt}/{MAX_ATTEMPTS}")
        if generate_once(keyframe_path, prompt, duration, aspect_ratio, output_path, shot_id):
            return True
        if attempt < MAX_ATTEMPTS:
            delay = BACKOFF_BASE_SECONDS * attempt
            print(f"    retrying in {delay}s")
            time.sleep(delay)
    return False


def main():
    if not have_higgsfield_creds():
        raise SystemExit(
            "ERROR: Higgsfield credentials not set. "
            "Export HF_API_KEY_ID + HF_API_KEY_SECRET (Paperclip env), "
            "or HF_KEY, or HF_API_KEY + HF_API_SECRET."
        )

    ensure_dirs()
    plan = load_remix_plan()
    manifest = load_manifest()
    shots = plan["shots"]
    if not shots:
        raise SystemExit("ERROR: plan has no shots. Re-run analyse.")

    aspect = plan.get("aspect_ratio") or manifest.get("aspect_ratio", "16:9")
    success = 0
    fail = 0

    for shot in shots:
        shot_id = shot["shot_index"]
        output_path = str(CLIPS_DIR / f"{shot_id}.mp4")
        duration = shot["duration_seconds"]

        if Path(output_path).exists() and validate_clip(output_path, duration):
            print(f"{shot_id}: exists, skipping")
            success += 1
            continue

        print(f"{shot_id}: generating {duration}s clip")
        if generate_shot(shot, aspect, output_path):
            success += 1
            print(f"  OK")
        else:
            fail += 1
            print(f"  FAILED")

        time.sleep(SHOT_DELAY_SECONDS)

    write_state("STATE_GENERATE_COMPLETE")
    print(f"\nVideo generation: {success} ok, {fail} failed")
    if fail:
        print("Re-run the script to retry failed shots (existing clips are kept).")
        sys.exit(1)


if __name__ == "__main__":
    main()
