# Brand Photographer

Multi-brand AI photography generator. One agent, many brands — strict
brand isolation.

The **Brand Photographer** agent loads a single brand configuration
per session and generates on-brand AI photography through a
generate → critique → revise loop. Each brand has its own art
direction, colour system, grid spec, prompt library, and critic
rubric under `brands/<brand_id>/`.

---

## How it works

```
Onboarding → Brand Loader → Prompt Engine → Image Model → Critic → Pass/Revise
                  │                                          │
                  └──── brand-scoped critique/library ────────┘
```

1. **Onboarding** locks the session to a single brand.
2. The **Brand Loader** validates and reads
   `brands/<brand_id>/brand.json` + referenced docs.
3. The **Prompt Engine** builds prompts using the brand's art
   direction rules and colour vocabulary.
4. The **Image Model** generates (OpenRouter / Nano Banana by
   default, Higgsfield Soul as legacy).
5. The **Critic** scores the image against the brand's rubric
   (constructed from `brand.json`).
6. Passes are locked into the brand's own library.

---

## Quick start

### 1. Set credentials

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENROUTER_API_KEY="sk-or-v1-..."
# Or for Higgsfield (legacy):
# export HF_KEY="..."
# export HF_SECRET="..."
```

### 2. Pick a brand

```python
from brand_photographer_api import BrandPhotographer
BrandPhotographer.list_brands()
# → ["bower", ...]
```

### 3. Run

```python
photographer = BrandPhotographer(brand_id="bower")
photographer.brand_summary()    # confirm which brand is loaded

photographer.generate("product_hero")
photographer.generate_grid(season="spring")
photographer.generate_campaign("mothers_day", flowers=["garden roses"])
```

### CLI

```bash
python3 references/brand_photographer_cli.py          # interactive
python3 references/brand_photographer_cli.py bower 1  # direct
```

---

## Directory layout

```
creative-brand-photographer/
├── SKILL.md                         ← Agent instructions
├── README.md                        ← This file
├── references/
│   ├── brand_photographer_api.py    ← Brand-agnostic API
│   ├── brand_photographer_cli.py    ← Brand-agnostic CLI
│   └── onboarding-template.md       ← For adding a new brand
└── brands/
    └── bower/
        ├── brand.json               ← Configuration
        ├── art-direction.md         ← Photography rules
        ├── colour-system.md         ← Palette + language
        ├── grid-spec.md             ← Grid pattern + rhythm
        └── prompt-library.json      ← Proven prompts
```

---

## Brand isolation

Every photographer instance is bound to one `brand_id`. The API only
reads/writes files under `brands/<brand_id>/`. Image outputs are
named `<brand_id>_<timestamp>.<ext>`. Critic system prompts are
constructed from the loaded brand's rubric alone.

To switch brands, instantiate a new `BrandPhotographer` — never reuse
an existing one.

---

## Onboarding a new brand

See `references/onboarding-template.md` for the checklist. In short:

1. Create `brands/<new_brand_id>/`.
2. Populate `brand.json` using the template structure.
3. Author `art-direction.md`, `colour-system.md`, `grid-spec.md`.
4. Seed `prompt-library.json` as `[]` (or with initial drafts).
5. Validate:
   ```python
   BrandPhotographer(brand_id="<new_brand_id>")
   ```
   Any error means the config is incomplete.

---

## Supported brands

| Brand | brand_id | Notes |
|-------|----------|-------|
| Bower | `bower`  | Premium Australian DTC floral brand. Tactile minimalism. |

Add more by following the onboarding flow.

---

## Costs (approx)

| Model           | Per generation  | Best for                    |
|-----------------|-----------------|-----------------------------|
| Nano Banana 2   | $0.02–0.04      | Day-to-day feed content     |
| Nano Banana Pro | $0.08–0.15      | Campaign hero shots         |
| Claude critic   | ~$0.003 / call  | Quality gate scoring        |
