# Brand Onboarding Template

Use this checklist to onboard a new brand to the Brand Photographer.
A brand is considered onboarded when `BrandPhotographer(brand_id=...)`
instantiates without raising.

## 1. Gather brand artefacts (from the user)

Before writing any files, collect:

- **Brand identity:** name, short description, product category,
  target channels.
- **Art direction:** lighting rules, composition preferences, colour
  grading direction, props/styling, casting guidance, always/never.
- **Colour system:** primary + secondary palette with hex values,
  ratio, forbidden pairings, prompt colour vocabulary.
- **Grid / content spec:** content types, rhythm rules, aspect ratios,
  channel-specific guidance.
- **Seed assets (optional but recommended):** real brand photography
  for compositing. See Step 5.
- **Seed prompts (optional):** any existing proven prompts with scores.

If you can't get brand identity, art direction, and colour system,
flag the gap and do NOT onboard. Partial onboarding produces
inconsistent output. Seed assets can be gathered after initial config.

## 2. Create the brand directory

```
brands/<brand_id>/
├── brand.json
├── art-direction.md
├── colour-system.md
├── grid-spec.md
├── prompt-library.json
├── seeds.json
└── seeds/
    ├── logos/
    ├── packaging/
    ├── bouquets/
    ├── models/
    ├── spaces/
    ├── lifestyle/
    └── products/
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
    "prompt_library": "prompt-library.json",
    "seeds_manifest": "seeds.json"
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
      {"name": "lighting",        "description": "<brand-specific>"},
      {"name": "composition",     "description": "<brand-specific>"},
      {"name": "colour",          "description": "<brand-specific>"},
      {"name": "styling",         "description": "<brand-specific>"},
      {"name": "technical",       "description": "<brand-specific>"},
      {"name": "brand_alignment", "description": "<brand-specific>"}
    ]
  },
  "prompt_construction": {
    "components": ["..."],
    "colour_vocabulary": {"<brand term>": "<not this generic term>"}
  },
  "grid_pattern": [
    {"slot": "<slot_id>", "type": "<type>", "ratio": "<ratio>"}
  ],
  "slot_to_shot": {
    "<slot_id>": "<shot_id in prompt-library.json or null for non-photo>"
  }
}
```

## 4. Author the reference docs

- `art-direction.md` — the photography rulebook.
- `colour-system.md` — palette, ratios, forbidden pairings, prompt
  colour vocabulary.
- `grid-spec.md` — content types, rhythm rules, aspect ratios,
  channel guidance.

## 5. Set up the seed system

### Create seeds.json

Start with an empty manifest:

```json
{"version": "1.0", "brand_id": "<brand_id>", "seeds": []}
```

### Gather seed assets (priority order)

| Priority | Category    | What to photograph                          | Min |
|----------|-------------|---------------------------------------------|-----|
| 1        | `logo`      | Wordmark, monogram, sticker — PNG, transparent bg | 2   |
| 2        | `bouquet`   | Wrapped bouquets, clean bg, no model. Vary flowers/seasons | 5   |
| 3        | `packaging` | Tissue, ribbon, box, sticker — different angles | 3   |
| 4        | `model`     | Fashion model refs, no bouquet. Varied poses/outfits | 3   |
| 5        | `spaces`    | Store, studio, warehouse (optional)         | 0   |
| 6        | `lifestyle` | Styled interiors with arrangements (optional) | 0   |
| 7        | `products`  | Non-floral products on clean bg (optional)  | 0   |

### Register each asset in seeds.json

Each seed entry needs at minimum:

```json
{
  "id": "<unique-id>",
  "file": "seeds/<category>/<filename>",
  "category": "<logo|packaging|bouquet|model|space|lifestyle|product>",
  "description": "<what's in the image>",
  "tags": ["<searchable>", "<tags>"],
  "use_for": ["<composite|style-reference|overlay|product-shot>"]
}
```

Additional fields by category:
- **bouquet:** `season`, `flowers`, `colour_story`, `pairs_with`
- **model:** `source`, `season`, `outfit_colours`, `pairs_with`
- **logo:** `subcategory`, `variant`, `background`, `format`

### Mode availability

| Seeds available             | Modes unlocked        |
|-----------------------------|-----------------------|
| None                        | Mode A only (text-to-image) |
| Logos + packaging           | Mode A + logo overlay |
| Logos + packaging + bouquets | Mode A + C (style-ref) |
| All of above + models       | Mode A + B (composite) + C |

## 6. Seed the prompt library

`prompt-library.json` starts as `[]` or with draft entries:

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
  "content_type": "<editorial|product|lifestyle|detail>",
  "seeds_used": []
}
```

The `seeds_used` field tracks which seed assets were used in Mode B/C
generations — enabling reproducibility.

## 7. Validate

```python
from brand_photographer_api import BrandPhotographer

assert "<brand_id>" in BrandPhotographer.list_brands()

photographer = BrandPhotographer(brand_id="<brand_id>")
print(photographer.brand_summary())
# Should show: seed count, available modes, library size
```

A successful instantiation is the completion criterion.
