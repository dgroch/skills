"""
Step 2: Use Claude to turn each keyframe + remix brief into per-shot prompts.

Uses the `claude` CLI available in the Paperclip environment — no
ANTHROPIC_API_KEY required.

Usage: python scripts/analyse.py "high level remix prompt"
"""

import base64
import json
import re
import subprocess
import sys

from config import (
    load_manifest,
    quantise_duration,
    save_remix_plan,
    write_state,
)

MAX_ANALYSIS_ATTEMPTS = 3

SYSTEM_PROMPT = """You are a video production assistant. You will receive:
- A keyframe image from an existing video shot
- A high-level remix brief from the director
- The shot index and duration target

For this shot, produce a JSON object with EXACTLY this shape:
{
  "shot_index": "shot_001",
  "original_description": "Brief description of the keyframe — subject, action, framing, lighting",
  "nano_banana_prompt": "Precise image-edit prompt that applies the remix brief to this specific shot. Preserve the original composition, camera angle, and framing. Be specific about character appearance, environment, lighting, and mood. If the brief changes the character, describe the NEW character in identical detail for every shot so identity holds across the video.",
  "veo_prompt": "Motion/action prompt (2-3 sentences) for image-to-video generation from the new keyframe. Describe camera movement, character action, and ambient motion. Prefer subtle moves (slow push, gentle pan) for fidelity.",
  "duration_seconds": 4
}

CRITICAL RULES:
- `duration_seconds` MUST be exactly 4, 6, or 8 (Veo 3.1 constraint).
- `shot_index` MUST match the shot id the user gives you.
- `nano_banana_prompt` must preserve original shot composition and framing.
- Respond with the JSON object only. No markdown fences. No preamble. No trailing text."""

_FENCE_RE = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.DOTALL)


def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def strip_fences(text: str) -> str:
    text = text.strip()
    match = _FENCE_RE.match(text)
    return match.group(1).strip() if match else text


def analyse_shot(shot: dict, remix_prompt: str) -> dict:
    """Analyse a keyframe via the local claude CLI (no API key needed).

    Sends a stream-json message containing the base64-encoded keyframe image
    and the remix brief to `claude -p`, then parses the JSON response.
    """
    image_b64 = encode_image(shot["keyframe_path"])
    target_duration = quantise_duration(shot["duration"])

    user_text = (
        f"Shot ID: {shot['shot_id']}\n"
        f"Source duration: {shot['duration']:.2f}s \u2192 target: {target_duration}s\n\n"
        f"REMIX BRIEF:\n{remix_prompt}"
    )

    # Build a stream-json user message with inline image + text.
    input_msg = json.dumps({
        "type": "user",
        "message": {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_b64,
                    },
                },
                {"type": "text", "text": user_text},
            ],
        },
    })

    result = subprocess.run(
        [
            "claude", "-p",
            "--input-format", "stream-json",
            "--output-format", "text",
            "--no-session-persistence",
            "--dangerously-skip-permissions",
            "--append-system-prompt", SYSTEM_PROMPT,
        ],
        input=input_msg + "\n",
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        raise ValueError(
            f"claude CLI failed (rc={result.returncode}): {result.stderr[:200]}"
        )

    text = strip_fences(result.stdout.strip())
    if not text:
        raise ValueError("claude CLI returned empty output")

    data = json.loads(text)

    required = ("shot_index", "nano_banana_prompt", "veo_prompt", "duration_seconds")
    missing = [k for k in required if not data.get(k)]
    if missing:
        raise ValueError(f"missing fields {missing}")

    # Force-correct obvious drift before handing back.
    data["shot_index"] = shot["shot_id"]
    if data["duration_seconds"] not in (4, 6, 8):
        data["duration_seconds"] = target_duration

    return data


def main():
    if len(sys.argv) < 2:
        print('Usage: python scripts/analyse.py "remix prompt"')
        sys.exit(1)

    remix_prompt = sys.argv[1]
    manifest = load_manifest()
    shots = manifest["shots"]
    if not shots:
        raise SystemExit("ERROR: manifest has no shots. Re-run decompose.")

    plan = {
        "remix_prompt": remix_prompt,
        "aspect_ratio": manifest.get("aspect_ratio", "16:9"),
        "shots": [],
        "failed_shots": [],
    }

    for shot in shots:
        print(f"Analysing {shot['shot_id']}...")
        last_error = None
        for attempt in range(1, MAX_ANALYSIS_ATTEMPTS + 1):
            try:
                result = analyse_shot(shot, remix_prompt)
                plan["shots"].append(result)
                desc = result.get("original_description", "")[:60]
                print(f"  OK \u2014 {desc}")
                break
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                last_error = e
                print(f"  attempt {attempt}/{MAX_ANALYSIS_ATTEMPTS} failed: {e}")
        else:
            print(f"  FAILED after {MAX_ANALYSIS_ATTEMPTS} attempts: {last_error}")
            plan["failed_shots"].append(shot["shot_id"])

    save_remix_plan(plan)
    write_state("STATE_ANALYSE_COMPLETE")
    print(f"\nAnalysis complete: {len(plan['shots'])}/{len(shots)} shots planned")
    if plan["failed_shots"]:
        print(f"Failed: {', '.join(plan['failed_shots'])}")


if __name__ == "__main__":
    main()
