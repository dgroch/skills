# Brand Onboarding Template

Use this checklist to onboard a new brand to the Brand Photographer.
A brand is considered onboarded when `BrandPhotographer(brand_id=...)`
instantiates without raising.

## 1. Gather brand artefacts (from the user)

Before writing any files, collect:

- **Brand identity:** name, short description, product category,
  target channels.
- **Art direction:** lighting rules, composition preferences, colour
  grading direction, props/styling, casting guidance, always/never
  rules.
- **Colour system:** primary + secondary palette with hex values,
  ratio (e.g. 60/30/10), forbidden pairings, prompt colour
  vocabulary.
- **Grid / content spec:** content types, rhythm rules, aspect
  ratios, channel-specific guidance.
- **Seed prompts (optional):** any existing proven prompts with
  scores.

If you can't get all of this, flag the gap and do NOT onboard. Partial
onboarding produces inconsistent output.

## 2. Create the brand directory

```
brands/<brand_id>/
├── brand.json
├── art-direction.md
├── colour-system.md
├── grid-spec.md
└── prompt-library.json
```

`<brand_id>` should be lowercase, hyphen-separated, no spaces.

## 3. Author `brand.json`

Use this structure. Every top-level key is required unless noted.

```json
{
  "brand_id": "<brand_id>",
  "brand_name": "<Brand Name>",
  "description": "<One-line brand description>",
  "product_category": "<category>",
  "channels": ["instagram", "email", "social"],
  "references": {
    "art_direction": "art-direction.md",
    "colour_system": "colour-system.md",
    "grid_spec": "grid-spec.md",
    "prompt_library": "prompt-library.json"
  },
  "image_backend": {
    "default": "openrouter",
    "model": "google/gemini-3.1-flash-image-preview",
    "hero_model": "google/gemini-3-pro-image-preview"
  },
  "quality_gate": {
    "pass_threshold": 7,
    "max_iterations": 5
  },
  "critic": {
    "model": "claude-sonnet-4-20250514",
    "dimensions": [
      {"name": "lighting",        "description": "<what good lighting looks like for this brand>"},
      {"name": "composition",     "description": "<composition rules>"},
      {"name": "colour",          "description": "<palette + grading rules>"},
      {"name": "styling",         "description": "<props, surfaces, do/don't>"},
      {"name": "technical",       "description": "<sharpness, artefacts, quality>"},
      {"name": "brand_alignment", "description": "<the 'feels like this brand' test>"}
    ]
  },
  "prompt_construction": {
    "components": [
      "SHOT TYPE", "SUBJECT", "CAMERA", "LIGHTING", "DEPTH OF FIELD",
      "COMPOSITION", "COLOUR PALETTE", "COLOUR GRADE", "MOOD", "EXCLUSIONS"
    ],
    "colour_vocabulary": {
      "<brand term>": "<not this generic term>"
    }
  },
  "grid_pattern": [
    {"slot": "<slot_id>", "type": "<product|lifestyle|detail>", "ratio": "<3:4|1:1|...>"}
  ],
  "slot_to_shot": {
    "<slot_id>": "<shot_id in prompt-library.json>"
  },
  "campaign_plan": [
    ["<shot_id>", "<ratio>"]
  ]
}
```

Notes:
- `critic.dimensions` becomes the critic's scoring schema. Choose
  dimensions that actually discriminate on-brand from off-brand
  output for this brand.
- `grid_pattern` and `slot_to_shot` can omit the grid if the brand
  doesn't use one — set `grid_pattern: []` and `generate_grid()` will
  return `[]`.
- `campaign_plan` is optional; defaults are used if missing.

## 4. Author the reference docs

- `art-direction.md` — the rulebook. Write it as if briefing a human
  photographer. Include sections on lighting, composition, colour
  grading, props/surfaces, casting, always/never.
- `colour-system.md` — palette with hex values, ratios, forbidden
  pairings, and the prompt colour vocabulary (brand term ↔ generic
  term).
- `grid-spec.md` — content types, rhythm rules, aspect ratio mapping,
  channel guidance.

Keep them concise but specific. The critic and prompt engine read
these to stay on brand.

## 5. Seed the prompt library

`prompt-library.json` is a JSON array. Start with `[]` if you have no
proven prompts. Otherwise, add entries in this shape:

```json
{
  "shot_id": "<id>",
  "shot_name": "<Display Name>",
  "prompt": "<full prompt text>",
  "image_url": "",
  "score": null,
  "iteration": 0,
  "status": "draft — run through quality gate to verify",
  "grid_slot": "<slot_id>",
  "content_type": "<product|lifestyle|detail>"
}
```

The quality gate will append passing runs with scores and critiques.

## 6. Validate

```python
from brand_photographer_api import BrandPhotographer

# Must appear in the list
assert "<brand_id>" in BrandPhotographer.list_brands()

# Must instantiate without error (this validates every required file
# and every reference path in brand.json)
photographer = BrandPhotographer(brand_id="<brand_id>")
print(photographer.brand_summary())
```

A successful instantiation is the completion criterion. If it raises:

- `BrandNotConfiguredError` → directory or `brand.json` missing
- `ValueError` (missing key / brand_id mismatch) → fix the config
- `FileNotFoundError` → one of the referenced files is missing
