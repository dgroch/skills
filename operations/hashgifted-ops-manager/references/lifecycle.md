# Hashgifted Lifecycle

Use this when deciding what action is due for a campaign or creator.

## Campaign Setup

Use `hashgifted-campaign-init` when no campaign exists yet or the marketer asks to start a new gifting round.

Required campaign inputs:

- Campaign name.
- Objective: audience awareness, content library, or both.
- Hard gates: location, follower minimums, platform, exclusions.
- Deliverables as free text.
- Target selected count.
- Target shortlist count if different from selected target.
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
| Creator agrees to messaging, deliverables, and deadline | `hashgifted-creator-select` may mark Selected |
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
- `Selected` means the creator has agreed to campaign messaging, required deliverables, and deadlines, then was accepted in Hashgifted.
- `Captured` means asset is downloaded, organised, synced to public CDN if required, and embedded or logged in Notion.
- `Declined` is available any time before completion, but should be used with clear reason and audit evidence.

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
