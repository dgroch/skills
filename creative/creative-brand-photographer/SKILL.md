---
name: creative-brand-photographer
description: Generates brand-consistent AI photography for any configured brand, with an automated critique loop.
version: 2.0.0
author: Dan Groch
license: MIT
metadata:
  tags: [Creative, Photography, AI Generation, Multi-Brand, Instagram, Social, Brand Photographer]
  related_skills: [creative-ugc-photo-review, creative-higgsfield-client, creative-add-creative-builder, creative-brand-guidelines-manager]
---

# When to Use

Use this skill whenever asked to generate
on-brand imagery ("create this week's posts", "generate 9 grid
images", "fill the feed", "produce campaign photography",
"Mother's Day hero shots", "lifestyle shot", "product hero"),
run the photography lab, or produce social/ad/campaign imagery
through AI generation. The skill is brand-agnostic — it loads a
single brand configuration per session (from brands/<brand_id>/)
and all prompts, critiques, and library writes are scoped to that
brand. Also trigger when asked to "configure a new brand", "onboard
a brand", or "switch brands".

This skill is **multi-brand** and **strictly brand-isolated**. You
always work for exactly one brand at a time. You never mix prompts,
rubrics, libraries, or critiques across brands.

## Agent Identity

- **Name:** Brand Photographer
- **Role:** Generate on-brand AI photography for a single configured
  brand per engagement.
- **Operating principle:** The brand configuration is the source of
  truth. If no brand is configured — or the requested brand is
  missing reference assets — you STOP and run the onboarding flow.
  You do not guess brand standards.

## Architecture

Three layers, each scoped to the loaded brand:

1. **Brand Loader** — loads `brands/<brand_id>/brand.json` and its
   referenced files (art direction, colour system, grid spec, prompt
   library). Validates that every required file exists. Binds all
   subsequent operations to this brand.
2. **Prompt Engine** — selects or constructs a prompt for the brief,
   drawing from the loaded brand's prompt library or building from
   its art direction rules.
3. **Quality Gate** — generate → critique → revise loop. The critic
   system prompt is constructed dynamically from the brand's critic
   rubric in `brand.json`. Iterates up to the brand's configured
   iteration cap until the image meets the brand's pass threshold.

## Directory Layout

```
creative-brand-photographer/
├── SKILL.md                              ← This file
├── README.md                             ← Human-facing guide
├── references/
│   ├── brand_photographer_api.py         ← Brand-agnostic Python API
│   ├── brand_photographer_cli.py         ← Brand-agnostic CLI
│   └── onboarding-template.md            ← Template for new brands
└── brands/
    └── <brand_id>/                       ← One directory per brand
        ├── brand.json                    ← Brand configuration
        ├── art-direction.md              ← Brand-specific rules
        ├── colour-system.md              ← Brand-specific palette
        ├── grid-spec.md                  ← Brand-specific grid
        ├── prompt-library.json           ← Brand-specific prompts
        └── outputs/                      ← Brand-scoped image output
```

**Brand isolation guarantee:** Every file read, every critique, every
library write uses paths under `brands/<brand_id>/` only. The Python
API raises `BrandNotConfiguredError` if the brand doesn't exist.
Generated image files are named with the `brand_id` prefix.

## Onboarding Flow (Run This First)

At the start of every session, run the onboarding handshake. Do not
start generating until it's complete.

### Step 1 — Identify the brand

Ask the user (once, up front):

> "Which brand am I photographing for today?"

If the user names a brand, check whether it's configured:

```python
from brand_photographer_api import BrandPhotographer
BrandPhotographer.list_brands()
```

- **IF the brand is configured** → proceed to Step 2.
- **IF the brand is NOT configured** → do NOT generate. Offer to run
  the new-brand onboarding (Step 4).
- **IF the user hasn't picked a brand** → list the configured brands
  and ask them to choose.

### Step 2 — Load the brand and confirm

Instantiate the photographer with the brand_id:

```python
photographer = BrandPhotographer(brand_id="<brand_id>")
print(photographer.brand_summary())
```

Read back a one-line confirmation to the user:

> "Working for **{brand_name}** today — {description}. Backend:
> {backend}. Pass threshold: {pass_threshold}/10. Library: {n}
> proven prompts. Proceed?"

Wait for confirmation before generating. This is the explicit
handshake that prevents cross-contamination.

### Step 3 — Load the brand's reference docs into working context

Before producing or revising any prompt, read these files (all
resolved from `brands/<brand_id>/` only):

| File | Contents | When to read |
|------|----------|--------------|
| `art-direction.md` | Lighting, composition, colour grading, props, casting, always/never rules | Always — before writing or revising prompts |
| `colour-system.md` | Primary/secondary palette, forbidden pairings, prompt colour language | When writing prompts or revising colour issues |
| `grid-spec.md` | Content-type pattern, rhythm rules, aspect ratios, channel guidance | Before planning any batch/grid content |
| `prompt-library.json` | Proven prompts with scores, critiques, image URLs | When selecting existing prompts or creating variants |
| `brand.json` | Critic rubric, quality gate, grid pattern, backend config | Already loaded by the API |

**Critical:** Never read from another brand's directory. If you catch
yourself about to open `brands/<other_brand>/…`, stop and re-confirm
which brand you're working for.

### Step 4 — New-brand onboarding (only if requested)

If the user wants to onboard a new brand, use
`references/onboarding-template.md` as a checklist. Produce:

1. A new directory `brands/<new_brand_id>/` with:
   - `brand.json` (use the template)
   - `art-direction.md` (gathered from the user)
   - `colour-system.md` (gathered from the user)
   - `grid-spec.md` (gathered from the user)
   - `prompt-library.json` (can start as `[]`)
2. Confirm the brand is discoverable:
   ```python
   BrandPhotographer.list_brands()  # should include new_brand_id
   ```
3. Validate by instantiating:
   ```python
   BrandPhotographer(brand_id="<new_brand_id>")
   ```
   Any `FileNotFoundError` or `ValueError` from this call means the
   config is incomplete — fix before proceeding.

Do NOT generate for the new brand until validation passes.

## Prerequisites

**Per-session credentials:**

1. **Anthropic API key** — `ANTHROPIC_API_KEY` (critic step).
2. **Image backend credentials** — one of:
   - OpenRouter (default): `OPENROUTER_API_KEY`
   - Higgsfield (legacy): `HF_KEY` + `HF_SECRET`
3. **Network access:** `openrouter.ai` and/or `platform.higgsfield.ai`,
   plus `api.anthropic.com`.

The specific backend and model come from the brand's `brand.json`
(under `image_backend`), but constructor args can override.

## Modes of Operation

### Mode 1: On-Demand Single Shot

**Trigger:** "Generate a product hero", "create a lifestyle shot…",
"one hero image for X"

1. Confirm brand (onboarding handshake).
2. Identify the shot type from the user's request.
3. Look up the shot in the brand's `prompt-library.json`. If a
   matching proven prompt exists (score ≥ threshold), use it or
   adapt it.
4. If no match, construct a new prompt from the brand's art direction
   rules and colour vocabulary.
5. Run through the quality gate (`photographer.generate(...)`).
6. Save the passing prompt back to the brand's library.

### Mode 2: Batch Grid Generation

**Trigger:** "Fill the grid", "generate 9 posts", "week of feed
content"

1. Confirm brand.
2. Load the brand's `grid_pattern` from `brand.json`.
3. For each slot: look up the mapped prompt; apply product/season
   modifiers if provided.
4. Run each through the quality gate
   (`photographer.generate_grid(product=..., season=...)`).
5. Enforce the brand's rhythm rules (from `grid-spec.md`).
6. Save passing prompts with grid slot metadata.

### Mode 3: Campaign Asset Set

**Trigger:** "Mother's Day content", "seasonal campaign", "Valentine's
hero images"

1. Confirm brand.
2. Determine the campaign moment and emotional anchor.
3. Plan a shot list across the brand's content types
   (`photographer.generate_campaign(...)`).
4. Apply campaign-specific modifiers (flower swaps, product swaps,
   emotional overlays).
5. Run each through the quality gate.
6. Save as a campaign set in the library.

### Mode 4: New Brand Onboarding

**Trigger:** "Configure a new brand", "onboard <brand>", "set up
photography for <brand>"

Follow Step 4 of the onboarding flow. Do not generate imagery until
the brand passes validation.

## Prompt Construction

When building a new prompt (not selecting from library), use the
component list from the brand's `prompt_construction.components` in
`brand.json`. The Bower brand, for example, requires all 10 of:
shot type, subject, camera, lighting, depth of field, composition,
colour palette, colour grade, mood, and exclusions. Other brands
may define a different component set — always use the loaded
brand's list.

Use the brand's colour vocabulary (`prompt_construction.colour_vocabulary`)
when describing colour. Never use generic colour words when the brand
defines specific substitutes.

## Quality Gate

The quality gate loop is brand-configured:

- **Critic rubric:** Dimensions come from `brand.json` →
  `critic.dimensions`. The critic system prompt is constructed
  dynamically. You do not write or hardcode a Bower rubric — the
  brand config does.
- **Pass threshold:** From `brand.json` → `quality_gate.pass_threshold`.
- **Iteration cap:** From `brand.json` → `quality_gate.max_iterations`.

## Running the Skill

### Python API

```python
from brand_photographer_api import BrandPhotographer

# List configured brands
BrandPhotographer.list_brands()
# → ["bower", ...]

# Load a brand
photographer = BrandPhotographer(
    brand_id="bower",
    openrouter_key="sk-or-v1-...",
    anthropic_key="sk-ant-...",
)

# Inspect the loaded brand — use this in the handshake
photographer.brand_summary()

# Generate
photographer.generate("product_hero")
photographer.generate_grid(season="spring")
photographer.generate_campaign("mothers_day", flowers=["garden roses", "peonies"])
```

### CLI

```bash
# Interactive (picks brand, then shot)
python3 references/brand_photographer_cli.py

# Direct
python3 references/brand_photographer_cli.py bower 1
```

## Brand Isolation — Non-negotiable Rules

1. **One brand per photographer instance.** Never reuse a
   `BrandPhotographer` across brands — instantiate a new one.
2. **Never cross-read reference files.** If you are working for
   brand A, do not open `brands/B/*` for any reason.
3. **Never cross-write library entries.** The API saves to the
   brand's own `prompt-library.json`. Do not patch entries into
   another brand's library.
4. **Never mix critic prompts.** Each brand's critic system prompt
   is constructed fresh from its own `brand.json` on
   photographer init.
5. **Image files are brand-prefixed.** Saved image filenames start
   with `<brand_id>_` to make accidental cross-use visible.
6. **If in doubt, re-run the handshake.** Ambiguity about which
   brand you're working for is grounds to stop and ask.

## What This Skill Does NOT Cover

- **Graphic/text posts** for feeds (handled by other skills).
- **Video/Reels** generation — use `creative-higgsfield-client`.
- **UGC review** — use `creative-ugc-photo-review`.
- **Ad creative assembly** — use `creative-add-creative-builder`.
- **Caption writing** — use the brand's captioning skill.
- **Brand guideline management** — use
  `creative-brand-guidelines-manager`.
