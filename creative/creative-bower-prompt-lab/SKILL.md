---
name: creative-bower-prompt-lab
description: >
  Generate brand-consistent AI photography for Bower's Instagram feed,
  campaigns, and social content using Higgsfield Soul with an automated
  critique loop. Use this skill whenever: generating feed content
  ("create this week's posts", "generate 9 grid images", "fill the feed"),
  producing campaign photography ("Mother's Day hero shots", "seasonal
  content"), creating on-demand single shots ("product hero for the
  Sunday Collection", "lifestyle shot with orchids"), or expanding the
  prompt library with new shot types or variations. Also trigger when
  asked to "run the prompt lab", "generate Bower photography", "create
  social assets", or any request to produce brand-aligned imagery via
  AI generation for Bower's social channels.
version: 1.0.0
author: Dan Groch
license: MIT
metadata:
  tags: [Creative, Photography, AI Generation, Higgsfield, Instagram, Social]
  related_skills: [photography-ugc-review, higgsfield-api, ad-creative-builder, ugc-photography-generation]
---

# Bower Prompt Lab

Generate brand-consistent AI photography for Bower using Higgsfield Soul,
with Claude Sonnet as an automated art-direction critic. The system produces
images that pass Bower's art direction rubric, respects the Instagram grid
pattern, and builds a growing library of proven prompts.

## Architecture

Three layers, each doing one job:

1. **Grid Planner** — decides *what* to generate based on the 9-post grid
   pattern and content rhythm rules.
2. **Prompt Engine** — selects or constructs a prompt for the brief, drawing
   from the prompt library or building from templates + variables.
3. **Quality Gate** — the generate → critique → revise loop. Submits to
   the image model (OpenRouter/Nano Banana 2 by default, or Higgsfield
   Soul as legacy fallback), sends the result to Claude Sonnet for scoring
   against the art direction rubric, applies revisions if needed, repeats
   up to 5 iterations until the image passes (score ≥ 7/10).

## Prerequisites

**OpenRouter backend (default — recommended):**

1. **OpenRouter API key** — `OPENROUTER_API_KEY` environment variable.
   Supports Nano Banana 2 (`google/gemini-3.1-flash-image-preview`)
   and Nano Banana Pro (`google/gemini-3-pro-image-preview`).
2. **Anthropic API key** — `ANTHROPIC_API_KEY` environment variable.
3. **Network access** — `openrouter.ai` and `api.anthropic.com`.

**Higgsfield backend (legacy):**

1. **Higgsfield credentials** — `HF_KEY` and `HF_SECRET` environment
   variables. Generate at https://cloud.higgsfield.ai.
2. **Anthropic API key** — `ANTHROPIC_API_KEY` environment variable.
3. **Network access** — `platform.higgsfield.ai` and `api.anthropic.com`.

## Reference Files

Read these before generating. They are the source of truth for all
creative decisions.

| File | Contents | When to read |
|------|----------|--------------|
| `references/grid-spec.md` | 9-post grid pattern, content type definitions, rhythm rules, stories vs feed | Always — before planning any content |
| `references/art-direction.md` | Lighting, composition, colour grading, props, casting, unboxing sequence, always/never rules | Always — before writing or revising prompts |
| `references/colour-system.md` | Primary/secondary palette, forbidden pairings, prompt colour language | When writing prompts or revising colour issues |
| `references/prompt-library.json` | Proven prompts with scores, critiques, and image URLs | When selecting existing prompts or creating variants |
| `references/bower_api.py` | Python API wrapper — dual-backend (OpenRouter / Higgsfield) | When generating images programmatically |
| `references/bower_prompt_lab.py` | CLI script with quality gate loop (Higgsfield backend) | When running interactively via command line |

## Modes of Operation

### Mode 1: Batch Grid Generation

**Trigger:** "Generate a week of feed content", "fill the grid",
"create 9 posts for the feed"

**Process:**

1. Read `references/grid-spec.md` to load the 9-post pattern.
2. Determine which grid positions need filling. If the user specifies
   a starting point or existing content, plan around it.
3. For each grid position, produce a brief:
   - Content type (product / lifestyle / detail)
   - Specific shot type (e.g., "product hero", "lifestyle doorstep")
   - Aspect ratio (1:1 for square grid slots, 3:4 for vertical)
   - Product/arrangement if specified, or seasonal default
   - Any campaign overlay (e.g., Mother's Day warmth)
4. Check `references/prompt-library.json` for existing proven prompts
   that match each brief. If a match exists with score ≥ 7, use it
   directly (or create a variant with product/seasonal substitutions).
5. If no match exists, construct a new prompt using the art direction
   rules and colour language from the reference files.
6. Run each prompt through the quality gate.
7. Enforce the rhythm rule: no more than 2 consecutive same-type posts.
   Re-order if needed.
8. Save passing prompts to the library with grid position metadata.

### Mode 2: On-Demand Single Shot

**Trigger:** "Generate a product hero", "create a lifestyle shot with
peonies", "I need a petal detail close-up"

**Process:**

1. Identify the shot type from the user's request.
2. Map it to a grid content type (product / lifestyle / detail).
3. Check the prompt library for a matching base prompt.
4. If found, adapt it (swap flowers, season, vase, etc.).
   If not, construct from art direction rules.
5. Run through the quality gate.
6. Save the passing prompt to the library.

### Mode 3: Campaign Asset Set

**Trigger:** "Mother's Day content", "seasonal campaign shots",
"Valentine's Day hero images", "launch campaign photography"

**Process:**

1. Determine the campaign moment and emotional anchor.
2. Define a campaign colour overlay if applicable (e.g., for
   Valentine's: lean into blush and soft pinks within the warm
   palette; for Mother's Day: lean into garden roses and eucalyptus).
3. Plan a shot list across all three content types — typically:
   - 2× product (hero + close-up)
   - 2× lifestyle (gifting moment + in-home)
   - 1× detail (texture/botanical)
4. Apply campaign-specific prompt modifiers to base templates.
5. Run each through the quality gate.
6. Save as a campaign set in the library.

## Grid Planner Logic

The planner enforces these rules from `references/grid-spec.md`:

### Content Type Distribution (per 9-post cycle)
- **Product:** 3 posts (close-up, hero, full)
- **Lifestyle:** 3 posts (wide, doorstep, table)
- **Detail:** 3 posts (texture, packaging, petal)

### Rhythm Rules
- No more than 2 consecutive posts of the same type
- Text posts: max 1 per 12 posts (not generated by this skill)
- Every image shares the same warm colour grade
- At least 1 human element per 4 product shots

### Aspect Ratio Mapping
Higgsfield Soul supports: `9:16`, `16:9`, `4:3`, `3:4`, `1:1`, `2:3`, `3:2`.

| Grid slot needs | Mapped to |
|-----------------|-----------|
| 4:5 vertical    | 3:4       |
| 1:1 square      | 1:1       |
| 9:16 stories    | 9:16      |
| 16:9 banner     | 16:9      |

## Prompt Construction

When building a new prompt (not selecting from library), follow this
template structure. Every prompt must include ALL of these components
drawn from `references/art-direction.md`:

```
1. SHOT TYPE — "Professional product photograph of..." / "Lifestyle photograph of..." / "Extreme close-up macro photograph of..."
2. SUBJECT — The specific arrangement, flowers, and vessel
3. CAMERA — Angle, format, lens characteristics
4. LIGHTING — Warm directional natural light, colour temperature, shadow quality
5. DEPTH OF FIELD — f-stop, what's sharp, what's blurred
6. COMPOSITION — Negative space percentage, framing, rule of thirds
7. COLOUR PALETTE — Use brand colour language (linen-cream, terracotta, sage-eucalyptus)
8. COLOUR GRADE — Warm shift, desaturated greens, lifted shadows, no crushed blacks
9. MOOD — The emotional quality (tactile, warm, considered, quiet, genuine)
10. EXCLUSIONS — "No text, no logos, no watermarks"
```

### Colour Language (from colour-system.md)

When describing colour in prompts, always use brand vocabulary:

| Say this              | Not this       |
|-----------------------|----------------|
| warm linen-cream      | white          |
| terracotta            | orange         |
| sage-eucalyptus green | green          |
| espresso              | black          |
| sandstone             | beige/tan      |

## Quality Gate (Critic Rubric)

The automated critic scores each image on 6 dimensions (1–10 each):

| Dimension       | What it checks                                                    |
|-----------------|-------------------------------------------------------------------|
| Lighting        | Warm directional natural light (3500–4500K), soft dimensional shadows |
| Composition     | 50–60% negative space, shallow DOF, correct angle                 |
| Colour          | Warm palette match, desaturated greens, lifted shadows            |
| Styling         | Raw linen, matte ceramics, max 2 props, no banned items           |
| Technical       | Sharp focus on subject, no AI artefacts, professional quality     |
| Brand alignment | Tactile minimalism, fashion-brand energy, not gift-shop/bridal    |

**Pass threshold:** Overall score ≥ 7/10 or verdict = "PASS"

**Iteration limit:** 5 attempts per shot. If no pass after 5, save
the best-scoring result and flag for human review.

## Running the Script

### Via Python API (recommended)

```python
import sys
sys.path.insert(0, "path/to/bower-prompt-lab/references")
from bower_api import BowerPromptLab

# OpenRouter + Nano Banana 2 (default)
lab = BowerPromptLab(
    openrouter_key="sk-or-v1-...",
    anthropic_key="sk-ant-...",
)

# Or switch to Nano Banana Pro for hero shots
lab = BowerPromptLab(
    openrouter_key="sk-or-v1-...",
    anthropic_key="sk-ant-...",
    model="google/gemini-3-pro-image-preview",
)

# Or use Higgsfield Soul (legacy)
lab = BowerPromptLab(
    backend="higgsfield",
    hf_key="...", hf_secret="...",
    anthropic_key="sk-ant-...",
)
```

### Via CLI (Higgsfield only)

The `references/bower_prompt_lab.py` script handles the quality gate loop using
the Higgsfield backend.

### Environment Setup
```bash
export HF_KEY="your-api-key"
export HF_SECRET="your-api-secret"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### Run a specific shot
```bash
python3 references/bower_prompt_lab.py <shot_number>
```

### Run interactively (menu)
```bash
python3 references/bower_prompt_lab.py
```

### Extending the Shot List
Add entries to the `SHOTS` list in the script. Each shot needs:
- `id`: slug identifier
- `name`: display name
- `ratio`: aspect ratio (auto-mapped to valid Soul ratios)
- `description`: one-line description
- `prompt`: the full generation prompt

### Output
- Images: URLs from Higgsfield CDN (valid ~7 days)
- Library: `prompt-library.json` with prompts, scores, and critiques
- Best results copied to `/mnt/user-data/outputs/`

## Expanding the Prompt Library

The library grows through use. Passing prompts are automatically saved.

### Variation Strategies

To create variants of existing prompts without starting from scratch:

- **Seasonal swap:** Replace flower types (roses → peonies for spring,
  dahlias for autumn, natives for winter)
- **Product swap:** Replace the vessel (terracotta vase → sandstone
  bowl → ribbed glass)
- **Scene swap:** Same shot type, different setting (kitchen table →
  dining room, bedroom side table)
- **Light swap:** Morning light → golden hour → overcast soft light
- **Mood modifier:** Add campaign emotional overlay without changing
  the base composition

## What This Skill Does NOT Cover

- **Graphic/text posts** for the feed (max 1/12, handled separately)
- **Video/Reels** generation — use `higgsfield-api` with i2v models
- **UGC review** — use `photography-ugc-review` skill
- **Ad creative assembly** — use `ad-creative-builder` skill
- **Caption writing** — use the Instagram caption skill
