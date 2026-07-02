---
name: fig-bloom-charcoal-photography
description: Run charcoal-look AI product photoshoots for Fig & Bloom catalogue products (figandbloom.com) — PDP sets, campaign sets, and single-format shots generated from real Shopify product photos via Higgsfield nano_banana_2. Triggers include "charcoal photoshoot for [product]", "charcoal shoot", "PDP set for [product]", "full 8-format set", "shoot [product] on charcoal", or any request for Fig & Bloom product/catalogue photography in the dark premium look. Do NOT use for Whoosh, Bower, Oddly, or non-product brand imagery — use brand-photographer for those.
---

# Fig & Bloom — Charcoal Product Photoshoot

Generate brand-approved product photography for any active Fig & Bloom catalogue product: real product locked as the reference, charcoal ground, one warm light, one idea per frame.

The complete art direction, anchor library, prompt phrasing and failure modes live in `references/charcoal-framework.md`. **Read it before generating anything.**

## Invocation

Pattern: `[product] + [formats, optional] + [constraints, optional]`

| Prompt | Result |
|--------|--------|
| "Charcoal photoshoot for Broome" | PDP trio (default): hero, macro, hand-held |
| "Charcoal photoshoot for Broome — full 8-format set" | All 8 formats |
| "Charcoal shoot for Genoa. Formats: hero, marble, hand-off. Use the smoke vase." | Named formats + constraint |

Defaults:
- **Scope:** PDP trio (hero, macro, hand-held) unless "full set" / "full 8-format set" or explicit formats are given
- **Model:** `nano_banana_2`, aspect 4:5, count 1 per shot, resolution 1k
- **Upscale:** approved frames only → bytedance 4K (source 928×1152)

Everything in the framework (likeness lock, warm grade, 80% held framing, no faces, single prop rule) is a default — the operator should never need to restate it. If they do, treat it as a skill bug and fix the skill.

## Workflow

1. **Resolve product** — Shopify `search_products` (or `get-product` if GID known). Confirm ACTIVE status. Pull the featured image URL; for vase products, pull the correct variant image (smoke preferred on charcoal).
2. **Import reference** — Higgsfield `media_import_url` with the Shopify CDN URL → `media_id`. Never generate without a real product reference.
3. **Build prompts** — one per format, using the four-block structure in the framework: LIKENESS LOCK → FORMAT BLOCK → LIGHT BLOCK → REGISTER LINE. Copy phrasing verbatim from the framework tables.
4. **Generate** — `generate_image`, one job per format, product `media_id` as image reference.
5. **Art-direct** — download and view every frame. Judge against framework Section 3 and the failure-mode table. Reshoot misses before moving to the next product; never ship a frame you haven't looked at.
6. **Upscale** — approved frames → `upscale_image` (bytedance, 4k, pass source width/height).
7. **Edits** — reframes / object removal via `generate_image` with the completed `job_id` as reference, prompt opening "The exact same image, but…".
8. **Archive** — push winners to R2 CDN (brand-cdn skill) when asked.

## Hard rules (summary — framework is authoritative)

- Real product photo as reference, always. Wrap/ribbon locked with the likeness-lock phrase in every prompt.
- Warm light on charcoal, every SKU. No cool/silver grades.
- Grounded, never floating. No faces. No patterned shadows. Max one prop.
- Held shots: bouquet ~80% of frame.
- Accessories from the product range only; smoke vase over pink on charcoal.

## Escalation

- Product not found / no ACTIVE variant → stop, report, don't substitute.
- Likeness drift persisting after 2 reshoots of a frame → flag to operator with both attempts rather than burning credits.
- Anything requiring a new format outside the 8 → propose it, get approval, then add it to the framework.
