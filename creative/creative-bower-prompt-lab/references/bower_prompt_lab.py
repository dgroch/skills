#!/usr/bin/env python3
"""
Bower Prompt Lab — Self-contained generation + critique loop.

Usage:
    export HF_KEY="your-api-key"
    export HF_SECRET="your-api-secret"
    python3 bower_prompt_lab.py

Requires: requests (pip install requests)
Talks to: platform.higgsfield.ai (image generation), api.anthropic.com (critique)
"""

import os
import sys
import json
import time
import base64
import requests
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────

HF_BASE = "https://platform.higgsfield.ai"
HF_MODEL = "higgsfield-ai/soul/standard"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-sonnet-4-20250514"

ANTHROPIC_HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": os.environ.get("ANTHROPIC_API_KEY", ""),
    "anthropic-version": "2023-06-01",
}

MAX_ITERATIONS = 5
PASS_THRESHOLD = 7
POLL_INTERVAL = 5  # seconds
POLL_TIMEOUT = 300  # 5 minutes

# Soul only accepts these ratios — map others to nearest valid
VALID_RATIOS = {"9:16", "16:9", "4:3", "3:4", "1:1", "2:3", "3:2"}
RATIO_MAP = {"4:5": "3:4", "5:4": "4:3"}

OUTPUT_DIR = Path("/home/claude/bower_outputs")
LIBRARY_FILE = OUTPUT_DIR / "prompt_library.json"

# ── Credentials ─────────────────────────────────────────────────────────

HF_KEY = os.environ.get("HF_KEY", "")
HF_SECRET = os.environ.get("HF_SECRET", "")

if not HF_KEY or not HF_SECRET:
    print("ERROR: Set HF_KEY and HF_SECRET environment variables.")
    print('  export HF_KEY="your-api-key"')
    print('  export HF_SECRET="your-api-secret"')
    sys.exit(1)

HF_HEADERS = {
    "Authorization": f"Key {HF_KEY}:{HF_SECRET}",
    "Content-Type": "application/json",
}

# ── Shot Types + Prompts ────────────────────────────────────────────────

SHOTS = [
    {
        "id": "product_hero",
        "name": "Product Hero",
        "ratio": "4:5",
        "description": "Eye-level arrangement on linen surface, warm directional light, shallow DOF, terracotta vase",
        "prompt": (
            "Professional product photograph of a seasonal flower arrangement in a "
            "handmade matte terracotta ceramic vase, placed on a draped raw linen cloth "
            "on a wooden surface. Eye-level camera angle, shot on medium format camera. "
            "Warm directional natural light from the left side, colour temperature around "
            "4000K, creating soft dimensional shadows. Shallow depth of field at f/2.8 — "
            "foremost petals and stems tack-sharp, background falling to a soft warm cream "
            "blur. Generous negative space above and to the right in warm linen-cream tones, "
            "approximately 55% of the frame. The arrangement features white garden roses, "
            "dried eucalyptus branches, chamomile, and dried oat grass — organic and slightly "
            "asymmetric, not overly manicured. Colour palette: warm creams, terracotta, muted "
            "sage greens, natural whites. Warm colour grade with lifted shadows, slightly "
            "desaturated greens shifted toward sage-eucalyptus tones, no crushed blacks. "
            "The image feels tactile, warm, and considered — like a premium lifestyle brand "
            "product shot. No text, no logos, no watermarks."
        ),
    },
    {
        "id": "product_detail",
        "name": "Petal Detail",
        "ratio": "1:1",
        "description": "Extreme close-up texture shot, macro DOF, warm sidelight on petals",
        "prompt": (
            "Extreme close-up macro photograph of flower petals, shot with very shallow "
            "depth of field at f/2.0 on a macro lens. Natural warm sidelight from the left "
            "creating gentle shadow across the petal surface texture. A single garden rose "
            "in sharp focus showing the delicate surface texture, subtle colour gradation "
            "from cream-white to soft blush at the petal edges. Background is a soft "
            "defocused blur of warm linen and sage green tones. One small dewdrop visible "
            "on a petal edge catching the light. Colour grade: warm, gently desaturated, "
            "film-like quality with lifted shadows. The image should feel deeply tactile — "
            "the viewer should want to reach out and touch the petal. Shot on professional "
            "camera, no AI artefacts on textures or surfaces. No text, no watermarks."
        ),
    },
    {
        "id": "kitchen_table",
        "name": "Kitchen Table",
        "ratio": "4:5",
        "description": "Self-purchase lifestyle — morning light, arrangement on kitchen table, quiet contentment",
        "prompt": (
            "Lifestyle photograph of a flower arrangement as centrepiece on a kitchen table "
            "in soft morning light. Warm directional sunlight streaming from a window on "
            "the left side, creating gentle shadows across the table. A matte ceramic vase "
            "in warm clay tones holds white roses, dried eucalyptus, and chamomile on a "
            "light timber table. A ceramic coffee cup sits partially visible at the frame "
            "edge. A woman's hand and forearm reach into frame from the right, gently "
            "adjusting a stem — natural, unposed gesture. Shallow depth of field with the "
            "flowers as focal point. The kitchen is minimal and warm — not styled for a "
            "photoshoot, but naturally beautiful. Australian home interior. Colour palette: "
            "warm creams, sage green, natural timber, terracotta. The mood is quiet morning "
            "contentment — unhurried, genuine, a private moment. Warm colour grade, "
            "desaturated greens, lifted shadows, no harsh contrast. Shot at eye level on "
            "professional camera. No text, no watermarks."
        ),
    },
    {
        "id": "doorstep_arrival",
        "name": "Doorstep Arrival",
        "ratio": "4:5",
        "description": "Gifting hero — delivery box on Australian doorstep, warm light, genuine moment",
        "prompt": (
            "Lifestyle photograph of a flower delivery arriving at an Australian home. A "
            "rectangular kraft-coloured cardboard box with a terracotta-coloured stripe "
            "accent sits on a front doorstep made of sandstone pavers. A woman's hands "
            "reach down into the frame from above, about to pick up the box — the gesture "
            "is natural and genuine, not posed. The home exterior shows a white rendered "
            "wall with a simple timber front door. Warm natural daylight, soft shadows "
            "from overhead. The box is the hero of the image, positioned in the centre-lower "
            "third of the frame. A doormat and the edge of a potted plant are partially "
            "visible for context. Colour palette: warm linen kraft, terracotta accents, "
            "sandstone, sage green foliage. The mood is genuine pleasant discovery — "
            "someone has just noticed the delivery. Not performed surprise. Shot from above "
            "at approximately 45 degrees. Warm colour grade, lifted shadows, natural tones. "
            "No text on the box, no logos, no watermarks."
        ),
    },
    {
        "id": "tissue_reveal",
        "name": "Tissue Reveal",
        "ratio": "4:5",
        "description": "Unboxing moment 3 — hands parting tissue paper, first glimpse of stems",
        "prompt": (
            "Close-up overhead photograph of hands opening a flower delivery box, gently "
            "parting sage-green tissue paper to reveal the first glimpse of flower stems "
            "and foliage inside. Shot from above at a 45-degree angle. The box is "
            "kraft-coloured, open, sitting on a linen cloth surface. The tissue paper is "
            "a muted eucalyptus sage green — the colour contrast between the green tissue "
            "and the cream-white flowers creates a moment of visual surprise. The hands "
            "are feminine, natural nails, no heavy jewellery — just a simple thin gold "
            "ring. Warm natural sidelight from the left. Shallow depth of field — hands "
            "and tissue paper in sharp focus, the box edges softly blurred. The mood is "
            "anticipation and discovery — the moment just before the full reveal. Warm "
            "colour grade, desaturated greens shifted toward eucalyptus tones, lifted "
            "shadows. Shot on professional camera. No text, no watermarks."
        ),
    },
    {
        "id": "living_room",
        "name": "Living Room Day 3",
        "ratio": "4:5",
        "description": "Longevity proof — settled arrangement in real living room, afternoon light",
        "prompt": (
            "Lifestyle photograph of a flower arrangement in a living room on its third "
            "day — the flowers are slightly relaxed and naturally opened but still "
            "beautiful, not wilted. A matte ceramic vase in warm terracotta tones sits "
            "on a low timber side table next to a linen-upholstered armchair. Warm "
            "afternoon light comes through a window, casting long soft shadows. A throw "
            "blanket drapes over the armchair arm. The room feels genuinely lived-in — a "
            "book on the armchair, a candle nearby. The arrangement features white roses "
            "that have softened and opened further, eucalyptus that has dried slightly, "
            "giving the composition a natural, settled quality. Shallow depth of field "
            "with the arrangement as focal point. Australian home interior, warm neutral "
            "palette. The mood is settled domestic warmth — these flowers live here, they "
            "weren't just placed for a photo. Warm colour grade, lifted shadows, gentle "
            "desaturation. Shot at eye level. No text, no watermarks."
        ),
    },
    # ── New grid-filling shots ──
    {
        "id": "product_closeup",
        "name": "Product Close-Up",
        "ratio": "1:1",
        "description": "Tight crop of arrangement top, 1:1 grid format, warm overhead angle",
        "prompt": (
            "Professional close-up photograph of the top of a flower arrangement, shot "
            "from slightly above at approximately 30 degrees. A matte sandstone ceramic "
            "bowl holds soft blush garden roses, dried eucalyptus sprigs, and white "
            "chamomile — the arrangement viewed from above reveals the organic spiral "
            "of stems and blooms. Shot on medium format camera with shallow depth of "
            "field at f/2.8, the centre blooms tack-sharp, the outer edges falling to "
            "a soft blur. Warm directional natural light from upper left, colour "
            "temperature around 4000K. The background is a raw linen surface in warm "
            "cream tones, visible around the edges of the bowl. Colour palette: warm "
            "linen-cream, soft blush pink, muted sage-eucalyptus greens, sandstone. "
            "Warm colour grade, slightly desaturated greens, lifted shadows, gentle "
            "film-like quality. The image feels intimate and tactile — close enough to "
            "smell the roses. No text, no logos, no watermarks."
        ),
    },
    {
        "id": "product_full",
        "name": "Product Full Frame",
        "ratio": "4:5",
        "description": "Full arrangement with maximum negative space, editorial framing",
        "prompt": (
            "Editorial product photograph of a flower arrangement in a handmade matte "
            "terracotta vase, placed on a warm stone surface. The arrangement is "
            "positioned in the lower-left third of the frame, leaving approximately "
            "60% generous negative space in warm linen-cream tones above and to the "
            "right. The arrangement features pale pink peonies, dried oat grass, "
            "eucalyptus branches, and white ranunculus — organic, slightly wild, not "
            "overly structured. Eye-level camera angle, shot on medium format camera. "
            "Warm directional natural light from the right side at colour temperature "
            "3800K, creating long soft shadows extending to the left. Very shallow "
            "depth of field at f/2.0 — the front blooms sharp, everything behind "
            "falling to a warm cream blur. Warm colour grade with lifted shadows, "
            "desaturated greens shifted toward sage tones, no crushed blacks. The mood "
            "is considered editorial minimalism — like a fashion brand lookbook page. "
            "No text, no logos, no watermarks."
        ),
    },
    {
        "id": "lifestyle_wide",
        "name": "Lifestyle Wide",
        "ratio": "4:5",
        "description": "Broader room scene with arrangement as environmental element, warm afternoon",
        "prompt": (
            "Lifestyle photograph of an Australian home interior, wider framing showing "
            "a full room corner. A flower arrangement in a matte ceramic vase sits on "
            "a low timber console table against a warm white rendered wall. The "
            "arrangement features white garden roses and dried eucalyptus. The room "
            "includes a linen-upholstered chair, a woven jute rug, and a single framed "
            "botanical print leaning against the wall. Warm afternoon light streams "
            "from a window on the left, casting long diagonal shadows across the floor "
            "and wall. The flowers are one element in a considered, lived-in space — "
            "not the sole subject but clearly the warmest point in the frame. Shallow "
            "depth of field at f/3.5, flowers and vase in focus, room edges softly "
            "blurred. Colour palette: warm linen-cream walls, natural timber, sage "
            "eucalyptus, terracotta ceramic accent. Warm colour grade, lifted shadows, "
            "desaturated greens. The mood is quiet domestic beauty — a space that "
            "someone actually lives in and has taken care to make beautiful. Shot at "
            "eye level on professional camera. No text, no watermarks."
        ),
    },
    {
        "id": "texture_stems",
        "name": "Texture Detail — Stems",
        "ratio": "1:1",
        "description": "Macro texture shot of eucalyptus stems and leaves, botanical study feel",
        "prompt": (
            "Extreme close-up macro photograph of dried eucalyptus stems and leaves "
            "against a raw linen cloth surface. Shot with very shallow depth of field "
            "at f/2.0 on a macro lens. Natural warm sidelight from the left creating "
            "subtle shadows that reveal the leaf texture and stem structure. Two or "
            "three eucalyptus branches arranged casually — not styled, as if just set "
            "down. The leaves show the desaturated sage-green tones with subtle silver "
            "undertones, the stems a warm brown. Background is soft warm linen in "
            "cream tones, gently out of focus. Colour grade: warm, gently desaturated, "
            "greens shifted toward sage-eucalyptus tones, lifted shadows with film-like "
            "quality. The image should feel like a botanical study — quiet, observational, "
            "deeply textural. Shot on professional camera, no AI artefacts on leaf "
            "textures or surfaces. No text, no watermarks."
        ),
    },
    {
        "id": "packaging_flat",
        "name": "Packaging Flat Lay",
        "ratio": "4:5",
        "description": "Open box from above showing tissue, note card, and first glimpse of stems",
        "prompt": (
            "Overhead flat-lay photograph of an open flower delivery box on a raw linen "
            "cloth surface. Shot from directly above. The kraft-coloured box is open, "
            "showing sage-green tissue paper neatly folded back to reveal the tops of "
            "cream-white flower stems and eucalyptus foliage. A small personal note card "
            "in warm linen-cream paper with handwritten text sits beside the box. A "
            "terracotta-coloured ribbon curls loosely near the box edge. The linen "
            "surface fills the frame around the box, providing approximately 40% "
            "negative space in warm cream tones. Warm natural light from above-left, "
            "soft shadows from the box edges and tissue folds. Shallow depth of field — "
            "note card and tissue sharp, box corners softly blurred. Colour palette: "
            "kraft paper, sage-eucalyptus green, warm linen-cream, terracotta accent. "
            "Warm colour grade, desaturated greens, lifted shadows. The mood is "
            "anticipation and considered presentation — every element placed with care. "
            "No branding on the box, no logos, no text, no watermarks."
        ),
    },
]

# ── Critic System Prompt ────────────────────────────────────────────────

CRITIC_SYSTEM = """You are a brand photography critic for "Bower" — a premium Australian DTC floral brand. Evaluate AI-generated images against Bower's art direction rubric and suggest specific prompt improvements.

BOWER ART DIRECTION RUBRIC:
- LIGHTING: Warm directional natural light (3500-4500K). Soft shadows with dimension. No flat lighting, no flash, no cool/blue casts. Morning or golden hour feel.
- COMPOSITION: 50-60% negative space in warm linen tones. Shallow DOF (f/2.0-3.5). Eye-level or slightly below for hero shots.
- COLOUR: Warm palette — linen (#EDE3D5), terracotta (#BF6B4A), espresso (#2B2220), eucalyptus (#7E9187). +10-15% warm shift. Greens desaturated toward sage. Shadows lifted, never crushed. No cool/blue tones.
- STYLING: Raw linen, warm stone, light timber, matte ceramics. Max 2 props. Never: plastic, bright coloured props, generic glass vases, confetti.
- TECHNICAL: Sharp focus on subject. No AI artefacts (warped hands, impossible physics, uncanny textures). Professional camera quality.
- BRAND ALIGNMENT: Tactile minimalism. Feels like a fashion brand that sells flowers. Warm, considered, quietly confident. NOT: gift shop, bridal, craft market, stock photography.

Respond ONLY with valid JSON (no markdown, no backticks, no preamble):
{
  "overall_score": <1-10>,
  "dimensions": {
    "lighting": {"score": <1-10>, "note": "<15 words max>"},
    "composition": {"score": <1-10>, "note": "<15 words max>"},
    "colour": {"score": <1-10>, "note": "<15 words max>"},
    "styling": {"score": <1-10>, "note": "<15 words max>"},
    "technical": {"score": <1-10>, "note": "<15 words max>"},
    "brand_alignment": {"score": <1-10>, "note": "<15 words max>"}
  },
  "verdict": "PASS or ITERATE",
  "prompt_revisions": "<If ITERATE: exact words to add/remove/change in the prompt. If PASS: empty string>"
}"""

# ── API Functions ───────────────────────────────────────────────────────

def submit_generation(prompt: str, aspect_ratio: str, max_retries: int = 3) -> str:
    """Submit to Higgsfield, return request_id. Retries on 5xx errors."""
    ar = RATIO_MAP.get(aspect_ratio, aspect_ratio)
    if ar not in VALID_RATIOS:
        ar = "3:4"  # safe fallback
    for attempt in range(max_retries):
        res = requests.post(
            f"{HF_BASE}/{HF_MODEL}",
            headers=HF_HEADERS,
            json={"prompt": prompt, "aspect_ratio": ar},
            timeout=30,
        )
        if res.status_code >= 500 and attempt < max_retries - 1:
            wait = 10 * (attempt + 1)
            print(f"    {res.status_code} — retrying in {wait}s (attempt {attempt+1}/{max_retries})")
            time.sleep(wait)
            continue
        res.raise_for_status()
        data = res.json()
        return data["request_id"]


def poll_until_done(request_id: str) -> str | None:
    """Poll until completed. Returns image URL or None."""
    start = time.time()
    while time.time() - start < POLL_TIMEOUT:
        time.sleep(POLL_INTERVAL)
        res = requests.get(
            f"{HF_BASE}/requests/{request_id}/status",
            headers=HF_HEADERS,
            timeout=15,
        )
        data = res.json()
        status = data.get("status", "unknown")
        elapsed = int(time.time() - start)
        print(f"    [{elapsed}s] status: {status}")

        if status == "completed":
            return data["images"][0]["url"]
        elif status == "failed":
            print(f"    FAILED: {data.get('error', 'unknown')}")
            return None
        elif status == "nsfw":
            print("    NSFW filter triggered — prompt needs adjustment")
            return None

    print("    TIMEOUT after 5 minutes")
    return None


def download_image(url: str, path: Path) -> bool:
    """Download image to local path."""
    try:
        res = requests.get(url, timeout=60)
        res.raise_for_status()
        path.write_bytes(res.content)
        return True
    except Exception as e:
        print(f"    Download error: {e}")
        return False


def image_to_base64(path: Path) -> str:
    """Convert image file to base64 string."""
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def critique_image(image_url: str, shot_name: str, prompt: str) -> dict | None:
    """Send image URL to Claude Sonnet for critique. Returns parsed JSON."""
    try:
        res = requests.post(
            ANTHROPIC_URL,
            headers=ANTHROPIC_HEADERS,
            json={
                "model": CLAUDE_MODEL,
                "max_tokens": 1000,
                "system": CRITIC_SYSTEM,
                "messages": [{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "url",
                                "url": image_url,
                            },
                        },
                        {
                            "type": "text",
                            "text": (
                                f'Shot type: "{shot_name}". '
                                f"Generation prompt:\n{prompt}\n\n"
                                "Score against the Bower rubric."
                            ),
                        },
                    ],
                }],
            },
            timeout=90,
        )
        res.raise_for_status()
        data = res.json()
        text = "".join(b.get("text", "") for b in data.get("content", []))
        clean = text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception as e:
        print(f"    Critique error: {e}")
        return None


def apply_revisions(prompt: str, revisions: str) -> str:
    """Ask Claude to apply revisions to the prompt and return the new prompt."""
    try:
        res = requests.post(
            ANTHROPIC_URL,
            headers=ANTHROPIC_HEADERS,
            json={
                "model": CLAUDE_MODEL,
                "max_tokens": 2000,
                "system": (
                    "You are a prompt engineer. Apply the requested revisions to the "
                    "image generation prompt. Return ONLY the revised prompt text — "
                    "no explanation, no markdown, no backticks."
                ),
                "messages": [{
                    "role": "user",
                    "content": (
                        f"CURRENT PROMPT:\n{prompt}\n\n"
                        f"REVISIONS TO APPLY:\n{revisions}\n\n"
                        "Return the revised prompt."
                    ),
                }],
            },
            timeout=30,
        )
        res.raise_for_status()
        data = res.json()
        return "".join(b.get("text", "") for b in data.get("content", [])).strip()
    except Exception as e:
        print(f"    Revision error: {e}, keeping original prompt")
        return prompt


# ── Main Loop ───────────────────────────────────────────────────────────

def run_shot(shot: dict, library: list) -> dict | None:
    """Run the full generate → critique → iterate loop for one shot type."""
    print(f"\n{'='*60}")
    print(f"  {shot['name']}  ({shot['ratio']})")
    print(f"  {shot['description']}")
    print(f"{'='*60}")

    prompt = shot["prompt"]
    best_result = None

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n  ── Iteration {iteration}/{MAX_ITERATIONS} ──")

        # Generate
        print(f"  Submitting to Higgsfield Soul...")
        try:
            request_id = submit_generation(prompt, shot["ratio"])
            print(f"    request_id: {request_id[:16]}...")
        except Exception as e:
            print(f"    Submit error: {e}")
            break

        # Poll
        print(f"  Polling for completion...")
        image_url = poll_until_done(request_id)
        if not image_url:
            print("  Generation failed — skipping to next iteration")
            continue

        # Skip local download (CDN not in egress allowlist) — pass URL to Claude directly
        print(f"  Image ready: {image_url[:60]}...")

        # Critique via URL
        print(f"  Sending to Claude for critique...")
        critique = critique_image(image_url, shot["name"], prompt)

        if not critique:
            print("  Critique failed — saving image without score")
            best_result = {
                "shot_id": shot["id"],
                "shot_name": shot["name"],
                "prompt": prompt,
                "image_path": "",
                "image_url": image_url,
                "score": None,
                "iteration": iteration,
            }
            continue

        score = critique.get("overall_score", 0)
        verdict = critique.get("verdict", "ITERATE")
        print(f"\n  Score: {score}/10 — {verdict}")

        # Print dimension scores
        dims = critique.get("dimensions", {})
        for dim_name, dim_data in dims.items():
            s = dim_data.get("score", "?")
            n = dim_data.get("note", "")
            marker = "✓" if isinstance(s, int) and s >= 7 else "✗"
            print(f"    {marker} {dim_name}: {s}/10 — {n}")

        result = {
            "shot_id": shot["id"],
            "shot_name": shot["name"],
            "prompt": prompt,
            "image_path": "",
            "image_url": image_url,
            "score": score,
            "iteration": iteration,
            "critique": critique,
        }

        if not best_result or (score and (not best_result.get("score") or score > best_result["score"])):
            best_result = result

        # Check pass
        if score >= PASS_THRESHOLD or verdict == "PASS":
            print(f"\n  ✓ PASSED — prompt locked for {shot['name']}")
            break

        # Apply revisions
        revisions = critique.get("prompt_revisions", "")
        if revisions and iteration < MAX_ITERATIONS:
            print(f"\n  Applying revisions: {revisions[:100]}...")
            prompt = apply_revisions(prompt, revisions)
            print(f"  Prompt updated for next iteration")
        elif iteration >= MAX_ITERATIONS:
            print(f"\n  Max iterations reached — saving best result (score: {best_result.get('score', '?')})")

    return best_result


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load existing library
    library = []
    if LIBRARY_FILE.exists():
        library = json.loads(LIBRARY_FILE.read_text())

    print("\n" + "="*60)
    print("  BOWER PROMPT LAB")
    print("  Model: Higgsfield Soul · Critic: Claude Sonnet")
    print(f"  Threshold: {PASS_THRESHOLD}/10 · Max iterations: {MAX_ITERATIONS}")
    print(f"  Output: {OUTPUT_DIR}")
    print("="*60)

    # Show menu
    print("\n  Shot types:")
    for i, shot in enumerate(SHOTS):
        print(f"    {i+1}. {shot['name']} ({shot['ratio']}) — {shot['description']}")
    print(f"    {len(SHOTS)+1}. Run ALL shots")
    print(f"    0. Exit")

    # CLI arg or interactive menu
    if len(sys.argv) > 1:
        choice = sys.argv[1].strip()
    else:
        choice = input("\n  Select (number): ").strip()

    if choice == "0":
        return

    if choice == str(len(SHOTS) + 1):
        shots_to_run = SHOTS
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(SHOTS):
                shots_to_run = [SHOTS[idx]]
            else:
                print("Invalid choice")
                return
        except ValueError:
            print("Invalid choice")
            return

    # Run selected shots
    for shot in shots_to_run:
        result = run_shot(shot, library)
        if result:
            library.append(result)
            LIBRARY_FILE.write_text(json.dumps(library, indent=2))
            print(f"  Saved to library ({len(library)} total)")

    # Summary
    print("\n" + "="*60)
    print("  SESSION COMPLETE")
    print("="*60)
    print(f"  Images: {OUTPUT_DIR}")
    print(f"  Library: {LIBRARY_FILE}")
    print(f"  Total saved: {len(library)} prompts")
    for item in library:
        s = item.get("score", "?")
        print(f"    • {item['shot_name']}: {s}/10 (iter {item.get('iteration', '?')})")
    print()

    # Save URLs for access
    for item in library:
        url = item.get("image_url", "")
        if url:
            print(f"  Image URL: {url}")


if __name__ == "__main__":
    main()
