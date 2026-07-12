# Phase 1 calibration feedback patterns

Use this reference when operating or improving the backlink critic approval loop from Daniel feedback.

## What Phase 1 review batches should contain

Daniel's time should be spent on decisions that could plausibly change behaviour:

- Prioritise current `approve_send_candidate` cards where the critic believes the draft is low-risk and sendable.
- Include borderline escalations only when the question is genuinely useful: "is the critic too cautious or correctly cautious?"
- Do **not** ask Daniel to review cards the critic already classifies as deterministic `revise_then_send` failures unless explicitly requested. Those are rewrite work, not good approval-training cards.
- If fewer than 10 plausible-pass cards exist, say so and provide the smaller honest set. Do not pad the batch with obvious fails.

## Approval vs training labels

- A `pass` on a Phase 1 digest is a calibration label, not a send event.
- Tick send approval gates only when Daniel explicitly asks to progress eligible passed cards, and only for actual send drafts.
- Never tick gates for `request_or_wait_for_draft` decisions or cards with no visible outreach draft.

## Daniel's repeated fail patterns

Treat these as approval blockers unless Daniel explicitly relaxes them:

1. **Non-human / domain-based greetings**
   - Bad: `Hi Mumsoftheshire team`, `Hi Betterbuilthomes team`.
   - Good: use a named person when known; otherwise use a human-readable outlet/team name.
2. **Stale or irrelevant Fig & Bloom source assets**
   - Reject outreach pushing old 2019/2020 seasonal Fig & Bloom blog posts, especially Valentine's Day/Father's Day/Mother's Day assets, as replacements for stale external guides.
   - Require a current, relevant asset or rewrite.
3. **Missing collaborative offer**
   - Even when a draft passes, note whether it lacks a soft offer to help with a guest paragraph, expert florist quote, practical tip, or other useful contribution.
   - Prefer drafts that sound collaborative rather than a resource-drop.
4. **Internal artifact leakage**
   - Hard fail if the customer-facing draft includes `CRITIC VERDICT`, JSON, word counts, parser notes, Trello/control-plane text, or anything that looks like agent metadata.
5. **Robotic scraped-context prose**
   - Hard fail if the opening reads like pasted card/context metadata rather than a human note from Dan.

## How to respond to user frustration

If Daniel asks why a batch contains obvious fails, acknowledge the workflow error directly and fix the filtering. The correct next action is to generate a plausible-pass batch, not to defend the generic digest logic.
