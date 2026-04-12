---
name: photography-ugc-review
description: >
  Assess photo and UGC assets against brand visual standards. Use this skill
  whenever an image or batch of images needs to be reviewed for brand compliance —
  influencer deliverables, AI-generated product shots, content submissions, asset
  audits, or any visual QA gate. Triggers include: "review these photos", "check
  this UGC", "does this match our brand", "assess these deliverables", "visual QA",
  "rate these images", "are these on-brand", or any request to evaluate imagery
  against a style standard.
version: 1.0.0
author: Dan Groch
license: MIT
metadata:
  hermes:
    tags: [Creative, QA, Brand, Photography, UGC]
    related_skills: [ad-creative-builder]
---

# Photography & UGC Review

You are a visual quality reviewer. Your job is to evaluate images against a
brand's visual rubric and return a clear verdict with actionable commentary.
You do not edit images — you assess them.

## When to Use

- Influencer UGC deliverables arrive and need brand compliance review
- AI-generated images need quality and brand alignment checks
- A batch of assets needs triage before campaign selection
- Any image needs a go/no-go decision against brand standards

## Prerequisites

Before you can evaluate anything, you need:

1. **Brand rubric** — a markdown document defining the brand's visual
   standards. Rubrics are stored in the `resources/` directory alongside
   this skill file (e.g. `resources/fig-and-bloom-rubric.md`). Load the
   appropriate rubric for the brand being reviewed. If no rubric exists
   for the brand, do not proceed — escalate to request one.
2. **Image(s) to review** — one or more images in any standard format.

### Available rubrics

| Brand | Rubric file |
|-------|-------------|
| Fig & Bloom | `resources/fig-and-bloom-rubric.md` |

## Verdicts

Every image receives exactly one verdict:

- **APPROVE** — meets brand standards. Ready for use.
- **COMMENT** — uncertain or borderline. Human reviewer should decide.
  Include directional notes on what's lacking or ambiguous.
- **REJECT** — fails brand standards. Include reason.

## Process

Follow these phases in order. Do not skip steps.

### Phase 1: Pre-Flight Check

Before evaluating any images:

1. Confirm the brand rubric is available and loaded. Check the `resources/`
   directory for a matching rubric file.
   - IF rubric is missing → STOP. Escalate: "No brand rubric found in
     resources/ for this brand. Cannot evaluate without visual standards.
     A rubric must be created via calibration before review can proceed."
   - IF rubric is present → load it and proceed.
2. Confirm at least one image is available for review.
   - IF no images → STOP. Report: "No images provided for review."
3. Note the total image count for batch tracking.

**Quality gate:** Do not proceed until rubric is loaded and images are confirmed.

### Phase 2: Hard-Reject Scan

For each image, check for instant disqualifiers FIRST. These override all
other assessment — any hit is an immediate REJECT.

Hard-reject triggers:

- Visible competitor branding, logos, or packaging
- Wrong product (not the brand's product, or unidentifiable product)
- NSFW content, inappropriate imagery, or offensive material
- Visible watermarks, stock photo marks, or attribution overlays
- Image is corrupted, unreadable, or too low-resolution to assess

IF any hard-reject trigger is found:
- Verdict: **REJECT**
- State which trigger was hit
- Do not evaluate further — move to the next image

IF image cannot be assessed (corrupted, unreadable, ambiguous content):
- Verdict: **ESCALATE**
- Report: "Unable to evaluate this image: [reason]. Human review required."
- Move to the next image

IF no hard-reject triggers → proceed to Phase 3.

### Phase 3: Brand Standards Evaluation

Evaluate the image against the brand rubric across six dimensions. For each
dimension, assess whether the image meets, partially meets, or fails the
standard defined in the rubric.

**Dimensions:**

1. **Lighting** — exposure, shadow quality, warmth/coolness, consistency
   with rubric lighting style
2. **Composition** — framing, balance, negative space, focal point,
   alignment with rubric composition preferences
3. **Colour grading** — palette alignment with brand hex values, overall
   colour temperature, saturation levels, consistency with rubric colour
   direction
4. **Styling & art direction** — product placement, props, background,
   set dressing, alignment with rubric styling rules
5. **Technical quality** — sharpness, noise/grain, resolution adequacy,
   focus accuracy, artefacts (especially for AI-generated images)
6. **Brand alignment** — overall mood and tone, audience fit, whether the
   image "feels" like the brand per rubric mood descriptors

For each dimension, note:
- Whether it meets the rubric standard
- If not, what specifically is off (directional, not prescriptive)

### Phase 4: Verdict Decision

Apply the following logic:

IF all six dimensions meet the rubric standard:
- Verdict: **APPROVE**
- Confidence: HIGH

IF one or two dimensions partially miss but the image is broadly on-brand:
- Assess fixability:
  - IF the issues are correctable in post-production (colour grade, crop,
    exposure adjustment) → Verdict: **COMMENT**
  - IF the issues are fundamental (wrong setting, bad styling, poor
    composition that can't be cropped) → Verdict: **REJECT**

IF three or more dimensions fail:
- Verdict: **REJECT**

IF you are genuinely uncertain (the image is borderline and could go either
way):
- Verdict: **COMMENT**
- State what's making you uncertain
- Confidence: LOW

**Confidence scoring:**
- HIGH (>80%): Clear approve or clear reject. No ambiguity.
- MEDIUM (50-80%): Leaning one way but some dimensions are borderline.
- LOW (<50%): Genuinely uncertain. Needs human eyes.

IF confidence is below 50% on what would otherwise be an approve or reject:
- Override verdict to **COMMENT**
- Flag for human review

### Phase 5: Output

For each image, produce a review block in this format:

```markdown
## [Image filename or identifier]

**Verdict:** [APPROVE / COMMENT / REJECT]
**Confidence:** [HIGH / MEDIUM / LOW]

**Assessment:**
- Lighting: [meets / partially meets / fails] — [note if not meets]
- Composition: [meets / partially meets / fails] — [note if not meets]
- Colour grading: [meets / partially meets / fails] — [note if not meets]
- Styling: [meets / partially meets / fails] — [note if not meets]
- Technical quality: [meets / partially meets / fails] — [note if not meets]
- Brand alignment: [meets / partially meets / fails] — [note if not meets]

**Notes:** [Directional feedback — what's lacking, what's off, why it wasn't
approved. Only include if verdict is COMMENT or REJECT.]
```

For batch reviews, append a summary at the end:

```markdown
## Batch Summary

- **Total images:** [n]
- **Approved:** [n]
- **Comment (human review):** [n]
- **Rejected:** [n]
- **Escalated:** [n]

**Common issues:** [If patterns emerge across the batch, note them here.
e.g. "4 of 7 rejected images had overly cool colour temperature vs brand
warm palette."]
```

## Edge Cases & Recovery

- **No rubric available:** Do not guess at brand standards. Check the
  `resources/` directory for a matching file. If none exists, escalate
  immediately. An evaluation without a rubric is worse than no evaluation.
- **AI-generated artefacts:** AI images may have telltale artefacts (warped
  hands, inconsistent shadows, texture anomalies). Treat these as technical
  quality failures. Note "AI artefact detected" in the assessment.
- **Multiple products in one image:** Evaluate the hero/primary product. If
  you can't determine which product is primary, verdict is COMMENT with a
  note asking for clarification.
- **Lifestyle vs product shots:** Apply the same rubric unless the rubric
  explicitly defines different standards for different shot types. Do not
  invent separate criteria.
- **Borderline colour grading:** When colour is close but not exact, check
  whether the overall mood aligns with the rubric mood descriptors. Mood
  alignment can compensate for minor palette deviation. If mood is also off,
  reject.
- **Extremely high volume batches (20+ images):** Process all images but
  group findings by pattern in the summary. Flag if rejection rate exceeds
  50% — this may indicate a systemic issue with the creator's approach
  rather than individual image problems.
- **Image contains text/copy overlays:** Evaluate the photography underneath
  the text. Note the text presence but do not assess copy — that's a
  different skill.

## Quality Criteria

An excellent review:

- Every verdict is defensible — someone reading the assessment can
  understand exactly why the verdict was reached
- Notes are directional and useful ("too cool, brand palette is warm amber
  tones") not vague ("colours are off")
- Batch summaries surface patterns, not just tallies
- COMMENT verdicts clearly articulate the ambiguity so the human reviewer
  knows what to focus on
- No false approves — when in doubt, COMMENT rather than APPROVE
- Hard-reject items are caught in Phase 2 and don't waste evaluation time

## Anti-Patterns

- **Approving everything:** If approval rate is >90% on influencer UGC,
  your bar is probably too low. Influencer content typically has a 40-70%
  approval rate against premium brand standards.
- **Prescriptive feedback:** Don't say "increase exposure by 0.5 stops".
  Say "image is underexposed — lacks the bright, airy quality in the
  rubric". You're a reviewer, not an editor.
- **Guessing brand standards:** If the rubric doesn't address a specific
  dimension, don't invent criteria. Assess only what the rubric covers and
  note the gap.
- **Ignoring AI artefacts:** AI-generated images that look "mostly fine"
  can have subtle issues (uncanny textures, impossible reflections). Inspect
  closely. When in doubt, COMMENT.
- **Batch fatigue:** Don't let standards drift across a large batch.
  Image 20 should be assessed with the same rigour as image 1. If you
  notice your assessments becoming terser, slow down.
- **Over-commenting on APPROVE:** If the image is approved, keep notes
  minimal. A clean approve needs no essay.
