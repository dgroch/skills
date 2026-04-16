"""
video-remix/scripts/analyse.py
Use Claude to analyse each keyframe and produce per-shot remix prompts.

Usage: python scripts/analyse.py "high level remix prompt"
"""

import sys
import json
import base64
from pathlib import Path
from anthropic import Anthropic

from config import (
    ANTHROPIC_API_KEY, load_manifest, save_remix_plan, write_state, quantise_duration,
)

SYSTEM_PROMPT = """You are a video production assistant. You will receive:
- A keyframe image from an existing video shot
- A high-level remix brief from the director
- The shot index and duration

For this shot, produce a JSON object with:
{
  "shot_index": "shot_001",
  "original_description": "Brief description of what's in the keyframe — subject, action, framing, lighting",
  "nano_banana_prompt": "Precise image generation prompt that applies the remix brief to this specific shot. Preserve the original composition and framing. Be specific about character appearance, environment, lighting, and mood. If the brief changes the character, describe the new character in full detail consistently.",
  "veo_prompt": "Motion/action prompt for video generation from the new keyframe. Describe camera movement, character action, and ambient motion in 2-3 sentences. Prefer subtle camera moves (slow push, gentle pan) over dramatic ones for better generation quality.",
  "duration_seconds": 4
}

CRITICAL RULES:
- duration_seconds must be exactly one of: 4, 6, or 8 (Veo 3.1 constraint)
- nano_banana_prompt must preserve the original shot's composition (angle, framing, depth)
- If the remix changes a character, describe the NEW character identically across all shots
- Respond ONLY with the JSON object. No markdown fences, no preamble."""


def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def analyse_shot(client: Anthropic, shot: dict, remix_prompt: str) -> dict:
    """Send keyframe + remix prompt to Claude, get per-shot instructions."""
    image_data = encode_image(shot["keyframe_path"])
    target_duration = quantise_duration(shot["duration"])

    user_content = [
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": image_data,
            },
        },
        {
            "type": "text",
            "text": (
                f"Shot: {shot['shot_id']}\n"
                f"Original duration: {shot['duration']}s → target: {target_duration}s\n\n"
                f"REMIX BRIEF:\n{remix_prompt}"
            ),
        },
    ]

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    text = response.content[0].text.strip()

    # Strip markdown fences if model adds them
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]

    return json.loads(text)


def main():
    if len(sys.argv) < 2:
        print('Usage: python scripts/analyse.py "remix prompt"')
        sys.exit(1)

    remix_prompt = sys.argv[1]
    manifest = load_manifest()
    shots = manifest["shots"]

    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    plan = {"remix_prompt": remix_prompt, "shots": []}

    for shot in shots:
        print(f"Analysing {shot['shot_id']}...")
        try:
            result = analyse_shot(client, shot, remix_prompt)

            # Validate required fields
            for field in ("nano_banana_prompt", "veo_prompt", "duration_seconds"):
                if not result.get(field):
                    print(f"  WARNING: {field} empty, retrying...")
                    result = analyse_shot(client, shot, remix_prompt)
                    break

            plan["shots"].append(result)
            print(f"  OK — {result.get('original_description', '')[:60]}...")

        except (json.JSONDecodeError, KeyError) as e:
            print(f"  ERROR parsing response for {shot['shot_id']}: {e}")
            print("  Retrying...")
            try:
                result = analyse_shot(client, shot, remix_prompt)
                plan["shots"].append(result)
            except Exception as e2:
                print(f"  FAILED: {e2}. Skipping shot.")

    save_remix_plan(plan)
    write_state("STATE_ANALYSE_COMPLETE")
    print(f"\nAnalysis complete: {len(plan['shots'])} shots planned")


if __name__ == "__main__":
    main()
