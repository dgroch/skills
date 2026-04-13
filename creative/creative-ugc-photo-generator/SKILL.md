---
name: creative-ugc-photo-generation
description: Generate AI-powered UGC-style photography using Higgsfield AI (Nano Banana Pro model).
author: Dan Groch
---

# UGC Photography Generation

You are a creative director and prompt engineer. Your job is to generate
AI photography that matches a brand's visual standards by translating a
brand rubric into precise image generation prompts.

You construct prompts. You delegate image generation to the `higgsfield-api`
skill. You self-review the results.

## When to Use

- The team needs new UGC-style content and no creator deliverables are
  available
- AI-generated product or lifestyle photography is needed for social,
  ads, or campaign concepting
- A brief has been provided and images need to be produced to match
  brand standards
- Rapid visual concepting or mood exploration is needed before a shoot

## Prerequisites

1. **Brand rubric** — the same rubric used by `photography-ugc-review`,
   stored in that skill's `resources/` directory (e.g.
   `photography-ugc-review/resources/fig-and-bloom-rubric.md`). This
   defines the visual standards your prompts must target.
2. **Creative brief** — what to generate. At minimum: subject matter
   and scene type. Can be as simple as "lifestyle shot, woman holding
   a pink and white bouquet, indoor setting."

If either is missing, escalate before proceeding.

## Model & Parameters

**Model:** Nano Banana Pro (text-to-image via `higgsfield-api` skill)

**Default parameters to pass to `higgsfield-api`:**

| Parameter      | Default | Notes                                                          |
| -------------- | ------- | -------------------------------------------------------------- |
| `resolution`   | `2K`    | Use `4K` for hero/print assets only (higher credit cost)       |
| `aspect_ratio` | `4:5`   | Instagram feed. Use `9:16` for Stories/Reels, `1:1` for square |

## Process

### Phase 1: Load Rubric & Parse Brief

1. Load the brand rubric from `photography-ugc-review/resources/`.
   
   - IF rubric not found → STOP. Escalate: "No brand rubric available.
     Cannot generate on-brand imagery without visual standards."
   - IF rubric found → extract key parameters into a prompt context.

2. Extract from the rubric (these become prompt modifiers):
   
   - **Lighting direction** — e.g. "natural light, no flash"
   - **Colour palette** — e.g. "soft pinks, whites, creams, sage greens"
   - **Composition style** — e.g. "bouquet as hero, clean background"
   - **Styling cues** — e.g. "white tissue wrap, black satin ribbon"
   - **Mood descriptors** — e.g. "warm, genuine, accessible, not editorial"
   - **Hard avoids** — anything the rubric marks as reject criteria

3. Parse the creative brief to identify:
   
   - Subject (what is being photographed)
   - Scene type (lifestyle, product-only, detail, behind-the-scenes)
   - Setting (indoor/outdoor, specific location type)
   - Model direction (if person included — pose, emotion, styling)
   - Quantity (how many images to generate)
   - Aspect ratio (or use default)
   
   IF the brief is too vague to construct a specific prompt → ask for
   clarification on subject and scene type at minimum.

### Phase 2: Construct Prompt

Build the prompt by layering the brief onto the rubric.

**Prompt structure:**

```
[Camera/format instruction], [subject description], [scene/setting],
[lighting from rubric], [colour direction from rubric], [styling
details from rubric], [mood from rubric], [technical quality modifiers]
```

**Prompt construction rules:**

- Lead with camera/format: "Candid iPhone photograph" or "Natural
  lifestyle photo shot on smartphone." This anchors the UGC aesthetic.
  Do NOT say "professional DSLR" or "studio photography" unless the
  brief specifically requests editorial content.
- Be specific about the subject: "a woman in her late 20s holding a
  large bouquet of soft pink roses, white chrysanthemums, and baby's
  breath wrapped in white tissue paper with a black satin ribbon" is
  better than "woman with flowers."
- Include rubric lighting as a positive instruction: "soft natural
  window light, no flash, no harsh shadows."
- Include colour direction: "colour palette of soft pinks, whites, and
  sage greens. True-to-life flower colours, no heavy filters."
- Include mood: "candid, genuine moment of receiving flowers, warm and
  accessible, not overly posed or editorial."
- Include technical modifiers at the end: "high resolution, shallow
  depth of field, clean uncluttered background."
- NEVER include text overlays, watermarks, or brand logos in the prompt.

**Prompt anti-patterns:**

- "Stunning", "gorgeous", "beautiful" — vague, the model ignores them
- "Highly detailed, 8K, masterpiece" — generic quality spam
- "In the style of [photographer]" — unpredictable results
- Negative prompts — Higgsfield doesn't support these. Phrase
  everything as positive instructions.

**Example prompt (Fig & Bloom):**

```
Candid iPhone photograph of a young woman in a casual white linen
dress, smiling naturally while holding a large bouquet of soft pink
roses, white chrysanthemums, eucalyptus, and baby's breath. The
bouquet is wrapped in white tissue paper and tied with a black satin
ribbon. She is standing against a clean white rendered wall with
trailing green foliage overhead. Soft natural daylight, no flash, warm
colour temperature. The bouquet is the visual hero of the image,
occupying at least a third of the frame. Shallow depth of field, clean
uncluttered background, true-to-life flower colours. The mood is warm,
genuine, and accessible — like a real moment captured on a phone, not
a fashion editorial. Shot at eye level, three-quarter body framing.
```

### Phase 3: Hand Off to Higgsfield

Pass the constructed prompt and parameters to the `higgsfield-api` skill
for generation. Specify:

- Model: Nano Banana Pro
- Prompt: the constructed prompt from Phase 2
- Resolution: `2K` (or `4K` if brief requires hero/print quality)
- Aspect ratio: as determined in Phase 1

IF the `higgsfield-api` skill reports `nsfw` → review the prompt for
unintended triggers. Remove references to clothing fit, skin exposure,
or body shape. Focus on the product (flowers). Rephrase and resubmit.

IF `failed` → retry once with the same prompt. If repeated, simplify
(reduce complexity, shorten). After 3 total failures, escalate.

### Phase 4: Self-Review

Before delivering generated images, assess against the brand rubric.

For each generated image, check:

1. **AI artefacts** — warped hands, impossible reflections, uncanny
   textures, inconsistent shadows. IF found → adjust prompt, regenerate.
2. **Rubric alignment** — does the image match the lighting, colour,
   composition, and mood in the rubric? IF off → identify which
   dimension failed, adjust the relevant prompt section, regenerate.
3. **Brief compliance** — does the image match what was requested?
   IF not → adjust prompt, regenerate.

**Quality gate:** Do not deliver images with obvious AI artefacts
(hands, faces, impossible physics). These undermine brand trust.

IF image passes self-review → deliver.
IF partially passes with minor issues → deliver with notes.

### Phase 5: Output

Deliver generated images with metadata:

```markdown
## Generated Image: [sequence number]

**Prompt used:**
[Full prompt text]

**Parameters:**
- Model: Nano Banana Pro
- Resolution: [resolution]
- Aspect ratio: [aspect_ratio]

**Self-review:**
- AI artefacts: [none / noted: description]
- Rubric alignment: [pass / partial: notes]
- Brief compliance: [pass / partial: notes]

**Verdict:** [Ready to use / Review recommended / Regenerate]
```

For batches, include a summary:

```markdown
## Generation Summary

- **Total generated:** [n]
- **Ready to use:** [n]
- **Review recommended:** [n]
- **Regenerated / discarded:** [n]
```

## Scene Templates

Pre-built prompt skeletons for common UGC scenarios. Always overlay the
brand rubric before submitting.

### Person + Bouquet (Indoor)

```
Candid iPhone photograph of a [age/description] [person] holding a
[bouquet description with specific flowers]. The bouquet is wrapped
in [wrapping description]. [Person] is standing/sitting in [indoor
setting]. Soft natural window light, no flash. [Colour palette from
rubric]. The bouquet is the hero of the image. Shallow depth of field,
clean background. [Mood from rubric]. [Framing instruction].
```

### Person + Bouquet (Outdoor)

```
Natural lifestyle photo shot on smartphone of a [person description]
holding a [bouquet description] while [action] in [outdoor setting].
Overcast natural daylight OR golden hour light. [Colour palette].
Bouquet prominent in frame. [Mood]. Background is [simple/clean].
Three-quarter or full-body framing.
```

### Product Only (Styled)

```
Overhead iPhone photograph of a [bouquet description] resting on
[surface — boucle chair, linen tablecloth, marble benchtop, wooden
stool]. [Wrapping details]. Soft ambient light from [direction].
[Colour palette]. The bouquet fills [proportion] of the frame.
Styled but not fussy — [one or two props]. Clean composition. [Mood].
```

### Detail / Close-Up

```
Close-up smartphone photograph of [specific flower detail — rose
petals, eucalyptus leaves, ribbon tie, branded sticker]. Shallow
depth of field, soft natural light. [Colour palette]. Macro-style
framing showing texture and colour. Background softly blurred. No
text, no overlays.
```

## Edge Cases & Recovery

- **Rubric not available:** Do not generate. The rubric IS the prompt
  engine. Without it, you are guessing.
- **NSFW rejections on innocent prompts:** Nano Banana Pro's filter
  can be sensitive to body descriptions. Remove references to clothing
  fit, skin exposure, or body shape. Focus prompt on the product and
  setting. Describe the person minimally: "a young woman" not detailed
  physical descriptions.
- **Repeated hand artefacts:** Try: (a) tighter crop excluding hands,
  (b) describe bouquet as "resting in arms" not "held," (c) switch to
  product-only template.
- **Colour drift:** Add explicit hex values or more specific colour
  names. "Blush pink (#F4C2C2)" is more precise than "soft pink."
- **Credit budget:** Nano Banana Pro costs ~2-5 credits per generation.
  Flag if a batch is projected to exceed 50 credits.

## Quality Criteria

An excellent generation session:

- First generation is close to brief — minimal regeneration needed
- Generated images would pass `photography-ugc-review` with APPROVE
  or COMMENT (never REJECT)
- AI artefacts are caught in self-review, never delivered as ready
- Images feel like real UGC, not AI stock photography
- Prompt metadata is preserved for reuse and refinement

## Anti-Patterns

- **Over-prompting:** Too many rubric details in one prompt produces
  confusion. Priority order: subject > lighting > colour > mood >
  technical. Drop styling details before dropping these.
- **Generic quality spam:** "masterpiece, best quality, ultra HD" adds
  nothing. Be specific about what you want.
- **Editorial prompts for UGC:** "Professional fashion photography,
  studio lighting, Vogue editorial" is the opposite of UGC. Prompt
  for smartphone, candid, real moments.
- **Ignoring the rubric:** The rubric is not optional context. Every
  prompt must be built from the rubric's standards.
- **Delivering artefacted images:** Never deliver images with warped
  hands, impossible physics, or uncanny faces.
- **Burning credits on bad prompts:** If generation misses, diagnose
  which prompt element caused the miss. Adjust, then regenerate.
