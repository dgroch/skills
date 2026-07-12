# Agent JSON Builder Workflow — Fig & Bloom Email Builder

## Why this exists

A session exposed a failure mode: the agent loaded the email builder skill, saw local v5-engine notes, could not find a complete runnable local engine, and fell back to hand-written Klaviyo HTML. That is the wrong default.

The hosted UI at `https://my-email-builder.onrender.com` is mostly for humans. Agents should not manually click blocks together unless debugging. The agent-facing workflow is JSON-first:

```text
brief / campaign objective → component strategy → campaign JSON → builder assemble/render/save → Notion source record → derived HTML/PNG/slices → Klaviyo draft after approval
```

HTML is a derived artefact, not the canonical deliverable.

## Agent contract

Before building, discover the current execution contract from the live builder rather than assuming local skill files are complete.

Known endpoints/surfaces:

- `GET /api/schema` — current component schema, token names, casing rules, palettes, component inventory.
- `POST /api/assemble` — assemble campaign JSON into live-preview HTML.
- `POST /api/render` — render full PNG.
- `POST /api/render-slices` — render block slices.
- `POST /api/klaviyo-draft` — create/push a Klaviyo draft.
- UI: Import JSON, Export JSON, Export HTML, Render PNG, Save/My designs, Push to Klaviyo.

If the backend later exposes `/api/agent-contract` or `/api/examples`, prefer those for workflow details and proven campaign JSON examples.

## Source-of-truth hierarchy

1. User brief / Paperclip / Notion campaign plan.
2. Current live builder schema and existing saved campaign JSON.
3. Brand voice and component strategy from this skill.
4. Builder-saved JSON in Notion/My Designs.
5. Exported HTML/PNG/slices.

Do not treat local HTML, a screenshot, or manually authored markup as source of truth.

## Default agent sequence

1. Parse the brief into:
   - campaign objective
   - audience / awareness state
   - primary CTA
   - urgency level
   - product hierarchy
   - proof/value modules needed
2. Fetch/inspect the builder schema or a known-good saved campaign JSON example.
3. Choose the component sequence deliberately.
4. Produce campaign JSON with correct tokens, links, images, palette choices, and casing.
5. Validate/assemble/render via builder API or import JSON into the UI for review.
6. Save the JSON to Notion/My Designs via the builder workflow.
7. Export HTML/PNG/slices only after the canonical JSON is saved.
8. Push/create Klaviyo draft only after approval.

If the builder/API is unavailable, stop and report the blocker. Only create standalone HTML if Daniel explicitly accepts an emergency non-canonical fallback.

## Campaign objective → component strategy

### Farewell / final weekend / sell-through

Goal: move known products without cheapening the brand.

Use:
- restrained `hero-d-clay`, `editorial-hero`, or calm `caption-bar-hero`
- `body-copy-plain`
- `section-headline`
- equal-weight product/design cards for the line-up
- quiet secondary module for “what’s next”

Avoid:
- `offer-panel`
- `promo-code`
- discount badges
- countdown timers
- loud urgency language
- anything that makes the products feel like clearance

### Range launch / tease

Goal: create anticipation and signal design progress.

Use:
- `editorial-hero`
- `caption-bar-hero`
- `story`
- `feature-list`
- `polaroid-collage` when there is strong visual material

Avoid:
- dense catalogue grids before the reveal
- discount-led modules

### Value proposition / offer

Goal: make value clear without damaging premium feel.

Use:
- `offer-panel`
- `comparison-vs`
- `feature-list`
- `howto-steps`

Avoid:
- emotional modules that obscure the offer mechanics
- discount language when the value is fulfilment-based (e.g. “20% more stems” is more product, not money off)

### Emotional occasion / gifting

Goal: help customers express a feeling or mark a moment.

Use:
- `story`
- softer `editorial-hero`
- `body-copy-plain`
- `polaroid-collage`
- opt-out block for sensitive holidays/occasions

Avoid:
- hard urgency
- guilt
- discount framing near sensitive occasions

### Product spotlight

Goal: make one hero product desirable and easy to buy.

Use:
- `editorial-hero` or `caption-bar-hero` with strong product image
- `designed-product-card` or `card-lifestyle-studio`
- testimonial/proof if available
- concise value/proof module

Avoid:
- equal-weight product grids that dilute the hero product

## Minimal campaign JSON shape

Use the live schema for exact token names, but the canonical structure is generally:

```json
{
  "campaignName": "RH | 2026-06 Farewell Weekend + Glow Up Tease",
  "bodyBg": "#2c2825",
  "blocks": [
    {
      "id": "header-1",
      "component": "header",
      "tokens": {}
    },
    {
      "id": "hero-1",
      "component": "hero-d-clay",
      "tokens": {
        "SUPER_LABEL": "FRIDAY 5 – SATURDAY 6 JUNE",
        "HEADLINE": "a fond farewell",
        "SUBHEADLINE": "Seven favourites are available for one last weekend.",
        "CTA_TEXT": "SHOP THE RANGE",
        "CTA_URL": "https://www.figandbloom.com.au/..."
      }
    }
  ]
}
```

## Completion checklist

Before reporting an email build as complete:

- [ ] Campaign JSON created.
- [ ] JSON validates against current builder schema.
- [ ] Assemble/render succeeded.
- [ ] Preview checked visually.
- [ ] Product URLs/images verified.
- [ ] Campaign JSON saved to Notion/My Designs.
- [ ] Derived HTML/PNG/slices exported only if requested.
- [ ] Klaviyo draft created only after approval.

If any item is missing, say exactly what is incomplete.
