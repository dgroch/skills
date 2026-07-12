---
name: hashgifted-creator-monitor
description: Sweep active Hashgifted campaigns, read each creator's current lifecycle state from Hashgifted and Notion, and produce a prioritised dispatch plan that names which lifecycle skill should run next per creator. Read-only orchestrator. Use when asked to monitor Hashgifted campaigns, run a morning sweep, identify which creators need action, surface story-capture or content-capture work, or check ghost timing. Does not click Select, Decline, Send, Mark complete, or Exclude; per-step skills handle those.
---

## Conversation Backlog Triage Mode

When Daniel says the Hashgifted routines have been paused, content has continued to roll in, or he needs **simple questions to answer so conversations can be wrapped up**, run a read-only chat triage instead of resuming any older selection/reply sweep script.

Rules for this mode:

- Do not screen new applicants, shortlist, select, decline, or send messages.
- Do not run legacy automation that can send initial outreach, nudges, missing-gate questions, order acknowledgements, or reject/decline actions.
- Read campaign wave rows and thread details only, using `markAsSeen=false` where the API supports it.
- Group output into batch decisions rather than hundreds of per-creator questions, e.g. old shortlisted replies, accepted creators with posted content, delivery/support issues, review requests, and no-action acknowledgements.
- Treat stale order-acknowledgement flags carefully: if content is already posted, prefer a posted-content warm receipt/capture path over sending an old pre-content order acknowledgement.
- Keep selection-paused creators on hold until new campaigns are launched; do not ask missing gates merely to progress candidate selection unless Daniel explicitly reopens screening.

# Hashgifted Creator Monitor

Sweep all live Hashgifted campaigns (`Open for Applicants`, `Active`, `Wrapping`), identify per-creator state across Hashgifted and Notion, and return a prioritised dispatch plan. This is the orchestrator for the Hashgifted lifecycle. It never performs write actions; it routes work to the per-step skills.

## Lifecycle Boundary

Reads only. The monitor:

- Lists live campaigns from the Notion Campaigns DB (`Open for Applicants`, `Active`, `Wrapping`).
- Reads campaign and creator state from Hashgifted (applicants, shortlist, selected, threads, completed gallery).
- Reads creator timing fields from the Notion Creators DB (`Last Contacted`, scores, manual flags).
- Reads matching Trello UGC card/list when available and flags stale cards for downstream reconciliation.
- Applies the state machine in `hashgifted-ops-manager/references/lifecycle.md`.
- Emits one dispatch item per creator naming the next skill, with priority and evidence.
- Stops. Per-step skills are invoked separately.

The monitor never clicks Select, Decline, Send, Mark complete, Exclude, or Change campaign status. It also never composes or sends messages. Story and content capture are dispatched to their dedicated skills, not performed inline.

## Required References

- Read `reference-browser-operator` before browser actions.
- Read `hashgifted-browser-adapter-map` for Hashgifted UI intents.
- Read `hashgifted-browser-adapter-map/references/gift-view-observations.md` before operating on a live campaign page.
- Read `hashgifted-ops-manager/references/lifecycle.md` to apply the creator state machine.
- Read `hashgifted-ops-manager/references/audit-log.md` before live runs.
- Read `hashgifted-ops-manager/references/story-capture.md` to recognise story-capture dispatch.
- Read `hashgifted-ops-manager/references/trello-ugc-board.md` to compare observed lifecycle state with the UGC Trello card/list. The monitor is read-only, so it reports needed Trello reconciliations but does not move cards.
- Read `references/dispatch-output-schema.md` for the dispatch plan structure.

## Required Inputs

Ask only for missing fields or an explicit override.

- Run mode: `plan`, `dry_run`, `assist`, or `auto`. Default to `assist`.
- Sweep scope: `all_active` (default) or a single campaign name or Hashgifted URL.
- Per-run creator cap. Default 25.
- Per-creator action cap. Default 1, per `hashgifted-ops-manager`.
- Optional priority floor, e.g. only return items at priority `selection` or higher.
- Optional creator allowlist or denylist for targeted sweeps.

No message templates or selection criteria are required because the monitor never communicates and never decides shortlist or decline.

## Run Mode Behaviour

Because the monitor never writes, run modes only constrain how much reading it performs.

- `plan`: list active campaigns and outline the sweep order without opening campaign pages.
- `dry_run`: perform full reads and return the dispatch plan. No browser writes occur in any mode.
- `assist`: same reads as `dry_run`. Output the plan and stop. Approval gates belong to the dispatched per-step skills.
- `auto`: same reads as `dry_run`. Use only when the user explicitly requested an unattended sweep.

The monitor itself is low-risk because it is read-only. Risk is deferred to the skills it dispatches.

## Pre-Flight Checks

- Confirm Notion connector access to the Campaigns DB and Creators DB. The Campaigns DB must expose `Status`, `Posting Deadline`, `Hashgifted URL`, and `Target Selected`. If a required column is missing, record `schema_gap` and stop. If the connector is unreachable, fall back to a single-campaign sweep using the user-supplied URL or stop in `plan`.
- Confirm browser runtime is healthy and the user is logged in to Hashgifted. Do not attempt to repair authentication.
- Confirm the runtime adapter exposes the intents in `hashgifted-browser-adapter-map/references/hashgifted-intents.md`. If a needed intent is missing for shortlisted, selected, or completed views, record `ui_changed` and continue with the readable subset.
- Start an audit record with run id, mode, runtime, scope, caps, and start screenshot.

## Sweep Sequence

1. Resolve campaign list.
   - `all_active`: query Notion Campaigns DB for `Status in ("Open for Applicants", "Active", "Wrapping")` and read each campaign's `Hashgifted URL`. `Active` is the priority bucket; `Open for Applicants` is shortlist work only; `Wrapping` is closeout, late captures, and gallery sweep only.
   - For any matching campaign with an empty `Hashgifted URL`, emit a `missing_hashgifted_url` warning, add the campaign to `manual_review`, and skip it. Do not stop the sweep.
   - Single campaign: use the supplied URL or look up by name.
2. Order campaigns by `Posting Deadline` ascending. Tie-break by `Target Selected` minus current selected-count (largest gap first), then by `Created` ascending.
3. For each campaign, run the per-campaign loop until the per-run creator cap is reached.

## Per-Campaign Loop

Repeat for each campaign in the sweep list. Stop early if the creator cap is hit.

1. Navigate: `navigate(campaign_url)` and `confirm_context("brands.hashgifted.com/gift-view")`.
2. Read campaign header: `read_card("campaign status")`. Capture `applicant_count`, `selected_count`, `target_selected`, posting deadline.
3. Detect story-link signals first because stories decay fastest:
   - Open the message centre or active threads for this campaign.
   - For each thread with a recent inbound message, `read_thread()` and look for `story link in thread`.
   - Cross-check against Notion `Last Captured Story` to skip already captured stories.
4. Read each lifecycle bucket relevant to the campaign's Status and apply the state machine to each creator found:
   - `Open for Applicants`: Applied tab only.
   - `Active`: Applied, Shortlisted, Selected, Threads, Completed gallery.
   - `Wrapping`: Selected, Threads, Completed gallery (Applied is closed for new entries).
5. For every candidate creator, build one dispatch item. Use the first matching state in `lifecycle.md`. Stop at the first match per creator.
6. Record evidence: campaign-context screenshot, optional creator-card screenshot, redacted thread excerpt for ghost timing claims.
7. Locate the matching Trello card by Hashgifted UID, exact `[HG] @handle — Campaign` title, or creator handle + campaign. Add current Trello list/card URL to evidence. If the card is missing or in a list that conflicts with the observed lifecycle state, add a `trello_reconcile_needed` warning and the expected target list from `hashgifted-ops-manager/references/trello-ugc-board.md`.
8. Append the dispatch item to the run plan. Increment the creator counter.

## Dispatch Priority

Apply this order when ranking the dispatch plan, matching `hashgifted-ops-manager`:

1. Story capture.
2. Content capture.
3. Creator closeout, delivered or ghost.
4. Creator selection.
5. Creator shortlisting.
6. Nudges and reminders.
7. Campaign setup or cleanup.

If a creator matches multiple states, emit only the highest-priority dispatch item for that creator in this cycle.

## Dispatch Item

For each creator, append to the plan using `references/dispatch-output-schema.md`. Minimum fields:

```json
{
  "creator": {"name": "Name", "handle": "@handle", "notion_id": "optional"},
  "campaign": {"name": "Campaign", "hashgifted_url": "https://...", "notion_id": "optional"},
  "current_state": "Applied|Shortlisted|Selected|AwaitingReply|PastDeadline|StoryPosted|Posted|Delivered|Ghosted",
  "matched_rule": "verbatim row label from lifecycle.md",
  "dispatch": "hashgifted-creator-shortlist|hashgifted-creator-select|hashgifted-content-capture|hashgifted-story-capture|hashgifted-creator-close|nudge",
  "priority": 1,
  "reason": "short human-readable reason",
  "confidence": "high|medium|low",
  "evidence": [],
  "warnings": []
}
```

Use `nudge` for the `+3 days` and `+7 days` reply or deadline nudges; the consuming skill is `hashgifted-creator-select` for reply nudges and `hashgifted-creator-select` or the close skill for deadline nudges, depending on lifecycle context. Record which one in `reason`.

## Exit Conditions

Stop when any condition is true:

- Per-run creator cap reached.
- Campaign list exhausted.
- No campaigns matched the live-status filter (`no_campaigns_in_scope`).
- Notion connector unreachable in `all_active` scope and no fallback URL was provided.
- Required Campaigns DB column missing (`schema_gap`).
- Authentication, rate limit, or page integrity issue appears.
- The adapter cannot unambiguously identify the active creator, campaign tab, or thread.
- A new intent is required that is not in the adapter map.

Under-dispatching is better than dispatching on weak evidence. A missed creator is recoverable next sweep; a wrong dispatch can pull a downstream skill into a high-risk action on the wrong creator.

## Failure Handling

- Notion read failure: fall back to single-campaign mode if a URL was supplied; otherwise stop and return what was read so far.
- Hashgifted page resort lag: wait for `next applicant loaded` or equivalent, then re-read before recording state.
- Creator identity ambiguous on a thread or gallery card: record `creator_identity_ambiguous` and emit `manual_review` instead of a dispatch.
- Story link parse failure: still emit the dispatch item with the raw thread excerpt so `hashgifted-story-capture` can retry; do not attempt to repair Instagram in this skill.
- Completed gallery shows an asset already logged in Notion: skip silently and record `not_applicable`.
- Adapter intent missing for shortlisted or selected views: record `ui_changed`, continue with the readable buckets, and add the gap to warnings.

## Reporting

Return a concise summary plus the dispatch plan:

- Campaigns swept: count and names.
- Creators evaluated: count.
- Dispatch items by skill: counts grouped by `dispatch`.
- Highest-priority items first, with creator handle, campaign, and matched rule.
- Manual review items.
- Trello status: missing cards, stale cards, and recommended target lists for downstream skills to move.
- Warnings.
- Audit log location or inline audit record.

The output of this skill is a plan. Confirm with the user before invoking any per-step skill from the dispatch list, unless the user has explicitly chosen `auto` for that downstream skill on this campaign.
