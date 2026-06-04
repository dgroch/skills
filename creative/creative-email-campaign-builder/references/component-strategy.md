# Component Strategy by Campaign Objective

The hardest part of building a Fig & Bloom email is **not** filling tokens — it is
choosing the components that make the campaign objective *visually obvious* before a
reader has parsed a single word. This file maps campaign objectives to component
choices, sequences, and the things to avoid.

Use it after you have the brief and **before** you write JSON. Always reconcile the
component names here against the live `GET /api/schema` (`components[].name`) — names
are **group-prefixed** (`heroes/…`, `sections/…`, `products/…`, `blocks/…`); only
`header` and `footer` are top-level.

> Brand guardrail (from `brand-voice.md` and the parent Editorial Framework):
> Fig & Bloom does not discount-lead, does not manufacture urgency, and lets craft +
> specificity carry the message. Component choice must honour that — a premium brand
> rarely looks like a clearance email.

---

## How to choose (the 30-second version)

1. **Name the objective** (taxonomy below). One primary objective per send.
2. **Name the awareness state** — does the reader already know this product/offer, or
   is this the first touch? Cold → lead with emotion/editorial; warm → lead with the
   specific thing.
3. **Pick the OPEN beat** (hero), **AFFIRM beat** (proof/story), **CLOSE beat** (CTA/upsell).
   See the beat/rotation scheme in `SKILL.md` and `manifest.json → variation_rules`.
4. **Check the avoid-list** for the objective. If a chosen component is on it, swap.
5. **Verify above-the-fold CTA** — the primary CTA must render within ~700px (a bare
   `heroes/hero-image-only` does not satisfy this; follow it with a CTA-bearing block).

---

## Campaign objective taxonomy

| Objective | Intent | Urgency | Leads with |
|---|---|---|---|
| `farewell_sellthrough` | Move known products without cheapening the brand | Low–medium (calm) | Emotion + finality |
| `range_launch` | Build anticipation; signal design progress | Low | Editorial tease |
| `product_spotlight` | Make one hero product irresistible | Low | A single product, beautifully |
| `occasion_gifting` | Help the reader express a feeling / mark a moment | Low (gentle) | The recipient's feeling |
| `discount_offer` | Communicate genuine value, premium intact | Medium | The value, stated plainly |
| `value_prop` | Rational reasons to choose Fig & Bloom | Low | Proof / comparison |
| `education_howto` | Teach (care, arranging, choosing) — give before asking | None | Useful method |
| `social_proof` | Borrow others' confidence | Low | Real customers' words |
| `lifecycle` | Welcome / win-back / retention | Low | Relationship, not product |

---

## Objective playbooks

### `farewell_sellthrough` — final weekend / sell-through
**Goal:** move known products without making the range feel like clearance.

**Use**
- OPEN: `heroes/hero-d-clay` (type-forward, dignified) · `blocks/editorial-hero` · restrained `blocks/caption-bar-hero`
- BODY: `sections/body-copy-plain`
- `sections/section-headline` to introduce the line-up
- Equal-weight product cards: `products/card-horizontal` + `products/card-horizontal-reversed` (alternating)
- Quiet "what's next" close: `sections/upsell-noir`

**Avoid:** `blocks/offer-panel`, `sections/promo-code`, discount badges, countdowns, loud urgency language — anything that reads as clearance.

*(Worked example: `RH | 2026-06 Farewell Weekend` — `header → heroes/hero-d-clay → sections/body-copy-plain → sections/section-headline → 7× products/card-horizontal{,-reversed} → sections/upsell-noir → sections/trust-bar → footer`.)*

### `range_launch` — launch / tease
**Goal:** create anticipation and signal design progress.

**Use:** `blocks/editorial-hero` · `blocks/caption-bar-hero` · `blocks/story` · `blocks/feature-list` · `blocks/polaroid-collage` (if strong visual material).
**Avoid:** heavy product grids before the reveal; discount-led modules.

### `product_spotlight`
**Goal:** make one hero product irresistible without a full grid.

**Use:** `blocks/designed-product-card` (badge + serif name/price) **or** `products/card-lifestyle-studio` (lifestyle+studio stack, one per email) · `blocks/feature-list` for reasons-to-believe · `sections/testimonial` to close.
**Avoid:** more than one spotlight treatment; dense competing grids.

### `occasion_gifting` — emotional occasion
**Goal:** help the reader express a feeling or mark a moment.

**Use:** `blocks/story` · a softer `blocks/editorial-hero` · `sections/body-copy-plain` · `blocks/polaroid-collage` · `sections/opt-out` early (after hero) for sensitive occasions (Mother's/Father's Day, Valentine's, pregnancy/baby, memorial — see brand-voice sensitivity rules).
**Avoid:** hard urgency; discount framing near sensitive occasions.

### `discount_offer`
**Goal:** make the value clear without damaging the premium feel.

**Use:** `blocks/offer-panel` (the designed offer hero) · `blocks/comparison-vs` · `blocks/feature-list` · `blocks/howto-steps`. For a giveaway, `blocks/offer-panel` in GIVEAWAY MODE (`PROMO_CODE=""`).
**Avoid:** heavily emotional story modules when the objective is rational/value-led; stacking `offer-panel` *and* `sections/promo-code` (pick one).

### `value_prop`
**Goal:** rational reasons to choose Fig & Bloom.

**Use:** `blocks/feature-list` · `blocks/comparison-vs` · `sections/trust-bar` · `sections/three-column-steps-*`.
**Avoid:** emotion-led openers that bury the argument.

### `education_howto`
**Goal:** teach (care / arranging / choosing) — value before the ask.

**Use:** `blocks/howto-steps` (vertical 3-step, photo per step) · `sections/body-copy-plain` · soft single CTA. Compact partner-flow instead → `sections/three-column-steps-*`.
**Avoid:** promo modules up front; making it feel like an ad.

### `social_proof`
**Goal:** borrow customers' confidence.

**Use:** `blocks/polaroid-collage` (scrapbook quotes) · `sections/testimonial` · `products/card-single-testimonial`.
**Avoid:** unbacked superlatives; fake-looking reviews.

### `lifecycle` — welcome / win-back / retention
**Goal:** relationship first, product second.

**Use:** `blocks/story` · `blocks/editorial-hero` · `sections/body-copy-plain` · one gentle product nudge.
**Avoid:** aggressive offers in a welcome; guilt in a win-back.

---

## Worked JSON — `farewell_sellthrough` (abridged, names verified against live schema)

```json
{
  "campaignName": "RH | 2026-06 Farewell Weekend",
  "bodyBg": "#2c2825",
  "blocks": [
    { "component": "header", "tokens": {} },
    { "component": "heroes/hero-d-clay", "tokens": {
        "SUPER_LABEL": "Friday 5 & Saturday 6 June",
        "HEADLINE": "a fond farewell",
        "SUBHEADLINE": "Seven designs take their final bow this weekend.",
        "CTA_TEXT": "Shop the farewell designs",
        "CTA_URL": "https://figandbloom.com/collections/bouquets" } },
    { "component": "sections/body-copy-plain", "tokens": {
        "SUPER_LABEL": "Seven favourites",
        "HEADLINE": "Seven you've loved, one last weekend.",
        "BODY_P1": "…", "BODY_P2": "…" } },
    { "component": "sections/section-headline", "tokens": {
        "SUPER_LABEL": "The line-up", "HEADLINE": "Seven favourites, taking a bow." } },
    { "component": "products/card-horizontal", "tokens": { "PRODUCT_NAME": "Lucerne", "…": "…" } },
    { "component": "products/card-horizontal-reversed", "tokens": { "PRODUCT_NAME": "Lisbon", "…": "…" } },
    { "component": "sections/upsell-noir", "tokens": {
        "SUPER_LABEL": "Next week", "HEADLINE": "a glow up, next week",
        "BODY": "…", "CTA_TEXT": "See what's coming", "CTA_URL": "https://figandbloom.com" } },
    { "component": "sections/trust-bar", "tokens": {} },
    { "component": "footer", "tokens": {} }
  ]
}
```

Casing reminder: `heroes/*` and `sections/upsell-noir` HEADLINEs are **Cervanttis →
lowercase**; `sections/section-headline` and `products/*` names are **Lust → Sentence
case**. Confirm per-token rules in `GET /api/schema` `tokenRules`.
