# v5 Email Engine Architecture

Built 2026-05-27 for Fig & Bloom. v5 is a modular primitive-based email composition pipeline replacing the monolithic v4 templates (moved to `templates-legacy/`).

> **DESIGN SYSTEM IS MANDATORY:** All 36 primitives implement the Fig & Bloom design system — brand fonts (Lust, Cervanttis, NeuzeitGro), colours (Noir, Clay, 50% Clay), illustrations (8 variants with opacity rules), button styles, and mobile responsive classes. The v4 component templates in `references/templates/` are the source of truth for each primitive's HTML output.

## Directory Structure

```
v5-engine/
├── briefs/              # Campaign brief JSON files (slot-based format)
├── primitives/          # 36 atomic rendering components (each render.js)
│   ├── hero-a/          # 14 hero variants (A, B×3, C1×3, C2×3, D×3, image-only)
│   ├── card-horizontal/ # 4 product card layouts
│   ├── body-copy/       # 2 body copy variants (with/without illustration)
│   ├── section-headline/
│   ├── testimonial/
│   ├── opt-out/
│   ├── promo-code/
│   ├── trust-bar/
│   ├── upsell-noir/
│   ├── delivery-cutoffs/
│   ├── three-column-steps/
│   ├── divider-illustration/
│   ├── divider-image/
│   ├── divider-line/
│   ├── divider-whitespace/
│   ├── header/
│   ├── footer/
│   ├── cta/
│   └── spacer/
├── output/              # Generated HTML + PNG/PDF
├── themes.json          # Single theme: fig-and-bloom (full brand tokens)
├── compose.js           # Main composition pipeline (slot-based + layout-based modes)
├── validate.js          # Pre-flight validation (brief + output)
├── render.js            # Playwright HTML → PNG/PDF rendering
├── klaviyo.js           # Klaviyo API integration (4-step campaign creation)
└── index.js             # CLI entry point (compose|validate|render|pipeline)
```

## Primitive Inventory (36)

### Heroes (14)

| Primitive | Description | Key Opts |
|-----------|-------------|----------|
| `hero-a` | Text over image (30% black mask, 500px height) | `superLabel`, `headline`, `subheadline`, `ctaText`, `ctaUrl`, `heroImage` |
| `hero-b-white` | Text band (white) + full-bleed photo | Same + `assetsBase` |
| `hero-b-noir` | Text band (black) + full-bleed photo | Same |
| `hero-b-clay` | Text band (#D8CCBE) + full-bleed photo | Same |
| `hero-c1` | Split: photo left / text right (white) | Same |
| `hero-c1-noir` | Split: photo left / text right (black) | Same |
| `hero-c1-clay` | Split: photo left / text right (clay) | Same |
| `hero-c2` | Split: text left / photo right (white) | Same |
| `hero-c2-noir` | Split: text left / photo right (black) | Same |
| `hero-c2-clay` | Split: text left / photo right (clay) | Same |
| `hero-d-noir` | Type-forward, no photo, flanking illustrations (black bg) | `superLabel`, `headline`, `subheadline`, `ctaText`, `ctaUrl`, `assetsBase` |
| `hero-d-white` | Type-forward (white bg) | Same |
| `hero-d-clay` | Type-forward (clay bg) | Same |
| `hero-image-only` | Full-width image, no text (4:5 ratio, 600×750px) | `heroImage`, `imageAlt`, `linkUrl` |

### Product Cards (4)

| Primitive | Description | Key Opts |
|-----------|-------------|----------|
| `card-horizontal` | Image left 280×350, info right 320px | `productImage`, `productName`, `productLabel`, `productOccasion`, `productPrice`, `productUrl` |
| `card-horizontal-reversed` | Info left, image right | Same |
| `card-lifestyle-studio` | Lifestyle 600×400 + studio 600×500, info below | `sectionSuper`, `sectionHeadline`, `lifestyleImage`, `studioImage`, `productDesc`, `ctaText`, `ctaUrl` |
| `card-single-testimonial` | Product 340px + testimonial 260px col (50% Clay bg) | Same + `quote`, `attribution`, `rating` |

### Sections (11)

| Primitive | Description | Key Opts |
|-----------|-------------|----------|
| `section-headline` | Lust 28px headline + super label | `headline`, `superLabel` |
| `body-copy` | Body copy with HandRose illustration accent | `headline`, `bodyP1`, `bodyP2`, `assetsBase` |
| `body-copy-plain` | Body copy without illustration | `headline`, `bodyP1`, `bodyP2` |
| `testimonial` | 50% Clay bg, stars, quote, Face illustration | `reviewStars`, `reviewText`, `reviewerName` |
| `opt-out` | 50% Clay bg, Cervanttis heading, outline CTA | `optOutHeadline`, `optOutBody`, `unsubscribeUrl` |
| `promo-code` | Dashed border, Lust code text | `promoCode`, `ctaText`, `ctaUrl` |
| `trust-bar` | 5-item USP icon row (CDN image) | `imageSrc` (optional override) |
| `upsell-noir` | Noir bg, flanking illustrations, Cervanttis headline | `headline`, `ctaText`, `ctaUrl` |
| `delivery-cutoffs` | 2-column region/cutoff date rows | `region1`, `cutoff1`, `region2`, `cutoff2` |
| `three-column-steps` | 3-col numbered steps, background variant | `headline`, `bgVariant` (white\|clay\|50clay\|beige), `step1Number`, `step1Text`, `ctaText`, `ctaUrl` |
| `footer` | Links, social, legal, unsubscribe | `links[]`, `social[]`, `unsubscribeHref`, `companyName` |

### Dividers (4)

| Primitive | Description | Key Opts |
|-----------|-------------|----------|
| `divider-line` | 1px solid #e8e2da rule | `color` (optional) |
| `divider-whitespace` | 48px breathing gap | `height`, `background` |
| `divider-image` | Full-bleed image strip (180px or 340px) | `imageUrl`, `height` |
| `divider-illustration` | Illustration strip with background variants | `bgVariant` (white\|clay\|50clay\|noir), `illustration` (BodyFlower, HandFlower, etc.) |

### Utilities (3)

| Primitive | Description | Key Opts |
|-----------|-------------|----------|
| `header` | Brand logo centred, 120×24px, bottom border | None (static) |
| `cta` | CTA buttons (primary/outline variants) | `buttons[]` ({text, href, variant}) |
| `spacer` | Vertical whitespace | `height` (px) |

## Composition Modes

### Mode 1: Slot-Based (Recommended)

Brief defines a `slots` object. Each slot specifies its `primitive` name and all options directly. Compose iterates in order.

```json
{
  "slots": {
    "header": {},
    "hero": {
      "primitive": "hero-b-white",
      "superLabel": "GIFTING",
      "headline": "when the card is the hard part",
      "ctaText": "FIND THE WORDS",
      "ctaUrl": "/blogs/..."
    },
    "body-main": {
      "primitive": "body-copy",
      "headline": "The flowers were easy.",
      "bodyP1": "You picked the bouquet in three minutes."
    }
  }
}
```

### Mode 2: Layout-Based (Legacy)

Brief specifies `layout` name; compose reads `layouts/<name>/layout.js` for slot order, defaults, and required slots. Uses `mapBriefToSlot()` to map flat brief fields to slot options.

## Theme

Single theme `fig-and-bloom` in `themes.json`:
- **Palette:** noir #000, white #FFF, clay #D8CCBE, clay50 #EBE5DF, border #e8e2da, bodyBg #2c2825
- **Typography:** Lust (display), Cervanttis (script accent, max 3/email, lowercase only), NeuzeitGro (body, Light 300 / Bold 700)
- **Buttons:** primary (#000→#FFF), outline (transparent, 1.5px solid #000), small (#000, 9px), primaryWhite, outlineWhite
- **Assets base:** Shopify CDN for fonts and illustrations

## Email Wrapper (`compose.js::wrapEmail()`)

- 7 @font-face declarations (Cervanttis, Lust, NeuzeitGro Light/Bold, Gill Sans Light/Regular/Bold)
- Full mobile @media block with responsive classes (.ew, .hh, .sh, .pn, .hc, .hi, .hinfo, .pt, .ptimg, .pttesti, .ud, .uil, .cc, .fi)
- Body background: #2c2825 (warm dark brown)
- 600px max-width container with `<center>` wrapper
- Apple data detector override

## Pipeline Commands

```bash
node index.js pipeline <brief.json>  # Full: validate → compose → validate output → render
node index.js compose <brief.json>   # HTML only
node index.js validate <brief.json>  # Validation only
node index.js render <brief.json>    # HTML → PNG (Playwright + Chromium)
```

## Rendering (Playwright)

`render.js` provides `renderToPng()` and `renderToPdf()`. Playwright launches headless Chromium.

**Setup:** `npm install playwright && PLAYWRIGHT_BROWSERS_PATH=/opt/data/.cache/playwright npx playwright install chromium`

**Pitfall:** `PLAYWRIGHT_BROWSERS_PATH` must be set unconditionally (not `||`) in both `render.js` and `index.js` before `require('playwright')` — the shell env default points to a read-only location. See `references/playwright-setup.md`.

## Klaviyo Upload

`klaviyo.js` provides 4-step campaign creation:

1. `POST /templates/` — upload HTML as CODE template (`editor_type: 'CODE'`)
2. `POST /campaigns/` — create campaign with `campaign-messages` as attribute, `audiences: { included: [id] }`
3. `POST /campaign-message-assign-template` — link template to message (Klaviyo clones it)
4. `DELETE /templates/{id}` — cleanup original template

**Full API details:** `references/klaviyo-campaign-api.md`

## Building New Primitives

**ALWAYS read the v4 template first:**
```bash
cat references/templates/heroes/hero-b-clay.html   # Read source template
# Then create primitives/hero-b-clay/render.js wrapping the exact HTML in a JS function
```

Each primitive is a `render.js` exporting: `module.exports = function(opts) { ... return html; }`

The function accepts an opts object and does `{{TOKEN}}` → value string replacement. Include JSDoc listing all opts and their token mappings. Keep ALL inline styles, classes, mobile classes, and MSO conditionals EXACTLY as in the v4 source.
