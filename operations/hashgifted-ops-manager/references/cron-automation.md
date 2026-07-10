# Hashgifted Cron Automation

Use this reference when registering or running unattended Hermes cron jobs for the Hashgifted lifecycle.

## Default Policy

### Trello UGC board sync

Every recurring Hashgifted job must load `hashgifted-ops-manager/references/trello-ugc-board.md` and reconcile the `🤖 User Generated Content` board (`zDpcpS3V`) for every creator/campaign row it touches.

- Upsert one Trello card per creator/campaign using `[HG] @handle — Campaign Name` and Hashgifted UID/Notion IDs for idempotency.
- Move cards according to the lifecycle mapping in `trello-ugc-board.md` after live Hashgifted/Notion state is verified.
- Verify Trello creates/moves/comments/labels by readback and include card URLs + final lists in the cron report.
- If Trello credentials, board, or lists are unavailable, continue safe Hashgifted/Notion work and report `trello_unavailable` or `trello_schema_changed`; do not claim kanban movement.

### New applicants / not-shortlisted candidates

Treat Applied candidates as a triage queue, not a conversation queue.

- Automatically shortlist high-confidence brand-fit creators in open campaigns after live Gifted/Hashgifted readback.
- Keep `maybe`, weak-fit, incomplete-evidence, or low-confidence creators in the ranked applicant pool. Place them in `Triage / Brand Fit` when inside the operational horizon or `Parked Applicant Pool` outside it; routine uncertainty is not a `Needs Daniel` reason.
- Do **not** automatically decline normal weak-fit candidates while campaigns are still open unless Daniel has explicitly enabled auto-decline for this run/campaign.
- Only propose auto-decline for very clear hard blockers or brand-safety issues, and even then report them as `decline_candidates` unless the cron prompt explicitly says `auto_decline_hard_blockers=true`.
- When a campaign is closed/full/wrapping, generate a cleanup plan for stale Applied rows, grouped by reason, but do not send closeout messages or decline in bulk without explicit approval.

Rationale: shortlisting is recoverable and non-communicative; decline is terminal and can remove a future reserve creator. Conversation before shortlist creates low-quality threads and trains creators to negotiate before we know brand fit.

### Shortlisted replies / selection

Treat Shortlisted candidates as a conversation and qualification queue.

For unattended runs, use the hybrid collect → Sol reason → deterministic validate/apply pipeline documented in `hashgifted-creator-select`. The collector must be read-only; Sol must interpret the complete ordered thread and return exact evidence quotes; the actioner must re-read live state before every side effect. Do not run a keyword classifier after the hybrid decision layer. Keyword checks remain safety/policy guards only, not conversational intent reasoning.

- Re-read every live Shortlisted thread before deciding.
- Reply to high-confidence, answerable questions using the approved answer bank.
- Ask only for missing qualification gates: current-round delivery eligibility, IG Reel acceptance, and brief preference/understanding.
- Before asking a missing-gate question, classify prior brand/template replies correctly even when the Hashgifted API omits sender metadata. Never treat our own previous missing-gate question or approved answer-bank text as creator text; otherwise the sweep can ask the same question repeatedly.
- If a creator has already given a clear creator-led creative direction that Daniel or policy accepts as aligned, do not keep asking them to restate a brief preference verbatim.
- Treat creator wording like “within the delivery area” as delivery-gate confirmation when it follows our explicit delivery-area question; do not require them to restate the city/suburb if they have clearly checked eligibility.
- Treat a clear commitment to create IG/TikTok content for the selected concept/brief as satisfying the creative-output gate unless the creator explicitly refuses the required video/content format.
- Daniel’s words `approved` / `accepted` usually mean business-approved from his perspective, not necessarily that the creator should be immediately moved to platform `ACCEPTED`. Translate Daniel approval into the correct lifecycle action based on capacity: select/accept now only if weekly capacity allows; otherwise keep the creator `SHORTLISTED` as approved/reserve and send expectation-setting.
- Selection cadence gates only the final `Select`/accept action, not creator communication or qualification. Continue replying to Shortlisted creators, answering approved questions, and confirming gates even when the current week's selection slots are full.
- Select only fully qualified creators and only inside the configured cadence.
- Current hard capacity: two platform selections/acceptances per campaign, released together on Monday in Australia/Melbourne, unless Daniel explicitly overrides. There is no additional global cap.
- Leave cadence-overflow qualified creators as approved/reserve; do not decline them. Send a warm expectation-setting reply when appropriate: confirm they are approved/qualified, explain there is a weekly maximum number of creator gifts, and say we will select them when the next slot is available.
- Route only commercial/policy exceptions, material delivery problems, genuine brand-safety ambiguity, and direct owner-level creator questions to `Needs Daniel`. Keep ordinary conversational ambiguity in the normal ranked/qualification lane and gather the smallest missing fact.
- When a selected/accepted creator has booked/placed their order, and no equivalent acknowledgement is visible in the thread, send the approved post-selection order acknowledgement from `selection-message-template.md`. This is a proactive quality-control message: thank them, invite questions, and ask them to tell us if flowers arrive below standard so Fig & Bloom can organise re-delivery rather than the creator fulfilling with substandard florals.

### Human-in-loop blocker taxonomy

When a replied Shortlisted creator cannot be selected or declined automatically, report them in one of these explicit buckets so Daniel can unblock lifecycle logic rather than reading raw chats:

- `selectable_now`: all gates are confirmed; only cadence/ranking may delay selection.
- `missing_gate`: positive reply but one gate is absent. Ask only the missing gate; no human decision needed.
- `delivery_outside_confirmed`: creator explicitly says they are outside current approved delivery areas. Keep ranked but ineligible; park outside the operational horizon and do not escalate or auto-close.
- `delivery_edge_question`: creator asks if a nearby region works. Current bouquet round approved edge regions: Geelong, Bannockburn, Sunshine Coast, and Gold Coast. Reply with the approved edge-delivery answer and continue qualification for those regions; keep other regions ranked but ineligible without escalating.
- `product_exception`: creator asks for a vase, different bouquet, payment, or other exception. Requires Daniel approval unless a matching one-off override exists. If an override exists, reply with approval and continue selection.
- `manual_hold_no_reply`: Daniel has explicitly said still considering / checking logistics and no further candidate reply is required. Persist a matching override and suppress automated replies, nudges, selections, or declines until Daniel gives a new decision.
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
- /opt/data/workspace/dgroch-skills/operations/hashgifted-ops-manager/references/trello-ugc-board.md
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
5. Keep maybe/low-confidence rows in the ranked pool, using `Triage / Brand Fit` inside the operational horizon and `Parked Applicant Pool` outside it. Do not use `Needs Daniel` for routine uncertainty.
6. Do not auto-decline unless there is an explicit hard blocker/brand-safety issue and auto-decline has been separately enabled; otherwise list decline candidates only.
7. Verify all mutations by re-fetching live campaign rows.
8. Upsert/move matching Trello UGC cards: Applied touched → `Inbox / Applied` or `Triage / Brand Fit`, outside the operational horizon → `Parked Applicant Pool`, shortlisted → `Shortlisted`, narrow owner-level exception → `Needs Daniel`, approved hard decline → `Lapsed / Declined / Do Not Use`. Verify by Trello readback.
9. Return concise counts by campaign: reviewed, shortlisted, left applied/manual-review, decline candidates, Trello cards created/updated/moved by list, warnings, audit artifact paths.
```

## Cron Prompt: Shortlisted Reply / Selection Sweep

**Production source of truth:** `/opt/data/profiles/creative/scripts/hashgifted_hybrid_cron_prompt.md`. The production cron must follow that collect → Sol reason → validate → apply sequence. The older policy-oriented task list below is background behaviour only; it must not be used to run the legacy deterministic classifier or bypass the strict decision bundle validator.

```text
You are running unattended as a Hermes cron job for Daniel's Fig & Bloom Hashgifted workflow. Do not ask questions; make conservative autonomous decisions and report results back to Daniel.

Load and follow Fig & Bloom/Hashgifted rules from:
- /opt/data/workspace/dgroch-skills/operations/hashgifted-ops-manager/SKILL.md
- /opt/data/workspace/dgroch-skills/operations/hashgifted-ops-manager/references/lifecycle.md
- /opt/data/workspace/dgroch-skills/operations/hashgifted-ops-manager/references/cron-automation.md
- /opt/data/workspace/dgroch-skills/operations/hashgifted-ops-manager/references/trello-ugc-board.md
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
9. Select the creator only in the weekly release window and when that campaign has capacity. Current bouquet cadence: two platform selections/acceptances per campaign, released together on Monday in Australia/Melbourne, unless Daniel explicitly overrides.
10. If capacity is full, leave qualified creators as approved/reserve in `SHORTLISTED`, report them, and send an expectation-setting message if no equivalent message is already visible: they are approved from Fig & Bloom’s side, Fig & Bloom has a maximum number of creator gifts per week, and we will select them when the next slot is available.
11. If latest inbound is explicit negative, mark declined post-shortlist; do not send further messages.
12. If the thread establishes a commercial/policy exception, material delivery problem, genuine brand-safety ambiguity, or direct owner-level question, report manual review and do not respond unless a matching Daniel-approved override exists in `/opt/data/tmp/hashgifted-manual-overrides.json`. For ordinary ambiguity, keep the creator ranked and ask only for the smallest missing qualification fact.
13. Upsert/move matching Trello UGC cards after verified actions: shortlisted/outreach/nudges → `Shortlisted`, qualified cadence-full → `Approved Reserve`, selected/accepted → `Selected / Brief Sent`, order/Q&A/awaiting content → `Active Q&A / Awaiting Content`, declined/ghosted → `Lapsed / Declined / Do Not Use`.
14. Verify sends with exact readback, selections by live row status re-fetch, and Trello moves by card readback.
15. Return concise counts by campaign: messages sent by type, order acknowledgements sent, qualified/approved reserves, selected, declined, manual review, Trello cards created/updated/moved by list, failures, warnings, audit artifact paths.
```

## Cron Prompt: Content Capture Sweep

```text
You are running unattended as a Hermes cron job for Daniel's Fig & Bloom Hashgifted workflow. Do not ask questions; make conservative autonomous decisions and report results back to Daniel.

Load and follow Fig & Bloom/Hashgifted rules from:
- /opt/data/workspace/dgroch-skills/operations/hashgifted-ops-manager/SKILL.md
- /opt/data/workspace/dgroch-skills/operations/hashgifted-ops-manager/references/lifecycle.md
- /opt/data/workspace/dgroch-skills/operations/hashgifted-ops-manager/references/cron-automation.md
- /opt/data/workspace/dgroch-skills/operations/hashgifted-ops-manager/references/trello-ugc-board.md
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
8. Upsert/move matching Trello UGC cards after verified content state: content detected → `Content Received`, saved/indexed → `Ingested / Indexed`, media-buyer handoff ready → `Ready to Schedule`, scheduled → `Scheduled in Later`, live verified → `Posted / Live`, complete/scored → `Completed / Scored`, ghosted/lapsed → `Lapsed / Declined / Do Not Use`.
9. Verify Drive upload/readback, Notion record readback, thank-you exact message readback, completion status re-fetch, and Trello card readback.
10. Return concise counts by campaign: new content detected, assets saved, Notion rows created/updated, creators thanked, marked complete, review scores, media-buyer handoffs, Trello cards created/updated/moved by list, manual review, failures, warnings, audit paths.

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
