# Creative Brand Photographer — Notion backend

The Brand Photographer can use a Notion data source as its canonical backend for brand configuration, prompt library entries, and seed metadata.

## What moves to Notion

Canonical in Notion:

- Brand config (`brand.json` equivalent)
- Art direction markdown
- Colour system markdown
- Grid spec markdown
- Prompt library entries (`prompt-library.json` rows)
- Seed manifest entries (`seeds.json` rows)

Still local on disk:

- Seed image files under `seeds/<category>/...`
- Generated image outputs under `outputs/`

Reason: generation backends need concrete image bytes/URLs. The Notion row stores the seed metadata and the relative `file` path; the image file remains the source asset used for compositing.

## Storage mode

Default remains file-backed for backwards compatibility.

To use Notion:

```bash
export BRAND_PHOTOGRAPHER_STORAGE=notion
export BRAND_PHOTOGRAPHER_NOTION_DATA_SOURCE_ID="<notion-data-source-id>"
export NOTION_API_KEY="<secret>"
```

`brand_photographer_api.py` also loads `/opt/data/.env` if those variables are not already in the process environment.

## Required Notion data source properties

Create one Notion database/data source with these properties:

- `Name` — title
- `Brand ID` — rich text
- `Artifact` — select
  - `brand_config`
  - `art_direction`
  - `colour_system`
  - `grid_spec`
  - `prompt`
  - `seed`
- `Record ID` — rich text
- `JSON` — rich text
- `Content` — rich text
- `Category` — select (optional convenience field)
- `File` — rich text (optional convenience field)
- `Score` — number (optional convenience field)

The `JSON` and `Content` properties are previews/index fields. Full JSON and long markdown are stored in each page's child blocks so they are not truncated by Notion's 2000-character rich-text property limit.

## Row model

### Brand config

- `Brand ID`: `<brand_id>`
- `Artifact`: `brand_config`
- `Record ID`: `config`
- Page body: compact JSON equivalent of `brand.json`

### Reference docs

One row each:

- `Artifact`: `art_direction`, `colour_system`, `grid_spec`
- `Record ID`: same as artifact name
- Page body: markdown/plain text content

### Prompt library

One row per prompt/result:

- `Artifact`: `prompt`
- `Record ID`: stable import row (`prompt:<shot_id>`) or generated result row (`<shot_id>:<timestamp>`)
- Page body: JSON object equivalent of one `prompt-library.json` entry

### Seed manifest

One row per seed:

- `Artifact`: `seed`
- `Record ID`: seed ID
- Page body: JSON object equivalent of one `seeds.json → seeds[]` entry

## Migration

After creating the Notion data source and sharing it with the integration:

```bash
python references/brand_photographer_notion_migrate.py --brand-id fig-and-bloom
# or migrate all file-backed brands:
python references/brand_photographer_notion_migrate.py
```

The migration is idempotent for initial import: it skips existing rows with the same `Brand ID + Artifact + Record ID`.

Then smoke-test Notion mode:

```bash
BRAND_PHOTOGRAPHER_STORAGE=notion \
BRAND_PHOTOGRAPHER_NOTION_DATA_SOURCE_ID="<notion-data-source-id>" \
python - <<'EOF'
import sys
sys.path.insert(0, "references")
from brand_photographer_api import BrandPhotographer
print(BrandPhotographer.list_brands())
print(BrandPhotographer.load_brand_config("fig-and-bloom")["brand_name"])
EOF
```

For actual generation, also provide the usual image backend credentials (`OPENROUTER_API_KEY` or Higgsfield credentials).

## Backwards compatibility

If `BRAND_PHOTOGRAPHER_STORAGE` is unset or set to `file`, all behaviour remains file-backed. Existing brand folders continue to work unchanged.
