# Builder JSON agent workflow

Use this when a user asks to build, edit, render, save, or deploy a Fig & Bloom marketing email.

## Core mental model

The hosted builder UI is mainly for humans. Agents should normally generate/import **campaign JSON** rather than click through the UI.

Canonical flow:

1. Read the user brief / Paperclip / Notion campaign plan.
2. Fetch or inspect the current builder schema, e.g. `https://my-email-builder.onrender.com/api/schema`.
3. Choose blocks based on campaign objective and audience awareness.
4. Produce builder-compatible campaign JSON.
5. Assemble/render via builder API or import JSON into the UI only for preview/debugging.
6. Save the campaign JSON/design to Notion/My Designs through the builder workflow.
7. Export HTML/PNG/slices as derived artefacts only.
8. Push/create Klaviyo draft only after approval.

HTML is never the source of truth.

## Required agent output

For a complete build, report:

- Notion/My Designs saved location or explicit blocker.
- Campaign JSON file/object location if saved locally.
- Render/preview status.
- Any derived HTML/PNG exports.
- Whether Klaviyo was only drafted or not touched.

If the builder/API cannot be reached, stop and report the blocker. Do not silently fall back to standalone hand-coded HTML unless the user explicitly asks for an emergency non-canonical artefact.

## Component strategy by objective

### Farewell / sell-through / final weekend

Goal: move known products without making them feel like clearance.

Use:

- `hero-d-clay`, restrained `editorial-hero`, or calm `caption-bar-hero`.
- `body-copy-plain` for readable editorial copy.
- `section-headline` before line-up.
- Equal-weight product/design cards for favourites taking a bow.
- Quiet secondary module for what is coming next.

Avoid:

- `promo-code`, discount badges, countdowns, loud urgency, clearance framing.
- Saying “20% off” when the offer is “20% more stems”.

### Range launch / tease

Goal: signal progress, anticipation, and design freshness.

Use:

- `editorial-hero`, `caption-bar-hero`, `story`, `feature-list`.
- Soft reveal imagery: packaging detail, wrapped/under-wraps, studio hint.

Avoid:

- Dense product grids before the reveal.
- Overclaiming products not yet ready to show.

### Offer / value proposition

Goal: make the value clear without damaging premium feel.

Use:

- `offer-panel`, `comparison-vs`, `feature-list`, `howto-steps`.
- Specific proof: more stems, better packaging, new sizes, service benefits.

Avoid:

- Emotional story modules if the brief is primarily rational/value-led.
- Discount language when the value is a fulfilment upgrade.

### Emotional occasion

Goal: help customers express a feeling or mark a moment.

Use:

- Softer `editorial-hero`, `story`, `body-copy-plain`, `polaroid-collage`.
- Opt-out module for sensitive holidays/occasions.

Avoid:

- Hard urgency, guilt, aggressive sales language.

## Backend improvements worth preserving

A useful builder backend exposes an agent contract:

- `/api/schema` for current component/token contract.
- `/api/assemble` for HTML preview from JSON.
- `/api/render` and `/api/render-slices` for visual QA/export.
- `/api/designs` or equivalent save endpoint returning Notion/design URL.
- `/api/examples?type=...` for approved campaign JSON patterns.

Schema should ideally include `bestFor`, `avoidFor`, `visualRole`, image requirements, casing rules, and palette presets per component.
