"""
video-remix/scripts/regenerate.py
Regenerate keyframes using Nano Banana 2 Edit via higgsfield-client SDK.

The SDK handles auth, polling, retries, and status tracking.
We just need to: upload the image → subscribe with model + arguments → download result.

Usage: python scripts/regenerate.py
"""

import time
import requests
from pathlib import Path

import higgsfield_client

from config import (
    KEYFRAMES_DIR, REGEN_DIR,
    ensure_dirs, load_remix_plan, load_manifest, write_state,
    IMAGE_EDIT_MODEL,
)


def regenerate_keyframe(
    original_keyframe_path: str,
    prompt: str,
    output_path: str,
    aspect_ratio: str = "auto",
    resolution: str = "2k",
) -> bool:
    """
    Upload keyframe → call Nano Banana 2 Edit → download result.

    Uses higgsfield_client.subscribe() which blocks until completion.
    """
    try:
        # 1. Upload the source keyframe to Higgsfield storage
        image_url = higgsfield_client.upload_file(original_keyframe_path)
        print(f"    Uploaded: {image_url[:60]}...")

        # 2. Submit and wait for result
        #    The SDK handles polling internally with subscribe().
        #
        #    Argument structure based on the Nano Banana 2 Edit API:
        #      model: "nano-banana-2-edit" (or namespaced path)
        #      images_list: [url] — array of reference image URLs
        #      prompt: edit instruction
        #      aspect_ratio: "auto", "16:9", "9:16", etc.
        #      resolution: "1k", "2k", "4k"
        result = higgsfield_client.subscribe(
            IMAGE_EDIT_MODEL,
            arguments={
                "images_list": [image_url],
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
            },
        )

        # 3. Extract the output image URL
        #    Result structure: result['images'][0]['url'] (based on SDK README)
        output_url = None
        if "images" in result and result["images"]:
            output_url = result["images"][0].get("url")
        elif "url" in result:
            output_url = result["url"]
        elif "output" in result:
            output_url = result["output"].get("url")

        if not output_url:
            print(f"    No image URL in result: {list(result.keys())}")
            return False

        # 4. Download
        img_resp = requests.get(output_url, timeout=60)
        img_resp.raise_for_status()
        Path(output_path).write_bytes(img_resp.content)

        # Validate
        if Path(output_path).stat().st_size < 10_000:
            print(f"    Image too small ({Path(output_path).stat().st_size}B)")
            return False

        return True

    except higgsfield_client.NSFW:
        print(f"    Content filter triggered — rephrase the prompt")
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
    shots = plan["shots"]

    # Determine aspect ratio from source video
    info = manifest["video_info"]
    ratio = info["width"] / info["height"]
    aspect = "9:16" if ratio < 1.0 else "16:9"

    success = 0
    fail = 0

    for shot in shots:
        shot_id = shot["shot_index"]
        original_path = str(KEYFRAMES_DIR / f"{shot_id}.png")
        output_path = str(REGEN_DIR / f"{shot_id}.png")

        # Skip if already done
        if Path(output_path).exists() and Path(output_path).stat().st_size > 10_000:
            print(f"{shot_id}: exists, skipping")
            success += 1
            continue

        print(f"{shot_id}: regenerating...")
        ok = regenerate_keyframe(
            original_path,
            shot["nano_banana_prompt"],
            output_path,
            aspect_ratio=aspect,
        )

        if ok:
            print(f"  OK")
            success += 1
        else:
            print(f"  FAILED")
            fail += 1

        # Courtesy delay between requests
        time.sleep(2)

    write_state("STATE_REGENERATE_COMPLETE")
    print(f"\nRegeneration: {success} ok, {fail} failed")


if __name__ == "__main__":
    main()
