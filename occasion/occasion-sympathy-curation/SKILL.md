---
name: occasion-sympathy-curation
description: Build and review sympathy, get-well, bereavement, and care occasion collections for Solace. Use for occasion collection curation, bereavement tone review, sympathy product selection, funeral-director outreach inputs, and sensitive customer journey checks.
---

# Sympathy and Care Occasion Curation

This skill helps Solace build emotionally literate occasion collections and messaging for moments where careless copy can harm trust.

## Trigger

Use when work involves:

- sympathy, bereavement, funeral, hospice, miscarriage, illness, recovery, or get-well collections;
- grief-literacy content;
- product selection for sensitive occasions;
- B2B funeral or care-sector outreach;
- tone review for sympathy emails, landing pages, cards, ads, or PR.

Always run `reference-brand-voice-guardrail` and, for outreach or public claims, `reference-pr-ethics-guardrail`.

## Principles

- Be useful, not comforting-by-default.
- Do not assume the relationship, faith, cause of death, prognosis, or emotional state.
- Do not brighten grief with cheerful framing.
- Keep CTAs practical: send care, choose a gesture, include a note.
- Give the sender confidence without claiming flowers fix anything.
- Prefer plain product names and restrained descriptions.

## Collection Workflow

1. Define the occasion and sensitivity level.
2. Select products by gesture job:
   - quiet condolence;
   - home care;
   - hospital or recovery;
   - funeral service;
   - ongoing support after the first week.
3. Remove products that feel too celebratory, loud, romantic, or logistically risky.
4. Check delivery constraints: hospital rules, funeral timing, card wording, substitutions, delivery notes.
5. Write collection guidance:
   - who it is for;
   - when to send;
   - what to write;
   - what to avoid.
6. Run tone review.

## Bereavement Tone Review

Flag and rewrite:

- `thinking of you in this difficult time` if overused without specificity;
- bright-side lines;
- `celebrate their life` unless context is known;
- `at least`, `everything happens`, or faith-based assumptions;
- sales urgency;
- excessive adjectives;
- exclamation marks.

## Funeral and Care Outreach Inputs

For funeral directors, hospices, or bereavement organisations:

- state the service plainly;
- avoid implying endorsement before agreement;
- focus on reducing sender friction and improving care;
- document referral terms, privacy handling, fulfilment constraints, and support owner.

## Output Format

```markdown
# Occasion Collection Spec - [Occasion]

## Occasion Standard
[audience, sensitivity, promise, exclusions]

## Product Set
[product, role, why it fits, risks]

## Copy Guidance
[collection intro, PDP guidance, card prompts, CTAs]

## Journey Notes
[email/SMS/site/support touchpoints]

## Outreach Inputs
[if B2B funeral/care outreach applies]

## Tone Review
[pass/fail table and required edits]
```

## Quality Gates

- No cheerful, assumptive, religious, or fixing language.
- Product selection matches the emotional and logistical context.
- Funeral/care outreach has privacy and endorsement guardrails.
- Banned words and exclamation marks are removed.
