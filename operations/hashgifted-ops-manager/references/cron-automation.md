# Hashgifted Cron Automation

Use this reference when registering or running unattended Hermes cron jobs for the Hashgifted lifecycle.

## Default Policy

### New applicants / not-shortlisted candidates

Treat Applied candidates as a triage queue, not a conversation queue.

- Automatically shortlist high-confidence brand-fit creators in open campaigns after live Gifted/Hashgifted readback.
- Leave `maybe`, weak-fit, incomplete-evidence, or low-confidence creators in Applied/manual-review state. Do **not** message them just to see whether they can be qualified; selection qualification happens only after shortlist.
- Do **not** automatically decline normal weak-fit candidates while campaigns are still open unless Daniel has explicitly enabled auto-decline for this run/campaign.
- Only propose auto-decline for very clear hard blockers or brand-safety issues, and even then report them as `decline_candidates` unless the cron prompt explicitly says `auto_decline_hard_blockers=true`.
- When a campaign is closed/full/wrapping, generate a cleanup plan for stale Applied rows, grouped by reason, but do not send closeout messages or decline in bulk without explicit approval.

Rationale: shortlisting is recoverable and non-communicative; decline is terminal and can remove a future reserve creator. Conversation before shortlist creates low-quality threads and trains creators to negotiate before we know brand fit.

### Shortlisted replies / selection

Treat Shortlisted candidates as a conversation and qualification queue.

- Re-read every live Shortlisted thread before deciding.
- Reply to high-confidence, answerable questions using the approved answer bank.
- Ask only for missing qualification gates: Melbourne/Sydney/Brisbane metro, IG Reel acceptance, and brief preference/understanding.
- Select only fully qualified creators and only inside the configured cadence.
- For the current Marseille/Savoie/Umbria bouquet round: max 2 selections per campaign per week, global cap 6/week, creators may choose either public brief.
- Leave cadence-overflow qualified creators as reserve; do not decline them.
- Route escalations, ambiguous replies, unhappy/damaged-flower messages, payment requests, deadline-extension requests, or product-change requests to manual review.

## Recurring Jobs

Register separate recurring cron jobs rather than one monolith:

1. `hashgifted-new-applicant-shortlist-sweep`
   - Frequency: daily during campaign intake, normally around Melbourne morning.
   - Purpose: find new Applied/SUBMITTED applicants across active/open Hashgifted campaigns, visually/API-assess enough evidence, auto-shortlist high-confidence fits, and report manual review/decline candidates.
   - Side effects allowed: Shortlist high-confidence fits only. No messages. No auto-declines unless explicitly configured.

2. `hashgifted-shortlisted-reply-selection-sweep`
   - Frequency: every 2 hours during active outreach windows.
   - Purpose: inspect Shortlisted threads, reply to creators, send missing-gate follow-ups, nudge eligible no-replies, and select fully qualified creators within cadence.
   - Side effects allowed: creator replies and selections when high-confidence and within cadence. Decline only for explicit creator negatives post-shortlist; otherwise report manual review.

3. `hashgifted-content-capture-sweep`
   - Frequency: every 4 hours during active campaigns.
   - Purpose: detect creator-produced content, save media/evidence to Google Drive, index assets into the Notion asset manifest, thank the creator, mark complete where deliverables are satisfied, leave creator review, and prepare a media-buyer handoff for Meta ads.
   - Side effects allowed: capture/index assets and send a thank-you only after the content is verified and saved. Mark complete only after deliverable evidence is present. Creator review and media-buyer handoff should be conservative and evidence-backed.

## Cron Prompt: New Applicant Shortlist Sweep

```text
You are running unattended as a Hermes cron job for Daniel's Fig & Bloom Hashgifted workflow. Do not ask questions; make conservative autonomous decisions and report results back to Daniel.

Load and follow Fig & Bloom/Hashgifted rules from:
- /opt/data/workspace/dgroch-skills/operations/hashgifted-ops-manager/SKILL.md
- /opt/data/workspace/dgroch-skills/operations/hashgifted-ops-manager/references/lifecycle.md
- /opt/data/workspace/dgroch-skills/operations/hashgifted-ops-manager/references/cron-automation.md
- /opt/data/workspace/dgroch-skills/operations/hashgifted-creator-shortlist/SKILL.md
- /opt/data/skills/business-development/fig-bloom-operations/references/hashgifted-influencer-shortlisting.md
- /opt/data/skills/productivity/notion/references/hashgifted-notion-access.md

Notion campaign discovery:
- Load `/opt/data/.env` before Notion API calls; never print secrets.
- Use Notion API version `2025-09-03`.
- Query Campaigns with the data source endpoint: `POST /v1/data_sources/a8602813-2cca-4f84-8c99-fad58b5c014b/query`.
- Verified IDs: UGC Hub page `35bfdc24-425f-80b1-99df-ea0d2b615ab9`; Campaigns data source `a8602813-2cca-4f84-8c99-fad58b5c014b`; Briefs data source `cc0a447f-7d17-4f26-9d2f-dcf007549a7a`; Creators data source `221846a5-866d-43ef-bb19-6883fe1c2bdb`.
- If Notion returns 404, treat it as target integration access or wrong endpoint/version, then fall back to the known current campaign set plus live Gifted rows. Do not create duplicate Campaigns databases.

Task:
1. Discover active/open Fig & Bloom Hashgifted campaigns from the known current campaign set and/or Notion Campaigns DB if available.
2. Fetch live Gifted/Hashgifted wave rows via the authenticated producer API. Use Gifted/Hashgifted as source of truth.
3. Inspect all new Applied/SUBMITTED applicants not already actioned.
4. Shortlist high-confidence brand-fit creators. Broadly shortlist valid fit; do not cap at 3–5.
5. Leave maybe/low-confidence rows for manual review. Do not message Applied candidates.
6. Do not auto-decline unless there is an explicit hard blocker/brand-safety issue and auto-decline has been separately enabled; otherwise list decline candidates only.
7. Verify all mutations by re-fetching live campaign rows.
8. Return concise counts by campaign: reviewed, shortlisted, left applied/manual-review, decline candidates, warnings, audit artifact paths.
```

## Cron Prompt: Shortlisted Reply / Selection Sweep

```text
You are running unattended as a Hermes cron job for Daniel's Fig & Bloom Hashgifted workflow. Do not ask questions; make conservative autonomous decisions and report results back to Daniel.

Load and follow Fig & Bloom/Hashgifted rules from:
- /opt/data/workspace/dgroch-skills/operations/hashgifted-ops-manager/SKILL.md
- /opt/data/workspace/dgroch-skills/operations/hashgifted-ops-manager/references/lifecycle.md
- /opt/data/workspace/dgroch-skills/operations/hashgifted-ops-manager/references/cron-automation.md
- /opt/data/workspace/dgroch-skills/operations/hashgifted-creator-select/SKILL.md
- /opt/data/workspace/dgroch-skills/operations/hashgifted-creator-select/references/selection-message-template.md
- /opt/data/workspace/dgroch-skills/operations/hashgifted-creator-select/references/reply-classification.md
- /opt/data/skills/business-development/fig-bloom-operations/references/hashgifted-influencer-shortlisting.md

Task:
1. Fetch live Gifted/Hashgifted rows for active Fig & Bloom campaigns, including SHORTLISTED, ACCEPTED, COMPLETED, REJECTED, SUBMITTED/NEGOTIATION as needed for context.
2. For every Shortlisted creator, read the full thread before deciding.
3. If no initial outreach has been sent, send the approved soft creative-direction qualification message with public Notion brief links.
4. If our last message has no inbound reply and timing qualifies, send +3 day or +7 day nudge.
5. If latest inbound is high-confidence answerable, reply from the approved answer bank.
6. If latest inbound is positive but missing gates, ask only for missing gates.
7. If latest inbound fully confirms metro eligibility, IG Reel acceptance, and brief preference/understanding, select the creator only if the campaign/week cadence allows it. Current bouquet cadence: max 2 selected per campaign per week; global max 6/week.
8. If cadence is full, leave qualified creators as reserve and report them.
9. If latest inbound is explicit negative, mark declined post-shortlist; do not send further messages.
10. If ambiguous/escalated/payment/extension/product issue/unhappy/damaged flowers, report manual review and do not respond.
11. Verify sends with exact readback and selections by live row status re-fetch.
12. Return concise counts by campaign: messages sent by type, selected, declined, reserves, manual review, failures, warnings, audit artifact paths.
```

## Cron Prompt: Content Capture Sweep

```text
You are running unattended as a Hermes cron job for Daniel's Fig & Bloom Hashgifted workflow. Do not ask questions; make conservative autonomous decisions and report results back to Daniel.

Load and follow Fig & Bloom/Hashgifted rules from:
- /opt/data/workspace/dgroch-skills/operations/hashgifted-ops-manager/SKILL.md
- /opt/data/workspace/dgroch-skills/operations/hashgifted-ops-manager/references/lifecycle.md
- /opt/data/workspace/dgroch-skills/operations/hashgifted-ops-manager/references/cron-automation.md
- /opt/data/skills/business-development/fig-bloom-operations/SKILL.md
- /opt/data/skills/business-development/fig-bloom-operations/references/hashgifted-influencer-shortlisting.md
- /opt/data/skills/business-development/fig-bloom-operations/references/brand-asset-manifesting.md

Task:
1. Fetch live Gifted/Hashgifted rows for active Fig & Bloom campaigns and identify Selected/Accepted creators with new post/reel/content evidence in Hashgifted's completed gallery or verified thread links.
2. For each new content item, verify creator identity, campaign, deliverable type, source URL, posted date if available, and whether it satisfies the agreed brief/deliverable.
3. Save the media file or best available evidence to Google Drive in the Fig & Bloom UGC/Hashgifted asset structure. Preserve source URLs, thumbnails/screenshots, captions, creator handle, campaign, brief, and capture timestamp.
4. Index the saved asset into the Notion asset manifest / UGC hub with provenance, rights/source context, campaign relation, creator relation when available, and Meta-ad readiness notes.
5. If all agreed deliverables are captured and indexed, send a warm thank-you to the creator and mark the creator/campaign row complete in Hashgifted/Notion. If evidence is partial, do not mark complete; report what is missing.
6. Leave a creator review based only on evidence: deliverables met, content quality/emotional fit, responsiveness, and timeliness. Use conservative scoring; flag Daniel for review before excluding or promoting Preferred unless policy explicitly allows it.
7. Prepare a media-buyer handoff for Meta ads: asset links, creator handle, campaign/brief, hook/angle summary, usage caveats, and recommended next action. If a direct destination/channel is unavailable, write the handoff to an audit artifact and report it.
8. Verify Drive upload/readback, Notion record readback, thank-you exact message readback, and completion status re-fetch.
9. Return concise counts by campaign: new content detected, assets saved, Notion rows created/updated, creators thanked, marked complete, review scores, media-buyer handoffs, manual review, failures, warnings, audit paths.

Important: never print secrets. If credentials or auth are missing, report the missing capability and stop safely. Do not invent content or mark complete from a creator's claim alone; require Hashgifted gallery evidence, direct source media, or verified link evidence.
```

## Reporting Format

Cron jobs should return Telegram-friendly bullets, not tables:

- Window/run timestamp
- Campaign counts
- Actions taken
- Manual review items with handle + reason
- Cadence/reserve status
- Audit paths
- Warnings / next required human decision
