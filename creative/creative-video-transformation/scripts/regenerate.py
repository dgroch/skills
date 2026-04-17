"""
Step 3: Regenerate keyframes via Nano Banana 2 Edit (Higgsfield SDK).

Usage: python scripts/regenerate.py
"""

import sys
import time
from pathlib import Path

import higgsfield_client
import requests

from config import (
    IMAGE_EDIT_MODEL,
    IMAGE_RESOLUTION,
    KEYFRAMES_DIR,
    REGEN_DIR,
    ensure_dirs,
    have_higgsfield_creds,
    load_manifest,
    load_remix_plan,
    save_remix_plan,
    write_state,
)

# Per-shot retry count for transient failures (network, rate limit, etc).
MAX_ATTEMPTS = 3
# Courtesy delay between shot submissions.
SHOT_DELAY_SECONDS = 2
# Exponential backoff base for retry sleeps.
BACKOFF_BASE_SECONDS = 15


def _queue_logger(shot_id: str):
    def _on(status):
        name = type(status).__name__
        print(f"    [{shot_id}] {name}")
    return _on


def _extract_image_url(result: dict) -> str | None:
    """Pull the output image URL out of a Higgsfield result payload.

    The documented shape is {"images": [{"url": "..."}], ...}. We defensively
    accept a few fallbacks because Higgsfield's per-model result shapes vary.
    """
    if not isinstance(result, dict):
        return None
    if isinstance(result.get("images"), list) and result["images"]:
        first = result["images"][0]
        if isinstance(first, dict) and first.get("url"):
            return first["url"]
    if isinstance(result.get("image"), dict) and result["image"].get("url"):
        return result["image"]["url"]
    if result.get("url"):
        return result["url"]
    output = result.get("output")
    if isinstance(output, dict) and output.get("url"):
        return output["url"]
    return None


def regenerate_once(
    keyframe_path: str,
    hero_ref_url: str | None,
    prompt: str,
    aspect_ratio: str,
    output_path: str,
    shot_id: str,
) -> tuple[bool, str | None]:
    """Run a single Nano Banana 2 Edit call and save the result.

    Returns (success, uploaded_url). `uploaded_url` is the regenerated image's
    public URL on success — useful for passing as a reference image on later
    shots (hero-reference mode).
    """
    try:
        image_url = higgsfield_client.upload_file(keyframe_path)
    except higgsfield_client.CredentialsMissedError:
        raise
    except Exception as e:
        print(f"    upload failed: {e}")
        return False, None

    images_list = [image_url]
    if hero_ref_url and hero_ref_url != image_url:
        images_list.append(hero_ref_url)

    try:
        result = higgsfield_client.subscribe(
            IMAGE_EDIT_MODEL,
            arguments={
                "images_list": images_list,
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "resolution": IMAGE_RESOLUTION,
            },
            on_queue_update=_queue_logger(shot_id),
        )
    except higgsfield_client.CredentialsMissedError:
        raise
    except higgsfield_client.HiggsfieldClientError as e:
        print(f"    SDK error: {e}")
        return False, None
    except Exception as e:
        print(f"    unexpected error: {e}")
        return False, None

    # subscribe() may return a status dataclass if the run terminated
    # non-successfully, depending on SDK version. Handle it defensively.
    if isinstance(result, higgsfield_client.NSFW):
        print("    content filter rejected the prompt")
        return False, None
    if isinstance(result, (higgsfield_client.Failed, higgsfield_client.Cancelled)):
        print(f"    generation terminal non-success: {type(result).__name__}")
        return False, None

    payload = result
    if isinstance(result, higgsfield_client.Completed):
        payload = getattr(result, "result", None) or getattr(result, "data", None) or {}

    output_url = _extract_image_url(payload)
    if not output_url:
        keys = list(payload.keys()) if isinstance(payload, dict) else type(payload).__name__
        print(f"    no image URL in result ({keys})")
        return False, None

    try:
        r = requests.get(output_url, timeout=120)
        r.raise_for_status()
        Path(output_path).write_bytes(r.content)
    except requests.RequestException as e:
        print(f"    download failed: {e}")
        return False, None

    size = Path(output_path).stat().st_size
    if size < 10_000:
        print(f"    image too small ({size}B)")
        return False, None

    return True, output_url


def regenerate_shot(
    shot: dict,
    hero_ref_url: str | None,
    aspect_ratio: str,
    output_path: str,
) -> tuple[bool, str | None]:
    """Retry wrapper around regenerate_once with exponential backoff."""
    shot_id = shot["shot_index"]
    original_path = str(KEYFRAMES_DIR / f"{shot_id}.png")
    if not Path(original_path).exists():
        print(f"    missing source keyframe {original_path}")
        return False, None

    prompt = shot["nano_banana_prompt"]
    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"    attempt {attempt}/{MAX_ATTEMPTS}")
        ok, url = regenerate_once(
            original_path, hero_ref_url, prompt, aspect_ratio, output_path, shot_id
        )
        if ok:
            return True, url
        if attempt < MAX_ATTEMPTS:
            delay = BACKOFF_BASE_SECONDS * attempt
            print(f"    retrying in {delay}s")
            time.sleep(delay)
    return False, None


def main():
    if not have_higgsfield_creds():
        raise SystemExit(
            "ERROR: Higgsfield credentials not set. Export HF_KEY or "
            "HF_API_KEY_ID + HF_API_KEY_SECRET."
        )

    ensure_dirs()
    plan = load_remix_plan()
    manifest = load_manifest()
    shots = plan["shots"]
    if not shots:
        raise SystemExit("ERROR: plan has no shots. Re-run analyse.")

    aspect = plan.get("aspect_ratio") or manifest.get("aspect_ratio", "16:9")
    hero_ref_url = plan.get("hero_ref_url")

    success = 0
    fail = 0
    first_success_was_cached = False

    for shot in shots:
        shot_id = shot["shot_index"]
        output_path = str(REGEN_DIR / f"{shot_id}.png")

        if Path(output_path).exists() and Path(output_path).stat().st_size > 10_000:
            print(f"{shot_id}: exists, skipping")
            success += 1
            if hero_ref_url is None and not first_success_was_cached:
                # Cached results predate the hero-ref feature; don't retro-upload.
                first_success_was_cached = True
            continue

        print(f"{shot_id}: regenerating")
        ok, url = regenerate_shot(shot, hero_ref_url, aspect, output_path)
        if ok:
            success += 1
            print(f"  OK")
            # The first successful shot becomes the hero reference for
            # subsequent shots. Nano Banana 2 Edit accepts up to 14 images
            # in images_list — we pass [original_keyframe, hero_ref].
            if hero_ref_url is None and url:
                hero_ref_url = url
                plan["hero_ref_url"] = url
                save_remix_plan(plan)
                print(f"  (captured hero reference for subsequent shots)")
        else:
            fail += 1
            print(f"  FAILED")

        time.sleep(SHOT_DELAY_SECONDS)

    write_state("STATE_REGENERATE_COMPLETE")
    print(f"\nRegeneration: {success} ok, {fail} failed")
    if fail:
        print("Re-run the script to retry failed shots (existing files are kept).")
        sys.exit(1)


if __name__ == "__main__":
    main()
