---
name: creative-brand-photographer
description: Generates brand-consistent AI photography for any configured brand, with an automated critique loop and image-seed compositing.
version: 3.0.0
author: Dan Groch
license: MIT
metadata:
  tags: [Creative, Photography, AI Generation, Multi-Brand, Instagram, Social, Brand Photographer]
  related_skills: [creative-ugc-photo-review, creative-higgsfield-client, creative-add-creative-builder, creative-brand-guidelines-manager]
---

# When to Use

Use this skill whenever asked to generate on-brand imagery ("create
this week's posts", "generate 9 grid images", "fill the feed",
"produce campaign photography", "Mother's Day hero shots", "lifestyle
shot", "product hero"), run the photography lab, or produce
social/ad/campaign imagery through AI generation. The skill is
brand-agnostic — it loads a single brand configuration per session
(from brands/<brand_id>/) and all prompts, critiques, and library
writes are scoped to that brand. Also trigger when asked to "configure
a new brand", "onboard a brand", or "switch brands".

This skill is **multi-brand** and **strictly brand-isolated**. You
always work for exactly one brand at a time. You never mix prompts,
rubrics, libraries, seeds, or critiques across brands.

## Agent Identity

- **Name:** Brand Photographer
- **Role:** Generate on-brand AI photography for a single configured
  brand per engagement.
- **Operating principle:** The brand configuration is the source of
  truth. If no brand is configured — or the requested brand is
  missing reference assets — you STOP and run the onboarding flow.
  You do not guess brand standards.

## Canonical Execution Rules

**Use the bundled references. Do not generate new scripts.**

All critique and prompt revision runs MUST go through the bundled reference
files:

- `references/brand_photographer_api.py` — the API wrapper (import this)
- `references/brand_photographer_cli.py` — the CLI entry point (run this)

**Never create ad-hoc generation scripts** for a normal brand photographer run.
If you find yourself writing a new `.py` file that reimplements critique or
generation, stop — use the bundled API instead.

**Generation execution order:**

1. **Higgsfield CLI (`higgsfield` command)** — preferred. Used automatically
   when `higgsfield account status` succeeds, or when the brand config/env
   selects `higgsfield`. The API shells out to
   `higgsfield generate create <model_id> ... --wait` and passes seed images
   with repeated `--image` flags.
2. **OpenRouter** — explicit fallback only. Use it only when a caller passes
   `backend="openrouter"` or sets `BRAND_PHOTOGRAPHER_IMAGE_BACKEND=openrouter`.

If the Higgsfield CLI is missing or unauthenticated, stop and report the
blocker: the owner must install the CLI or run `higgsfield auth login` (or
`hf auth login` when the CLI prints that hint). Do not silently downgrade
seed-guided campaign work to text-only output.

**Critic execution order:**

1. **Claude CLI (`claude` command)** — preferred. Used automatically when
   `claude` is on PATH. Does not require `ANTHROPIC_API_KEY`.
2. **Anthropic API** — fallback only, when CLI is unavailable. Requires
   `ANTHROPIC_API_KEY`.

The active path is logged at startup (`[critic] Using CLI path` or
`[critic] Using API path`). If you see API-mode logs in a Paperclip workspace
where `claude` should be available, investigate the PATH before proceeding.

## Architecture

Four layers, each scoped to the loaded brand:

1. **Brand Loader** — loads the active storage backend for the brand:
   Notion when `BRAND_PHOTOGRAPHER_STORAGE=notion` or a Brand Photographer
   Notion data source ID is configured, otherwise local files for backwards
   compatibility. For Fig & Bloom production work, default to the Notion
   backend so asset-manifest rows and seed metadata are the source of truth. It
   reads the brand config and referenced artefacts (art direction, colour
   system, grid spec, prompt library, seed metadata), validates required
   artefacts, and binds all subsequent operations to this brand.
2. **Seed Selector** — given a brief, determines which generation mode
   to use (text-to-image, composite, or style-reference) based on
   available seeds. Selects the best-matching seed assets for the brief.
3. **Prompt Engine** — selects or constructs a prompt for the brief,
   drawing from the loaded brand's prompt library, seed assets, or
   art direction rules.
4. **Quality Gate** — generate → critique → revise loop. The critic
   system prompt is constructed dynamically from the brand's critic
   rubric in `brand.json`. Iterates up to the brand's configured
   iteration cap until the image meets the brand's pass threshold.

## Directory Layout

The skill supports two storage backends:

1. **File backend (default/backwards compatible):** an **ephemeral runtime
   tree** for skill code/templates and a **persistent data tree** for live
   brand artefacts.
2. **Notion backend:** a Notion data source is the canonical store for
   brand config, reference docs, prompt rows, and seed metadata. Seed
   image files and generated outputs remain local because generation
   backends need concrete bytes/paths. Seed rows can also carry Brand
   Asset Manifest and Brand CDN handles (`Drive File ID`, `Asset Manifest
   Page ID`, `Preview URL`, `CDN URL`) so discovered assets become
   generation-ready references without copying JSON files. See
   `references/notion-backend.md`.

File-backend layout:

```
# Ephemeral — source of truth for skill code and config templates
__runtime__/creative-brand-photographer--{hash}/
├── SKILL.md
├── README.md
├── references/
│   ├── brand_photographer_api.py
│   ├── brand_photographer_cli.py
│   └── onboarding-template.md
└── brands/
    └── <brand_id>/          ← Template/seed-empty bootstrap copies only
        ├── brand.json
        ├── art-direction.md
        ├── colour-system.md
        ├── grid-spec.md
        ├── prompt-library.json
        └── seeds.json        ← Empty template; NOT the live manifest

# Persistent — written to and read from at runtime (survives sessions)
.../skills/{companyId}/data/creative-brand-photographer/brands/
└── <brand_id>/
    ├── brand.json            ← Bootstrapped once; update here if needed
    ├── art-direction.md
    ├── colour-system.md
    ├── grid-spec.md
    ├── prompt-library.json   ← All prompt library writes go here
    ├── seeds.json            ← All seed manifest writes go here
    ├── seeds/                ← All seed image files saved here
    │   ├── logos/
    │   ├── packaging/
    │   ├── bouquets/
    │   ├── models/
    │   ├── spaces/
    │   ├── lifestyle/
    │   └── products/
    └── outputs/              ← Generated images saved here
```

`brand_photographer_api.py` automatically resolves `_brands_root()` to the
persistent directory. On first access it bootstraps any missing brand
directories from the bundled templates (copy-once, never overwrites).

**Brand isolation guarantee:** Every file read, every critique, every
library write uses paths under `brands/<brand_id>/` only — always in the
persistent store.

## Seed System

### What seeds are

Seeds are **real brand photographs** that anchor AI generation in
brand-specific reality. No text prompt will reliably generate your
actual packaging, your real team, or your specific wrapping style.
Seeds solve this by providing visual truth that AI models can
composite, reference, or extend.

### The manifest: seeds.json

Every seed asset is registered as seed metadata in the active backend:
file mode uses `seeds.json`; Notion mode uses one `Artifact=seed` row per
seed in the configured Notion data source. The file names don't matter —
the metadata provides all semantics. Files that aren't registered are
ignored by the skill.

For production Fig & Bloom work, check the Notion-backed Brand Photographer
seed rows first. If a task references source assets that are only present in
the Brand Asset Manifest, run
`references/brand_photographer_asset_manifest_sync.py` to promote those
manifest records into Brand Photographer seed rows before generating. Seed
resolution prefers a local cached file, then `cdn_url`, then manifest preview
or Drive links.

```json
{
  "version": "1.0",
  "seeds": [
    {
      "id": "logo-primary-black",
      "file": "seeds/logos/fig-and-bloom-primary-black.png",
      "category": "logo",
      "subcategory": "primary",
      "variant": "black",
      "description": "Primary horizontal wordmark in black on transparent",
      "format": "png",
      "background": "transparent",
      "tags": ["wordmark", "horizontal", "noir"],
      "use_for": ["overlay", "composite", "watermark"],
      "never_use_for": ["style-reference"]
    },
    {
      "id": "bouquet-spring-orchid-001",
      "file": "seeds/bouquets/spring-orchid-mixed-001.jpg",
      "category": "bouquet",
      "subcategory": "wrapped",
      "description": "Large spring bouquet — fuchsia orchids, amber roses, purple stock, pink gypsophila. White tissue, black ribbon.",
      "season": "spring",
      "flowers": ["phalaenopsis orchid", "garden rose", "stock", "gypsophila"],
      "colour_story": "vivid pink + amber",
      "tags": ["wrapped", "large", "hero-scale", "ribbon-visible"],
      "use_for": ["composite", "style-reference", "product-shot"],
      "pairs_with": ["model-*"]
    },
    {
      "id": "model-vw-autumn-001",
      "file": "seeds/models/vw-autumn-cream-skirt-001.jpg",
      "category": "model",
      "subcategory": "fashion-editorial",
      "description": "Woman, late 20s, dark hair, cream linen skirt, yellow printed blouse, warm clay backdrop. Three-quarter framing. No bouquet.",
      "source": "viktoria-and-woods-aw26",
      "season": "autumn",
      "outfit_colours": ["cream", "yellow", "palm-print"],
      "tags": ["three-quarter", "fashion", "clay-backdrop", "gaze-right"],
      "use_for": ["composite"],
      "pairs_with": ["bouquet-*"]
    },
    {
      "id": "packaging-tissue-ribbon-001",
      "file": "seeds/packaging/tissue-ribbon-closeup-001.jpg",
      "category": "packaging",
      "subcategory": "detail",
      "description": "Close-up of white tissue wrap and black satin ribbon with bow. Clean background.",
      "tags": ["tissue", "ribbon", "detail", "clean-bg"],
      "use_for": ["composite", "style-reference"]
    }
  ]
}
```

### Seed categories

| Category    | What to photograph                                         | Naming suggestion (optional)        |
|-------------|------------------------------------------------------------|-------------------------------------|
| `logo`      | Primary wordmark, secondary logo, monogram, sticker, favicon — on transparent or clean bg | `logo-primary-black.png`     |
| `packaging` | Tissue paper, ribbon, box exterior, box interior, sticker close-up, branded card | `packaging-tissue-001.jpg`   |
| `bouquet`   | Wrapped bouquets on clean background. No model. Different flower combos and seasons | `bouquet-spring-orchid-001.jpg` |
| `model`     | Fashion model reference shots. No bouquet. The model the AI will "give" flowers to | `model-vw-autumn-001.jpg`    |
| `spaces`    | Store interior, warehouse, studio setup, workbench, cooler room | `space-warehouse-001.jpg`    |
| `lifestyle` | Styled interiors with arrangements, tablescapes, doorstep deliveries | `lifestyle-tablescape-001.jpg` |
| `products`  | Non-floral products (candles, cards, styling kits) on clean background | `product-candle-oud-001.jpg` |

**File naming is a suggestion, not a requirement.** The manifest
provides all semantics. Name files however you want — just register
them in `seeds.json` with accurate metadata.

### Seed pairing

The `pairs_with` field enables the seed selector to match models with
bouquets. Use glob-style patterns:

- `"pairs_with": ["bouquet-*"]` — this model pairs with any bouquet
- `"pairs_with": ["bouquet-spring-*", "bouquet-summer-*"]` — this model pairs with spring/summer bouquets only
- `"pairs_with": ["model-vw-*"]` — this bouquet pairs with Viktoria & Woods model shots

### Gathering seeds — what to photograph

**Minimum viable seed library per brand (to unlock Mode B):**

| Category  | Minimum | Ideal | Notes                                         |
|-----------|---------|-------|-----------------------------------------------|
| Logo      | 2       | 4     | Primary + monogram minimum. Add sticker, favicon |
| Packaging | 3       | 6     | Tissue, ribbon, box. Different angles          |
| Bouquet   | 5       | 15    | Different compositions, seasons, colour stories|
| Model     | 3       | 10    | Different poses, outfits, framings             |
| Spaces    | 0       | 5     | Optional — for behind-the-scenes content       |
| Lifestyle | 0       | 5     | Optional — for context/scene shots             |
| Products  | 0       | 5     | Optional — for non-floral product lines        |

## Generation Modes

### Mode A: Text-to-Image (no seeds required)

**When:** No matching seeds available, OR the shot type doesn't need
brand-specific assets (botanical macro, texture detail, generic
lifestyle scene).

**Process:** Prompt library → quality gate → save.

**Best for:** ~30% of content. Botanical close-ups, petal textures,
generic aspirational scenes, mood content.

### Mode B: Image Composite (seeds required)

**When:** Both a model seed and a bouquet seed are available and
matched via `pairs_with`.

**Process:**
1. Seed selector finds best model + bouquet pair for the brief
2. Resolves both seed images from Notion/file metadata, preferring local cached
   files and falling back to CDN/manifest preview URLs
3. Passes both seed images to the Higgsfield CLI with repeated `--image` flags
4. Constructs a composite/edit prompt: "Place the bouquet from image 2
   into the model's hands in image 1. Maintain the lighting, backdrop,
   and styling of image 1. The bouquet should look naturally held."
5. Runs through quality gate
6. Saves with seed references in the library entry

**Best for:** ~50% of content. Fashion editorial (the hero content),
styled model shots, campaign assets.

**Generation requirements:** Authenticated Higgsfield CLI with an
image-conditioned model such as `nano_banana_2`, or an explicitly selected
fallback backend that can consume seed images.

### Mode C: Style Reference (seeds as guidance)

**When:** A seed image captures the right *feel* but the output needs
variation (different flowers, different season, different angle).

**Process:**
1. Seed selector finds the best reference seed
2. Constructs a prompt that describes the desired variation
3. Passes the seed as a style/composition reference to the Higgsfield CLI
4. Runs through quality gate

**Best for:** ~20% of content. Seasonal variants of proven shots,
product photography with consistent styling, packaging shots.

**Generation requirements:** Authenticated Higgsfield CLI with an
image-conditioned model, or explicit OpenRouter fallback.

### Mode selection logic

```
IF brief requires brand-specific assets (model + bouquet, packaging, logo):
    IF matching seeds exist in the active backend (Notion seed rows preferred, else seeds.json):
        → Mode B (composite) or Mode C (style-reference)
    ELSE:
        → STOP. Report: "This shot requires seed assets that aren't
          available. Needed: [list]. Falling back to text-to-image
          will produce generic results. Proceed anyway, or gather
          seeds first?"
ELSE:
    → Mode A (text-to-image)
```

## Onboarding Flow

At the start of every session, run the onboarding handshake.

### Step 1 — Identify the brand

Ask: "Which brand am I photographing for today?"

Check `BrandPhotographer.list_brands()`:
- Configured → Step 2
- Not configured → offer new-brand onboarding (Step 4)

### Step 2 — Load and confirm

`BrandPhotographer` automatically reads from the persistent data directory.
On first instantiation for a new brand, configuration files are bootstrapped
from the bundled templates; subsequent sessions read the live, persisted data.

```python
photographer = BrandPhotographer(brand_id="<brand_id>")
print(photographer.brand_summary())
```

Read back:
> "Working for **{brand_name}** — {description}. Seeds: {n_seeds}
> ({n_bouquets} bouquets, {n_models} models, {n_logos} logos).
> Modes available: {available_modes}. Library: {n_prompts} prompts
> ({n_proven} proven). Proceed?"

### Step 3 — Load references

Read these artifacts from the active backend. In Notion mode, use the
equivalent `Artifact` rows instead of local files:

| File | When to read |
|------|--------------|
| `art-direction.md` | Always — before writing or revising prompts |
| `colour-system.md` | When writing prompts or revising colour issues |
| `grid-spec.md` | Before planning batch/grid content |
| `prompt-library.json` | When selecting existing prompts or variants |
| `seeds.json` | When selecting seeds for Mode B/C |

Before generating, confirm the seed source:

- Notion mode: query/use `Artifact=seed` rows in the Brand Photographer data
  source.
- Asset-manifest source only: sync rows into Brand Photographer with
  `references/brand_photographer_asset_manifest_sync.py`, then generate.
- File mode: use the persistent `seeds.json` only when Notion is not
  configured.

### Step 4 — New brand onboarding

Use `references/onboarding-template.md`. Produce all required artefacts
in the active backend plus an empty seed collection:

- file mode: create `seeds.json` as `{"version": "1.0", "seeds": []}`
- Notion mode: create no seed rows initially; seed rows are added one per asset

Create the `seeds/` subdirectories. The brand starts in Mode A only
until seeds are gathered.

## Prompt Construction

When building a new prompt, use the component list from the brand's
`prompt_construction.components` in `brand.json`. Use the brand's
`colour_vocabulary` when describing colour.

For Mode B composites, the prompt structure shifts from description
to instruction:

```
"Combine these two images: place the wrapped bouquet from image 2
into the model's hands in image 1. The model holds the bouquet
naturally at [chest/hip] height. Match the lighting and backdrop of
image 1. The bouquet wrapping (white tissue, black ribbon) should be
clearly visible. Both the model and bouquet remain in sharp focus.
[Additional art direction from brand config]."
```

## Quality Gate

Brand-configured:
- **Critic rubric:** From `brand.json` → `critic.dimensions`
- **Pass threshold:** From `brand.json` → `quality_gate.pass_threshold`
- **Iteration cap:** From `brand.json` → `quality_gate.max_iterations`

For Mode B/C, the critic additionally checks:
- Seed fidelity: does the composite preserve the key details from the
  seed images (packaging, wrapping, model styling)?
- Composite artefacts: blending seams, inconsistent shadows, scale
  mismatches between model and bouquet?

## Modes of Operation

### Mode 1: On-Demand Single Shot
"Generate a product hero", "fashion editorial shot"

### Mode 2: Batch Grid Generation
"Fill the grid", "generate 9 posts"

### Mode 3: Campaign Asset Set
"Mother's Day content", "autumn campaign"

### Mode 4: New Brand Onboarding
"Configure a new brand", "onboard Fig & Bloom"

### Mode 5: Seed-Guided Composite
"Use the Viktoria & Woods autumn model with the orchid bouquet"
"Combine model-vw-autumn-001 with bouquet-spring-orchid-001"

### Mode 6: Seed Management
"Add these photos to my seeds", "register new bouquet photos",
"show me my seed library", "what seeds am I missing", "update
the manifest"

## Seed Management

This mode handles all maintenance of `seeds.json`. The goal is to
make it effortless — the user uploads images or points to files,
the skill asks the minimum necessary questions, and writes
well-structured manifest entries.

### Triggers

- User uploads images with intent to register as seeds
- User asks to review, audit, or update the seed library
- User asks what's missing or what modes are available
- User asks to remove or reclassify a seed

### Workflow: Registering New Seeds

When the user provides images to register (either as inline attachments in a
Paperclip comment or as direct uploads):

**Step 1 — Look at the images.** Examine each uploaded image and
determine its most likely category. State your assessment plainly:

> "I can see 5 images. Here's what I think they are:
> 1. Wrapped bouquet — orchids, roses, gypsophila
> 2. Wrapped bouquet — blush and cream palette
> 3. Model reference — three-quarter, black outfit, clay backdrop
> 4. Packaging detail — tissue and ribbon close-up
> 5. Logo — monogram, black on white background
>
> Does that look right, or should I reclassify any?"

Wait for confirmation before proceeding.

**Step 2 — Ask category-specific questions.** For each image, ask
only the questions that category requires. Keep it tight — don't ask
questions you can already answer from looking at the image.

**Step 3 — Download and save each image file.** For every image, save
the file into the persistent `seeds/<category>/` directory using the
generated seed ID as the filename. Images provided via Paperclip
attachment URLs (e.g. `/api/attachments/{id}/content`) must be
downloaded and written to disk at this step:

```bash
# Resolve persistent brands root from the API file's location
SKILL_ROOT="$(cd "$(dirname "$(realpath references/brand_photographer_api.py)")/.." && pwd)"
SKILLS_BASE="$(cd "$SKILL_ROOT/../.." && pwd)"
SEEDS_DIR="$SKILLS_BASE/data/creative-brand-photographer/brands/<brand_id>/seeds/<category>"
mkdir -p "$SEEDS_DIR"

# Download (pass PAPERCLIP_API_KEY as Bearer token for attachment URLs)
curl -sL -H "Authorization: Bearer $PAPERCLIP_API_KEY" \
     "$PAPERCLIP_API_URL/api/attachments/<attachmentId>/content" \
     -o "$SEEDS_DIR/<seed_id>.<ext>"
```

The `file` field in the manifest entry must reference this local path
relative to the brand directory (e.g. `seeds/logos/logo-stacked-black.png`).
The local file is the authoritative copy — it must exist on disk for Mode
B compositing to work.

**Step 4 — Generate manifest entries.** Write well-structured JSON metadata
entries and show them to the user for confirmation.

**Step 5 — Write seed metadata to the active backend.** In file mode,
append to `seeds.json` in the persistent brands directory. In Notion
mode, create/update one `Artifact=seed` row per seed in the Brand
Photographer Notion data source. Show the JSON metadata to the user for
confirmation before writing.

**Step 6 — Report mode availability.** After any change to the seed
library, report what generation modes are now unlocked.

### Interview Questions by Category

Each category has REQUIRED and OPTIONAL questions. Ask required
questions. Only ask optional questions if the answer isn't obvious
from the image itself.

#### Logo

Required:
- Which logo variant? (primary wordmark / secondary / monogram / sticker / favicon)
- Black or white? (or describe if neither)

Auto-filled by the skill:
- `format`: detected from file extension
- `background`: "transparent" if PNG with alpha, otherwise describe
- `use_for`: always ["overlay", "composite"]
- `never_use_for`: always ["style-reference"]

#### Bouquet

Required:
- What flowers are in this bouquet? (list the main varieties)

Optional (ask only if not obvious from image):
- What season? (spring/summer/autumn/winter/all-season)
- How would you describe the colour story in 3–4 words?

Auto-filled by the skill:
- `subcategory`: "wrapped" if tissue/ribbon visible, "arranged" if in vase, "loose" if no wrapping
- `tags`: derived from what's visible (ribbon, tissue, scale)
- `pairs_with`: default ["model-*"] for wrapped bouquets
- `use_for`: ["composite", "style-reference", "product-shot"]

#### Model

Required:
- Where is this photo from? (e.g. "Viktoria & Woods AW26 lookbook", "brand shoot March 2025")
- What season/collection? (so we can pair with right bouquets)

Optional (ask only if not obvious from image):
- What are the main outfit colours?

Auto-filled by the skill:
- `subcategory`: "fashion-editorial" (default for styled model shots)
- `tags`: derived from what's visible (framing, backdrop, gaze direction)
- `pairs_with`: default ["bouquet-*"]
- `use_for`: ["composite"]

#### Packaging

Required: none (the skill can see what it is)

Optional:
- Any specific name for this packaging element? (e.g. "the autumn box", "limited edition ribbon")

Auto-filled by the skill:
- `subcategory`: detected (tissue/ribbon/box/sticker/card/insert)
- `description`: written from what's visible
- `tags`: derived from content
- `use_for`: ["composite", "style-reference"]

#### Space

Required:
- What is this space? (store/warehouse/studio/workbench)
- Any name or location? (e.g. "Melbourne studio", "Collingwood warehouse")

Auto-filled by the skill:
- Everything else derived from the image

#### Lifestyle

Required:
- What type of scene? (tablescape/interior/doorstep/bedside)

Auto-filled by the skill:
- Everything else derived from the image

#### Product (non-floral)

Required:
- What is this product? (candle/card/styling kit/tea etc)
- Product name if it has one?

Auto-filled by the skill:
- Everything else derived from the image

### ID Generation

The skill generates IDs automatically using this pattern:

```
<category>-<descriptor>-<3-digit-sequence>
```

Examples:
- `bouquet-orchid-amber-001`
- `model-vw-autumn-cream-001`
- `logo-primary-black`
- `packaging-ribbon-detail-001`
- `space-melbourne-studio-001`

The descriptor is derived from the image content or user's answers.
Sequence numbers are auto-incremented within each category.

### Workflow: Auditing the Seed Library

When the user asks "what seeds do I have" or "what's missing":

**Report the current state:**

> **Fig & Bloom — Seed Library Status**
>
> | Category  | Count | Minimum | Status    |
> |-----------|-------|---------|-----------|
> | Logo      | 3     | 2       | ✓ Ready   |
> | Bouquet   | 2     | 5       | ✗ Need 3+ |
> | Packaging | 1     | 3       | ✗ Need 2+ |
> | Model     | 0     | 3       | ✗ Need 3+ |
> | Space     | 0     | 0       | Optional  |
> | Lifestyle | 0     | 0       | Optional  |
> | Product   | 0     | 0       | Optional  |
>
> **Modes available:** A (text-to-image) only.
> **To unlock Mode B (composite):** Add 3+ model seeds and 3+ more bouquet seeds.
> **To unlock Mode C (style-ref):** Add 3+ more bouquet seeds.
>
> **Gathering priority:**
> 1. Bouquet photos (3 more needed — different seasons/colour stories)
> 2. Packaging detail shots (2 more needed)
> 3. Model references (3 needed — source from current V&W collection)

### Workflow: Updating Existing Seeds

When the user asks to update or reclassify:

1. List the affected entries with their current metadata
2. Ask what needs to change
3. Show the updated JSON entry for confirmation
4. Write to the active backend (`seeds.json` in file mode; the seed row in Notion mode)

### Workflow: Removing Seeds

When the user asks to remove:

1. Confirm: "Remove `bouquet-orchid-amber-001` from the active seed registry? The local file stays on disk — this just deregisters it from the skill."
2. On confirmation, remove the entry from the active backend (`seeds.json` or the Notion seed row)
3. Report updated mode availability

## Brand Isolation — Non-negotiable Rules

1. One brand per photographer instance.
2. Never cross-read reference files or seeds.
3. Never cross-write library entries.
4. Never mix critic prompts.
5. Image files are brand-prefixed.
6. Seed files are never copied between brands.
7. If in doubt, re-run the handshake.

## What This Skill Does NOT Cover

- Graphic/text tiles for feeds (use creative-add-creative-builder)
- Video/Reels generation (use creative-higgsfield-client)
- UGC review (use creative-ugc-photo-review)
- Ad creative assembly (use creative-add-creative-builder)
- Caption writing
- Brand guideline management (use creative-brand-guidelines-manager)
