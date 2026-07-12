# Builder JSON agent contract

## Why this exists

A Fig & Bloom email build went wrong when the agent treated the email builder as either a local CLI engine or a human-only UI, then fell back to hand-written Klaviyo HTML. That is not the canonical workflow.

The current system is **JSON-first**:

```text
agent generates campaign JSON → builder assembles/renders/saves to Notion → derived HTML/PNG/Klaviyo draft
```

The Render UI is mainly for humans, but agents should use the same builder contract by generating/importing campaign JSON and using the backend/API workflow where possible.

## Source-of-truth hierarchy

1. User brief / Paperclip / Notion campaign plan.
2. Live builder schema, e.g. `/api/schema` from `https://my-email-builder.onrender.com`.
3. Existing campaign JSON in Notion / My Designs.
4. Brand voice and component strategy in this skill.
5. Rendered HTML, PNGs, and slices.

HTML is a derived artefact, never the primary source of truth.

## Agent workflow

1. Load this skill and read `references/brand-voice.md`.
2. Fetch/inspect the current builder schema or a current saved campaign JSON example.
3. Identify the campaign objective, awareness state, and tone.
4. Choose components to visually express the objective.
5. Emit builder-compatible campaign JSON.
6. Validate/assemble/render through the builder API or import JSON into the UI for preview/debugging.
7. Save the campaign JSON to Notion/My Designs through the builder workflow.
8. Export HTML/PNG/slices only as derived artefacts.
9. Push/create Klaviyo draft only after approval.

Do not hand-code standalone HTML unless the builder/API is unavailable and the user explicitly accepts an emergency non-canonical fallback.

## Component strategy by objective

### Farewell / final weekend / sell-through

Goal: move known products without cheapening the brand.

Use:
- restrained hero (`hero-d-clay`, `editorial-hero`, or calm `caption-bar-hero`)
- `body-copy-plain`
- `section-headline`
- equal-weight product/design cards or grid
- quiet secondary module for “what’s next”

Avoid:
- `offer-panel`
- `promo-code`
- discount badges
- countdowns
- loud urgency language
- anything that makes the range feel like clearance

### Range launch / tease

Goal: create anticipation and signal design progress.

Use:
- `editorial-hero`
- `caption-bar-hero`
- `story`
- `feature-list`
- `polaroid-collage` if visual material is strong

Avoid:
- dense product grids before reveal
- discount-led modules

### Offer / value proposition

Goal: make value clear while protecting premium feel.

Use:
- `offer-panel`
- `comparison-vs`
- `feature-list`
- `howto-steps`

Avoid:
- vague emotional story if the objective is rational/value-led
- percentage-off framing unless the campaign is explicitly a discount campaign

### Emotional occasion

Goal: help customers express a feeling or mark a moment.

Use:
- `story`
- softer `editorial-hero`
- `body-copy-plain`
- `polaroid-collage`
- opt-out module where sensitive

Avoid:
- hard urgency
- discount framing near sensitive occasions

## Completion checklist

Before reporting an email build complete:

- [ ] Campaign JSON created.
- [ ] JSON validates against current builder schema.
- [ ] Assemble/render succeeded.
- [ ] Preview checked visually.
- [ ] Product URLs/images verified.
- [ ] Campaign JSON saved to Notion/My Designs.
- [ ] Derived HTML/PNG exported only if requested.
- [ ] Klaviyo draft created only after approval.

If any item is missing, report it as incomplete rather than presenting the build as finished.

## Useful backend hardening ideas

If maintaining the builder backend, expose/discover:

- `/api/agent-contract` — canonical workflow, endpoints, required fields, and `htmlIsDerived: true`.
- `/api/examples?type=<campaign_type>` — approved campaign JSON examples.
- component schema metadata: `bestFor`, `avoidFor`, `visualRole`, `tone`, `imageRatio`.
- a clean `POST /api/designs` endpoint returning `notionPageId`, `notionUrl`, `designId`, and `previewUrl`.
