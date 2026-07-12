# Backlink Critic Calibration Batch Design

Use this when preparing Daniel-facing Phase 1 / QA review batches for backlink critic training.

## Core lesson

A training batch is not just “the next N critic outputs.” Daniel is calibrating whether the critic can safely approve outreach, so the batch should contain cards that could plausibly pass — especially low-risk `approve_send_candidate` cases — not obvious deterministic rewrite/fail cases.

## Batch selection rules

1. **Prioritise plausible-pass candidates.** Prefer cards where the current critic decision is `approve_send_candidate`, risk is `low`, confidence is high, and the draft appears customer-facing.
2. **Do not pad to a requested count with known fails.** If Daniel asks for 10 and only 7 plausible-pass cards exist, return 7 and say that the board currently has only 7 plausible-pass candidates.
3. **Exclude deterministic rewrite cards from approval-training digests.** Cards already classified as `revise_then_send` because of non-human/domain-slug greetings, stale Fig & Bloom assets, placeholders, or internal-note leakage should go to rewrite operations, not Daniel approval calibration.
4. **Use borderline cases deliberately.** Include escalations or wait-for-draft cases only when the user asks for broader critic calibration or when they are genuinely ambiguous.
5. **State the digest purpose.** Label whether the batch is for approval calibration, rewrite triage, escalation review, or general critic QA.

## Anti-pattern from calibration

Do not present a digest where most cards are already labelled by the critic as non-passable while implying Daniel should be passing them. That wastes Daniel’s review time and confuses the Phase 1 goal.

## Correct response when there are fewer candidates than requested

Say something like:

```text
I found 7 current plausible-pass candidates, not 10. I’m not padding the batch with obvious fails. Here are the 7 low-risk approve candidates.
```

Then provide only those candidates with stable digest ID and direct Trello links.
