---
name: creative-copy-qa
description: Paperclip creative workflow for Copy QA. Use this skill when you need to review customer-facing copy for brand voice, clarity, and tone compliance before approval.
---

# Copy QA

You are the tonal gatekeeper for Fig & Bloom. This skill gives you a structured process for evaluating any piece of customer-facing copy against the brand's voice standards. Your job is to catch drift before it reaches the customer.

## When to use this skill

- Copywriter submits copy for review
- You're self-checking before handing off to a media buyer or email specialist
- Brand audit — reviewing live copy across channels
- Any agent asks you to validate written content

## Dependencies

This skill references the **brand-guidelines-manager** skill for the canonical tone of voice rules. If in doubt on any rule, consult that skill first.

---

## Voice standard (quick reference)

These are the filters. Memorise them — every review passes through all six.

### The voice is:

1. **Warm** — Feels like a thoughtful friend, not a brand talking at you
2. **Intentional** — Every word earns its place. No padding, no filler
3. **Quietly confident** — Knows its worth without shouting about it
4. **Australian English** — Spelling, idiom, and cultural register
5. **Identity-affirming** — Makes the reader feel seen as someone who lives beautifully
6. **Emotionally led** — Sells the feeling, not the feature

### The voice is never:

- Salesy, hype-driven, or urgency-for-its-own-sake
- American English (color → colour, customize → customise, etc.)
- Generic or transactional ("Buy now!", "Don't miss out!", "Limited stock!")
- Over-descriptive or adjective-heavy
- Feature-led ("Our bouquets contain 12 stems of premium roses")
- Performatively cheerful or forced

---

## Review process

### Step 1: Identify context

Before reviewing, confirm:

- **Format** — What is this? (ad headline, email body, product description, social caption, etc.)
- **Persona** — Who is it speaking to? (Gratitude Expressor, Romantic Giver, Self-care Enthusiast, Thoughtful Gift Giver, Space Transformer, Host/Event Organiser, Corporate Client Buyer)
- **Channel** — Where will it appear? (Meta ad, Google ad, Klaviyo email, Instagram, website PDP, etc.)
- **Campaign** — Is it tied to a seasonal or thematic campaign?

If any of these are unclear, ask before reviewing.

### Step 2: Run the six filters

Evaluate the copy against each voice filter. For each, assign one of:

| Rating   | Meaning                                  |
| -------- | ---------------------------------------- |
| ✅ Pass   | Meets the standard                       |
| ⚠️ Drift | Partially off — fixable with minor edits |
| ❌ Fail   | Materially off-brand — needs rework      |

### Step 3: Check specifics

Beyond the six filters, check for:

- **Spelling** — Australian English throughout (colour, organised, centre, etc.)
- **Tagline integrity** — "For Moment Makers" not modified or paraphrased
- **Brand name** — "Fig & Bloom" — ampersand, not "and". Capital F, capital B.
- **Persona alignment** — Does the messaging hook match the target persona?
- **CTA tone** — CTAs should feel inviting, not pushy. Prefer "Make their day" over "Buy now". Prefer "Treat yourself" over "Shop the sale".
- **Discount framing** — Offers framed around emotion/intention, never price savings. No percentage discounts as default. Use credit, exclusivity, or bundled value.
- **Word economy** — Flag any sentence that could lose 30%+ of its words without losing meaning

### Step 4: Produce the review

Output a structured review in this format:

```
## Copy QA Review

**Item:** [what's being reviewed]
**Persona:** [target persona]
**Channel:** [where it appears]

### Filter results

| Filter              | Rating | Notes                          |
|---------------------|--------|--------------------------------|
| Warm                | ✅/⚠️/❌ | [specific observation]        |
| Intentional         | ✅/⚠️/❌ | [specific observation]        |
| Quietly confident   | ✅/⚠️/❌ | [specific observation]        |
| Australian English  | ✅/⚠️/❌ | [specific observation]        |
| Identity-affirming  | ✅/⚠️/❌ | [specific observation]        |
| Emotionally led     | ✅/⚠️/❌ | [specific observation]        |

### Specifics

[Flag any issues from Step 3 checks]

### Verdict

**Approved** / **Approved with edits** / **Rework required**

### Suggested edits

[If Approved with edits or Rework required, provide specific rewrites —
not just "make it warmer", but the actual rewritten copy.]
```

---

## Severity and escalation

- **Approved** — Ship it. No changes needed.
- **Approved with edits** — Minor drift. Apply the suggested edits and it's ready. No second review needed unless the edits are substantial.
- **Rework required** — Materially off-brand. Return to the Copywriter (or whoever submitted it) with the review and suggested direction. Requires a second review after rework.

If the same drift pattern appears across multiple pieces from the same source, flag it to the MarketingManager as a systemic issue — don't just fix it piece by piece.

---

## Common drift patterns

These are the most frequent ways Fig & Bloom copy goes off-brand. Watch for them:

| Pattern               | Example                                             | Fix                                                                     |
| --------------------- | --------------------------------------------------- | ----------------------------------------------------------------------- |
| American English      | "colorful bouquet"                                  | "colourful bouquet"                                                     |
| Urgency spam          | "HURRY! Only 3 left!"                               | Remove. If scarcity is real, state it once, calmly.                     |
| Feature-leading       | "12 premium long-stem roses in a signature box"     | Lead with the feeling: "A gesture that says everything."                |
| Generic CTA           | "Shop Now" / "Buy Today"                            | "Make their day" / "Send something beautiful"                           |
| Adjective stacking    | "stunning, breathtaking, gorgeous arrangement"      | Pick one. Or none — let the image do the work.                          |
| Salesy framing        | "Save 20% this weekend only!"                       | "A little something on us — $20 credit for your next bloom moment."     |
| Performative warmth   | "We're SO excited to share this with you!!!"        | Dial it back. Quiet confidence. One exclamation mark maximum per piece. |
| Passive voice padding | "Your order will be carefully prepared by our team" | "We prepare every order with care."                                     |

---

## Batch review mode

When reviewing multiple pieces at once (e.g. a full campaign's ad copy set), use a summary table:

```
| # | Item                    | Verdict              | Key issue              |
|---|-------------------------|----------------------|------------------------|
| 1 | Meta headline - gifting | ✅ Approved           | —                      |
| 2 | Meta primary text       | ⚠️ Approved w/ edits | American spelling ×2   |
| 3 | Google RSA headline set | ❌ Rework             | Feature-led, no emotion|
```

Then provide detailed reviews only for items rated ⚠️ or ❌.

---

## Self-check mode

When you (the BrandManager) have written copy yourself, run the same process. Don't skip it because you wrote it. Use the six filters, check the specifics, and document the result. If you catch drift in your own work, fix it before handing off.

<!--
Version log:
- 2026-04-11: Initial SKILL.md created
-->
