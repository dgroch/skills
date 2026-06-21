---
name: creative-email-campaign-builder
description: Build complete Klaviyo email campaigns for Fig & Bloom. The builder is JSON-first — the agent reasons about strategy and components, then produces campaign JSON that the hosted builder assembles, renders, and persists. Use this skill whenever someone asks to create an email campaign, email design, Klaviyo email, marketing email, promotional email, newsletter, or EDM for Fig & Bloom.
---

# CANONICAL WORKFLOW — READ FIRST

**The Fig & Bloom email builder is JSON-first. The deliverable is campaign JSON, saved to the builder (Notion-backed). HTML/PNG/slices are *derived artefacts*, never the deliverable.**

The agent's job is strategy and component reasoning: understand the campaign objective, choose the components that visually express it, and emit valid builder JSON. The hosted builder does assembly, rendering, and persistence.

Hosted builder: **https://my-email-builder.onrender.com** (free Render plan — first request after idle is a slow cold start; retry).

### The agent MUST
1. **Fetch the live schema** — `GET /api/schema` — to discover the current component list, exact token names, palette presets, and case rules. The schema is the execution contract; never assume it from memory.
2. **Identify the campaign objective and awareness state** (see *Component strategy by objective* below and `references/component-strategy.md`).
3. **Select components that express the objective**, then **generate builder campaign JSON**.
4. **Validate/assemble/render via the API** — `POST /api/assemble` (preview HTML + `unfilled` token report), `POST /api/render` / `POST /api/render-slices` (PNGs).
5. **Save the campaign JSON to the builder** — `POST /api/designs` (new) or `PUT /api/designs/:id` (update). This is the source of record. Capture the returned design `id`.
6. **Treat HTML/PNG/slices as derived** — export (`POST /api/export`) only when explicitly asked.
7. **Push to Klaviyo only after human approval** — `POST /api/klaviyo-draft`. Never auto-send.

### The agent MUST NOT
- **Hand-code standalone HTML as the deliverable.** Only as an emergency fallback when the builder/API is unavailable *and* the user explicitly approves it.
- **Treat local `v4`/`v5`/"engine" files as the source of truth.** The live builder + its `/api/schema` are canonical. The bundled template library in `references/` is the *rendering layer* the builder uses — read it to understand components, not to bypass the JSON workflow.
- **Drive the UI manually** except to import/preview/debug. The UI is a human surface over the same API; agents use the API.
- **Skip persistence.** An email isn't "built" until its JSON is saved and the returned design `id` is confirmed.

### Campaign objectives (taxonomy)

One primary objective per send. These are the `objectives[].id`/`label` from
`GET /api/schema` (canonical — confirm there before relying on this list). Each carries a
`blockSequence`, `heroOptions`, `proofModules`, `avoid` list, and `subjectPatterns` in the
schema; the playbooks live in `references/component-strategy.md`.

| Objective id | Label |
|---|---|
| `farewell_sellthrough` | Farewell / final sell-through of a discontinued range |
| `range_launch` | Launch a new range or collection |
| `product_spotlight` | Spotlight a single hero product |
| `occasion_gifting` | Occasion / seasonal gifting (Mother’s Day, Valentines, etc.) |
| `discount_offer` | Discount / promotional offer |
| `value_prop` | Communicate why we’re different (value proposition) |
| `education_howto` | Educational / how-to / care content |
| `social_proof` | Reviews / testimonials / customer stories |
| `lifecycle` | Lifecycle / nurture (welcome, re-engagement, post-purchase) |
| `editorial_digest` | Recurring editorial digest / monthly newsletter |

Pick the send's `subjectLine` from that objective's `subjectPatterns` and persist it
(with `previewText`) on the saved design — see the completion checklist and
`references/component-strategy.md`.

### Component identifiers are GROUP-PREFIXED (critical)
`/api/assemble` resolves `component` to `design-system/templates/<component>.html`, so the value **must include the group folder**:

- Heroes → `heroes/hero-a`, `heroes/hero-d-clay`, `heroes/hero-image-only`
- Sections → `sections/body-copy-plain`, `sections/section-headline`, `sections/upsell-noir`, `sections/trust-bar`, `sections/full-width-image`
- Products → `products/card-horizontal`, `products/card-lifestyle-studio`
- Designed blocks → `blocks/caption-bar-hero`, `blocks/editorial-hero`, `blocks/offer-panel`, `blocks/image-text`
- Dividers → `dividers/divider-line`, `dividers/divider-illo-clay`
- **Top-level (no prefix):** `header`, `footer`

A **bare** name like `hero-d-clay` renders nothing. The fastest guard is **`POST /api/validate`** (preferred): it returns structured, teaching errors — for a bare name it gives `rule`, `message`, and a `suggestion` (e.g. `"heroes/hero-d-clay"`) — and also flags casing violations, **without rendering**. Run it before saving. (As a fallback, `POST /api/assemble` surfaces the same class of failure as `(missing template)` entries in `unfilled`.) Component names can also be checked directly against `GET /api/schema` `components[].name`.

### Source-of-truth hierarchy
1. User brief / Paperclip / Notion campaign plan (intent)
2. Live builder schema — `GET /api/schema` (execution contract)
3. Existing campaign JSON in the builder — `GET /api/designs`, `GET /api/designs/:id`
4. Brand voice + component strategy in this skill (`references/`)
5. Rendered HTML / PNG / slices — **derived, never source**

### Decision tree
- **"Build an email"** → fetch schema → choose components for the objective (use `/api/schema` `objectives` + each component's `bestFor`/`avoidFor`) → generate JSON → **`POST /api/validate`** (fix any errors) → `POST /api/assemble` → render to preview → **save** (`POST /api/designs`) → report the design `id`/URL.
- **"Show me a proven example"** → `GET /api/examples?objective=<type>` for an approved campaign JSON to start from, then adapt.
- **"Edit this email"** → `GET /api/designs` to find it → `GET /api/designs/:id` → modify the JSON `blocks`/`tokens` → validate → re-assemble/render → `PUT /api/designs/:id`.
- **"Give me the HTML"** → still generate/validate JSON first, then `POST /api/export`. Note that designed `blocks/*` ship as rasterised PNGs (upload to Klaviyo), not live HTML.
- **Builder/API unavailable** → **stop and report the blocker.** Only hand-code HTML if the user approves an emergency, explicitly non-canonical fallback.

### Live API (verified)
| Method | Path | Body | Returns |
|---|---|---|---|
| GET  | `/api/schema` | — | components (group-prefixed names + intent metadata `bestFor`/`avoidFor`/`visualRole`/`tone`), tokens, palette presets, case + ordering rules, `objectives` taxonomy |
| POST | `/api/validate` | `{campaign}` | `{ok, issues[]}` — teaching errors (unknown/bare component → `suggestion`; casing violations). No render. **Run before saving.** |
| GET  | `/api/examples` | `?objective=<type>` | approved campaign JSON exemplars (filterable by objective) |
| POST | `/api/assemble` | `{campaign}` | `{html, unfilled}` — preview HTML + leftover/missing tokens |
| POST | `/api/render` | `{campaign}` | `{pngBase64, brokenImages, height}` — full email PNG |
| POST | `/api/render-slices` | `{campaign}` | per-block PNG slices for Klaviyo upload |
| POST | `/api/export` | `{campaign}` | `{html, unfilled, campaign}` — production HTML (keeps `{{ASSETS_BASE}}` + Klaviyo tags) |
| GET  | `/api/designs` | — | `{designs:[{id,name,createdAt,updatedAt}]}` |
| GET  | `/api/designs/:id` | — | full saved record incl. `campaign` |
| POST | `/api/designs` | `{name, campaign}` | created record (capture `id`) |
| PUT  | `/api/designs/:id` | `{name, campaign}` | updated record |
| POST | `/api/designs/:id/clone` | `{}` | cloned record |
| DELETE | `/api/designs/:id` | — | deletes |
| GET  | `/api/klaviyo-audiences` | — | lists/segments for targeting |
| POST | `/api/klaviyo-draft` | `{campaign, ...}` | creates a Klaviyo draft (**after approval only**) |

> **Discovery entry point:** `GET /api/schema` is the canonical contract (components, intent metadata, `objectives`, rules). There is intentionally **no** `/api/agent-contract` — it would duplicate the schema and the workflow above. Use `/api/schema` + `/api/examples` + this skill.

### Minimal valid campaign JSON
A `campaign` is `{ campaignName, bodyBg, blocks: [{ component, tokens }] }`. Note the group-prefixed `component` values:

```json
{
  "campaignName": "RH | 2026-06 Farewell Weekend",
  "bodyBg": "#2c2825",
  "blocks": [
    { "component": "header", "tokens": {} },
    { "component": "heroes/hero-d-clay", "tokens": {
        "SUPER_LABEL": "Friday 5 & Saturday 6 June",
        "HEADLINE": "a fond farewell",
        "SUBHEADLINE": "Seven favourites are available for one last weekend.",
        "CTA_TEXT": "Shop the farewell designs",
        "CTA_URL": "https://figandbloom.com/collections/bouquets" } },
    { "component": "sections/body-copy-plain", "tokens": {
        "SUPER_LABEL": "Seven favourites",
        "HEADLINE": "Seven you've loved, one last weekend.",
        "BODY_P1": "…", "BODY_P2": "…" } },
    { "component": "sections/trust-bar", "tokens": {} },
    { "component": "footer", "tokens": {} }
  ]
}
```

> `HEADLINE` casing depends on the component's font (Cervanttis heroes → lowercase; Lust sections/cards → Sentence case). See *Step 3* and `token_rules` in `/api/schema`. Worked JSON examples per objective are in `references/component-strategy.md`.

### Completion checklist (report any unmet item as incomplete)
- [ ] Campaign JSON created with **group-prefixed** component names
- [ ] `GET /api/schema` consulted for current components + token names
- [ ] `POST /api/validate` returns `ok: true` (no unknown-component or casing errors)
- [ ] `POST /api/assemble` returns **no** `(missing template)` and **no** unexpected `unfilled` tokens
- [ ] Render/preview checked visually; `brokenImages` empty
- [ ] Each designed-block PNG passed the visual-QA rubric (composition, type contrast, focal clarity, brand restraint); levers regenerated on any fail
- [ ] `subjectLine` + `previewText` set, chosen from the objective's `subjectPatterns` (`/api/schema`), and persisted on the design (`POST`/`PUT /api/designs`)
- [ ] Product URLs/images verified (live, correct ratio)
- [ ] Campaign JSON **saved** (`POST`/`PUT /api/designs`) and design `id`/URL captured
- [ ] Derived HTML/PNG exported only if requested
- [ ] Klaviyo draft created only after explicit approval

---

# Email Campaign Builder — Fig & Bloom

> **How this document is organised.** The block above is the canonical, JSON-first
> operating contract — follow it. The sections below are the **rendering / design
> reference layer**: they describe the locked template library, component semantics,
> token rules, slicing, and Klaviyo handoff that the hosted builder applies when it
> assembles your JSON. Read them to reason about *which* components to choose and
> *how* their tokens behave — not as an alternative to the JSON workflow. Where the
> older step-by-step pipeline below describes building slices and HTML by hand, that
> is the builder's internal job; the agent's deliverable remains validated, saved
> campaign JSON.

Builds production-ready Klaviyo emails by assembling pre-built, locked templates. The agent selects components and injects content. It does not write HTML or make design decisions.

## Core principle

**The agent is a content editor, not a designer or developer.**

Every layout decision, style rule, illustration, icon, and colour is already baked into the template files. The agent's only job is:
1. Select the right templates for this campaign
2. Write good copy for the token values
3. Assemble and validate

---

## Pipeline

```
1. BRIEF         → Campaign parameters
2. PRODUCTS      → Fetch from Shopify, select 3–5
3. COPY          → Write all token values (headlines, body, CTAs)
4. SELECT        → Choose components from references/manifest.json
5. RENDER        → Fill tokens into templates → slice visual components to PNG via puppeteer skill
6. VALIDATE      → Check all tokens filled, all slices produced, pre-flight checks
7. PREVIEW       → Assemble preview email (slices + HTML text blocks). Save to Google Drive only. Wait for approval.
8. UPLOAD        → Upload approved slices to Klaviyo media library. Get hosted URLs.
9. PRODUCTION    → Assemble final email HTML (Klaviyo slice URLs + text block HTML)
10. KLAVIYO      → Upload template + create campaign. Wait for approval before scheduling.
```

**Every numbered step is a gate. Do not skip ahead.**

**Dependency:** This skill requires the `puppeteer` skill to be installed and configured on the VPS. Verify with `node -e "require('puppeteer'); console.log('OK')"` before first use.

---

## Google Workspace Credentials

All Google Drive operations in this skill use the **`$GWS_USER_ADMIN`** credential (admin@figandbloom.com.au). This account has access to the Paperclip shared drive and all Marketing department folders.

**Important:** The `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` env var is set globally and takes precedence over `GOOGLE_WORKSPACE_CLI_CONFIG_DIR`. Always unset it when using a profile-based config:

```bash
env -u GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE \
  GOOGLE_WORKSPACE_CLI_CONFIG_DIR=$GWS_USER_ADMIN \
  gws drive ...
```

Use this pattern for every `gws drive` command in Steps 7 and 9.

---

## Step 1: Campaign Brief

Collect or parse:
```
Campaign name, goal, audience, tone, products (Shopify collection URL),
promo code (if any), opt-out required (yes/no), delivery cutoffs, accent colour (if any)
```

Auto-infer opt-out requirement:
- **Required:** Mother's Day, Father's Day, Valentine's Day/Galentine's, pregnancy/baby, memorial
- **Not required:** seasonal, product launch, general promo, retention

---

## Step 2: Product Selection

Read `references/product-selection.md` before fetching.

Fetch the Shopify collection. Select 3–5 products optimising for price spread, visual variety, and type mix. Assign card layout per product:
- Hero/spotlight product → `card-lifestyle-studio` (one per email max)
- Equal-weight products → `card-horizontal` + `card-horizontal-reversed` (alternating)
- Product with strong review → `card-single-testimonial`

Present selection with rationale. Wait for approval.

---

## Step 3: Copy (Token Values)

Read `references/brand-voice.md` before writing any copy.

Write values for every token that will be used. Key rules:
- `HEADLINE` case **depends on the font used in the selected template** — check the template comment block:
  - **Cervanttis templates** (hero-a, hero-b, hero-c, hero-d, upsell-noir, opt-out) → **MUST be lowercase**. e.g. `"for the one who does it all"`
  - **Lust templates** (body-copy, section-headline, all product cards) → **Sentence case**. e.g. `"Some gestures speak before words do."`
- `OPT_OUT_HEADLINE` → always lowercase (Cervanttis)
- `UNSUBSCRIBE_URL` token value → `{{ unsubscribe_url }}` (single braces, spaces inside — exact Klaviyo syntax)
- `REVIEW_STARS` → use Unicode star characters: `★★★★★`
- `BODY_P2` → empty string `""` if only one paragraph needed

---

## Step 4: Component Selection

Read `references/manifest.json` to confirm component file paths and token names.

Standard component order:

```
header                       ← always first
hero (choose one variant)    ← always
opt-out                      ← if required (immediately after hero)
body-copy
divider (optional — max 1 non-line divider per email)
section-headline
products (1–5 cards, mixed types)
testimonial                  ← if review copy available
promo-code                   ← if campaign has offer
upsell-noir                  ← closing beat
delivery-cutoffs             ← if hard deadline
trust-bar                    ← always
footer                       ← always last
```

**Hero selection guide:**

| Variant | When to use |
|---|---|
| `hero-a` | Standard campaigns. Maximum photo impact. |
| `hero-b-white/clay/noir` | Photo must be seen unobscured. Editorial feel. |
| `hero-c1` / `hero-c2` × `white/clay/noir` | Portrait photography. Most editorial. |
| `hero-d-noir` | Launches, VIP, re-engagement. Maximum brand statement. |
| `hero-d-clay` / `hero-d-white` | Type-forward but warmer tone. |

### Designed blocks (graphic-designed image blocks)

Designed blocks live in `references/templates/blocks/` and are listed under `components.blocks` in the manifest. They are graphic-designed, fully-composed image blocks (600px wide, variable height) that are **always sliced to PNG** — never shipped as live email HTML. Because they are rasterised, they use rich CSS (`transform:rotate`, `position:absolute` layering, `box-shadow`, negative-margin overlap) that email clients would strip or break. They drop into the single 600px column exactly like any other sliced component, and use the same locked system (Cervanttis lowercase script, Lust sentence-case display, NeuzeitGro sans, Noir/Clay/White, square black buttons).

| Block | When to use | Notes |
|---|---|---|
| `editorial-hero` | Opening beat for editorial/engagement sends where one strong photo carries the story. | Photo + Lust headline + Cervanttis accent + square button on a plate that overlaps the photo. One per email; place a normal `header` above it. |
| `feature-list` | Explaining 2–4 reasons-to-believe / value props beside a single product polaroid. Mid-email. | Tilted polaroid + clay disc bullets. Max one per email. |
| `polaroid-collage` | Social-proof / "in their words" moment, or a multi-occasion montage. After products, before the closing beat. | Three tilted overlapping polaroids on Clay + Lust pull-quote. Max one per email. |
| `caption-bar-hero` | Photo-led opening where one image carries the story and the message is a short caption (editorial / occasion / flower-of-the-month). The corpus's most common opener. | Full-bleed photo + caption bar (NeuzeitGro label + Cervanttis caption + button). Parametrised palette. First-class **GIF-hero** candidate. One per email; header above it. |
| `story` | Founder / behind-the-scenes / brand-story "note" beat. Mid-email, after the hero. | Tilted-polaroid portrait + Lust headline + narrative + Cervanttis signature. Parametrised palette. Max one per email. |
| `designed-product-card` | A single spotlight product that needs a designed treatment (badge + big serif name/price). Use plain `card-*` for 3–5 product grids. | Photo + tilted Cervanttis badge ribbon + Lust name/price + button. Parametrised palette; `BADGE_TEXT=""` hides the ribbon. Max one per email. |
| `offer-panel` | Promo / sale / flash / Black Friday / free-shipping / rewards — and **giveaways** (GIVEAWAY MODE). Open or strong-close beat for promo sends. | Huge Lust offer value + dashed promo-code box + rotated Cervanttis sticker + button. Parametrised palette (+ seasonal accent allowed). `PROMO_CODE=""` for giveaways. The designed hero version of `sections/promo-code`. Max one per email. |
| `howto-steps` | Care guides / how-to / "make them last" sequences — a **vertical** numbered 3-step flow with a photo per step. Mid-email affirm beat. | Big Lust step numerals + NeuzeitGro caps titles + tilted framed step photos (alternating left/right). Parametrised palette. Exactly three steps. Use `sections/three-column-steps-*` for a compact horizontal partner-flow instead. Max one per email. |
| `comparison-vs` | Us-vs-them / bought-vs-got / before-after side-by-side. Mid-email affirm beat for differentiation moments. | Two square photos (left greyscaled "before/others", right bordered "after/us") + central circular Cervanttis "vs" badge straddling the columns. Parametrised palette. Max one per email. |
| `image-text` | A product/range spotlight pairing one strong image with a short headline + body + button (spotlight / range launch / value prop / occasion gifting). Mid-email beat. | 2/3-width image (400px) + 1/3 text column (NeuzeitGro super-label, Lust headline, NeuzeitGro body, square button). `IMG_SIDE` lever flips the image `left`/`right`. Parametrised palette. Max one per email. |
| `editorial-collage` **(DRAFT — pending design review)** | A more art-directed editorial/newsletter opener or affirm beat wanting a layered, gallery-wall feel beyond `polaroid-collage`. | Three overlapping tilted photo frames + NeuzeitGro label + Cervanttis accent + Lust pull-quote + button. Parametrised palette; `ROTATION` lever. **Max one per email; slice to PNG.** Draft — not ship-ready until a designer signs off. |
| `annotated-product` **(DRAFT — pending design review)** | A single hero product whose 2–3 reasons-to-believe read best as hand-written callouts pinned on the photo — a playful alternative to `designed-product-card`. Mid-email. | Product photo + three rotated, overlapping Cervanttis callout chips + Lust name/price + button. Parametrised palette; `ROTATION` lever. **Max one per email; slice to PNG.** Draft — not ship-ready until a designer signs off. |

**Selection rules for designed blocks:**
- They are *content blocks*, not replacements for `header`/`footer` — keep the standard `header` first and `footer` last.
- `editorial-hero` may be used **instead of** a standard hero (it is the hero), or after one for a second editorial beat. Do not stack two designed blocks back-to-back without a divider.
- Treat each as a single sliced unit: fill tokens, render, upload, link. No per-element editing.
- Token case follows the same font rules: any Cervanttis token (`ACCENT_SCRIPT`, `*_CAPTION`, `QUOTE_ACCENT`, `CAPTION`, `SIGNATURE`, `BADGE_TEXT`) is **lowercase**; Lust tokens (`HEADLINE`, `PULL_QUOTE`, `PRODUCT_NAME`, `PRODUCT_PRICE`) are sentence case.

### `blocks/journal-tile` — live-HTML "From the Journal" row (the exception)

Unlike every other `blocks/*` entry above, `journal-tile` is **not sliced to PNG** — it
ships as **live HTML** (it is listed in `manifest.json → assembly.html_only_components`).
That is deliberate: each tile is its own `<a href>`, so all 2–3 article links work in the
Klaviyo push (a single sliced PNG could only carry one link).

- **When to use:** linking **2–3 blog posts** (e.g. "More from Kellie", "From the
  Journal"). An editorial "more reading" beat — place it **after products, before
  `upsell-noir`**. Best for `editorial_digest` / `lifecycle` / `social_proof`; avoid for
  `discount_offer` / `occasion_gifting`.
- **Why not product cards:** `journal-tile` has **no price field** and carries **article
  semantics**; `products/card-*` imply a buyable SKU. Use `journal-tile` (not a repurposed
  `products/card-horizontal`) whenever the row links blog posts rather than products.
- **Lean tokens (no `PANEL_*` palette):** per tile — `TILE_n_IMAGE_URL`, `TILE_n_EYEBROW`,
  `TILE_n_TITLE` (**sentence case**), `TILE_n_TEASER`, `TILE_n_LINK_URL`; plus section-level
  `SECTION_LABEL` and `SECTION_HEADLINE`. **Tile 3 is optional** — set
  `TILE_3_IMAGE_URL=""` (and the other `TILE_3_*` to `""`) to render a 2-up row.
- **Caveat — fonts:** because it is live HTML, the inbox uses **web-safe fonts** (title
  falls back to **Georgia**, eyebrow/teaser to Gill Sans). Don't expect Lust rendering as
  you would on a sliced block — it's a secondary "more reading" module, not a hero.

### Parametrised palette (designed blocks)

`caption-bar-hero`, `story`, `designed-product-card`, `offer-panel`,
`howto-steps` and `comparison-vs` are **parametrised on
palette**. Each exposes four `PANEL_*` tokens — fill all four by **copying one
preset row verbatim** from `manifest.json → components.block_palette_presets`
(or the `PALETTE PRESETS` block in the template comment). The agent never
invents a hex value, so every variation stays inside the locked
Noir/Clay/White system.

| Preset | PANEL_BG | PANEL_TEXT | PANEL_SUB | PANEL_BORDER | button |
|---|---|---|---|---|---|
| white | `#ffffff` | `#444444` | `#aaaaaa` | `#e8e2da` | black-on-white |
| clay | `#D8CCBE` | `#000000` | `#5f574d` | `#c7b9a9` | black-on-white |
| 50clay | `#EBE5DF` | `#666666` | `#8a8178` | `#ded7cf` | black-on-white |
| noir | `#000000` | `#cfcac3` | `#888888` | `#2c2825` | **white-on-black** |

On the **noir** preset only, swap the button background to `#ffffff` and the
button text to `#000000`. Layout levers: `caption-bar-hero` `IMG_HEIGHT` =
`600` (square) or `440` (editorial 3:2); `designed-product-card` `BADGE_TEXT` =
lowercase ribbon text or `""` to hide.

**Composition levers (locked enums — a third variation axis).** Several designed
blocks (`editorial-hero`, `story`, `polaroid-collage`, `designed-product-card`, and the
draft `editorial-collage` / `annotated-product`) expose composition levers in addition to
palette — set them from the locked enum values only (never free hex/px), copying from
`manifest.json → components.<block>.levers` or the template comment:

| Lever | Values | Blocks |
|---|---|---|
| `TYPE_SCALE` | `regular` \| `oversized` | `editorial-hero`, `story`, `designed-product-card` |
| `ROTATION` | `flat` \| `subtle` \| `jaunty` | `editorial-hero`, `story`, `polaroid-collage`, `designed-product-card`, `editorial-collage`, `annotated-product` |
| `DENSITY` | `tight` \| `regular` \| `airy` | `polaroid-collage` |
| `ACCENT_ILLO` | `on` \| `off` | `editorial-hero`, `story`, `polaroid-collage`, `designed-product-card` |
| `IMG_SIDE` | `left` \| `right` | `image-text` (which side the image sits) |

Default to the restrained values (`ROTATION=subtle`, `TYPE_SCALE=regular`,
`DENSITY=regular`, `ACCENT_ILLO=off`); reach for `oversized` / `jaunty` / `airy` / `on` as
a deliberate, occasional accent — restraint over loudness. These are also the levers the
Step 6 visual-QA loop **regenerates** when a rendered block fails the rubric.

### Variation & rotation scheme (don't ship same-y sends)

The corpus mine (`references/research/freq.json`,
`references/research/corpus-mine.md`) drives this. Build every email as three
beats and **rotate** so consecutive sends of a series don't repeat:

```
OPEN    → editorial-hero | caption-bar-hero | hero-a/b/c/d | hero-image-only
AFFIRM  → feature-list | story | polaroid-collage | testimonial | designed-product-card | howto-steps | comparison-vs
CLOSE   → upsell-noir | promo-code | designed-product-card
```

Rotation rules (see `manifest.json → components.variation_rules`):
- Track the previous send's `(open_block, palette)` pair and pick a **different**
  combination for the next send in the series. Also vary the composition levers —
  don't repeat the same `(ROTATION, TYPE_SCALE)` pair on the OPEN block in consecutive
  sends.
- Editorial / newsletter sends (the corpus's largest bucket, 25.5%) lean on
  `caption-bar-hero` + `story`; promo sends lean on `editorial-hero` +
  `designed-product-card`.
- **Max one of each designed block per email**; never stack two designed blocks
  back-to-back without a divider; never repeat the OPEN palette on consecutive
  sends.
- Accent (non-monochrome) colour only on occasion/promo sends, only as a
  panel/border — never on type.

### Above-the-fold CTA rule (locked)

Corpus emails are long single-column scrolls (median ~5,000px), so a skimmer
sees only the **top ~700px**. The mine found the primary CTA falls **below**
the fold in the majority of sends — fix that here:

- The **primary CTA must render within the first ~700px** of the assembled
  email. `caption-bar-hero` (button in the caption bar) and `editorial-hero`
  (button on the plate) satisfy this by construction; a bare photo hero
  (`hero-image-only`) does **not** — follow it immediately with a CTA-bearing
  block.
- Enforced by the Step 6 **above-the-fold pre-flight check**.

---

## Step 5: Render (token injection + slicing)

This step fills tokens into templates and renders visual components as PNG slices using the `puppeteer` skill.

### 5a. Classify components

Divide the selected component list into two groups:

**Slice to PNG** (visual — render via Puppeteer `slice.js`):
- header, all hero variants, all product cards, **all designed blocks (`blocks/*` — editorial-hero, feature-list, polaroid-collage, caption-bar-hero, story, designed-product-card, offer-panel, howto-steps, comparison-vs, image-text)**, body-copy (illustrated variant), testimonial, upsell-noir, trust-bar, divider-illo-*

**Slice to animated GIF** (animated hero — render via `slice-gif.js`, Step 5e):
- A `caption-bar-hero` / `editorial-hero` / `hero-image-only` whose hero is animated. ~31% of the corpus ships an animated GIF hero — treat it as a first-class output, not an afterthought.

**Keep as HTML** (safe in all email clients, stays selectable/responsive):
- opt-out, section-headline, delivery-cutoffs, footer, body-copy-plain, divider-line, divider-whitespace
- **Live-HTML image components (NOT sliced):** `journal-tile` (per-tile links) and `full-width-image` (a single 600px image kept live so it keeps its own click-through link and an animated GIF keeps animating). Both are listed in `manifest.json → assembly.html_only_components`.

**Body-copy variant selection:**
- `body-copy` (sliced) — includes the HandRose accent illustration (bottom-right, 10% opacity). Use when you want the illustration.
- `body-copy-plain` (HTML) — no illustration, pure typography. **Prefer this by default** — text stays selectable, accessible, and responsive in email clients.

### 5b. Pre-download product images

Shopify CDN URLs are flaky when fetched concurrently during slicing. **Pre-flight each URL then download every image before rendering.** Use local `file://` paths in token values for all `{{PRODUCT_IMAGE_URL}}`, `{{LIFESTYLE_IMAGE_URL}}`, and `{{STUDIO_IMAGE_URL}}` tokens.

#### Preflight: validate image URLs before downloading

For every product image URL, confirm it resolves to an actual image before attempting the full download:

```bash
# Check Content-Type header — must start with "image/"
CONTENT_TYPE=$(curl -sI --max-time 10 "[shopify-url]" | grep -i '^content-type:' | awk '{print $2}' | tr -d '\r')
if [[ "$CONTENT_TYPE" != image/* ]]; then
  echo "ERROR: URL does not resolve to an image (got: $CONTENT_TYPE) — [shopify-url]"
  # Use fallback URL or abort
fi
```

If a URL fails preflight:
1. Try the product's alternate image URL (next variant or `.jpg` format swap).
2. If no alternate is available, flag the product and remove it from the campaign — **do not proceed with a broken image URL**.

#### Download with MIME and byte-size checks

```bash
mkdir -p /tmp/[campaign-slug]/product-images

download_image() {
  local url="$1"
  local dest="$2"
  local min_bytes=5000   # reject files smaller than 5KB as likely error pages

  # Up to 3 attempts with exponential back-off
  for attempt in 1 2 3; do
    curl -sL --max-time 30 "$url" -o "$dest"
    local status=$?
    if [ $status -ne 0 ]; then
      echo "  Attempt $attempt: curl error ($status) for $url"
      sleep $((attempt * 2))
      continue
    fi

    # Byte-size check
    local file_size
    file_size=$(wc -c < "$dest")
    if [ "$file_size" -lt "$min_bytes" ]; then
      echo "  Attempt $attempt: download too small (${file_size} bytes) — likely error page for $url"
      sleep $((attempt * 2))
      continue
    fi

    # MIME check on downloaded file
    local mime
    mime=$(file --mime-type -b "$dest")
    if [[ "$mime" != image/* ]]; then
      echo "  Attempt $attempt: downloaded file is not an image (MIME: $mime) for $url"
      sleep $((attempt * 2))
      continue
    fi

    echo "  ✓ Downloaded $dest (${file_size} bytes, $mime)"
    return 0
  done

  echo "ERROR: Failed to download valid image after 3 attempts: $url"
  return 1
}

# For each product image:
download_image "[shopify-url]" "/tmp/[campaign-slug]/product-images/[slug].jpg" || exit 1
```

After all downloads complete, verify none of the files are missing or zero-byte:

```bash
for f in /tmp/[campaign-slug]/product-images/*.jpg; do
  [ -s "$f" ] || { echo "ERROR: Empty or missing: $f"; exit 1; }
done
```

#### Use local file:// paths in tokens

Then in Step 5c token values, use `file://` paths instead of Shopify URLs:
- `{{PRODUCT_IMAGE_URL}}` = `file:///tmp/[campaign-slug]/product-images/[slug].jpg`
- `{{LIFESTYLE_IMAGE_URL}}` = `file:///tmp/[campaign-slug]/product-images/[slug]-lifestyle.jpg`
- `{{STUDIO_IMAGE_URL}}` = `file:///tmp/[campaign-slug]/product-images/[slug]-studio.jpg`

The same applies to every image token in a **designed block** — pre-download each and point the token at a local `file://` path:
- `editorial-hero`: `{{HERO_IMAGE_URL}}`
- `feature-list`: `{{POLAROID_IMAGE_URL}}`
- `polaroid-collage`: `{{PHOTO_1_URL}}`, `{{PHOTO_2_URL}}`, `{{PHOTO_3_URL}}`

The product photos are baked into the slice PNGs during rendering — Step 8 uploads the composited slices to Klaviyo, so the original URLs aren't needed downstream.

### 5c. Prepare component HTML files

> **Note on template size:** Templates contain `{{ASSETS_BASE}}` tokens instead of base64 illustration data. This keeps each template file under 5KB so the agent can read them without context window pressure. The `slice.js` script resolves `{{ASSETS_BASE}}` to the absolute assets path at render time — the agent never handles image data directly.

For each **visual** component:
1. Read the template from `references/templates/[path].html`
2. Wrap it in `references/shell/shell-preview.html` (base64 fonts for correct Puppeteer render)
3. Replace every `{{TOKEN}}` with its value (product images use `file://` paths from 5b)
4. Verify no `{{` or `}}` remain
5. Save as a standalone HTML file in a working directory: `/tmp/[campaign-slug]/components/[name].html`

For each **text** component:
1. Read the template from `references/templates/[path].html`
2. Replace every `{{TOKEN}}` with its value
3. Verify no `{{` or `}}` remain
4. Hold in memory — these go directly into the final email HTML

### 5d. Slice visual components

Call the `puppeteer` skill's `slice.js` on the components directory. **Capture stdout to a file** so the `__SLICE_MANIFEST__` can be parsed in Step 6:

```bash
node [puppeteer-skill-path]/references/scripts/slice.js \
  --input /tmp/[campaign-slug]/components/ \
  --output /tmp/[campaign-slug]/slices/ \
  --assets [puppeteer-skill-path]/references/assets \
  --width 600 \
  --scale 2 \
  --verbose \
  | tee /tmp/[campaign-slug]/slice-output.txt
```

The `--assets` flag is required — it tells `slice.js` where to find the illustration PNG assets for `{{ASSETS_BASE}}` token substitution.

Parse the `__SLICE_MANIFEST__` from `/tmp/[campaign-slug]/slice-output.txt` to get the list of produced PNG files. The manifest includes a `broken_images` array per slice — if any entry is non-empty, the slice has failed image loads and must be re-rendered (check the `file://` path exists and the pre-download in 5b succeeded).

If any slice fails → fix the component HTML and re-run before proceeding.

### 5e. Animated GIF hero (procedural image-creation workflow)

~31% of corpus emails ship an **animated GIF hero**, and `image/gif` always
means *animated* (the mine found 20/20 sampled GIFs were multi-frame). When a
campaign calls for an animated hero, produce it with `slice-gif.js` instead of a
static PNG. The corpus animates heroes three ways — pick the matching frame
recipe:

| Pattern | Frames | How each frame differs |
|---|---|---|
| **Reveal** (flower-of-the-month / product reveal) | 2–4 | swap `HERO_IMAGE_URL` (teaser → reveal) and/or `CAPTION` |
| **UGC / review carousel** | 8–18 | swap `HERO_IMAGE_URL` to each UGC/review photo |
| **Sale / urgency flash** | 4–5 | swap `PANEL_BG`/`CAPTION` to flash the offer (e.g. white ↔ clay, "ends tonight") |

**Workflow** (uses `caption-bar-hero` / `editorial-hero` / `hero-image-only`):

1. **Pick the hero block** and the frame recipe above. Decide N frames.
2. **Pre-download every frame image** to local `file://` paths (Step 5b rules —
   pre-flight, MIME + byte-size checks). Every frame must render at the **same
   content height** — author the block height (e.g. `IMG_HEIGHT`) identically
   across frames.
3. **Build N frame HTML files** in a frames dir, named so they sort in play
   order: `frame-00.html`, `frame-01.html`, … Each is the *same* block with one
   token changed per the recipe, wrapped in `shell-preview.html` and fully
   token-filled (no `{{ }}` left).
4. **Render to one looping GIF:**

   ```bash
   node [puppeteer-skill-path]/references/scripts/slice-gif.js \
     --frames /tmp/[campaign-slug]/gif-frames/ \
     --output /tmp/[campaign-slug]/slices/hero.gif \
     --assets [puppeteer-skill-path]/references/assets \
     --width 600 --scale 1 --delay 700 --loop 0 --verbose
   ```

   `--scale 1` keeps the GIF file size email-friendly; `--delay` is per-frame ms;
   `--loop 0` loops forever. The script prints a `__GIF_MANIFEST__` block (frame
   count, dimensions, bytes) — confirm `frames` matches N.
5. **Treat the GIF like any other slice** downstream: upload it in Step 8
   (`POST /api/images/` accepts GIF), get the Klaviyo CDN URL, and in Step 9
   drop it in as `<img src="…hero.gif" width="600">` wrapped in the CTA
   `<a href>`. No special production handling — it's just an animated slice.

> **Deps:** `slice-gif.js` uses `gifenc` + `pngjs`, installed by the same
> `npm install` in `references/` as `slice.js` (Troubleshooting). If missing,
> re-run `npm install` there.

---

## Step 6: Validation

**Slice validation:**
- [ ] `__SLICE_MANIFEST__` parsed — all expected PNG files are listed
- [ ] Every visual component has a corresponding PNG in `/tmp/[campaign-slug]/slices/`
- [ ] No slice errors in the Puppeteer output
- [ ] Every manifest entry has `broken_images: []` — any failures mean a pre-downloaded image is missing or `file://` path is wrong

**Product-grid aggregate check (mandatory):**

After parsing `__SLICE_MANIFEST__`, collect all product-card slice entries and verify the entire grid is clean — not just individual cards:

```bash
# Parse manifest and check all product card slices collectively
node -e "
const fs = require('fs');
const out = fs.readFileSync('/tmp/[campaign-slug]/slice-output.txt', 'utf8');
const match = out.match(/__SLICE_MANIFEST__([\s\S]*?)__END_MANIFEST__/);
if (!match) { console.error('No manifest found'); process.exit(1); }
const manifest = JSON.parse(match[1]);

const productSlices = manifest.slices.filter(s =>
  s.file.match(/card-|product-/i)
);
const gridBroken = productSlices.flatMap(s =>
  (s.broken_images || []).map(img => ({ slice: s.file, img }))
);

if (gridBroken.length > 0) {
  console.error('PRODUCT GRID BROKEN IMAGES:');
  gridBroken.forEach(b => console.error('  ' + b.slice + ': ' + b.img));
  process.exit(1);
}
console.log('Product grid OK — ' + productSlices.length + ' card(s), 0 broken images');
"
```

**Fail the build** if any broken-image indicator appears across the composed product grid. Do not proceed to Step 7 until all product card slices are clean.

If a card has broken images:
1. Confirm the corresponding `file://` path in the component HTML matches the pre-downloaded file.
2. Re-run the download for that image (Step 5b `download_image` function).
3. Re-render only the affected card slice (pass the single HTML file to `slice.js --input`).
4. Re-check manifest before continuing.

**Token validation (text components):**
- [ ] No `{{` or `}}` characters remain in any text component HTML
- [ ] `{{ unsubscribe_url }}` is present in footer with single braces and internal spaces

**Content checks:**
- [ ] Cervanttis headlines (hero, upsell-noir, opt-out) are lowercase in token values
- [ ] Lust headlines (body-copy, section-headline, product cards) are sentence case
- [ ] `REVIEW_STARS` uses `★` Unicode characters

**Visual QA loop — render-and-critique (mandatory for every designed `blocks/*`):**

A designed block can validate cleanly (tokens filled, no broken images) and still *look*
wrong — unbalanced, low-contrast, off-brand. After `POST /api/render` (or
`POST /api/render-slices`), **the agent must actually view the returned PNG** for each
designed block and score it against this short rubric before accepting it:

| Criterion | Pass looks like |
|---|---|
| **Composition balance** | Weight is distributed; nothing crammed or stranded; tilt/overlap reads intentional, not accidental. |
| **Type contrast** | Clear hierarchy — Lust display vs NeuzeitGro body vs Cervanttis accent are distinct; the headline leads. |
| **Focal clarity** | One obvious focal point (the product / the photo / the quote); the eye knows where to land and where the CTA is. |
| **Brand restraint** | Locked Noir/Clay/White palette only, monochrome type, square black button — no off-brand colour/type, no clearance-y loudness. |

If a block **fails** any criterion, **regenerate its levers** — adjust `ROTATION`,
`TYPE_SCALE`, `DENSITY`, `ACCENT_ILLO`, or the `palette` preset (locked enum values only —
never hand-edit the PNG or invent hex/px) — re-render, and re-score. Loop until it passes.
This is a composition tune, not a redesign; a block that can't pass within the locked
levers is a template issue → flag for design review (and for the DRAFT blocks
`editorial-collage` / `annotated-product`, expect to flag rather than ship).

**Gate inbound imagery through `creative-ugc-photo-review` first.** Any customer/UGC or
externally-supplied photo destined for a block (`HERO_IMAGE_URL`, `PHOTO_*_URL`,
`FRAME_*_URL`, `PORTRAIT_IMAGE_URL`, `PRODUCT_IMAGE_URL`) must clear the
`creative-ugc-photo-review` skill's standard (`resources/fig-and-bloom-rubric.md`) **before**
it is placed in a token — reuse that rubric so the photo meets brand visual standards;
don't let unreviewed imagery enter a render.

**Above-the-fold pre-flight check (mandatory):**

A skimmer must be able to click without scrolling. Sum the rendered heights of
the assembled slices/blocks from the top and confirm the **primary CTA falls
within the first ~700px**:

```bash
node -e "
const fs=require('fs');
// [{name, height_css_px, has_primary_cta}] in assembly order, from the slice manifest + text-block heights
const blocks = JSON.parse(fs.readFileSync('/tmp/[campaign-slug]/assembly-order.json','utf8'));
let y=0, foldCta=false;
const FOLD=700;
for (const b of blocks){ if(b.has_primary_cta && y<FOLD){foldCta=true;break;} y+=b.height_css_px; }
if(!foldCta){ console.error('ABOVE-FOLD FAIL: primary CTA does not appear within '+FOLD+'px. Lead with a CTA-bearing hero (editorial-hero / caption-bar-hero) or add a CTA block right under the photo hero.'); process.exit(1); }
console.log('Above-fold OK — primary CTA within '+FOLD+'px');
"
```

- `header` (~64px) + a CTA-bearing hero (`editorial-hero`, `caption-bar-hero`,
  `hero-a/b/c/d`) passes by construction.
- A bare `hero-image-only` (600×750) pushes the CTA past the fold — **fail**:
  follow it immediately with a CTA-bearing block, or switch the opener.

**Variation check (campaign series):**
- [ ] The `(open_block, palette_preset)` pair differs from the previous send in
      the series (see `manifest.json → components.variation_rules`)
- [ ] No designed block (`blocks/*`) appears more than once in the email
- [ ] No two designed blocks are stacked back-to-back without a divider

---

## Step 7: Preview

Assemble a preview email that mixes local slice paths (for review) with the text HTML blocks.

**Preview assembly structure** (table-based, 600px wide):
```
[header slice img — local path]
[hero slice img — local path]
[opt-out HTML — if required]
[body-copy slice img — local path]
[section-headline HTML]
[product card slices — local paths, wrapped in <a href>]
[testimonial slice — local path]
[upsell slice — local path, wrapped in <a href>]
[delivery-cutoffs HTML — if required]
[trust-bar slice — local path]
[footer HTML]
```

For preview, slice `<img>` tags use `file://` local paths. These will be replaced with Klaviyo CDN URLs in Step 9.

Save preview HTML to Google Drive only — do not write preview HTML to local disk. Read `reference-google-drive` skill for conventions:
- Folder: use the Step 7a run folder (`Campaign Drafts/{YYYYMMDDhhmm}/{campaign-slug}-{run-id}`)
- Title: `{YYYY-MM-DD} {Campaign Name} — Design Preview`
- mimeType: `text/html`, disableConversionToGoogleType: `true`
- Use `GWS_USER_ADMIN` credentials for all Drive API calls (see **Google Workspace Credentials** section above)

State: *"Preview uses locally-rendered PNG slices — fonts, illustrations, and layout are browser-rendered and pixel-accurate. Review at 600px width."*

### Step 7a: Create deterministic run-scoped Drive folders

Before uploading any preview/production artifacts, create and use nested subfolders under the Campaign Drafts parent. Use `GWS_USER_ADMIN` for all Drive folder creation calls:

```bash
env -u GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE \
  GOOGLE_WORKSPACE_CLI_CONFIG_DIR=$GWS_USER_ADMIN \
  gws drive files create \
  --json '{"name": "{TIMESTAMP_YYYYMMDDHHMM}", "mimeType": "application/vnd.google-apps.folder", "parents": ["14SJXWGGrZAoJUmkEb0FlBDSHHNyf_bIj"]}' \
  --params '{"fields": "id,name,webViewLink", "supportsAllDrives": true}'
```

1. Compute `TIMESTAMP_YYYYMMDDHHMM` in UTC by default (`YYYYMMDDhhmm`, 24-hour clock).
2. If the caller explicitly provides a timezone override, compute the same format in that timezone.
3. Under parent `Campaign Drafts` (`14SJXWGGrZAoJUmkEb0FlBDSHHNyf_bIj`), create/use:
   - timestamp folder: `{TIMESTAMP_YYYYMMDDHHMM}`
   - run folder inside timestamp folder: `{campaign-slug}-{run-id}`
4. Save all campaign artifacts (preview HTML, production HTML, and any optional packaging files) into this run folder.
5. In run comments, always include links to:
   - Campaign Drafts parent folder
   - timestamp folder
   - run folder
   - uploaded artifact files

This structure is required to avoid destination collisions across concurrent runs and to keep outputs traceable.

**Wait for explicit human approval before proceeding to Step 8.**

If edits are requested:
- **Copy changes** → update token values, re-render affected slices, re-assemble
- **Component changes** → update selection, re-render, re-assemble
- **Visual/design changes** → these require a template file update. Flag to human.

---

## Step 8: Upload slices to Klaviyo

Upload each PNG slice from `/tmp/[campaign-slug]/slices/` to the Klaviyo media library.

```
POST /api/images/
```

Note the returned Klaviyo CDN URL for each slice. Store as a mapping:
```json
{
  "header": "https://cdn.klaviyo.com/media/.../header.png",
  "hero-a": "https://cdn.klaviyo.com/media/.../hero-a.png",
  "product-card-1": "https://cdn.klaviyo.com/media/.../product-card-1.png",
  ...
}
```

See `references/klaviyo-html.md` for the image upload API spec.

## Step 9: Production HTML

Assemble the final email HTML using Klaviyo CDN slice URLs (replacing local file paths).

**Production assembly rules:**
- All slice `<img>` tags: `src` = Klaviyo CDN URL, `width="600"`, `style="display:block;width:600px;"`
- All CTAs: slice `<img>` wrapped in `<a href="{{CTA_URL}}">`
- Optional button: every button is wrapped in `{{#CTA_TEXT}}…{{/CTA_TEXT}}` — leave `CTA_TEXT` empty to hide the button; if `CTA_URL` is set the whole (sliced) component still links to it (designed blocks are sliced to PNG on publish and the slice is linked via `deriveLink` / `CTA_URL`)
- Decorative slices: empty `alt=""`
- Hero/product slices: descriptive `alt="{{HEADLINE}}"` or `alt="{{PRODUCT_NAME}}"`
- Text components: inserted as raw HTML (no shell wrapper needed — inline styles only)
- Unsubscribe: `{{ unsubscribe_url }}` in footer — exact Klaviyo syntax

Save to Google Drive only — do not write production HTML to local disk:
- Folder: use the Step 7a run folder (`Campaign Drafts/{YYYYMMDDhhmm}/{campaign-slug}-{run-id}`)
- Title: `{YYYY-MM-DD} {Campaign Name} — Production HTML`
- mimeType: `text/html`, disableConversionToGoogleType: `true`
- Use `GWS_USER_ADMIN` credentials for all Drive API calls (see **Google Workspace Credentials** section above)

**Font check:** grep production HTML for `base64` in `<style>` blocks. Should find none — the production email has no embedded fonts, only Klaviyo-hosted slice images.

**Wait for explicit human approval before proceeding to Step 10.**

---

## Step 10: Klaviyo Deployment

Read `references/klaviyo-html.md` before making API calls.

**Create template:**
```
POST /api/templates/
{
  "data": {
    "type": "template",
    "attributes": {
      "name": "{Campaign Name} — {YYYY-MM-DD}",
      "editor_type": "CODE",
      "html": "{production_html}"
    }
  }
}
```

Assign template to campaign message. Set list/segment and scheduled send time.

Wait 2–3 seconds after template creation before any follow-up API call (known Klaviyo 404 bug).

**Confirm with human before scheduling send. Never auto-send.**

---

## Template library reference

All templates are in `references/templates/`. Always read the actual file — never reconstruct template HTML from memory.

Read `references/manifest.json` to confirm exact file paths and token names before assembly.

| Reference file | Read before... |
|---|---|
| `references/component-strategy.md` | Choosing components for the campaign objective (before writing JSON) |
| `references/brand-voice.md` | Writing any copy (Step 3) |
| `references/product-selection.md` | Selecting products (Step 2) |
| `references/manifest.json` | Component selection, token names, palette presets, variation rules, gif-hero (Steps 4–5) |
| `references/research/freq.json` | Variation / rotation, block-frequency, gif-hero & above-fold decisions (Steps 4–6) |
| `references/research/corpus-mine.md` | Why those rules exist — the readable corpus analysis |
| `references/klaviyo-html.md` | Klaviyo API calls (Steps 8, 10) |
| `reference-google-drive` skill | Google Drive uploads (Steps 7, 9) — use `$GWS_USER_ADMIN` |
| `puppeteer` skill | Slice rendering (`slice.js`, Step 5) + animated GIF heroes (`slice-gif.js`, Step 5e) — install on VPS first |

---

## Product-card / product-grid regression checklist

Run this checklist any time a campaign includes product card slices before proceeding to Step 7:

- [ ] **URL preflight passed** — every product image URL returned `Content-Type: image/*` before download
- [ ] **All images downloaded** — every `file://` path referenced in component HTML exists on disk
- [ ] **MIME check passed** — every downloaded file identified as `image/*` by `file --mime-type`
- [ ] **Byte-size check passed** — no downloaded file is under 5KB
- [ ] **Per-card broken_images empty** — `broken_images: []` for every card entry in `__SLICE_MANIFEST__`
- [ ] **Grid aggregate check passed** — zero broken-image indicators across all `card-*` and `product-*` slices combined
- [ ] **Visual spot-check** — open at least one product card PNG and confirm the product photo renders (not a grey placeholder or browser broken-image icon)

---

## Troubleshooting

### `minimist` not found when running slice.js

**Symptom:**
```
Error: Cannot find module 'minimist'
    at Function.Module._resolveFilename (node:internal/modules/cjs/loader:1039:15)
```

**Cause:** The `reference-puppeteer` skill's npm dependencies have not been installed, or were installed in the wrong directory.

**Fix:**
```bash
# Navigate to the puppeteer skill's references directory and install deps
cd [puppeteer-skill-path]/references
npm install

# Verify
node -e "require('minimist'); console.log('minimist OK')"
node -e "require('puppeteer'); console.log('puppeteer OK')"
```

The `references/` directory contains `package.json` with `minimist`, `puppeteer`, `gifenc` and `pngjs` as dependencies (the last two power the animated GIF-hero path, `slice-gif.js`). Running `npm install` inside that directory is the only setup step needed. Do not run `npm install` at the repo root.

### Product images render as broken placeholders despite successful slice.js run

**Symptom:** slice.js exits 0 and produces PNGs, but the PNG shows a grey box or browser broken-image icon where the product photo should be.

**Cause:** `file://` path in the component HTML is wrong — mismatched slug, extension, or directory path.

**Fix:**
1. Open the failing component HTML file and find the `<img src="file:///...">` value.
2. Check that exact path exists: `ls -lh "file-path-here"` (strip `file://` prefix).
3. If missing, re-run the `download_image` function from Step 5b for that URL.
4. If the path is wrong, correct the token value in the component HTML and re-render.

### `broken_images` non-empty for a slice but PNG looks correct

**Symptom:** `__SLICE_MANIFEST__` reports `broken_images` for a slice, but the PNG appears correct when opened.

**Cause:** Puppeteer flagged an image that loaded with zero natural dimensions (e.g., a 1×1 tracking pixel, SVG with no intrinsic size). This is usually harmless for illustration assets but should be investigated.

**Fix:** Check each URL in `broken_images`:
- If it's a decoration/illustration asset, confirm it renders visually in the PNG — if so, it can be treated as a known false positive.
- If it's a product image, treat as broken and re-download.
- Never mark a broken product image as an acceptable false positive.

---

## What the agent does NOT do in v4

- Write HTML
- Choose colours, fonts, or spacing
- Resize or reposition illustrations
- Add, remove, or modify SVG icons
- Override any locked style in a template

If a campaign need cannot be met with the existing templates, escalate for template development. Do not improvise HTML.

---

## Companion: `fig-bloom-email-generator`

> A new companion skill — **`creative/fig-bloom-email-generator`** — packages the brand + persona + lens-routing + schema context into a single LLM call, so a brief (from the email-builder "Create Campaign" button or an agent conversation) produces a complete, validated campaign JSON in one shot.

**Workflow:**
1. Brief comes in (button click → textarea, or agent → user message).
2. Host loads the **system prompt** (`fig-bloom-email-generator/references/system-prompt.md`) — bakes in brand POV, the 8 personas, the Sales Legends lens system, component strategy, token rules, the output schema, and the 13-point QA bar.
3. Host fills the **user template** (`fig-bloom-email-generator/references/user-prompt-template.md`) with the brief + audience.
4. LLM returns campaign JSON. Host validates via `POST /api/validate` and saves via `POST /api/designs`.
5. From here, this skill's workflow takes over: assemble → render → save (already done) → optional Klaviyo draft.

**When to use the generator:** any time a free-form brief needs to become a campaign JSON. The generator handles the *content* (strategy, components, copy, tokens, persona routing). This skill handles the *workflow* (validate, render, save, Klaviyo, slicing).

**See:** `creative/fig-bloom-email-generator/SKILL.md` for the full skill.
