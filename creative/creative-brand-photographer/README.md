# Brand Photographer

Multi-brand AI photography generator. One agent, many brands — strict
brand isolation.

The **Brand Photographer** agent loads a single brand configuration
per session and generates on-brand AI photography through a
generate → critique → revise loop. Each brand has its own art
direction, colour system, grid spec, prompt library, and seed metadata.
The default backend remains local files under `brands/<brand_id>/`; the
same API can also use a Notion data source as the canonical backend by
setting `BRAND_PHOTOGRAPHER_STORAGE=notion`. Seed metadata can also be synced from the Brand Asset Manifest database and resolved through Brand CDN preview URLs for model-readable references.

---

## How it works

```
Onboarding → Brand Loader → Prompt Engine → Image Model → Critic → Pass/Revise
                  │                                          │
                  └──── brand-scoped critique/library ────────┘
```

1. **Onboarding** locks the session to a single brand.
2. The **Brand Loader** validates and reads the active backend:
   local `brands/<brand_id>/brand.json` + referenced docs by default,
   or the configured Notion data source in Notion mode.
3. The **Prompt Engine** builds prompts using the brand's art
   direction rules and colour vocabulary.
4. The **Image Model** generates (OpenRouter / Nano Banana by
   default, Higgsfield Soul as legacy).
5. The **Critic** scores the image against the brand's rubric
   (constructed from `brand.json`).
6. Passes are locked into the brand's own library.

---

## Canonical execution

**Always use the bundled reference files.** Do not generate ad-hoc scripts or
inline reimplementations for normal runs — use `brand_photographer_api.py` and
`brand_photographer_cli.py` directly. This ensures consistent behaviour and
makes debugging deterministic.

The critic pipeline runs **Claude CLI first** when `claude` is available on
PATH. Direct Anthropic API calls are the fallback only. The active path is
logged at startup:

```
[critic] Claude CLI found on PATH — using CLI mode
```
or
```
[critic] Claude CLI not found — falling back to API mode
```

### Smoke test

Verify the intended critic path can execute before running a full generation:

```bash
# 1. Confirm claude CLI is on PATH (expected: a file path)
which claude

# 2. Run the CLI in interactive mode to confirm brand loads and critic path logs correctly
python3 references/brand_photographer_cli.py bower

# 3. Non-interactive single-shot test (pick shot index 1)
python3 references/brand_photographer_cli.py bower 1

# 4. Confirm critic mode in brand_summary (should show "cli" when claude is on PATH)
python3 - <<'EOF'
import sys; sys.path.insert(0, "references")
from brand_photographer_api import BrandPhotographer
p = BrandPhotographer(brand_id="bower")
print(p.brand_summary())
EOF
```

Expected output when CLI is available:

```
[critic] Claude CLI found on PATH — using CLI mode
Brand Photographer configured for 'Bower' (brand_id=bower)
{'critic_mode': 'cli', ...}
```

---

## Quick start

### 1. Set credentials

```bash
# Optional: switch from file-backed storage to the Notion backend
export BRAND_PHOTOGRAPHER_STORAGE=notion
export BRAND_PHOTOGRAPHER_NOTION_DATA_SOURCE_ID="<notion-data-source-id>"
export NOTION_API_KEY="<secret>"

# OPENROUTER_API_KEY is always required for the default image generation backend
export OPENROUTER_API_KEY="sk-or-v1-..."
# Or for Higgsfield (legacy):
# export HF_KEY="..."
# export HF_SECRET="..."

# ANTHROPIC_API_KEY is only needed if the Claude CLI is NOT installed.
# When `claude` is on PATH, the CLI handles critique — no API key required.
export ANTHROPIC_API_KEY="sk-ant-..."   # fallback only
```

### Brand Asset Manifest / CDN sync

To promote discovered asset-manifest rows into generation seeds, use:

```bash
python references/brand_photographer_asset_manifest_sync.py \
  --brand-id fig-and-bloom \
  --manifest-json <drive-video-manifest-backup.json> \
  --category bouquet \
  --dry-run
```

For Notion-to-Notion sync, set `NOTION_BRAND_ASSET_DATABASE_ID` and the Brand
Photographer Notion backend env vars. For CDN publication, add
`--upload-cdn --cdn-bucket <bucket> --cdn-key-prefix seeds/<brand-id>`. Existing
manifest `Preview URL` values are reused as `cdn_url` unless
`--force-cdn-upload` is passed.

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

# Seed-constrained image+text generation (OpenRouter)
photographer.generate(
    "fashion_hero",
    fidelity_mode="strict",
    seed_constraints={
        "must_include_flowers": ["phalaenopsis orchid", "garden rose"],
        "forbidden_substitutions": ["tulip", "gerbera"],
        "composition_rules": ["hero bouquet occupies >= 30% frame"],
        "colour_targets": ["vivid pink + amber"],
    },
)
```

### Seed-constrained fidelity modes

- `fidelity_mode="guided"`: uses selected seeds as references and scores fidelity in critique.
- `fidelity_mode="strict"`: if bouquet fidelity is graded as mismatched, quality gate forces iterate even when overall score is high.

Seed images are passed to OpenRouter as multimodal `image_url` content parts (image + text prompt in one request).

### CLI

```bash
python3 references/brand_photographer_cli.py          # interactive
python3 references/brand_photographer_cli.py bower 1  # direct
```

---

## Storage backends

- `BRAND_PHOTOGRAPHER_STORAGE=file` (default): reads/writes the persistent
  local brand folder.
- `BRAND_PHOTOGRAPHER_STORAGE=notion`: reads/writes brand config,
  reference docs, prompt rows, and seed metadata from the Notion data
  source specified by `BRAND_PHOTOGRAPHER_NOTION_DATA_SOURCE_ID`.

See `references/notion-backend.md` for the schema and migration command.

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
