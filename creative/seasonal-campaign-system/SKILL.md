---
name: seasonal-campaign-system
description: Produce a unified visual system for a campaign moment — colour overlays, typography treatments, graphic motifs, photography direction — that spans ads, email, and organic/web placements.
---

# Seasonal Campaign System

## Overview

Define the complete visual system for a campaign moment — the palette,
typography, motifs, photography direction, and layout principles that make
a campaign feel unified across every channel. This skill produces a
**Campaign Style Guide** that downstream execution skills (ad-creative-builder,
email-template-builder, etc.) consume to produce final assets.

The system must feel emotionally specific to the moment, unmistakably
on-brand, and robust enough to travel across Meta ads, email banners,
organic social, and web placements without breaking.

Trigger this skill when any upstream agent delivers a campaign brief, or when the task involves: "campaign look and feel", "seasonal visuals", "campaign style guide", "visual system for [moment]", "Mother's Day / Valentine's / EOFY / launch creative direction", "collab visual identity", "campaign design system", or any request to define the visual language for a multi-channel campaign. Also trigger when asked to "create a mood" or "set the creative direction" for a marketing moment. Do NOT trigger for individual asset production (use ad-creative-builder), email template builds, or copy-only tasks.

## Prerequisites

- **Campaign brief** (structured input from strategist or manager agent).
  Required fields:
  - `campaign_name`: string
  - `moment_type`: enum [seasonal, product_launch, collab, brand_moment]
  - `emotion`: 1–3 words describing the feeling (e.g., "warm gratitude",
    "wild elegance", "grounded calm")
  - `hero_product`: string or null (the lead SKU or collection)
  - `channels`: list of [meta_ads, email, organic_social, web, stories]
  - `date_range`: start and end dates
  - `audience_segment`: enum [moment_makers, self_care_enthusiasts,
    space_transformers] or "all"
  - Optional: `collab_partner` (object with partner name, partner brand
    guidelines URL/file, co-branding rules)
  - Optional: `budget_tier` (enum [high, standard, lean]) — affects
    moodboard sourcing and mockup depth
  - Optional: `exclusions` (things to avoid — e.g., "no pink", "no cliché
    heart motifs")

- **Master brand guide** accessible at the canonical brand guide path.
  Must contain: primary palette, typography hierarchy, logo usage rules,
  photography style principles, and banned-word list.

- **Asset library access** for sourcing existing brand photography and
  motif references.

## Process

### Phase 1: Brief Intake & Validation

**Entry conditions:** Campaign brief received from upstream agent.

1. Parse the campaign brief and validate all required fields are present.
2. IF any required field is missing or ambiguous:
   - IF `emotion` is missing → STOP. Escalate to brief owner. Do not
     invent the emotional anchor — this is a strategic decision.
   - IF `hero_product` is null → proceed; system will be collection-level,
     not product-specific.
   - IF `channels` is missing → default to [meta_ads, email, organic_social].
   - IF `audience_segment` is missing → default to "all".
3. IF `moment_type` is `collab`:
   - Confirm `collab_partner` object is present with partner guidelines.
   - IF partner guidelines are missing → escalate. Co-branded work without
     partner guardrails will fail review.
4. Load the master brand guide into context.
5. Log the brief summary for audit trail.

**Quality gate:** All required fields validated. Brand guide loaded. Do not
proceed until confirmed.

**What a junior gets wrong:** Proceeding without a clear emotional anchor,
then defaulting to cliché (pink for Mother's Day, red for Valentine's).
The emotion field is the most important input in the entire brief.

---

### Phase 2: Mood Discovery

**Entry conditions:** Validated brief. Emotional anchor defined.

The goal is to translate the emotional anchor into a concrete visual
direction via a moodboard of 5–8 reference images.

1. **Interpret the emotion.** Expand the 1–3 word emotion into a richer
   sensory description. Ask: what textures, lighting, movement, and
   colour temperature does this emotion evoke?
   - Example: "warm gratitude" → soft natural light, linen textures,
     muted terracotta and sage, unhurried composition, gentle depth of field.
   - Example: "wild elegance" → dramatic light, untamed foliage,
     rich jewel tones against dark grounds, organic asymmetry.

2. **Source references from three pools:**
   - **Brand library:** Pull 2–3 existing brand images that align with
     the mood. These anchor the system to the brand's established visual
     world.
   - **Web/external inspiration:** Search for 2–3 references from
     adjacent premium brands, editorial photography, or design archives.
     Search for the sensory description, not the occasion name.
     DO: search "soft natural light linen floral editorial"
     DON'T: search "Mother's Day campaign 2026"
   - **AI-generated mood concepts:** Generate 1–2 images to fill gaps
     where no existing reference captures the intended mood. Use these
     as directional only — they are for mood extraction, not final use.

3. **Assemble moodboard.** Arrange the 5–8 references and annotate
   each with what it contributes to the system (colour cue, texture
   reference, composition style, lighting mood, motif inspiration).

4. **Extract the preliminary palette.** From the moodboard, identify:
   - 1 primary seasonal accent colour (hex)
   - 1 secondary seasonal accent colour (hex)
   - 1 neutral/ground tone that bridges the accents to the base brand palette
   - Note which base brand colours carry through unchanged.

**Quality gate:** Moodboard contains 5–8 images spanning all three source
pools. Preliminary palette identified. The moodboard should feel
emotionally cohesive — if any image jars, remove it.

**What a junior gets wrong:**
- Searching for the occasion name instead of the sensory qualities.
  This produces generic, expected results.
- Using only AI-generated images. The moodboard needs real-world
  photographic anchors to stay grounded.
- Pulling too many references (10+). The system gets muddy.

**Decision point — palette tension with brand:**
- IF a seasonal accent clashes with the base brand palette (e.g., a warm
  coral against Fig & Bloom's cool-toned palette) → test at 30% application.
  If it still fights, shift the accent toward a hue that bridges both worlds.
  Do not force-fit a colour that breaks brand coherence.
- IF the brief includes `exclusions` that conflict with the natural mood
  direction (e.g., emotion says "warm gratitude" but exclusions say "no
  warm tones") → escalate the tension to the brief owner. Do not silently
  override either instruction.

---

### Phase 3: System Extraction

**Entry conditions:** Approved moodboard. Preliminary palette defined.

Build the five mandatory components of the visual system:

#### 3a. Colour Overlay Palette
1. Finalise the seasonal accent palette:
   - Primary accent: used for headlines, CTAs, key graphic elements.
   - Secondary accent: used for supporting elements, backgrounds, dividers.
   - Bridge neutral: used for grounds and to connect accents to the base
     brand palette.
2. Define interaction rules:
   - Which base brand colours pair with which seasonal accents.
   - Minimum contrast ratios for text-on-colour combinations (WCAG AA:
     4.5:1 for body text, 3:1 for large text).
   - Specify which accent is dominant vs. subordinate (ratio guidance,
     e.g., "Primary accent at ~20% of canvas, secondary at ~10%").
3. Provide hex values, and RGB values for all colours.

#### 3b. Typography Treatment
1. Confirm which brand typefaces carry through (these are the 70% lock).
2. IF a seasonal display typeface is warranted:
   - It must complement, not compete with, the brand's primary typeface.
   - Use it for headlines and feature text only — never body copy.
   - Specify the exact pairing rules: sizes, weights, line-height, and
     letter-spacing for each hierarchy level (H1, H2, body, caption).
3. IF no seasonal display face is needed → document that the base
   typography carries through unchanged, with any seasonal colour
   application to type noted.

**Decision point — when to introduce a seasonal display typeface:**
- IF `moment_type` is `seasonal` or `brand_moment` AND the emotion
  calls for a distinctly different texture (e.g., hand-lettered warmth,
  editorial sharpness) → introduce a display face.
- IF `moment_type` is `product_launch` → lean toward base typography
  to keep product as hero. Display face only if the launch has a
  distinct sub-brand character.
- IF `moment_type` is `collab` → check partner guidelines. If the
  partner has a distinctive typeface, negotiate a pairing that gives
  both brands presence without typographic clutter.

#### 3c. Graphic Motif
1. Define one repeatable visual element drawn from the moodboard:
   pattern, texture overlay, illustration element, shape language, or
   border treatment.
2. The motif must:
   - Be simple enough to read at 80px wide (Stories sticker, email icon).
   - Be complex enough to carry a full-bleed background at 1920px.
   - Work in both the seasonal accent colours AND in single-colour
     (knockout/reversed) application.
3. Provide the motif as a rendered asset (SVG preferred for scalability,
   PNG fallback at 2x resolution).
4. Define usage rules: where the motif appears (background, border,
   accent element) and where it does not (never over hero product
   photography, never competing with the logo).

**What a junior gets wrong:**
- Motif is too detailed. If it doesn't read at thumbnail scale, it
  will fail on Stories and mobile placements.
- Motif is too literal. A heart for Valentine's Day or a wrapped gift
  for Christmas is generic. Push for abstraction — a petal scatter
  pattern, a brushstroke texture, a tonal wave — that evokes the mood
  without stating the occasion.

#### 3d. Photography Direction
1. Document lighting direction: natural/studio, warm/cool, soft/dramatic.
2. Document composition notes: centred/asymmetric, negative space
   guidance, depth of field preference.
3. Document prop/styling cues: textures, surfaces, supporting objects
   that reinforce the mood without distracting from the product.
4. IF hero product is specified → note how the product is positioned
   relative to the seasonal styling. Product is always the focal point;
   seasonal styling is the environment, not the subject.

#### 3e. Layout Principles
1. Define how the system adapts across four format archetypes:
   - **Hero landscape** (1200×628 — Meta feed ad, email banner)
   - **Square** (1080×1080 — Instagram feed, Meta ad)
   - **Vertical** (1080×1920 — Stories, Reels cover)
   - **Email module** (600px wide, variable height)
2. For each archetype, specify:
   - Where the motif sits (e.g., "bottom-right corner at 15% opacity").
   - Where the logo sits.
   - Where the headline sits relative to the product image.
   - Minimum clear-space rules.
3. These are principles, not pixel-perfect layouts. Execution skills
   will handle final composition.

**Quality gate:** All five components documented with concrete
specifications (hex values, sizing, usage rules). No component is
described only in subjective terms — every element has at least one
measurable or binary criterion.

---

### Phase 4: Cross-Format Validation

**Entry conditions:** All five system components defined.

1. Generate three test mockups applying the full system:
   - 1× Meta ad (1080×1080 square)
   - 1× Email hero banner (600×250)
   - 1× Story frame (1080×1920)
2. Evaluate each mockup against these criteria:
   - **Brand coherence:** If you strip the seasonal layer, does it still
     read as Fig & Bloom? (The 70/30 test.)
   - **Emotional accuracy:** Does the mockup evoke the brief's emotion,
     or has it drifted to something generic?
   - **Motif scalability:** Does the motif work at this format's scale
     without overwhelming or disappearing?
   - **Legibility:** Do all text-on-colour combinations meet contrast
     requirements?
   - **Channel fit:** Does the mockup feel native to the channel (e.g.,
     Story frame feels like a Story, not a shrunk-down banner)?

3. IF any mockup fails one or more criteria:
   - Identify the failing component (palette, motif, type, layout).
   - Adjust that component and re-render the failing mockup.
   - This is **self-correction loop 1**.

4. IF the adjusted mockup still fails:
   - Re-evaluate whether the issue is a component flaw or a systemic
     mismatch (e.g., the mood direction doesn't translate to the required
     channels).
   - Adjust and re-render. This is **self-correction loop 2**.

5. IF the mockup still fails after two correction loops:
   - **ESCALATE.** Package the brief, moodboard, current system, and
     failing mockups with a clear description of what isn't working.
     Send to the human creative director for intervention.
   - Do NOT continue iterating. Two failed loops indicates a strategic
     misalignment that the agent cannot resolve autonomously.

**Quality gate:** Three mockups pass all five criteria. Do not proceed
to handoff with any failing mockup.

---

### Phase 5: Handoff Package Assembly

**Entry conditions:** All three test mockups pass validation.

1. Assemble the **Campaign Style Guide** as a structured document
   (Markdown with embedded images). Contents:
   - Campaign name, moment type, date range, emotion anchor
   - Colour palette (hex, RGB) with interaction rules
   - Typography specs (faces, weights, sizes, hierarchy, pairing rules)
   - Graphic motif assets (SVG + PNG) with usage rules
   - Photography direction notes
   - Layout principles per format archetype
   - The three validated test mockups as reference
   - Do/Don't usage examples (minimum 2 dos, 2 don'ts)
2. Package motif assets as separate downloadable files alongside the
   guide.
3. Deliver the Campaign Style Guide to the requesting agent or to
   the designated handoff channel for downstream execution skills.

**Quality gate:** Style guide is self-contained — a downstream agent
should be able to produce on-brand campaign assets using only this
document and the master brand guide, with no further clarification needed.

---

## Edge Cases & Recovery

### Overlapping campaigns
IF two campaigns run concurrently (e.g., a product launch during a
seasonal moment):
- Determine which is primary (higher commercial priority).
- The secondary campaign borrows the primary's palette and adapts its
  own motif as a subordinate element.
- Escalate if the brief doesn't specify priority.

### Collab partner brand clash
IF the collab partner's brand guidelines fundamentally conflict with
Fig & Bloom's identity (e.g., neon palette vs. muted naturals):
- Default to Fig & Bloom's brand as the host environment.
- Introduce the partner's identity through one contained element (a
  co-branded lockup, a partner-coloured CTA) rather than blending both
  palettes across the full system.
- Escalate if the partner requires 50/50 visual parity — this is a
  strategic negotiation, not a design decision.

### Brief emotion is vague or contradictory
IF the emotion field contains conflicting signals (e.g., "bold yet
understated") or is too vague to extract a sensory direction (e.g.,
"nice"):
- Escalate to the brief owner with two concrete interpretations and
  ask them to choose. Do not proceed with an ambiguous anchor.

### Seasonal moment is culturally sensitive
IF the campaign moment has cultural or religious significance (e.g.,
Lunar New Year, Diwali):
- Research appropriate visual conventions and avoid motifs that are
  disrespectful or reductive.
- Escalate if uncertain about cultural appropriateness. Err on the
  side of restraint.

### Lean budget tier
IF `budget_tier` is `lean`:
- Reduce moodboard to 3–5 references (skip AI-generated concepts).
- Skip the seasonal display typeface — use base brand typography.
- Reduce test mockups to 2 (drop the format with lowest channel priority).
- The system quality bar does not lower — only the production depth.

---

## Quality Criteria

**Excellent looks like:**
- The system evokes a specific, ownable emotion — not a generic seasonal
  vibe. You could not swap in a competitor's logo and have it still work.
- Every component has concrete specs. No "use a warm colour" — instead,
  "#C4704E at 20% canvas coverage, paired with #E8DDD3 ground."
- The three test mockups feel like they belong to the same campaign AND
  the same brand, despite being different formats.
- A downstream agent can produce assets from the style guide without
  asking a single clarifying question.
- The do/don't examples prevent the most likely misapplication.

**Adequate looks like:**
- System is complete and on-brand but emotionally safe — it works, but
  it wouldn't stop anyone mid-scroll.
- Specs are present but some are subjective ("keep it airy") rather than
  concrete.

**Poor looks like:**
- System is a collection of aesthetic choices with no unifying emotion.
- Could belong to any premium brand — nothing is specific to Fig & Bloom.
- Motif doesn't scale or clashes with product photography.
- Downstream agent would need to make significant interpretation calls
  to produce assets.

---

## Anti-patterns

- **Cliché-first design.** Starting with the expected visual trope (pink
  for Mother's Day, red for Valentine's) instead of starting with emotion.
  The emotion should drive the palette, not the calendar.

- **Over-flexing the brand.** Introducing more than the allowed 30% flex.
  If the seasonal system needs a new primary typeface, a new palette, AND
  a new photography style, the brand has been abandoned, not extended.

- **Motif overload.** Using more than one graphic motif. One motif,
  applied consistently with variation, creates a system. Two motifs
  create visual noise.

- **Skipping the cross-format check.** Assuming that a system designed at
  square format will work at vertical and landscape. It often doesn't.
  The validation phase is not optional.

- **Subjective-only specs.** Describing the system in mood language
  without translating to concrete values. "Warm and organic" is a mood.
  "#B8703F on #FAF5F0 with 12px border-radius" is a spec. The style
  guide needs both, but the spec is what the downstream agent executes.

- **Literal motifs for the occasion.** Hearts, gift boxes, snowflakes,
  and other clip-art-level motifs signal low craft. Push toward
  abstraction that evokes without illustrating.

- **Ignoring the product.** The seasonal system serves the product, not
  the other way around. If the motif or palette pulls attention from
  the hero product, the system has failed its commercial purpose.
