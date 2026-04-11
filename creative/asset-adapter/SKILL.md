---
name: asset-adapter
description: >
  Take a hero ad creative and reformat it into platform-specific variants
  with rules-based cropping, safe-zone compliance, and text resizing.
  Use this skill whenever someone asks to resize, adapt, reformat, or
  repurpose an existing creative for different platforms or placements.
  Triggers include: "resize this for Stories", "I need a 728x90 version",
  "adapt this for email", "make feed and story versions", "create display
  banners from this ad", "reformat for Instagram/Facebook/Google Display",
  or any request to produce multiple size variants from a single source
  creative. This skill does NOT create original layouts or compositions —
  it transforms existing ones. If no hero creative exists yet, delegate
  to ad-creative-builder first.
version: 1.0.0
author: Dan Groch
license: MIT
metadata:
  hermes:
    tags: [Design, Advertising, Resizing, Adaptation, Multi-format]
    related_skills: [ad-creative-builder, ai-image-generation]
---

# Asset Adapter

## Overview

Transform a completed hero creative into platform-specific format
variants using deterministic rules for cropping, safe zones, and text
resizing. This is a production skill — it applies mechanical adaptation
logic, not creative judgment. The creative decisions were already made
upstream in `ad-creative-builder`.

## Prerequisites

- **Hero creative**: A finished, QA-passed creative from
  `ad-creative-builder` (or a human-supplied source file). Must be
  the highest-resolution version available.
- **Figma API access**: Same project and permissions as
  `ad-creative-builder`.
- **Source template ID**: The Figma template used to build the hero,
  so format variants of the same template can be selected.
- **Target format list**: Which platforms/placements to produce.

## Scope

### In scope
- Adapting a hero creative to any supported output format
- Rules-based cropping with safe-zone enforcement
- Text resizing within defined constraints
- Logo repositioning per format-specific rules
- CTA re-scaling and re-anchoring
- Vision-based QA of each variant
- Batch production of multiple formats in a single run
- Uploading variants to Google Drive alongside the hero

### Out of scope
- **Creating original compositions** → `ad-creative-builder`
- **Generating new photography** → `ai-image-generation`
- **Rewriting copy** → if the copy doesn't fit after adaptation,
  flag it. Do not rewrite.
- **Video adaptation** → `ai-video-generation`
- **Designing new templates or format variants** → human task

## Supported Output Formats

| Format         | Dimensions   | Aspect Ratio | Use Case                    |
|----------------|-------------|-------------|------------------------------|
| Feed           | 1080 × 1080 | 1:1         | Instagram/Facebook feed      |
| Stories/Reels  | 1080 × 1920 | 9:16        | Instagram/Facebook Stories    |
| Feed portrait  | 1080 × 1350 | 4:5         | Instagram/Facebook feed      |
| Landscape      | 1200 × 628  | 1.91:1      | Facebook link ads, OG images |
| Leaderboard    | 728 × 90    | ~8:1        | Google Display Network       |
| Medium rect    | 300 × 250   | 6:5         | Google Display Network       |
| Skyscraper     | 160 × 600   | ~1:3.75     | Google Display Network       |
| Email header   | 600 × 200   | 3:1         | Email marketing              |

If a requested format is not in this table → ask the requester for
exact pixel dimensions and intended platform before proceeding.

## Process

### Phase 1: Ingest Hero Creative

**Entry conditions:** A hero creative file or Figma template instance
is referenced.

**Actions:**
1. Identify the source:
   - If a Figma template instance → retrieve the instance ID and
     extract: hero image, headline text, body text, CTA text, logo
     placement, colour tokens.
   - If a flat image file (PNG/JPEG) → this skill can only crop and
     overlay. Text resizing and slot manipulation require the Figma
     source. Flag: "I have the flat file but not the Figma source.
     I can crop and reposition, but text will be baked in and may
     become unreadable at small sizes. Provide the Figma source for
     best results."
2. Record the hero's format (dimensions, aspect ratio).
3. Parse the target format list from the request.

**Decision tree:**
- If hero is a Figma instance → proceed to Phase 2 (template-based).
- If hero is a flat file and target formats are all larger or similar
  aspect ratio → proceed with crop-only path (Phase 2b).
- If hero is a flat file and target includes extreme aspect ratios
  (leaderboard 728×90, skyscraper 160×600) → warn: "Adapting a flat
  file to [format] will require heavy cropping and baked-in text may
  be lost. Recommend using the Figma source." Proceed only if
  instructed.

**Quality gate:** Hero source is accessible and all target formats
are identified.

### Phase 2: Template-Based Adaptation (Figma Source)

**Entry conditions:** Figma instance ID is available. Target formats
are defined.

For each target format:

**Actions:**
1. **Select format variant template:**
   - Look for a variant of the hero's base template at the target
     dimensions.
   - If no variant exists → report: "No [format] variant of template
     [name] exists. Cannot adapt." Skip this format.

2. **Transfer content to variant:**
   - Copy all slot content from the hero instance (image, headline,
     body, CTA, logo) into the format variant.

3. **Apply adaptation rules:**

   **Image cropping:**
   - Detect the subject focal point in the hero image.
   - Crop to the target aspect ratio, keeping the focal point within
     the safe zone (see Safe Zone Rules below).
   - If cropping would remove more than 50% of the original frame →
     flag: "Heavy crop required for [format]. Subject may be partially
     cut. Review recommended."

   **Text resizing:**
   - Calculate the ratio between hero text area and target text area.
   - Scale font size proportionally.
   - Apply constraints:
     - Minimum font size: 12px at 1x resolution (24px at 2x export).
       Below this → text is unreadable on target device.
     - If headline falls below minimum after scaling → options in
       priority order:
       1. Reduce to two lines (if currently single-line).
       2. Truncate with ellipsis.
       3. Hide headline entirely (display ads only — leaderboard,
          medium rect, skyscraper).
     - Body copy: hide entirely if target area is less than 40% of
       hero body area. Body is expendable; headline and CTA are not.
   - CTA text: never truncate. If it doesn't fit → reduce font size
     to minimum. If still overflowing → flag for human review.

   **Logo repositioning:**
   - Use format-specific logo placement rules:
     - 1:1, 4:5, 9:16: logo in original position (template default).
     - Landscape (1.91:1): logo top-right or bottom-right, scaled to
       max 15% of frame width.
     - Leaderboard (728×90): logo left-aligned, max height 70% of
       banner height. CTA right-aligned.
     - Medium rect (300×250): logo bottom-centre or bottom-right,
       max 20% of frame width.
     - Skyscraper (160×600): logo top-centre, max 80% of frame width.
     - Email header (600×200): logo left-aligned, max height 60% of
       banner height.

   **CTA repositioning:**
   - For display formats (leaderboard, medium rect, skyscraper): CTA
     must be the dominant element. Scale CTA button to occupy at least
     25% of the total frame area in these formats.
   - For social formats: maintain template default CTA placement.

4. **Render preview** via Figma API (1x resolution PNG).

### Phase 2b: Flat-File Adaptation (No Figma Source)

**Entry conditions:** Only a flat image file is available.

For each target format:

1. Detect focal point in the source image.
2. Crop to target aspect ratio using focal-point-centred cropping.
3. If the target format is significantly smaller (e.g., leaderboard) →
   crop aggressively to the most visually impactful region.
4. Export at target dimensions.
5. Flag in delivery: "Adapted from flat file — text elements are
   baked in and may not be legible at this size."

No text resizing or slot manipulation is possible in this path.

### Phase 3: Safe Zone Validation

**Entry conditions:** Variant is composed (from Phase 2 or 2b).

Each platform has UI elements that overlay parts of the ad. Critical
content must avoid these zones.

**Safe zone rules:**

- **Instagram Stories (9:16):** Top 14% (status bar, account name)
  and bottom 20% (CTA swipe-up area, message bar) are unsafe. All
  text and logo must sit within the middle 66%.
- **Instagram Feed (1:1, 4:5):** Bottom 10% may be overlaid by
  like/comment bar in some views. Keep CTA above this line.
- **Facebook Feed (all):** 20% text rule is deprecated but high
  text density still reduces delivery. Keep text to under 30% of
  frame area.
- **Google Display (all banner sizes):** No platform overlay, but
  ensure 4px inner padding — no content touching the frame edge.
  AdSense requires a visible border or distinct background.
- **Email header:** No safe zone constraints, but right 30% may be
  clipped on mobile clients. Keep critical content left-aligned.

**Actions:**
1. For each rendered variant, check via vision:
   - Is any critical element (headline, CTA, logo) inside an unsafe
     zone for that platform?
   - Does text occupy more than 30% of the frame?
2. If a violation is detected → adjust element position within the
   Figma template and re-render. For flat files → re-crop.

**Quality gate:** All variants pass safe zone validation.

### Phase 4: Vision QA

**Entry conditions:** All variants rendered and safe-zone-validated.

**Actions:**
1. For each variant, inspect the rendered PNG using vision. Checklist:

   **Must pass (blocking):**
   - [ ] Text is legible at the target viewing context (mobile for
         social, desktop for display, inbox for email)
   - [ ] CTA is visible and has sufficient contrast
   - [ ] Logo is present and not cropped
   - [ ] No empty slots, placeholder text, or broken layout
   - [ ] Subject in hero image is recognisable after cropping
   - [ ] No content in platform-specific unsafe zones

   **Should pass (warning):**
   - [ ] Visual hierarchy is maintained (headline > CTA > body)
   - [ ] Image quality is acceptable (no visible pixelation)
   - [ ] Colour contrast meets accessibility baseline (4.5:1 for text)

2. **Decision tree:**
   - Any "must pass" failure → return to Phase 2/2b, fix, re-render.
     Max 3 retries per variant. After 3 → escalate with the rendered
     image and failure description.
   - Only "should pass" warnings → note in delivery, proceed.

**Quality gate:** All variants pass all "must pass" checks.

### Phase 5: Export & Deliver

**Entry conditions:** All variants have passed QA.

**Actions:**
1. Export final assets from Figma API:
   - Resolution: 2x for social formats, 1x for display/email
     (matching standard ad-serving expectations).
   - Format: PNG (default), JPEG if file size exceeds 5MB.
2. Name files consistently:
   `[campaign]-[product]-[format]-[dimensions]-v[N].png`
   e.g., `mothers-day-native-bouquet-feed-1080x1080-v1.png`
3. Upload to Google Drive:
   - Folder: `Ad Creatives / [Campaign Name] / [Date] / Variants`
   - Place alongside the hero creative (not in a separate tree).
4. Post delivery summary to Paperclip:
   - List of all variants with Drive links
   - Any warnings (heavy crop, text hidden, flat-file limitations)
   - Formats that could not be produced (missing template variants)

**Quality gate:** All files uploaded. Drive links resolve correctly.

### Phase 6: Handle Change Requests

**Entry conditions:** Delivery complete. Change request received.

**Actions:**
1. Categorise the change:
   - **"Adjust crop on [format]"** → return to Phase 2 for that
     format only, re-crop, re-QA.
   - **"Text is too small on [format]"** → return to Phase 2, adjust
     text sizing within constraints. If already at minimum → report
     options (truncate, hide body, use fewer words).
   - **"Add a format I didn't ask for"** → return to Phase 2 for the
     new format only.
   - **"The hero changed"** → re-run from Phase 1 with the new hero.
     All variants must be regenerated.
   - **"Move the logo"** → adjust per format, re-QA that variant only.
2. Re-run Phases 4–5 for any modified variant.
3. Increment version suffix in filenames.

## Edge Cases & Recovery

- **Hero image has text baked into the photograph** (e.g., product
  packaging with brand name): Focal-point detection should prioritise
  the product, not the text. Flag: "Source image contains embedded
  text which may be partially cropped in smaller formats."
- **Target format is portrait but hero is landscape (or vice versa):**
  This is normal. The cropping rules handle it. But if the aspect
  ratio flip is extreme (e.g., 9:16 hero → 728×90 leaderboard) →
  warn that the result will look very different from the hero.
- **Multiple hero creatives in one request** ("adapt all five of
  these"): Process sequentially. Deliver each hero's variants as a
  batch before starting the next.
- **Figma API timeout during batch export:** Export one format at a
  time rather than bulk. Retry failed exports up to 3 times with
  exponential backoff.
- **Requested format matches the hero format:** Skip adaptation.
  Deliver the hero file directly, renamed to match the convention.
- **Brand has dark and light logo variants:** Use dark logo on light
  backgrounds, light logo on dark backgrounds. Determine by sampling
  the background colour in the logo region of the rendered variant.

## Quality Criteria

**Excellent output:**
- Every variant looks intentionally designed for its platform, not
  just mechanically resized
- Text is legible at intended viewing distance for every format
- No content sits in platform-unsafe zones
- CTA is prominent and actionable across all sizes
- File naming is consistent and all variants live in the right Drive
  folder alongside the hero
- Produced in a single pass with no QA failures

**Poor output:**
- Text unreadable in smaller formats (too small or cropped)
- Subject lost to aggressive cropping
- Logo missing in some variants but not others
- Inconsistent naming or scattered file locations
- Display ads with no clear CTA
- Social formats with content in unsafe zones

## Anti-Patterns

- **Treating this as a creative skill.** This skill adapts, it does
  not design. If the hero doesn't exist → call `ad-creative-builder`.
  Do not compose layouts from scratch.
- **Uniform scaling without format awareness.** A 9:16 creative
  scaled to 728×90 is not an adaptation — it's a thumbnail. Each
  format has its own layout logic.
- **Keeping body copy in display formats.** Leaderboard and medium
  rect have no room for body text. Hide it. Headline + CTA + logo
  is sufficient.
- **Ignoring safe zones.** An Instagram Story with the CTA in the
  bottom 20% is invisible behind the platform UI. Always validate.
- **Silently hiding elements.** If body copy or headline is removed
  to fit a format, say so in the delivery summary. The brief owner
  needs to know what was dropped.
- **Re-exporting at hero resolution for display ads.** A 728×90
  banner exported at 2x is unnecessary and inflates file size.
  Match export resolution to format conventions.
