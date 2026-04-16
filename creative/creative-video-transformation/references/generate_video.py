"""
video-remix/scripts/generate_video.py
Generate video clips from regenerated keyframes using Veo 3.1 I2V
via the official higgsfield-client SDK.

Usage: python scripts/generate_video.py
"""

import time
import json
import subprocess
import requests
from pathlib import Path

import higgsfield_client

from config import (
    REGEN_DIR, CLIPS_DIR,
    ensure_dirs, load_remix_plan, load_manifest, write_state,
    VIDEO_I2V_MODEL,
)


def validate_clip(path: str) -> bool:
    """Check clip is playable via FFprobe."""
    try:
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        probe = json.loads(result.stdout)
        duration = float(probe["format"].get("duration", 0))
        return duration > 0.5
    except Exception:
        return False


def generate_clip(
    keyframe_path: str,
    veo_prompt: str,
    duration: int,
    aspect_ratio: str,
    output_path: str,
) -> bool:
    """
    Upload regenerated keyframe → call Veo 3.1 I2V → download result.

    Veo 3.1 on Higgsfield supports:
      - image_url or images_list (for multi-reference mode)
      - prompt: motion/action description
      - duration: 4, 6, or 8 seconds
      - resolution: "720p" or "1080p"
      - aspect_ratio: "16:9" or "9:16"
    """
    try:
        # 1. Upload keyframe
        image_url = higgsfield_client.upload_file(keyframe_path)
        print(f"    Uploaded: {image_url[:60]}...")

        # 2. Submit and wait
        #    subscribe() blocks until the job completes.
        #    For video, this may take 1-5 minutes.
        result = higgsfield_client.subscribe(
            VIDEO_I2V_MODEL,
            arguments={
                "image_url": image_url,
                "prompt": veo_prompt,
                "duration": duration,
                "resolution": "1080p",
                "aspect_ratio": aspect_ratio,
            },
        )

        # 3. Extract video URL
        #    Video results may use 'video_url', 'url', or nested 'output.url'
        video_url = (
            result.get("video_url")
            or result.get("url")
            or (result.get("output", {}) or {}).get("url")
            or (result.get("videos", [{}])[0].get("url") if result.get("videos") else None)
        )

        if not video_url:
            print(f"    No video URL in result: {list(result.keys())}")
            return False

        # 4. Download
        vid_resp = requests.get(video_url, timeout=120)
        vid_resp.raise_for_status()
        Path(output_path).write_bytes(vid_resp.content)

        # 5. Validate
        if not validate_clip(output_path):
            print(f"    Downloaded file is not a valid video")
            return False

        return True

    except higgsfield_client.NSFW:
        print(f"    Content filter — soften the prompt and retry manually")
        return False

    except (higgsfield_client.Failed, higgsfield_client.Cancelled) as e:
        print(f"    Generation failed: {e}")
        return False

    except Exception as e:
        print(f"    Error: {e}")
        return False


def main():
    ensure_dirs()
    plan = load_remix_plan()
    manifest = load_manifest()

    info = manifest["video_info"]
    ratio = info["width"] / info["height"]
    aspect = "9:16" if ratio < 1.0 else "16:9"

    shots = plan["shots"]
    success = 0
    fail = 0

    for shot in shots:
        shot_id = shot["shot_index"]
        keyframe_path = str(REGEN_DIR / f"{shot_id}.png")
        output_path = str(CLIPS_DIR / f"{shot_id}.mp4")

        # Skip if already done
        if Path(output_path).exists() and validate_clip(output_path):
            print(f"{shot_id}: exists, skipping")
            success += 1
            continue

        if not Path(keyframe_path).exists():
            print(f"{shot_id}: no keyframe, skipping")
            fail += 1
            continue

        duration = shot["duration_seconds"]
        print(f"{shot_id}: generating {duration}s clip...")

        ok = generate_clip(
            keyframe_path,
            shot["veo_prompt"],
            duration,
            aspect,
            output_path,
        )

        if ok:
            print(f"  OK")
            success += 1
        else:
            print(f"  FAILED")
            fail += 1

        # Courtesy delay — video gen is heavier
        time.sleep(5)

    write_state("STATE_GENERATE_COMPLETE")
    print(f"\nVideo generation: {success} ok, {fail} failed")


if __name__ == "__main__":
    main()
