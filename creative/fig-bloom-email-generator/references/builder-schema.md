# Fig & Bloom — Email Builder Schema (live reference)

> The campaign builder is JSON-first. The schema is the **execution contract** — every campaign JSON validates against it before saving. **Always reconcile against the live `GET /api/schema`**; this file is the at-a-glance summary.

## The schema lives at

```
GET https://my-email-builder.onrender.com/api/schema
```

The host calls this at build time and injects the result into the LLM call (so the model has the *current* component list, not a stale one). The components below are the locked 2026-06 set.

## Components — group-prefixed

The schema carries per-component `bestFor`, `avoidFor`, `visualRole`, `tone`. Use those to pick the right component for the objective + persona. Group prefixes are mandatory:

### Heroes (`heroes/*`)
- `heroes/hero-a` — Standard, maximum photo impact.
- `heroes/hero-b-white` / `hero-b-clay` / `hero-b-noir` — Photo unobscured, editorial.
- `heroes/hero-c1` / `hero-c2` × `white`/`clay`/`noir` — Portrait photography, most editorial.
- `heroes/hero-d-clay` / `hero-d-white` / `hero-d-noir` — Type-forward, dignified (premium + launch beats).
- `heroes/hero-image-only` — Photo-only. **Does not satisfy above-the-fold CTA requirement**; must be followed by a CTA-bearing block.

### Sections (`sections/*`)
- `sections/body-copy-plain` — Centre-aligned body copy, 1–2 paragraphs max.
- `sections/section-headline` — Headline to introduce a line-up or transition. Lust (Sentence case).
- `sections/upsell-noir` — Quiet "what's next" close. Cervanttis (lowercase).
- `sections/trust-bar` — Always present, just before footer.
- `sections/opt-out` — Required for sensitive occasions (after hero).
- `sections/promo-code` — Discount code reveal. **Avoid for `farewell_sellthrough`, sympathy, sensitive.**
- `sections/testimonial` — Single-testimonial beat.
- `sections/three-column-steps-*` — Compact 3-step horizontal flow (care / how-to).
- `sections/delivery-cutoffs` — Hard-deadline delivery module. Use sparingly; avoid panic language.

### Products (`products/*`)
- `products/card-horizontal` / `card-horizontal-reversed` — Equal-weight product card, alternating.
- `products/card-lifestyle-studio` — One per email max. Lifestyle + studio stack, spotlight.
- `products/card-single-testimonial` — One product with a strong review.

### Designed blocks (`blocks/*`) — always rasterised to PNG
- `blocks/caption-bar-hero` — Photo-led opener. Most common opener. CTA in the caption bar.
- `blocks/editorial-hero` — Lust headline + Cervanttis accent + square button on a plate that overlaps the photo. **One per email.**
- `blocks/feature-list` — 2–4 reasons-to-believe beside a polaroid. **One per email.**
- `blocks/polaroid-collage` — 3 tilted polaroids + Lust pull-quote. Social proof / "in their words".
- `blocks/story` — Founder / behind-the-scenes. Mid-email.
- `blocks/designed-product-card` — One product, badge + Lust name/price. **One per email.**
- `blocks/offer-panel` — Promo / giveaway. `PROMO_CODE=""` for giveaway mode. **Avoid for farewell, sympathy.**
- `blocks/howto-steps` — Vertical 3-step care / how-to. Exactly three steps. **One per email.**
- `blocks/comparison-vs` — Us-vs-them / before-after. **One per email.**
- `blocks/editorial-collage` *(DRAFT — pending design review)* — Layered editorial opener.
- `blocks/annotated-product` *(DRAFT — pending design review)* — One product, 2–3 Cervanttis callouts.

### Dividers (`dividers/*`)
- `dividers/divider-line` — Hairline rule.
- `dividers/divider-illo-clay` — Decorative clay illustration divider. **Max 1 non-line divider per email.**

### Top-level (no prefix)
- `header` — Always first.
- `footer` — Always last.

## Token rules by font

| Font | Components | Casing | Example |
|---|---|---|---|
| **Cervanttis** (script) | `heroes/*`, `sections/upsell-noir`, `sections/opt-out`, `ACCENT_SCRIPT`, `*_CAPTION`, `QUOTE_ACCENT`, `CAPTION`, `SIGNATURE`, `BADGE_TEXT` | **lowercase** | `"a fond farewell"` |
| **Lust** (display serif) | `sections/body-copy-plain` `HEADLINE`, `sections/section-headline` `HEADLINE`, `products/*` `PRODUCT_NAME`, `PULL_QUOTE`, `PRODUCT_PRICE` | **Sentence case** | `"Some gestures speak before words do."` |
| **Neuzeit Grotesk** (body sans) | `BODY_P1`, `BODY_P2`, body UI, supers, captions | Sentence case | `"Each one is still hand-tied..."` |

## Palette presets

The schema carries `palette` presets per designed block. Locked Fig & Bloom palette:

| Token | Hex | Use |
|---|---|---|
| White | `#FFFFFF` | Background, plate |
| Ink | `#1A1612` | Primary text |
| Tan-1 | `#F0E5D0` | Background variant, plate |
| Tan-2 | `#B89A75` | Accent |
| Noir | `#2c2825` | Premium dark beats (default `bodyBg`) |
| Soft sage | `#7D8979` | Accent / sage variants |
| Soft rose | `#D8B9AD` | Accent / rose variants |
| Mushroom | `#B9AA9E` | Accent / mushroom variants |

## Validating a campaign

```bash
curl -X POST https://my-email-builder.onrender.com/api/validate \
  -H "Content-Type: application/json" \
  -d '{"campaign": <your_campaign_object>}'
```

Returns `{ ok: true }` or `{ ok: false, issues: [{rule, message, suggestion?, ...}] }`. Fix every issue before saving. Common issues:

- **Bare component name** — `hero-d-clay` → `heroes/hero-d-clay` (suggestion given).
- **Casing violation** — `HEADLINE: "A Fond Farewell"` in a Cervanttis template.
- **Unknown component** — name not in the schema. Add it to the schema, or pick a different one.
- **Above-the-fold CTA** — `heroes/hero-image-only` without a following CTA-bearing block.

## Saving a campaign

```bash
curl -X POST https://my-email-builder.onrender.com/api/designs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "RH | 2026-06 Farewell Weekend",
    "campaign": { ... },
    "subjectLine": "Seven designs, one last weekend",
    "previewText": "Lucerne, Lisbon, Savoie and four more take their final bow."
  }'
```

Returns the created record (capture `id`).

## Pushing to Klaviyo (only after human approval)

```bash
curl -X POST https://my-email-builder.onrender.com/api/klaviyo-draft \
  -H "Content-Type: application/json" \
  -d '{
    "designId": "<id>",
    "listId": "<KLAVIYO_LIST_ID>",
    "fromEmail": "hello@figandbloom.com.au",
    "fromLabel": "Fig & Bloom",
    "replyToEmail": "hello@figandbloom.com.au"
  }'
```

Returns `{ campaignId, messageId, sliceCount }`. **This is a draft only — never auto-send.**
