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
- Ask only for missing qualification gates: current-round delivery eligibility, IG Reel acceptance, and brief preference/understanding.
- Selection cadence gates only the final `Select`/accept action, not creator communication or qualification. Continue replying to Shortlisted creators, answering approved questions, and confirming gates even when the current week's selection slots are full.
- Select only fully qualified creators and only inside the configured cadence.
- For the current Marseille/Savoie/Umbria bouquet round: max 2 selections per campaign per week, global cap 6/week, creators may choose either public brief.
- Leave cadence-overflow qualified creators as approved/reserve; do not decline them. Send a warm expectation-setting reply when appropriate: confirm they are approved/qualified, explain there is a weekly maximum number of creator gifts, and say we will select them when the next slot is available.
- Route escalations, ambiguous replies, unhappy/damaged-flower messages, payment requests, deadline-extension requests, or product-change requests to manual review.
- When a selected/accepted creator has booked/placed their order, and no equivalent acknowledgement is visible in the thread, send the approved post-selection order acknowledgement from `selection-message-template.md`. This is a proactive quality-control message: thank them, invite questions, and ask them to tell us if flowers arrive below standard so Fig & Bloom can organise re-delivery rather than the creator fulfilling with substandard florals.

### Human-in-loop blocker taxonomy

When a replied Shortlisted creator cannot be selected or declined automatically, report them in one of these explicit buckets so Daniel can unblock lifecycle logic rather than reading raw chats:

- `selectable_now`: all gates are confirmed; only cadence/ranking may delay selection.
- `missing_gate`: positive reply but one gate is absent. Ask only the missing gate; no human decision needed.
- `delivery_outside_confirmed`: creator explicitly says they are outside current approved delivery areas. Escalate to Daniel rather than auto-closing, because delivery policy is evolving.
- `delivery_edge_question`: creator asks if a nearby region works. Current bouquet round approved edge regions: Geelong, Bannockburn, Sunshine Coast, and Gold Coast. Reply with the approved edge-delivery answer and continue qualification for those regions; escalate other regions.
- `product_exception`: creator asks for a vase, different bouquet, payment, or other exception. Requires Daniel approval unless a matching one-off override exists. If an override exists, reply with approval and continue selection.
- `creative_format_question`: creator asks about VO, text-on-screen, caption style, or similar execution detail. Current approved answer: voiceover is optional; text on screen and/or caption is fine, as long as the story is clear and aligned with the brief.
- `negative_but_warm`: creator is interested but cannot participate due to delivery or fit. Close politely and do not keep nudging.

Reports should include recommended next action and the smallest policy question needed to make the same case automatic next time.

## Recurring Jobs

Register separate recurring cron jobs rather than one monolith:

1. `hashgifted-new-applicant-shortlist-sweep`
   - Frequency: daily during campaign intake, normally around Melbourne morning.
   - Purpose: find new Applied/SUBMITTED applicants across active/open Hashgifted campaigns, visually/API-assess enough evidence, auto-shortlist high-confidence fits, and report manual review/decline candidates.
   - Side effects allowed: Shortlist high-confidence fits only. No messages. No auto-declines unless explicitly configured.

2. `hashgifted-shortlisted-reply-selection-sweep`
   - Frequency: every 2 hours during active outreach windows.
   - Purpose: inspect Shortlisted threads, reply to creators, send missing-gate follow-ups, nudge eligible no-replies, qualify creators regardless of cadence fullness, set expectations for approved/reserve creators when slots are full, select fully qualified creators within cadence, and acknowledge selected/accepted creators who have booked/placed their flower order.
   - Side effects allowed: creator replies, qualification/approval/reserve expectation-setting messages, order-booking acknowledgements, and selections when high-confidence and within cadence. Decline only for explicit creator negatives post-shortlist; otherwise report manual review.

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
3. For every Selected/Accepted creator with a booked/placed flower order, read the full thread; if no equivalent order acknowledgement has already been sent, send the approved post-selection order acknowledgement from `selection-message-template.md`. Do not ask for address or delivery details.
4. If no initial outreach has been sent, send the approved soft creative-direction qualification message with public Notion brief links.
5. If our last message has no inbound reply and timing qualifies, send +3 day or +7 day nudge.
6. If latest inbound is high-confidence answerable, reply from the approved answer bank.
7. If latest inbound is positive but missing gates, ask only for missing gates.
8. If latest inbound fully confirms current-round delivery eligibility, IG Reel acceptance, and brief preference/understanding, mark them qualified/approved in the audit state regardless of cadence fullness. Current approved delivery regions: Melbourne/Sydney/Brisbane metro plus Geelong, Bannockburn, Sunshine Coast, and Gold Coast. Edge regions ship by overnight courier in a large box.
9. Select the creator only if the campaign/week cadence allows it. Current bouquet cadence: max 2 selected per campaign per week; global max 6/week.
10. If cadence is full, leave qualified creators as approved/reserve, report them, and send an expectation-setting message if no equivalent message is already visible: they are approved, Fig & Bloom has a maximum number of creator gifts per week, and we will select them when the next slot is available.
11. If latest inbound is explicit negative, mark declined post-shortlist; do not send further messages.
12. If ambiguous/escalated/payment/extension/product issue/unhappy/damaged flowers, report manual review and do not respond, except when a matching Daniel-approved override exists in `/opt/data/tmp/hashgifted-manual-overrides.json`; in that case reply with the approved answer and continue selection/approved-reserve handling.
13. Verify sends with exact readback and selections by live row status re-fetch.
14. Return concise counts by campaign: messages sent by type, order acknowledgements sent, qualified/approved reserves, selected, declined, manual review, failures, warnings, audit artifact paths.
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
