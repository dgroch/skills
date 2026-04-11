---
name: ad-creative-builder
description: >
  Build production-ready static and carousel ad creatives by composing
  photography, copy, and brand elements into Figma templates and rendering
  final assets. Use this skill whenever someone asks to create ads, social
  media graphics, promotional banners, campaign assets, carousel posts,
  or any branded visual content that combines photography with graphic
  design. Also triggers for: "make creatives for this campaign", "I need
  Meta/Instagram/Facebook ad assets", "resize this ad for Stories",
  "create a set of ads from these product shots", "build a carousel",
  or any request to assemble final ad artwork from existing imagery.
  This skill does NOT generate photographs or video — it consumes them.
  Delegate to ai-image-generation for photographic assets and
  ai-video-generation for video clips and timeline assembly.
version: 1.0.0
author: Dan Groch
license: MIT
metadata:
  hermes:
    tags: [Design, Advertising, Creative, Figma, Brand]
    related_skills: [ai-image-generation, ai-video-generation]
---

# Ad Creative Builder

## Overview

Assemble production-ready ad creatives (static images and carousels) by
compositing photography, copy, CTAs, and brand elements into Figma
templates, then rendering final assets at platform-specific dimensions.
This is the graphic design skill — it owns the canvas, layout, and
brand application, not the raw photography or video production.

## Prerequisites

Before execution, the following must be available:

- **Figma templates**: Pre-built design templates with named component
  slots (hero image, headline, body, CTA, logo). Templates must exist
  in the shared Figma project before this skill can run.
- **Figma API access**: Valid API token with read/write/export permissions
  on the template project.
- **Brand guidelines**: Colours (hex values), typography (font families,
  weights, sizes per slot), logo files, and any brand-trained LoRA
  identifier if available.
- **Brief**: At minimum — campaign type, product category, copy (headline +
  body + CTA text), and target platform(s).
- **Photography**: Product or lifestyle images, either already available
  on Google Drive or to be requested from the `ai-image-generation` skill.

## Scope

### In scope
- Selecting the correct Figma template for the brief
- Placing photography into hero/image slots
- Populating text slots (headline, body, CTA)
- Applying brand elements (colours, fonts, logo)
- Cropping and focal-point adjustment for image fitting
- Adapting a 9:16 hero layout to 4:5 and 1:1 derivatives
- Rendering final PNG/JPEG exports via Figma API
- Building carousel ads (multi-frame template instances)
- Self-QA via vision inspection of rendered output
- Handling change requests ("make the CTA bigger", "try a different image")
- Uploading final assets to Google Drive

### Out of scope — delegate to sibling skills
- **Generating photographs** → `ai-image-generation`
- **Generating video clips** → `ai-video-generation`
- **Video timeline assembly** (cuts, overlays, music) → `ai-video-generation`
- **Creating new Figma templates** → human-led task (v1)
- **Writing ad copy from scratch** → copywriting skill or human brief

## Process

### Phase 1: Parse Brief

**Entry conditions:** A brief has been received (message, document, or
structured input).

**Actions:**
1. Extract from the brief:
   - Campaign type (promo, seasonal, awareness, launch)
   - Product category
   - Target platform(s) and format(s): 9:16, 4:5, 1:1
   - Headline text
   - Body copy (if any)
   - CTA text
   - Asset references (Drive links, filenames, or "generate new")
   - Any specific template requested by name
2. Identify missing required fields.

**Decision tree:**
- If headline, CTA, or campaign type is missing → ask the brief owner
  for clarification. Ask one focused question only. Do not proceed
  without headline and CTA at minimum.
- If no platform specified → default to 9:16 + 4:5.
- If no photography referenced → check Google Drive for recent product
  shots matching the product category. If none found → delegate to
  `ai-image-generation` with a shot description derived from the brief.
  Pause this skill until assets are returned.
- If copy exceeds expected character limits for the template slot →
  flag in Phase 3, do not reject the brief.

**Quality gate:** Do not proceed until campaign type, headline, CTA text,
target format(s), and at least one image asset (or a pending delegation)
are confirmed.

### Phase 2: Select Template

**Entry conditions:** Brief is parsed and complete.

**Actions:**
1. Query the Figma template library for templates matching:
   - Campaign type (primary filter)
   - Product category (secondary filter)
   - Format (9:16 as the hero; derivatives handled in Phase 5)
2. If multiple templates match, select based on:
   - Most recently used for this campaign type (consistency within campaign)
   - Best fit for the number of text elements in the brief
3. If no template matches → escalate to a human. Do not improvise layouts.

**Decision tree:**
- If brief explicitly names a template → use it, skip selection logic.
- If only one template matches → use it.
- If multiple match and no campaign history exists → select the template
  with the fewest slots (simplest layout). State which template was
  chosen and why.
- If zero templates match → stop. Report: "No template found for
  [campaign type] × [product category]. A new template needs to be
  created in Figma before I can proceed."

**Quality gate:** A specific template ID is selected and confirmed
accessible via Figma API.

### Phase 3: Compose Layout

**Entry conditions:** Template selected. Photography available (on Drive
or returned from `ai-image-generation`).

**Actions:**
1. **Image fitting:**
   - Retrieve the hero image slot dimensions from the template.
   - Analyse the source photograph's aspect ratio and subject position.
   - If the source image aspect ratio does not match the slot:
     - Use focal-point detection to identify the subject centre.
     - Crop to the slot aspect ratio, keeping the subject within the
       centre 60% of the frame.
   - If the source image resolution is lower than the slot dimensions →
     flag a warning but proceed. Note in delivery that the image may
     appear soft.
   - Place the processed image into the hero slot via Figma API.

2. **Text population:**
   - Insert headline into the headline component.
   - Insert body copy into the body component (if the template has one).
   - Insert CTA text into the CTA component.
   - **Copy fitting rules:**
     - If text overflows the bounding box at the template's default
       font size → first attempt: reduce font size by 10% increments
       down to a floor of 70% of the default size.
     - If still overflowing at 70% → truncate with ellipsis and flag
       to the brief owner: "Headline truncated — original was X chars,
       max is ~Y chars at minimum readable size."
     - Never reduce font size below the floor — readability is
       non-negotiable.

3. **Brand application:**
   - Confirm logo is placed in the template's logo slot (templates
     should have this pre-set, but verify it hasn't been cleared).
   - Verify brand colours are applied to CTA button, background
     accents, and text per the template's colour tokens.

**Quality gate:** All slots populated. No empty component slots remain
in the template instance.

### Phase 4: Self-QA (Vision Check)

**Entry conditions:** Layout composition is complete.

**Actions:**
1. Export a preview render from Figma API (PNG, 1x resolution is fine
   for QA).
2. Inspect the rendered image using vision. Check against this list:

   **Must pass (blocking):**
   - [ ] Text is fully visible and not clipped by edges or overlapping
         elements
   - [ ] Hero image is not awkwardly cropped (subject is recognisable)
   - [ ] CTA button/text is legible and has sufficient contrast
   - [ ] Logo is present and correctly positioned
   - [ ] No empty/placeholder slots visible
   - [ ] Overall layout is not broken (no overlapping layers, no
         misaligned elements)

   **Should pass (warning, do not block):**
   - [ ] Text hierarchy is clear (headline reads as dominant element)
   - [ ] Image quality appears acceptable (not pixelated)
   - [ ] Colour palette matches brand guidelines

3. **Decision tree:**
   - If any "must pass" item fails → diagnose the issue, return to
     Phase 3 to fix, then re-export and re-check. Maximum 3 retry
     loops. If still failing after 3 attempts → escalate to human
     with the rendered image and a description of what's failing.
   - If only "should pass" items flag → note them in the delivery
     message but proceed.

**Quality gate:** All "must pass" checks clear.

### Phase 5: Format Adaptation

**Entry conditions:** Hero format (9:16) has passed QA.

**Actions:**
1. For each additional format requested (4:5, 1:1):
   - Select the corresponding format variant of the same template.
   - Re-run Phase 3 (compose) with the same assets and copy.
   - Re-run Phase 4 (QA) for the new format.
2. Image re-cropping may be needed — the focal-point logic from
   Phase 3 applies again for the new aspect ratio.

**Decision tree:**
- If the template does not have a variant for the requested format →
  report: "No [format] variant exists for template [name]. Available
  formats: [list]." Do not attempt to manually resize.
- If carousel → each slide is a separate template instance. Repeat
  Phases 3–4 per slide, using the carousel-specific template.

**Quality gate:** Each format variant has independently passed Phase 4 QA.

### Phase 6: Render & Deliver

**Entry conditions:** All formats have passed QA.

**Actions:**
1. Export final assets from Figma API:
   - Format: PNG (static) or JPEG (if file size is a concern)
   - Resolution: 2x for production quality
   - Naming convention: `[campaign]-[product]-[format]-[variant].png`
     e.g., `mothers-day-native-bouquet-9x16-v1.png`
2. Upload all assets to Google Drive:
   - Target folder: `Ad Creatives / [Campaign Name] / [Date]`
   - Create the folder if it doesn't exist.
3. Post a delivery summary to Paperclip with:
   - Google Drive links to each asset
   - Thumbnail previews (if supported)
   - Any warnings from QA (image quality, copy truncation)
   - Template name used
   - Formats delivered

**Quality gate:** Files are uploaded and accessible. Drive links resolve.

### Phase 7: Handle Change Requests

**Entry conditions:** Delivery is complete. A change request is received.

**Actions:**
1. Parse the change request. Categorise:
   - **Copy change** (different headline, CTA, body) → return to Phase 3,
     text population step only. Skip image fitting.
   - **Image change** ("try a different hero") → return to Phase 3,
     image fitting step. If new photography is needed → delegate to
     `ai-image-generation`, pause until returned.
   - **Layout change** ("make the CTA bigger", "move the logo") →
     if adjustable via Figma component properties (size, position
     overrides) → adjust and re-render. If the change requires a
     structural template edit → escalate: "This requires a template
     modification in Figma. I can apply it once the template is updated."
   - **Format addition** ("also give me a 1:1") → return to Phase 5.
   - **Unclear request** → ask one clarifying question.
2. After applying changes, re-run Phase 4 (QA) and Phase 6 (delivery).
3. Increment the version suffix in filenames: v1 → v2 → v3.

**Decision tree:**
- If more than 5 revision rounds on the same creative → flag:
  "We're on v6. Want to reconsider the brief or template choice?"
  Continue if instructed.

## Edge Cases & Recovery

- **Figma API rate limit hit:** Back off with exponential delay
  (1s, 2s, 4s, max 30s). Retry up to 5 times. If still failing →
  report the error and estimated retry window.
- **Figma template has been modified by someone else mid-composition:**
  Re-fetch the template state before writing. If slots have changed
  names → report the mismatch and ask which template version to use.
- **Photography is portrait but slot is landscape (or vice versa):**
  Apply focal-point cropping. If cropping would remove more than 40%
  of the subject → flag: "This image doesn't fit the slot well.
  Options: (1) use a different image, (2) proceed with heavy crop."
- **Google Drive upload fails:** Retry 3 times. If persistent → save
  files locally and provide the local path as fallback.
- **Brief contains no body copy but template has a body slot:** Leave
  the body slot empty if the template supports it (optional component).
  If the slot is mandatory and renders as placeholder text → hide the
  component or set text to a single space. Flag in delivery.
- **Multiple products in one brief:** Create one creative per product
  unless the brief explicitly asks for a multi-product layout. Confirm
  with the brief owner before producing.

## Quality Criteria

**Excellent output:**
- All text is legible at intended viewing distance (mobile screen)
- Photography is well-cropped with subject clearly visible
- Brand is immediately recognisable (colours, logo, typography)
- CTA is the most prominent actionable element
- Files are correctly sized for target platform (no letterboxing,
  no cropping by the platform itself)
- Naming convention is consistent and sortable
- Delivered within a single pass (no QA failures requiring retry)

**Poor output:**
- Text overlapping images or clipped at edges
- Logo missing or barely visible
- Wrong aspect ratio for the target platform
- Placeholder text or empty slots visible
- Inconsistent naming, files dumped without folder structure
- Multiple QA retries with issues still unresolved

## Anti-Patterns

- **Designing from scratch without a template.** This skill does not
  freehand layouts. If no template exists, escalate — do not attempt
  to generate a layout via prompting an image model.
- **Generating photography.** Delegate to `ai-image-generation`. This
  skill assembles, it does not create source imagery.
- **Silently truncating copy.** Always flag when copy has been modified
  to fit. The brief owner decides if the shorter version is acceptable.
- **Skipping QA on derivative formats.** A layout that works at 9:16
  can break at 1:1. Always re-check.
- **Over-iterating without pushback.** If revision requests are
  contradictory or endless, surface the pattern and suggest revisiting
  the brief.
- **Reducing font size below the floor.** Readability on mobile is
  non-negotiable. Truncate before making text unreadable.
- **Using stale template state.** Always fetch the current template
  from Figma before writing to slots.
