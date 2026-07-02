# Fig & Bloom — Charcoal Photography Framework
**Anchor library · Art direction · Prompt system**
Distilled from approved session output, July 2026. Governs AI product photography across the Flowers collection.

---

## 1. The look, in one line

Real product, charcoal ground, one warm light, one idea per frame.

This is the premium counter to the Daily Blooms / LVLY pink-studio register: same shopping cues (held, texture, gifting moment, treat), shot darker, quieter, and with restraint.

---

## 2. Anchor library (approved frames)

All frames generated with `nano_banana_2`, 4:5, from real Shopify product photos. Use these as style references for future generations and as the visual QA benchmark.

### Format anchors — the proven shot list

| # | Format | Anchor frame | Product | Notes |
|---|--------|-------------|---------|-------|
| 1 | **Charcoal macro** | `51149a20` / upscale `eff377a9` | Marseille | Blooms dense in frame, chiaroscuro, no wrap or hands |
| 2 | **Hand-held** | `1ce62816` (Marseille), `a5d5fab4` (Osaka) | — | One hand from below, charcoal seamless, wrap locked to product |
| 3 | **White on black hero** | `ca0e989e` / round-1 `7d36d2fa`, upscale `ec4d1ccf` | Pyrenees | Standing wrapped on dark stone, max tonal contrast |
| 4 | **Shaft of light** | `d7401cdf` | Osaka | Charcoal linen, single window beam, dust motes — the "after delivery" shot |
| 5 | **The hand-off** | `6ee84ade` | Marseille | Two hands at dusk doorway, warm lamp behind, no faces |
| 6 | **Moody flat lay** | `8de28b32` (Lucerne), `483cfd5b` (Pyrenees) | — | Overhead on slate, one plate + one treat, warm side light |
| 7 | **The carry** | `84428b0a` (corridor), `3da44bed` (Osaka dusk street) | — | From behind, blooms over shoulder in focus, lit doorway ahead |
| 8 | **Black marble reflection** | `9116d9ab` (Osaka), `0b4a58b5` (Pyrenees) | — | Polished marble, mirror reflection, single candle |

### Product-specific anchors

| Frame | Product | Format |
|-------|---------|--------|
| `dae4d877` | Osaka | Hero — dark timber bench, plain soft dusk gradient (no shadow patterns) |
| `3b2b13bb` | Osaka | Macro — blossom petals, warm rim light |
| `04143b73` | Osaka | In situ — **smoke ribbed vase** (actual product), teacup, single beam |

### Environment plates (compositing anchors)

Commissioned empty for reuse behind any product or type:

- **Slate flat-lay plate** — `38539a62` (derived from `c16bc061`): bare charcoal slate, overhead, cool-silver side light
- **Marble scene plate** — `2eda8fc4` (derived from `0b4a58b5`): empty black marble, reflections, candle, panelled wall

CloudFront URL pattern: `https://d8j0ntlcm91z4.cloudfront.net/user_37eOCLtZIPCkaohdAZeO6O287If/hf_<timestamp>_<job-id>.png`

---

## 3. Art direction rules

### Non-negotiables

1. **Real product only.** Every generation references the actual Shopify product photo (imported via `media_import_url`). Never generate a bouquet from imagination.
2. **Wrap is sacred.** The wrap, tissue and ribbon must match the product photo exactly. The model will invent kraft paper if given the chance — the likeness-lock phrase (below) is mandatory in every prompt.
3. **Grounded, never floating.** Levitating bouquets read cheap. Product stands, lies, or is held.
4. **No faces.** Hands, arms, backs of figures — yes. Faces — never.
5. **One idea per frame.** If the shot needs a second sentence to explain, it's two shots.
6. **Actual accessories.** Vases and props from the product range only. On charcoal, choose the smoke vase over pink — tonal reads more expensive.

### Light

- **Warm on charcoal is the house grade.** The cool/silver experiment was tested and rejected — even for white product. Warm key, deep neutral shadow, every SKU.
- One light source per frame. Side or upper-left key, or a single motivated beam (window, doorway, lamp, candle).
- **No patterned shadows.** Grid and slat shadows (shoji, blinds) read as bars. Soft gradients only.
- Charcoal, not black: the ground should hold texture — plaster, linen, slate, stone, marble.

### Composition

- 4:5 portrait, generous negative space — except held shots, where the bouquet fills **~80% of frame**.
- Props: maximum one, placed well apart from product, with breathing room.
- Restraint beats story. Elaborate "brand worlds" (themed sets, riviera tables, balconies) were tested and rejected. The environment serves the product; it is never the subject.

### The register test

Before approving a frame, ask: *would this run in a fashion magazine's back pages, or a supermarket catalogue?* Warm, quiet, considered = pass. Bright, busy, cheerful = reshoot.

---

## 4. Prompt framework

### Structure

Every prompt = **LIKENESS LOCK + FORMAT BLOCK + LIGHT BLOCK + REGISTER LINE**

**Likeness lock** (always first, verbatim):
> "The exact bouquet from the reference image, keeping its exact original wrapping and presentation exactly as shown — do not change the wrap,"

For macro shots, swap to:
> "Extreme macro close-up of the exact [colour] blooms from the reference bouquet," + "...no wrap or hands visible."

**Format block** — one of the 8 proven formats:

| Format | Core phrase |
|--------|------------|
| Macro | "densely filling the frame against a deep charcoal background, shallow depth of field" |
| Hand-held | "held aloft by a single elegant hand entering frame from below, against a seamless deep charcoal studio backdrop, bouquet filling ~80% of the frame" |
| Hero | "standing wrapped on a dark stone surface against a matte charcoal backdrop, maximum tonal contrast" |
| Shaft of light | "on a charcoal linen tablecloth in a dark moody interior, a single shaft of warm light falling across the flowers from a window off-frame, dust motes visible" |
| Hand-off | "being passed between two hands — one giving, one receiving — at a dark doorway, warm interior lamplight behind, cool dusk in front" |
| Flat lay | "lying flat on a dark charcoal slate surface beside a small ceramic plate holding a single elegant treat, photographed from directly above" |
| The carry | "carried by a person seen from behind through a dark corridor toward a lit doorway, blooms over the shoulder facing camera in sharp focus, figure soft" |
| Marble | "standing on polished black marble with a soft mirror reflection beneath, dark charcoal interior behind, one small lit candle glowing warm" |

**Light block:**
> "Single [hard side / soft upper-left / motivated] warm light, dramatic shadow falloff, deep charcoal tones dominating."

**Register line** (always last):
> "Premium editorial florist campaign photography, cinematic contrast, restrained and considered composition, no faces visible."

### Worked example — new product, hand-held format

> "The exact bouquet from the reference image, keeping its exact original wrapping and presentation exactly as shown — do not change the wrap — held aloft by a single elegant hand entering frame from below, against a seamless deep charcoal studio backdrop, bouquet filling approximately 80% of the frame. Hard directional side light sculpting the blooms, dramatic shadow falloff. Premium editorial florist campaign photography, cinematic contrast, warm skin tone, restrained composition, no face visible."

### Negative cues to write in when relevant

- "no kraft paper" (if the wrap drifts)
- "no hard shadow patterns" (any wall-adjacent shot)
- "no warm amber tones" — **deprecated**; warm is the approved grade
- "grounded, not floating"

---

## 5. Production pipeline

1. **Source** — pull the product's featured image URL from Shopify (`search_products` / `get-product`)
2. **Import** — `media_import_url` → `media_id`
3. **Generate** — `nano_banana_2`, aspect 4:5, count 1, product `media_id` as image reference, prompt per framework
4. **Review** — art-direct against Section 3; reshoot misses before moving on
5. **Upscale** — approved frames → `upscale_image`, bytedance, 4K (source 928×1152 at 1k)
6. **Edit passes** — reframes and object removal via `nano_banana_2` with the completed `job_id` as reference ("the exact same image, but…")
7. **Archive** — winners to R2 CDN for use in ads, email, social, PDP

### Per-product minimum set

Hero + macro + hand-held (the PDP trio). Add hand-off / carry / flat lay / marble for campaign and social inventory.

---

## 6. Failure modes (tested, rejected — don't repeat)

| Failure | Lesson |
|---------|--------|
| Kraft paper wrap invented | Likeness lock phrase mandatory, every prompt |
| Shoji/grid shadow on wall | Reads as prison bars — soft gradients only |
| Themed "brand worlds" (riviera, balcony, apéritif) | Over-plotted. Environment never competes with product |
| Cool/silver grade on Pyrenees | House grade is warm on charcoal, all SKUs |
| Cluttered flat lay (plate + napkin + two treats) | One prop, spaced generously |
| Pink vase on charcoal | Drags toward competitor palette — smoke over pink |
