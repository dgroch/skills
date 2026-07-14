---
name: creative-social-media-builder
description: Plan and generate branded Fig & Bloom social media creatives — screens of 9 grid tiles (the default unit of work), rows of 3, and individual creatives (Instagram/Facebook story 1080×1920 and post 1080×1350) — as flat PNG images via the hosted social builder API or the local locked-template render pipeline. Use this skill whenever someone asks to plan the next screen or grid batch, complete a grid row, or create a Fig & Bloom social post, story, Instagram/Facebook creative, carousel cover, quote card, statement graphic, giveaway/poll graphic, link-in-bio card, or illustrated social tile.
---

# Social Media Builder — Fig & Bloom (v1)

Generates production-ready social creatives by filling content tokens into pre-built, locked templates and rendering them to flat PNGs. The agent picks a template and injects content. It does not write HTML or make design decisions.

This skill is the social-media sibling of `creative-email-campaign-builder` and deliberately mirrors its architecture: locked templates, a machine-readable `manifest.json`, a base64-font preview shell, and a headless-render harness (the `puppeteer` skill). Font handling, token injection, and the render approach are reused from that skill — not reinvented.

## Read this first: the operating layer

**`references/operating-instructions.md` is mandatory reading before planning or rendering anything.** It is the judgment layer that sits on top of this file: the grid system (screens of 9, column roles, adjacency and rhythm rules), the hosted-builder operating loop, the caption-luminance rule and its fallback ladder, brand voice guardrails, and the corrections log of past mistakes. This file tells you how to render a tile; that file tells you which tiles to make, where they go, and what "done" means.

Companion skills:

- **`creative-design-discipline`** — the craft layer for every individual tile: grid/margins, type scale, spacing rhythm, focal-point and logo discipline, and the critique loop. Apply it to each tile at 100% render; the contact sheet in this skill's workflow is for **grid-level cohesion only**, never per-tile approval.
- **`creative-social-grid-planner`** — campaign theming: turning an occasion or campaign into a 9/12-tile content world. Use it to decide *what the screen is about*; the operating instructions here govern *where each tile may sit* (columns, adjacency, rhythm). When the two conflict on placement, the operating instructions win.

## Unit of work: the screen, not the asset

The deliverable is a **cohesive screen of 9 tiles**, planned as three rows before anything is rendered. Canonical invocation:

> "Plan the next screen — 9 tiles, following the grid system. Here's what's ready: [reflexed roses content, quiet arts #2, …]"

Three modes, defined fully in the operating instructions:

- **Screen (default)** — plan 9 tiles from the ready-content list, render all, deliver a 3×3 contact sheet for approval, then the posting order (reverse row order).
- **Row (3 tiles)** — only with grid state: a user-supplied screenshot of the current grid top, or a best-effort headless-browser screenshot via `references/scripts/grid-snapshot.js`. **No grid state → no row** — escalate to a full screen instead.
- **Single tile** — only as a fill for a named slot in an approved screen plan, or as evergreen silent padding. Never scheduled outside a row or screen plan.

## Render paths

- **Hosted builder (primary):** `my-social-builder.onrender.com` — JSON-first API. Loop: `GET /api/schema` (always first — it is versioned and moves) → `GET /api/library` (copy a preset row verbatim) → `POST /api/validate` → `POST /api/render` → decode and eyeball every slice. Payload gotchas and levers are in the operating instructions.
- **Local pipeline (fallback / template development):** the locked T1–T9 templates and `render.js` harness documented in the rest of this file. Use when the hosted builder is unreachable or when working on the templates themselves.

Brand voice guardrails apply on both paths and are non-negotiable: no exclamation marks, Australian English, flower names lowercase, banned words (blooms, gorgeous, stunning, luxury, exquisite, elevate, curate), Cervanttis always lowercase.

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

## Pipeline (local render path)

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
  - Per-template groups: `t1_container_presets`, `t1_attr_presets`, `t3_type_presets`, `t4_caption_presets`, `t4_photo_presets`, `t5_visual_presets`, `t8_label_presets`.

Optional tokens (e.g. an unused `CTA`, `OVERLINE`, `ATTRIBUTION_ROLE`) take the empty string `""` — empty text holders collapse automatically.

Illustration tokens (T9, and any `{{ASSETS_BASE}}` reference) take a **filename** from `references/illustrations/` (e.g. `HandFlower_Black.png`) — `render.js` resolves the path.

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
- [ ] Cervanttis values are lowercase; Lust values sentence case.

If a result reports overflow (usually T5/T6 body or a too-long T3 phrase on the 1350 post), **shorten the copy** (or split to the story-only ratio) and re-render. Do not ship a creative with a non-empty `errors` array.

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
| `references/operating-instructions.md` | **Anything** — grid planning, tile production, copy, captions. The judgment layer over this file |
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
