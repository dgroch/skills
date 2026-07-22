---
name: hashgifted-creator-select
description: Drive the Hashgifted UI to communicate with shortlisted creators, capture their agreement on deliverables and deadline, send brief options after positive reply, and click Select to add agreed creators to the campaign roster. Sends initial selection messages, +3 and +7 day reply nudges, and brief-option follow-ups. Use when asked to message shortlisted Hashgifted creators, run a selection round, send the next batch of selection messages, send a reply nudge, or finalise a creator who has agreed. Does not shortlist applicants, capture content, or send campaign-full closeout messages.
---

# Hashgifted Creator Select

Move shortlisted creators from `Shortlisted` to `Selected`. This is a two-message arc:

1. Initial qualification message shares the relevant Notion brief link(s) and asks the creator to confirm delivery eligibility, willingness to create and supply around five high-resolution aesthetic still photographs featuring the bouquet, and brief understanding/agreement. No Instagram Reel is required for new selections unless Daniel explicitly overrides the campaign.
2. After a positive reply that confirms the gates, rank qualified creators and sequence `Select` actions according to the configured selection cadence. When the creator has chosen/accepted a brief and fits the current cadence slot, click Select and confirm the Accept modal.

If a creator does not reply, send a +3 day gentle nudge, then a +7 day final nudge. The monitor dispatches `hashgifted-creator-close` at +10 days for the ghost path; this skill does not handle that.

## Lifecycle Boundary

This skill handles only the Shortlisted → Selected transition and its associated thread communication. It:

- Sends or drafts the initial qualification message, including Notion brief links plus current delivery-area eligibility, agreement to create and supply around five high-resolution aesthetic still photographs, and brief understanding/agreement. No Reel is required for newly selected creators by default.
- Sends +3 and +7 day reply nudges keyed off Notion `Last Contacted`.
- Sends the brief-options message after a positive reply.
- Clicks `Select creator` and confirms `Accept this creator` only once the creator is qualified, ranking has been applied, and the configured selection cadence allows another selection for that campaign/week.
- Updates Notion `Last Contacted` after every send and writes `Status = Selected` after the Accept modal confirms.

It does not:

- Shortlist or decline applicants pre-selection (that is `hashgifted-creator-shortlist`).
- Send a closeout message to creators left Shortlisted when the campaign hits `Target Selected`. That step is manual by design; do not synthesise a message.
- Close ghosted creators at +10 days (`hashgifted-creator-close`, dispatched by the monitor).
- Capture posts, reels, or stories.

## Required References

- Read `reference-browser-operator` before browser actions.
- Read `hashgifted-browser-adapter-map` for Hashgifted UI intents.
- Read `hashgifted-browser-adapter-map/references/gift-view-observations.md` before operating on a live campaign page.
- Read `hashgifted-ops-manager/references/lifecycle.md` for the creator state machine and nudge timing.
- Read `hashgifted-ops-manager/references/audit-log.md` before live runs.
- Read `hashgifted-ops-manager/references/trello-ugc-board.md` before sending, qualifying, selecting, reserving, declining, or acknowledging a creator; Trello mirrors the creator lifecycle for Daniel.
- Read `references/selection-message-template.md` before composing any outbound.
- Read `references/reply-classification.md` before acting on an inbound reply.

## Required Inputs

Load from the dispatch plan or the Notion Campaign record. Ask only for missing fields or an explicit override.

- Campaign name and `Hashgifted URL`.
- Run mode: `plan`, `dry_run`, `assist`, or `auto`. Default to `assist`.
- Creator scope: a single creator handle (when invoked from a monitor dispatch), a comma-separated list, or `all_shortlisted` for a full pass.
- Per-run send cap. Default 10 outbound messages per run.
- Selection cadence config for this lifecycle entry. Capture it before selecting, not as a global constant. Required fields: `max_selects_per_campaign_per_week`, `campaigns_in_scope`, `week_start`, and optional `global_weekly_gift_cap`. For the current Marseille/Savoie/Umbria bouquet round, Daniel approved `max_selects_per_campaign_per_week = 2`, `campaigns_in_scope = 3`, and `global_weekly_gift_cap = 6`.
- Brief mapping for the campaigns in scope. If a campaign does not have a one-to-one brief mapping yet, ask whether shared brief options are acceptable. For the current Marseille/Savoie/Umbria bouquet round, creators across all three campaigns may choose **Brief 1 or Brief 2**.
- Optional dispatch hint from the monitor: `selection_initial`, `nudge_3d`, `nudge_7d`, or `mark_selected`. The skill always re-reads the thread to confirm the actual state and treats the hint as advisory, not authoritative.

## Run Mode Behaviour

Sends are reversible (a misfired message can be corrected in-thread); state transitions are not (`Select` + `Accept` commits a roster slot, `Decline` ends the conversation). Modes differ on whether the irreversible writes pause for approval.

- `plan`: outline the per-creator action plan from Notion + dispatch input. No browser reads.
- `dry_run`: open threads, read state, compose drafts (initial messages, nudges, brief-options copy), classify any inbound replies, and return everything as a plan. No `compose_message`, `send_message`, `Select creator`, `Accept this creator`, or Notion `Status` writes.
- `assist`: full reads + drafts. Draft outbound messages (`selection_initial`, `nudge_3d`, `nudge_7d`, `brief_options`, or approved Q&A answer) and pause for Daniel's approval before sending. The skill also pauses for a single approval before each irreversible write — the `Select creator` + `Accept this creator` sequence, and any post-shortlist `Status = Declined` write. Approval is per creator, not per click.
- `auto`: full reads + writes with no approval prompts. Intended for unattended scheduled runs only after this workflow is explicitly promoted to auto mode.

Structural safeguards apply in every mode that writes (see Pre-Flight, Per-Creator Loop, and Stop Rules). The skill never "guesses" past ambiguity to keep up momentum.

## Pre-Flight Checks

- Confirm the page or target URL is the expected campaign: `confirm_context("brands.hashgifted.com/gift-view")` after `navigate(campaign_url)`.
- Read `campaign status`. If `selected_count >= target_selected`, stop. Campaign-full closeout is manual by design.
- Confirm the runtime adapter exposes `Message composer`, `Send message`, `message sent`, `Select creator`, `Accept this creator`, and the thread reading intents.
- Resolve campaign-to-brief mapping before outbound messages. Use Notion `Brief.Public Link` values, not private workspace URLs. If the public link is missing, stop with `brief_public_link_missing` rather than sending an internal link.
- Resolve the selection cadence before any `Select creator` action. Treat cadence as a parameter of this selection lifecycle entry, not a hardcoded skill default.
- Verify Trello access to the `🤖 User Generated Content` board (`zDpcpS3V`) and read required list IDs before Trello writes. If unavailable, continue safe Hashgifted/Notion actions and report `trello_unavailable`.
- Start an audit record with run id, mode, runtime, campaign, scope, send cap, and start screenshot.
- For unattended cron runs, also read `hashgifted-ops-manager/references/cron-automation.md`; use conservative auto rules, verify every external send with exact thread readback, verify every selection with live row status re-fetch, and report manual-review items instead of asking questions.

## Hybrid Conversation Classification for Unattended Runs

For recurring `auto` selection/reply sweeps, do not let keyword or last-message rules make creator decisions. Use the maintained hybrid pipeline:

- Collector: `/opt/data/profiles/creative/scripts/hashgifted_hybrid_pipeline.py collect` reads complete ordered Hashgifted threads plus pending Trello commands without writing.
- Reasoner: GPT-5.6 Sol reads `/opt/data/profiles/creative/scripts/hashgifted_hybrid_classifier_prompt.md` and returns exactly one strict JSON decision per candidate, with explicit facts and exact supporting quotes.
- Validator: `hashgifted_hybrid_pipeline.py validate` rejects missing/duplicate decisions, invented quotes, unsafe messages, unsupported actions, low-confidence automatic actions, ignored human commands, and selections lacking all qualification gates.
- Actioner: `hashgifted_hybrid_pipeline.py apply` re-fetches each live thread, blocks if its SHA-256 changed since reasoning, enforces the Monday Australia/Melbourne release window and two selections per campaign per week, executes only validated actions, and verifies external writes by live readback.

The LLM interprets conversational meaning; deterministic code owns policy and side effects. Generic biography/application/capability text saying a creator takes photos is not a campaign-specific commitment to create and supply the requested photo set. Existing in-flight threads may retain an earlier explicit Reel commitment or Daniel-approved alternative as valid legacy evidence; do not retroactively change agreed deliverables. Ordinary styling language such as “vase” is not a product exception unless the full conversation establishes an actual request. A clear earlier answer remains valid when followed by concept detail. A Daniel/Fig & Bloom-approved alternative output format may satisfy the deliverable gate only when the approval is explicit in the thread.

Never run the legacy deterministic classifier as a second decision-maker after the hybrid actioner. Explicit Trello `SEND TO CREATOR`, `APPROVE CREATOR`, and `REJECT CREATOR` commands remain deterministic inputs and must be acknowledged by source comment ID. A standalone/manual creator message must preserve the card's current lifecycle list (especially `Approved Reserve` or `Needs Daniel`) unless the validated decision explicitly names a new target list; sending a message is not itself a lifecycle downgrade.

## Per-Creator Loop

Repeat for each creator in scope until the per-run send cap is reached, the creator list is exhausted, or a stop rule fires.

1. Resolve the creator: handle, name, Notion id, last `Last Contacted` timestamp.
   - Upsert or locate the matching Trello card (`[HG] @handle — Campaign Name`) using `hashgifted-ops-manager/references/trello-ugc-board.md`.
2. Open the thread: `click_action("Open creator thread")` or `navigate(thread_url)`.
3. `read_thread()` and determine the actual current state:
   - No outbound from us yet → `selection_initial`.
   - Last outbound was the initial message, no inbound, age ≥ 3 days and < 7 → `nudge_3d`.
   - Last outbound was the initial or +3 nudge, no inbound, age ≥ 7 days and < 10 → `nudge_7d`.
   - Inbound exists → classify per `references/reply-classification.md`.
4. Reconcile against the dispatch hint. If the actual state differs from the hint, log `state_mismatch`, follow the actual state, and continue.
5. Re-confirm creator identity from the thread header before any write. Stop and flag `creator_identity_ambiguous` if uncertain.
6. Act on the resolved state:
   - **`selection_initial`**: compose using `references/selection-message-template.md` skeleton + 2-3 personalised hooks pulled from the shortlist signals or thread context. Include the Notion brief link(s), ask which brief they prefer where multiple briefs are available, and ask them to confirm all qualification gates: current delivery-area eligibility, happy to create and supply around five high-resolution aesthetic still photographs featuring the bouquet, and comfortable with the brief direction. State that no Reel is required for this default photo deliverable. `compose_message(text)`, screenshot draft, then in `assist` pause for approval.
   - **`nudge_3d` / `nudge_7d`**: use the matching nudge variant in the template reference. Same draft/send sequence and Notion update. Keep/move Trello to `Shortlisted` and add a nudge comment after send readback.
   - **Inbound = positive/partial**: classify which qualification gates are explicitly confirmed. If delivery eligibility, the agreed photo deliverable, brief preference, or brief understanding/agreement is missing, ask only for the missing item(s). Do not click Select on a soft yes that has not confirmed all gates. Keep/move Trello to `Shortlisted`; routine missing evidence or ambiguity is not a Daniel decision. For existing in-flight threads, previously agreed Reel or explicitly approved alternative evidence remains valid.
   - **Inbound = fully qualified**: re-confirm the picked brief is one of the approved campaign brief options and that all gates are explicit in the thread. Rank the creator against other qualified creators in the campaign and current week. If cadence slots are already full, leave them qualified/reserve and report `cadence_full`; move Trello to `Approved Reserve` and comment the gate evidence + next cadence window. If a slot is available, in `assist` surface the creator + chosen brief + gate evidence + rank + remaining weekly slots and pause for a single approval before proceeding; in `auto`, proceed without prompting only when evidence and cadence are unambiguous. Click `Select creator`, screenshot, `wait_for_change` to detect the Accept modal, click `Accept this creator`, screenshot, wait for state change. Write Notion `Status = Selected`, record the chosen brief, qualification gates, and cadence week. After live row readback verifies selected/accepted, move Trello to `Selected / Brief Sent`.
   - **Inbound = answerable question**: use `references/reply-classification.md` and `references/selection-message-template.md` Q&A answer bank to draft a reply. In `assist`, pause for Daniel approval before sending; in `auto`, send only if the answer class is high-confidence and not escalated. Move Trello to `Shortlisted` for pre-selection Q&A or `Active Q&A / Awaiting Content` for post-selection Q&A.
   - **Inbound = escalated question or soft yes**: ask only for routine missing gates. Move to `Needs Daniel` only when the conversation establishes a commercial/policy exception, material delivery problem, genuine brand-safety ambiguity, or direct owner-level question; include the smallest decision question and do not auto-respond to that exception.
   - **Inbound = negative**: in `assist`, surface the inbound and pause for approval before writing; in `auto`, proceed. Write Notion `Status = Declined` with reason `creator declined post-shortlist`. Move Trello to `Lapsed / Declined / Do Not Use`. Do not send further messages.
   - **Inbound = ambiguous**: leave the creator ranked in `Shortlisted` and gather the smallest missing fact. Escalate to `Needs Daniel` only if the ambiguity falls into one of the narrow exception categories above.
   - **Selected/accepted creator has booked/placed order and acknowledgement sent**: move/update Trello to `Active Q&A / Awaiting Content` after exact message readback.
   - **Selected/accepted creator sends a post-selection support/Q&A message after the latest brand reply**: do not silently ignore it. Classify delivery/damage/booking/content questions; send only safe acknowledgements or standard content answers; upsert/move the Trello card to `Active Q&A / Awaiting Content` for active support/Q&A. Use `Needs Daniel` only for a commercial/policy exception, material delivery problem, genuine brand-safety ambiguity, or direct owner-level question, with the exact creator message in the card/comment.
   - Conversation log sync: mirror every Hashgifted thread message read by the workflow into Trello comments using `RECEIVED MESSAGE` for creator/influencer messages and `SENT MESSAGE` for brand/Hermes messages. Include a deterministic `Message sync id` derived from Hashgifted row UID, sender type, timestamp, and message text; never create duplicate Trello comments for the same message on later sweeps. The Trello card description must also include `Hashgifted campaign URL`, `Hashgifted conversation link` (campaign URL plus the exact wave UID), the row UID, gate values, and a full latest thread transcript so Daniel can review the actual chat from the card without guessing from summary comments. When the live thread proves a Melbourne/Sydney/Brisbane/rest-of-Australia location gate, set the corresponding Trello `Location: ...` label so Daniel can see location gating at a glance.
   - **Daniel leaves a Trello comment beginning with `SEND TO CREATOR`**: treat it as an explicit manual instruction to pass the message to the mapped Hashgifted creator, after verifying the Trello card maps to one Hashgifted row/campaign and the message passes safety checks. Required format:

     ```text
     SEND TO CREATOR

     Message:
     <exact message to send>
     ```

     Optional `Mode: draft only` prevents sending; optional `Mode: send` is the default. Reject/block comments that ask for detailed street address details, promise payment/discounts/exclusivity/future work, include private Notion links, or cannot be mapped unambiguously. After sending, verify exact Hashgifted thread readback and comment `SENT TO CREATOR` on the Trello card with the source Trello comment id.
   - **Daniel leaves a Trello comment containing exactly `APPROVE CREATOR` on its own line**: treat it as explicit approval to proceed with that creator. Re-read the Hashgifted thread first; only select if delivery/photo-deliverable/brief gates are still true and the campaign weekly cap has room. Existing in-flight Reel commitments or explicitly approved alternatives remain valid legacy deliverable evidence. If the cap is full, move/keep the card in `Approved Reserve` and do not click Select. Confirm back on Trello with `CREATOR DECISION ACTIONED` or `CREATOR DECISION BLOCKED` and the source comment id.
   - **Daniel leaves a Trello comment containing exactly `REJECT CREATOR` on its own line**: treat it as explicit instruction to decline/reject the creator in Hashgifted. Optional `Reason:` may be included. Verify live status after rejection, move the card to `Lapsed / Declined / Do Not Use` when verified, and confirm on Trello with `CREATOR DECISION ACTIONED` or `CREATOR DECISION BLOCKED` and the source comment id.
7. Audit: append send/Select/Trello event with creator id, intent, screenshot before/after, Trello card URL/final list, and any warnings.
8. Decrement the send cap (sends only; `Select` clicks do not count against the cap). Continue or exit.

## Stop Rules

Stop when any condition is true:

- Per-run send cap reached.
- Creator scope exhausted.
- `selected_count` reaches `target_selected` mid-run. Do not message remaining shortlisted creators.
- Current cadence is full for the campaign/week. Do not select additional creators; keep qualified creators as reserve for the next cadence window.
- Authentication, rate limit, or page integrity issue appears.
- Adapter cannot unambiguously identify the active creator, the message composer, or the Select control.
- A required intent is missing from the adapter map.

Under-sending is better than sending on weak evidence. A skipped creator is recoverable next run; a misidentified send is not.

## Failure Handling

- **Detailed delivery addresses in chat:** Do not ask creators to type street address/unit/recipient details in Hashgifted messages. This appears to trigger a Hashgifted system/safety message. Selection messages should ask only for broad Melbourne/Sydney/Brisbane metro eligibility; address/order details are handled later by Hashgifted's post-selection booking flow.
- Composer renders but `Send message` does not confirm: do not click again. Re-read the thread; if the message is visible, log success and continue. If not, mark `send_failed` and skip.
- Select click does not surface the Accept modal: stop and flag `select_modal_missing`. Do not retry.
- Notion write fails after a successful send or Select: continue, log `notion_write_failed` with the missing field. The Hashgifted state is the source of truth; the next monitor sweep will reconcile.
- Brief link not found on the Campaign record or approved shared-brief config: log `briefs_missing`, skip outbound, and leave the creator for the next sweep. Never send private Notion workspace URLs.
- Two creators on a thread (rare): stop with `creator_identity_ambiguous`.

## Reporting

Return a concise summary plus the audit:

- Sends by intent: count of `selection_initial`, `nudge_3d`, `nudge_7d`, `brief_options`.
- Selected: count and creator handles.
- Declined post-shortlist: count and creator handles.
- Manual review: count, reasons, and the Trello card URL for each creator escalated to `Needs Daniel` or manual review. Do not report a manual-review item without a Trello link unless Trello is unavailable. If a Trello `APPROVE CREATOR` / `REJECT CREATOR` decision has already been actioned for that card in the same run, reconcile the audit before reporting/syncing so the creator is not also listed as manual review or moved back to `Needs Daniel`.
- Trello cards created/updated/moved by list, including `Approved Reserve`, `Selected / Brief Sent`, `Needs Daniel`, and `Active Q&A / Awaiting Content` counts.
- Stop reason: `cap_reached`, `scope_exhausted`, `target_selected_reached`, `auth_required`, `adapter_gap`.
- Audit log location.
