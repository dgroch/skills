---
name: creative-social-media-builder
description: Generate branded Fig & Bloom social media creatives (Instagram/Facebook story 1080×1920 and post 1080×1350) as flat PNG images by filling content tokens into pre-built, locked templates. Use this skill whenever someone asks to create a Fig & Bloom social post, story, Instagram/Facebook creative, quote card, statement graphic, giveaway/poll graphic, link-in-bio card, or illustrated social tile.
---

# Social Media Builder — Fig & Bloom (v1)

Generates production-ready social creatives by filling content tokens into pre-built, locked templates and rendering them to flat PNGs. The agent picks a template and injects content. It does not write HTML or make design decisions.

This skill is the social-media sibling of `creative-email-campaign-builder` and deliberately mirrors its architecture: locked templates, a machine-readable `manifest.json`, a base64-font preview shell, and a headless-render harness (the `puppeteer` skill). Font handling, token injection, and the render approach are reused from that skill — not reinvented.

## Core principle

**The agent is a content editor, not a designer or developer.**

Every layout, colour, illustration, and type rule is baked into the template files. The agent's only job per request:

1. Pick the right template for the message.
2. Write good copy for the token values.
3. Set the style tokens by **copying a preset row verbatim** from `manifest.json` (never invent a hex value).
4. Render, validate, present for approval.

The 9 templates are *purposes*, not one file per design. Visual variety comes from the shared token + preset system.

---

## Output spec

- **Format:** flat PNG.
- **Ratios (both required):**
  - `1080×1920` — **Story** (primary canvas — all source PSDs are this ratio).
  - `1080×1350` — **Post** (4:5). Templates **reflow** to this, not just crop.
- **Render path:** HTML/CSS template → headless Chromium → PNG, via `references/scripts/render.js` (which reuses the `puppeteer` skill's installed Chromium).
- **Fonts:** Cervanttis (script), Lust (serif), Neuzeit Grotesk (sans) — loaded base64 in `shell-preview.html` for pixel-accurate offline rendering, with a CDN-backed `shell-production.html` fallback.

---

## Pipeline

```
1. BRIEF     → message, template choice, ratio(s)
2. COPY      → write token values (quote, headline, body, caption, CTA)
3. SELECT    → pull the template + its preset groups from references/manifest.json
4. FILL      → write the token values to a JSON file (content + a verbatim preset row)
5. RENDER    → node references/scripts/render.js → PNG at the requested ratio(s)
6. VALIDATE  → __RENDER_MANIFEST__ ok:true, every result errors:[] (dims, overflow, broken images)
7. PREVIEW   → present the PNG(s) for approval. Do not finalise before sign-off.
```

**Every numbered step is a gate. Do not skip ahead.** Validation must pass at **both** ratios — the 4:5 reflow is the main risk.

**Dependency:** the `puppeteer` skill. Verify before the first render:
```bash
node -e "require('puppeteer'); console.log('OK')"
```
If it fails, run `npm install` in `reference/reference-puppeteer/references/` (see Troubleshooting).

---

## Step 1 — Brief

Collect or parse: the **message**, the **template** (or let the message imply it — see the table), and which **ratio(s)** are needed (default: both).

## Step 2 — Copy

Write the token values. Case rules (enforced in Step 6):
- **Cervanttis** values (T1 signature, T3 script phrase, T4 script caption, T8 poll label) → **lowercase**.
- **Lust** values (quotes, headlines, body, link lines) → **sentence case**. T2's headline renders small-caps from sentence-case input.

## Step 3 — Select the template

| ID | Template | Use it for | Photo? | Key tokens |
|---|---|---|---|---|
| **T1** | Quote / Testimonial | Pull-quote + attribution (printed or script signature) | optional bg | `QUOTE`, `ATTRIBUTION_NAME`, `ATTRIBUTION_ROLE` |
| **T2** | Statement + Attribution | Overline + serif-caps headline, bottom-anchored | optional bg | `OVERLINE`, `HEADLINE`, `LOGO` |
| **T3** | Display Phrase | One oversized word/phrase (WIN, giveaway, "celebrate love") | optional bg | `PHRASE` (+ `t3_type_presets`) |
| **T4** | Captioned Photo | Photo + short caption (lower-third label / script) | required | `PHOTO_URL`, `CAPTION`, `CTA` |
| **T5** | Long-form Story | Serif headline + body on a panel + link-in-bio footer | optional left col | `BODY`, `FOOTER_CTA` (+ `t5_visual_presets`) |
| **T6** | Feature Card | White-canvas editorial: headline + inset photo + body + CTA | required inset | `HEADLINE`, `INSET_PHOTO`, `BODY`, `CTA` |
| **T7** | Link / CTA Card | Near-empty canvas, one line + logo | no | `LINE`, `LOGO` |
| **T8** | Comparison / Poll | Two stacked photos + script label ("this or that?") | required ×2 | `PHOTO_TOP`, `PHOTO_BOTTOM`, `LABEL` |
| **T9** | Illustration Hero | Hero brand illustration + serif headline | no (illustration) | `HEADLINE`, `ILLUSTRATION` (+ `style_presets`) |

Read the chosen template's comment block **and** its `manifest.json` entry to confirm the exact token list and which preset groups apply.

## Step 4 — Fill (write a tokens JSON)

Write a flat `{ "TOKEN": "value" }` JSON file. Two kinds of token:

- **Content tokens** — the copy and the image paths. Prefer **`file://` paths** for photos (offline-safe render); pre-download remote images first.
- **Preset tokens** — fill by **copying ONE preset row verbatim** from the relevant `manifest.json` group:
  - `style_presets` (every template): `photo-dark`, `photo-plain`, `black`, `white`, `clay`, `paper` → fills `BG_COLOR`/`PANEL_BG`, `INK`, `SCRIM`.
  - Per-template groups: `t1_container_presets`, `t1_attr_presets`, `t3_type_presets`, `t4_caption_presets`, `t4_photo_presets`, `t4_placement_presets`, `t5_visual_presets`, `t8_label_presets`.

Optional tokens (e.g. an unused `CTA`, `OVERLINE`, `ATTRIBUTION_ROLE`) take the empty string `""` — empty text holders collapse automatically.

Illustration tokens (T9, and any `{{ASSETS_BASE}}` reference) take a **filename** from `references/illustrations/` (e.g. `HandFlower_Black.png`) — `render.js` resolves the path.

### T4 — caption placement (legibility)

Text on a photo is the one place a creative can fail silently, so T4 has explicit rules (the render contrast validator in Step 6 enforces them).

**Caption ink rule — ink follows the band:**
- **White ink over dark/mid bands; dark ink over light bands.** Set `BAR_INK` to match the band, not the other way round.
- "Light" is not enough — the band must be **clean AND shadow-free (uniform luminance)**. A caption that crosses a shadow edge reads badly even at a good average contrast.
- Avoid mid-tones where neither black nor white wins cleanly — choose a different band or use the serif-box fallback.

**Band selection logic:**
1. Identify the cleanest band (uniform luminance, no shadow) in the photo.
2. Choose the anchor (`BAR_ANCHOR: top:88px` for a top band, `bottom:140px`/`bottom:90px` for a bottom band) to land the caption there — copy a `t4_placement_presets` row.
3. Choose `PHOTO_POS` (CSS `background-position`, e.g. `center 30%`) to crop/shift the photo so the clean band is in view.
4. Set `BAR_INK` by band luminance: dark band → white ink; light band → dark ink.
5. Drop the `CTA` (`""`) when it would collide with the subject or a busy area. The CTA renders in NeuzeitGro **Light (300)**; `CTA_SIZE` controls its size (`28px` for the serif-box).

**Fallback ladder (cheapest first):**
1. **Anchor** to an existing clean band (`upper-band` / `lower-band` preset) — free, instant.
2. **Reframe** via `PHOTO_POS` to expose a clean band — free.
3. **Serif-box** (`t4_caption_presets:serif-box` + `t4_placement_presets:serif-box`) — a white box guarantees legibility when no clean band exists — free.
4. **Generative outpaint** (Higgsfield Nano Banana 2 Edit) to manufacture negative space — **only** when 1–3 cannot resolve. Pull the full-res original via Drive File ID (not the preview URL), save the result to R2, and log a new manifest row.

## Step 5 — Render

```bash
node references/scripts/render.js \
  --template T1 \
  --tokens /tmp/<creative>/t1.json \
  --all-ratios \
  --output-dir /tmp/<creative>/out
```
- `--all-ratios` renders both 1080×1920 and 1080×1350 (named `<template>-<ratio>.png`). For a single ratio use `--ratio 1080x1920 --output out.png`.
- `--shell production` swaps the base64 preview shell for the CDN shell (needs network); the default base64 preview shell is recommended.
- `--scale 2` is for high-DPI proofing only — ship `--scale 1` (1080px wide is already the target).

## Step 6 — Validate

`render.js` prints a `__RENDER_MANIFEST__ … __END_MANIFEST__` JSON block and exits non-zero on any failure. The build passes only when:

- [ ] `ok: true` and **every** result has `errors: []`.
- [ ] `canvas` equals the target (1080×1920 / 1080×1350) for both ratios.
- [ ] `overflow.right / bottom / scroll` are all 0 — **no text or photo exceeds the canvas at either ratio** (the 4:5 reflow check).
- [ ] `broken_images` is empty for every result.
- [ ] **Contrast** — every `contrast[]` entry is ≥ 3:1 (no contrast error) and ideally ≥ 4.5:1. Resolve `warnings` for low contrast or a textured/shadowed band (`band_stdev` > 0.16) before shipping on-image text (T1 over photo, T2, T3, T4).
- [ ] Cervanttis values are lowercase; Lust values sentence case.

If a result reports **overflow** (usually T5/T6 body or a too-long T3 phrase on the 1350 post), **shorten the copy** (or split to the story-only ratio) and re-render. If it reports a **contrast** failure or warning, follow the T4 fallback ladder (re-ink → reframe via `PHOTO_POS` → serif-box → outpaint). Do not ship a creative with a non-empty `errors` array.

## Step 7 — Preview

Present the PNG(s) for approval. State the template, ratio(s), and that fonts/illustrations are browser-rendered and pixel-accurate. **Wait for explicit sign-off before finalising.**

If edits are requested:
- **Copy / colour-preset / photo changes** → update token values, re-render.
- **Layout / new-treatment changes** → these require a template file update. Flag for template development — do not improvise HTML.

---

## Assets

- **Fonts:** `references/fonts/` — `cervanttis.ttf`, `Lust-Regular.otf`, `NeuzeitGro-Lig.otf`, `NeuzeitGro-Bol.otf`. Full set present; embedded base64 in `shell-preview.html`.
- **Illustrations:** `references/illustrations/` — the locked solid brand set in Black & White: Body, BodyFlower, Face1, Face2, FrontFace, HandFlower, HandPlant, HandRose. Use `*_Black` on light backgrounds, `*_White` on dark.
- **Logo:** rendered as Lust text — `"F&B"` (monogram) or `"Fig & Bloom"` (full lockup) — for offline-safe rendering. The raster horizontal lockup also exists on the Shopify CDN (see `manifest.json → gaps.logo_assets`).

## Reference files

| File | Read before... |
|---|---|
| `references/manifest.json` | Selecting a template, confirming tokens, copying preset rows (Steps 3–4) |
| `references/design-system.md` | Any question about colour, type scale, illustration, or photography rules |
| `references/templates/*.html` | Filling tokens — read the actual file's comment block; never reconstruct from memory |
| `references/shell/shell-preview.html` | (render.js handles this) base64-font wrapper for rendering |
| `puppeteer` skill | First render — install on the VPS first |

---

## Known gaps (see `manifest.json → gaps`)

1. **Line-art illustration library — unconfirmed.** T9 and the line-art variant of T1 currently use the locked **solid** brand set (whose Black variants already read as fine-line drawings). If a dedicated single-line library is required, it must be extracted from the PSD layers or supplied separately.
2. **Logo assets** — text lockups are used by default; confirm whether a raster monogram + full lockup should be embedded instead.
3. **Corpus housekeeping** — `tmp/` (PSDs/JPGs) must not ship; it is `.gitignored`. Recommendation: push the heavy binaries to the R2 CDN (`brand-cdn` skill) and keep only links.

---

## What the agent does NOT do

- Write or edit HTML/CSS.
- Choose colours, fonts, sizes, or spacing (copy a preset row instead).
- Resize or reposition illustrations.
- Ship a creative that fails Step 6 validation.

If a request cannot be met with the existing 9 templates and their presets, escalate for template development. Do not improvise HTML.

---

## Troubleshooting

### `Cannot find module 'minimist'` / `'puppeteer'` when running render.js

The `puppeteer` skill's dependencies aren't installed. Fix:
```bash
cd reference/reference-puppeteer/references
npm install
node -e "require('puppeteer'); console.log('puppeteer OK')"
```
`render.js` auto-discovers that `node_modules`; or point it explicitly with `--puppeteer <path>` or `PUPPETEER_SKILL_NODE_MODULES=<path>`.

### A photo renders as a blank/placeholder area

Photos are CSS backgrounds. Confirm the `file://` path exists (`ls` the path without the `file://` prefix) and points at a real image; pre-download remote images before rendering.

### Overflow error on the 1080×1350 post but the 1080×1920 story is clean

Expected — the post canvas is shorter. Shorten the body/phrase, or render that creative at the story ratio only.
