# Hashgifted Workflow Build State

_Last updated: 2026-05-11 12:30 AEST_

## Current objective

Finish the Hashgifted operator skill suite for Fig & Bloom creator gifting workflows. Keep skills portable by writing business workflows against the `reference-browser-operator` vocabulary, with concrete UI details living in `hashgifted-browser-adapter-map` references.

## Source-of-truth assets

- Skills repo: `/opt/data/workspace/dgroch-skills`
- Ops manager: `operations/hashgifted-ops-manager/SKILL.md`
- Browser operator reference: `reference/reference-browser-operator/SKILL.md`
- Hashgifted adapter map: `operations/hashgifted-browser-adapter-map/`
- Notion UGC Hub page: `35bfdc24-425f-80b1-99df-ea0d2b615ab9`
- Notion data sources:
  - Campaigns: `a8602813-2cca-4f84-8c99-fad58b5c014b`
  - Briefs: `cc0a447f-7d17-4f26-9d2f-dcf007549a7a`
  - Creators: `221846a5-866d-43ef-bb19-6883fe1c2bdb`

## Architecture note: creator communications

Creator communications were anticipated in the existing scaffold, primarily inside `hashgifted-creator-select` for selection messages, reply nudges, Q&A, eligibility checks, and brief-option follow-ups. Closeout belongs in `hashgifted-creator-close`; content/story capture have their own skills. Do not add a separate generic creator-communications skill unless the message surface expands beyond these lifecycle-bound interactions.

Current communication guardrails:

- `assist` mode drafts creator messages and pauses for Daniel approval before sending.
- `auto` mode may send only after explicit promotion to auto and only for approved high-confidence answer classes.
- Escalate unhappy/damaged/missing flowers, payment, extensions, product swaps, and negative-review risk.
- Fig & Bloom campaigns are deliverable only to Melbourne, Sydney, and Brisbane metro areas; final selection requires explicit metro eligibility confirmation in-thread.

## Notion state verified

Briefs exist and have public links populated:

- `Guess I Really Am Loved`
  - Public URL: `https://abrupt-paneer-687.notion.site/Guess-I-Really-Am-Loved-35bfdc24425f81459e0cdb914e0e9791`
- `You Weren't Expecting Flowers`
  - Public URL: `https://abrupt-paneer-687.notion.site/You-Weren-t-Expecting-Flowers-35bfdc24425f81bb89fbd0055a34c216`

Campaigns data source is visible to the Notion integration, but currently has zero rows as of this check. Schema fields:

- `Campaign Name`
- `Status`
- `Hashgifted URL`
- `Briefs`
- `Creators`
- `Hard Gates`
- `Deliverables`
- `Target Selected`
- `Deadline Window`
- `Posting Deadline`
- `Notes`
- `Created`

## Hashgifted browser state verified

- Navigating to `https://brands.hashgifted.com/` in the default Hermes browser redirected to signup/login flow, not an authenticated dashboard.
- Starting a fresh Browserbase session without a saved Hashgifted context also showed the public signup page.
- Current runtime environment exposes `BROWSERBASE_API_KEY`, but no `BROWSERBASE_HASHGIFTED_CONTEXT_ID` was present in the live process environment or `/opt/data/.env` during this check.
- Therefore Hermes cannot yet see live Hashgifted campaigns unless one of these is provided:
  1. A campaign `gift-view` URL, plus an authenticated browser/session for that URL; or
  2. A saved Browserbase context ID for a logged-in Hashgifted brand session; or
  3. Hashgifted login credentials/manual browser takeover to establish auth state.

## Safe next steps

1. Capture Hashgifted access:
   - Ask Daniel for the relevant campaign `gift-view` URL(s), or have him paste them into `Campaign.Hashgifted URL` in Notion.
   - Establish a persistent authenticated browser context and store its ID as `BROWSERBASE_HASHGIFTED_CONTEXT_ID`.
   - Re-run a read-only campaign discovery pass.

2. Sync Notion Campaign rows:
   - If live Hashgifted campaigns exist but Notion Campaigns is empty, create one Campaign row per live campaign.
   - Link the two published Brief rows where relevant.
   - Fill `Hashgifted URL`, `Target Selected`, `Deadline Window`, hard gates, and deliverables.

3. Finish/refine skill suite in this order:
   - `hashgifted-browser-adapter-map`: add dashboard/campaign-list discovery observations once authenticated access works.
   - `hashgifted-campaign-init`: patch now that the Notion API exposes `public_url` after manual publish; agent can fill `Brief.Public Link` automatically after Daniel flips Share-to-web.
   - `hashgifted-creator-shortlist`: validate against a real applicant list in plan/dry-run mode only.
   - `hashgifted-creator-select`: keep approval-gated; no selecting without Daniel confirmation.
   - `hashgifted-creator-monitor`: dispatch lifecycle tasks from Campaign rows with `Hashgifted URL` populated.
   - Add missing skills: `hashgifted-content-capture`, `hashgifted-creator-close`, `hashgifted-story-capture`.

## Guardrails

- Do not click `Decline`, `Select`, `Send message`, `Mark complete`, `Stop applications`, or campaign status controls without explicit approval.
- Read-only inspection should avoid clicking applicant rows when possible, because the UI may mark applicants as read.
- Screenshot or structured-read evidence is required before and after any high-risk browser action.
- Never invent campaign state. If Hashgifted auth is absent, report that campaigns are not visible from the agent runtime.
