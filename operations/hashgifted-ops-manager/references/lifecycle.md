# Hashgifted Lifecycle

Use this when deciding what action is due for a campaign or creator.

## Campaign Setup

Use `hashgifted-campaign-init` when no campaign exists yet or the marketer asks to start a new gifting round.

Required campaign inputs:

- Campaign name.
- Objective: audience awareness, content library, or both.
- Hard gates: location, follower minimums, platform, exclusions. For Fig & Bloom, delivery location is limited to Melbourne, Sydney, and Brisbane metro areas.
- Deliverables as free text.
- Target selected count.
- Posting deadline, defaulting to 7 days from receipt of gift unless overridden.
- One or two concepts with emotional arc and visual moment.
- One-off calibration notes.

Do not accept a vague one-line concept. Ask for the feeling, the visual moment, and the story arc.

## Creator State Machine

Apply in order; first match wins.

| State | Action |
| --- | --- |
| Applied, not reviewed | Dispatch `hashgifted-creator-shortlist` |
| Shortlisted, not yet contacted for selection | Dispatch `hashgifted-creator-select` |
| Selection message sent, no creator reply, +3 days | Dispatch gentle nudge |
| Selection message sent, no creator reply, +7 days | Dispatch final reply nudge |
| Selection message sent, no creator reply, +10 days | Dispatch `hashgifted-creator-close` with ghost path |
| Creator confirms Melbourne/Sydney/Brisbane metro eligibility and agrees to messaging, deliverables, and deadline | `hashgifted-creator-select` may mark Selected |
| Selected, no post detected, deadline -2 days | Dispatch deadline reminder |
| Selected, past deadline, no post, +7 days | Dispatch final deadline nudge |
| Selected, past deadline, no post, +10 days | Dispatch `hashgifted-creator-close` with ghost path |
| Story link in thread, not captured | Dispatch `hashgifted-story-capture` immediately |
| New post or reel in completed gallery | Dispatch `hashgifted-content-capture` |
| All deliverables captured, no closeout | Dispatch `hashgifted-creator-close` with delivered path |

## Definitions

- `Posted` means the post or reel appears in Hashgifted's completed gallery. Thread claims are useful signals but not proof.
- `Last Contacted` in Notion is the source of truth for nudge timing.
- `Applied` means the creator has applied in Hashgifted and has not been qualified.
- `Shortlisted` means the creator passed campaign/aesthetic qualification, but has not been contacted or selected.
- `Selected` means the creator has confirmed delivery eligibility and agreed to campaign messaging, required deliverables, and deadlines, then was accepted in Hashgifted.
- `Metro eligible` means the creator confirms they live in Melbourne, Sydney, or Brisbane metro. Inferred profile location is useful for prioritisation but not enough for final selection unless already explicit. A creator “30km out of Brisbane” qualifies as Brisbane metro for profile-inference purposes; apply the same 30km-radius rule to Melbourne/Sydney/Brisbane unless the campaign says otherwise.
- `Captured` means asset is downloaded, organised, synced to public CDN if required, and embedded or logged in Notion.
- `Declined` is available any time before completion, but should be used with clear reason and audit evidence.

## Creator CRM Requirement

Back the whole lifecycle with the Notion Creators DB. Every applicant review should upsert/reuse the creator row and store lifecycle status, location inference/confirmation, campaign relationship, follower/engagement metrics, and visual feed-inspection properties. Do not leave visual judgements only in transient audit logs; they must be queryable later so future campaign applications do not repeat the same work.

Use `references/notion-creator-crm.md` for the canonical creator schema and scripts.

## Notion Operating State

Known UGC hub references:

- UGC hub: `https://www.notion.so/35bfdc24425f80b199dfea0d2b615ab9`
- Briefs DB: `cc0a447f-7d17-4f26-9d2f-dcf007549a7a`
- Creators DB: `221846a5-866d-43ef-bb19-6883fe1c2bdb`
- Campaigns DB: `a8602813-2cca-4f84-8c99-fad58b5c014b`

If a connector cannot access these databases, ask the marketer for the campaign records or continue in `plan`/`dry_run`.

## Closeout Scoring

Score delivered creators 1 to 5 based on:

- Deliverables met.
- Content quality and emotional fit to brief.
- Responsiveness.
- Timeliness.

Set status:

- Score below 3: `Excluded`.
- Score 3 or 4: `Active`.
- Score 5: suggest `Preferred`; do not auto-promote without explicit approval.

Ghost path is silent. Do not send a reproach message.
