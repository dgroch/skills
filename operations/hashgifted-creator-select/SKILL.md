---
name: hashgifted-creator-select
description: Drive the Hashgifted UI to communicate with shortlisted creators, capture their agreement on deliverables and deadline, send brief options after positive reply, and click Select to add agreed creators to the campaign roster. Sends initial selection messages, +3 and +7 day reply nudges, and brief-option follow-ups. Use when asked to message shortlisted Hashgifted creators, run a selection round, send the next batch of selection messages, send a reply nudge, or finalise a creator who has agreed. Does not shortlist applicants, capture content, or send campaign-full closeout messages.
---

# Hashgifted Creator Select

Move shortlisted creators from `Shortlisted` to `Selected`. This is a two-message arc:

1. Initial selection message confirms interest, deliverables, and deadline.
2. After a positive reply, send brief options. When the creator picks one, click Select and confirm the Accept modal.

If a creator does not reply, send a +3 day gentle nudge, then a +7 day final nudge. The monitor dispatches `hashgifted-creator-close` at +10 days for the ghost path; this skill does not handle that.

## Lifecycle Boundary

This skill handles only the Shortlisted → Selected transition and its associated thread communication. It:

- Sends the initial selection message.
- Sends +3 and +7 day reply nudges keyed off Notion `Last Contacted`.
- Sends the brief-options message after a positive reply.
- Clicks `Select creator` and confirms `Accept this creator` once a brief is picked and agreement is recorded in the thread.
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
- Read `references/selection-message-template.md` before composing any outbound.
- Read `references/reply-classification.md` before acting on an inbound reply.

## Required Inputs

Load from the dispatch plan or the Notion Campaign record. Ask only for missing fields or an explicit override.

- Campaign name and `Hashgifted URL`.
- Run mode: `plan`, `dry_run`, `assist`, or `auto`. Default to `assist`.
- Creator scope: a single creator handle (when invoked from a monitor dispatch), a comma-separated list, or `all_shortlisted` for a full pass.
- Per-run send cap. Default 10 outbound messages per run.
- Optional dispatch hint from the monitor: `selection_initial`, `nudge_3d`, `nudge_7d`, or `mark_selected`. The skill always re-reads the thread to confirm the actual state and treats the hint as advisory, not authoritative.

## Run Mode Behaviour

The mode is the gate. There are no per-action HIL pauses. Review happens in `dry_run`; once the marketer is satisfied, switch to `assist` or `auto` and the skill executes without further prompts.

- `plan`: outline the per-creator action plan from Notion + dispatch input. No browser reads.
- `dry_run`: open threads, read state, compose drafts (initial messages, nudges, brief-options copy), classify any inbound replies, and return everything as a plan. No `compose_message`, `send_message`, `Select creator`, or `Accept this creator` calls.
- `assist`: full reads + writes. Marketer is co-present; live audit log and screenshots are the review surface.
- `auto`: identical writes to `assist`. Intended for unattended scheduled runs.

Structural safeguards apply in every mode that writes (see Pre-Flight, Per-Creator Loop, and Stop Rules). The skill never "guesses" past ambiguity to keep up momentum.

## Pre-Flight Checks

- Confirm the page or target URL is the expected campaign: `confirm_context("brands.hashgifted.com/gift-view")` after `navigate(campaign_url)`.
- Read `campaign status`. If `selected_count >= target_selected`, stop. Campaign-full closeout is manual by design.
- Confirm the runtime adapter exposes `Message composer`, `Send message`, `message sent`, `Select creator`, `Accept this creator`, and the thread reading intents.
- Start an audit record with run id, mode, runtime, campaign, scope, send cap, and start screenshot.

## Per-Creator Loop

Repeat for each creator in scope until the per-run send cap is reached, the creator list is exhausted, or a stop rule fires.

1. Resolve the creator: handle, name, Notion id, last `Last Contacted` timestamp.
2. Open the thread: `click_action("Open creator thread")` or `navigate(thread_url)`.
3. `read_thread()` and determine the actual current state:
   - No outbound from us yet → `selection_initial`.
   - Last outbound was the initial message, no inbound, age ≥ 3 days and < 7 → `nudge_3d`.
   - Last outbound was the initial or +3 nudge, no inbound, age ≥ 7 days and < 10 → `nudge_7d`.
   - Inbound exists → classify per `references/reply-classification.md`.
4. Reconcile against the dispatch hint. If the actual state differs from the hint, log `state_mismatch`, follow the actual state, and continue.
5. Re-confirm creator identity from the thread header before any write. Stop and flag `creator_identity_ambiguous` if uncertain.
6. Act on the resolved state:
   - **`selection_initial`**: compose using `references/selection-message-template.md` skeleton + 2-3 personalised hooks pulled from the shortlist signals or thread context. `compose_message(text)`, screenshot draft, `send_message()`, `wait_for_change("message sent")`. Update Notion `Last Contacted`.
   - **`nudge_3d` / `nudge_7d`**: use the matching nudge variant in the template reference. Same send sequence and Notion update.
   - **Inbound = positive (no brief picked yet)**: send the brief-options message using the campaign's linked Briefs. Same send sequence and Notion update.
   - **Inbound = brief picked**: re-confirm the picked brief is one linked to this campaign. Click `Select creator`, screenshot, `wait_for_change` to detect the Accept modal, click `Accept this creator`, screenshot, wait for state change. Write Notion `Status = Selected`, record the chosen brief.
   - **Inbound = question or soft yes**: log `manual_review` with the question. Do not auto-respond.
   - **Inbound = negative**: write Notion `Status = Declined` with reason `creator declined post-shortlist`. Do not send further messages.
   - **Inbound = ambiguous**: log `manual_review`.
7. Audit: append send/Select event with creator id, intent, screenshot before/after, and any warnings.
8. Decrement the send cap (sends only; `Select` clicks do not count against the cap). Continue or exit.

## Stop Rules

Stop when any condition is true:

- Per-run send cap reached.
- Creator scope exhausted.
- `selected_count` reaches `target_selected` mid-run. Do not message remaining shortlisted creators.
- Authentication, rate limit, or page integrity issue appears.
- Adapter cannot unambiguously identify the active creator, the message composer, or the Select control.
- A required intent is missing from the adapter map.

Under-sending is better than sending on weak evidence. A skipped creator is recoverable next run; a misidentified send is not.

## Failure Handling

- Composer renders but `Send message` does not confirm: do not click again. Re-read the thread; if the message is visible, log success and continue. If not, mark `send_failed` and skip.
- Select click does not surface the Accept modal: stop and flag `select_modal_missing`. Do not retry.
- Notion write fails after a successful send or Select: continue, log `notion_write_failed` with the missing field. The Hashgifted state is the source of truth; the next monitor sweep will reconcile.
- Brief link not found on the Campaign record: log `briefs_missing`, skip the brief-options message, leave the creator on the positive-reply state for the next sweep.
- Two creators on a thread (rare): stop with `creator_identity_ambiguous`.

## Reporting

Return a concise summary plus the audit:

- Sends by intent: count of `selection_initial`, `nudge_3d`, `nudge_7d`, `brief_options`.
- Selected: count and creator handles.
- Declined post-shortlist: count and creator handles.
- Manual review: count and reasons.
- Stop reason: `cap_reached`, `scope_exhausted`, `target_selected_reached`, `auth_required`, `adapter_gap`.
- Audit log location.
