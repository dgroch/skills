---
name: creative-email-campaign-builder
description: Build complete Klaviyo email campaigns for Fig & Bloom using the v4 template library. Use this skill whenever someone asks to create an email campaign, email design, Klaviyo email, marketing email, promotional email, newsletter, or EDM for Fig & Bloom.
---

# Email Campaign Builder — Fig & Bloom (v4)

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
7. PREVIEW       → Assemble preview email (slices + HTML text blocks). Save + Google Drive. Wait for approval.
8. UPLOAD        → Upload approved slices to Klaviyo media library. Get hosted URLs.
9. PRODUCTION    → Assemble final email HTML (Klaviyo slice URLs + text block HTML)
10. KLAVIYO      → Upload template + create campaign. Wait for approval before scheduling.
```

**Every numbered step is a gate. Do not skip ahead.**

**Dependency:** This skill requires the `puppeteer` skill to be installed and configured on the VPS. Verify with `node -e "require('puppeteer'); console.log('OK')"` before first use.

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

---

## Step 5: Render (token injection + slicing)

This step fills tokens into templates and renders visual components as PNG slices using the `puppeteer` skill.

### 5a. Classify components

Divide the selected component list into two groups:

**Slice to PNG** (visual — render via Puppeteer):
- header, all hero variants, all product cards, body-copy, testimonial, upsell-noir, trust-bar, divider-illo-*

**Keep as HTML** (text-only — safe in all email clients):
- opt-out, section-headline, delivery-cutoffs, footer, divider-line, divider-whitespace

### 5b. Pre-download product images

Shopify CDN URLs are flaky when fetched concurrently during slicing. Download every `{{PRODUCT_IMAGE_URL}}`, `{{LIFESTYLE_IMAGE_URL}}`, and `{{STUDIO_IMAGE_URL}}` value to local disk before rendering, and use local `file://` paths in the token values.

```bash
mkdir -p /tmp/[campaign-slug]/product-images
# For each product image:
curl -sL "[shopify-url]" -o /tmp/[campaign-slug]/product-images/[slug].jpg
```

Then in Step 5c token values, use `file://` paths instead of Shopify URLs:
- `{{PRODUCT_IMAGE_URL}}` = `file:///tmp/[campaign-slug]/product-images/[slug].jpg`
- `{{LIFESTYLE_IMAGE_URL}}` = `file:///tmp/[campaign-slug]/product-images/[slug]-lifestyle.jpg`
- `{{STUDIO_IMAGE_URL}}` = `file:///tmp/[campaign-slug]/product-images/[slug]-studio.jpg`

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

Call the `puppeteer` skill's `slice.js` on the components directory:

```bash
node [puppeteer-skill-path]/references/scripts/slice.js   --input /tmp/[campaign-slug]/components/   --output /tmp/[campaign-slug]/slices/   --width 600   --scale 2   --verbose
```

Parse the `__SLICE_MANIFEST__` from stdout to get the list of produced PNG files. The manifest includes a `broken_images` array per slice — if any entry is non-empty, the slice has failed image loads and must be re-rendered (check the file:// path exists and the pre-download in 5b succeeded).

If any slice fails → fix the component HTML and re-run before proceeding.

---

## Step 6: Validation

**Slice validation:**
- [ ] `__SLICE_MANIFEST__` parsed — all expected PNG files are listed
- [ ] Every visual component has a corresponding PNG in `/tmp/[campaign-slug]/slices/`
- [ ] No slice errors in the Puppeteer output
- [ ] Every manifest entry has `broken_images: []` — any failures mean a pre-downloaded image is missing or `file://` path is wrong

**Token validation (text components):**
- [ ] No `{{` or `}}` characters remain in any text component HTML
- [ ] `{{ unsubscribe_url }}` is present in footer with single braces and internal spaces

**Content checks:**
- [ ] Cervanttis headlines (hero, upsell-noir, opt-out) are lowercase in token values
- [ ] Lust headlines (body-copy, section-headline, product cards) are sentence case
- [ ] `REVIEW_STARS` uses `★` Unicode characters

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

Save preview HTML to:
- `/mnt/user-data/outputs/{YYYY-MM-DD}-{campaign-slug}-preview.html`
- Google Drive (read `reference-google-drive` skill):
  - Folder: Campaign Drafts (ID: `14SJXWGGrZAoJUmkEb0FlBDSHHNyf_bIj`)
  - Title: `{YYYY-MM-DD} {Campaign Name} — Design Preview`
  - mimeType: `text/html`, disableConversionToGoogleType: `true`

State: *"Preview uses locally-rendered PNG slices — fonts, illustrations, and layout are browser-rendered and pixel-accurate. Review at 600px width."*

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
- Decorative slices: empty `alt=""`
- Hero/product slices: descriptive `alt="{{HEADLINE}}"` or `alt="{{PRODUCT_NAME}}"`
- Text components: inserted as raw HTML (no shell wrapper needed — inline styles only)
- Unsubscribe: `{{ unsubscribe_url }}` in footer — exact Klaviyo syntax

Save to:
- `/mnt/user-data/outputs/{YYYY-MM-DD}-{campaign-slug}-production.html`
- Google Drive: `{YYYY-MM-DD} {Campaign Name} — Production HTML` (same Campaign Drafts folder)

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
| `references/brand-voice.md` | Writing any copy (Step 3) |
| `references/product-selection.md` | Selecting products (Step 2) |
| `references/manifest.json` | Component selection and token names (Steps 4–5) |
| `references/klaviyo-html.md` | Klaviyo API calls (Steps 8, 10) |
| `reference-google-drive` skill | Google Drive uploads (Steps 7, 9) |
| `puppeteer` skill | Slice rendering (Step 5) — must be installed on VPS first |

---

## What the agent does NOT do in v4

- Write HTML
- Choose colours, fonts, or spacing
- Resize or reposition illustrations
- Add, remove, or modify SVG icons
- Override any locked style in a template

If a campaign need cannot be met with the existing templates, escalate for template development. Do not improvise HTML.
