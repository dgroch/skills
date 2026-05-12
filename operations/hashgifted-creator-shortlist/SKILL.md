---
name: hashgifted-creator-shortlist
description: Qualify Hashgifted applicants for Fig & Bloom creator campaigns before any creator communication by reviewing hard gates, campaign objectives, brand aesthetics, audience fit, and engagement quality, then moving suitable applicants from Applied to Shortlisted or declining clear mismatches. Use when asked to shortlist Hashgifted applicants, qualify creators, review applied creators, build a shortlist for a gifting campaign, or refactor applicant review workflows on brands.hashgifted.com. Does not send messages or select creators; selection and creator agreement happen in a separate workflow.
---

# Hashgifted Creator Shortlist

Review applied creators in Hashgifted and decide whether each should move from `Applied` to `Shortlisted`, be declined, or remain for manual review. This is a pre-communication qualification step.

## Lifecycle Boundary

Creator states:

1. `Applied`
2. `Shortlisted`
3. `Selected`
4. `Complete`

`Declined` is a side state available any time before completion.

This skill only handles `Applied -> Shortlisted` qualification and pre-selection decline. It does not message creators, request agreement, discuss deliverables, set deadlines, or select creators. Those belong in a separate selection workflow.

## Required References

- Read `reference-browser-operator` before browser actions.
- Read `hashgifted-browser-adapter-map` for Hashgifted UI intents.
- Read `hashgifted-browser-adapter-map/references/gift-view-observations.md` before operating on a live campaign page.
- Read `hashgifted-ops-manager/references/brand-aesthetic-rubric.md` for shared Fig & Bloom creator fit rules.
- Read `hashgifted-ops-manager/references/audit-log.md` before live runs.
- Read `references/qualification-framework.md` before making creator decisions.

## Required Inputs

Load these from the Campaign record created by `hashgifted-campaign-init`. Ask only for missing fields or an explicit override.

- Campaign name and Hashgifted campaign URL.
- Run mode: `plan`, `dry_run`, `assist`, or `auto`. Default to `assist`.
- Campaign objective: audience awareness, content library, or both.
- Campaign aesthetic and concept calibration.
- Hard gates: location, platform, minimum follower count if any, category exclusions. For Fig & Bloom delivery, valid delivery areas are Melbourne, Sydney, and Brisbane metro only; if not explicit, preserve as a selection-stage eligibility question rather than declining on weak inference.
- Review limit or stop condition for the current run, if any.
- One-off calibration, such as mums with kids 0-5, avoid fitness aesthetic, prioritise Melbourne creators, or favour strong video creators.

No message templates are required because shortlisting happens before communications.

## Run Mode Behaviour

- `plan`: inspect inputs and outline the qualification approach.
- `dry_run`: read applicants and return proposed shortlist/decline/review decisions without clicking.
- `assist`: read applicants, then ask approval before each Shortlist or Decline action.
- `auto`: shortlist only when the match is high-confidence and the user explicitly requested auto. Declines still require approval unless the user explicitly allows auto-decline for hard gate failures.

Decline is high-risk because it removes the creator from the campaign path. Shortlist is medium-risk because it advances the creator but does not communicate or commit.

In `auto`, process every currently live applicant in the requested open campaigns before applying final actions. Keep `maybe`/reserve applicants untouched rather than inventing a Hashgifted action for uncertainty; only mutate rows that are confident `shortlist` decisions, and never auto-decline unless the user explicitly requested auto-decline.

## Pre-Flight Checks

- Confirm the current page or target URL is the expected Hashgifted campaign: `confirm_context("brands.hashgifted.com/gift-view")`.
- Prefer the authenticated Gifted/Hashgifted producer API for complete applicant extraction and pagination when credentials are available. The visual/UI layer is useful for profile/media evidence, but the API is the source of truth for live wave rows, statuses, UIDs, ranks, and campaign membership.
- Open the Applicants tab: `click_action("Open applicants tab")`.
- Read campaign status: `read_card("campaign status")`.
- Stop if there are no applicants or the requested run limit has already been reached.
- Start an audit record with campaign, mode, runtime, and initial screenshot.
- For unattended cron runs, also read `hashgifted-ops-manager/references/cron-automation.md` and honour its Applied-candidate policy: auto-shortlist high-confidence fits; leave maybe/low-confidence rows Applied/manual-review; do not message Applied candidates; do not auto-decline unless explicitly enabled for hard blockers.

## Per-Applicant Loop

Repeat until an exit condition is met.

1. Read the top applicant: `read_card("active applicant profile")`.
2. Confirm the applicant is still in `Applied` status and has not already been actioned in this run.
3. Open applicant details if needed: `click_action("Open applicant details")`. Note that this may mark the applicant as read.
4. Open social profiles by intent: `open_in_new_tab("Open first Instagram profile")`, then TikTok if Instagram is unavailable.
5. Read visible social signals: `read_card("active applicant social signals")`.
6. Close social tabs and return to the campaign context with `switch_tab` or `close_tab`.
7. Apply `references/qualification-framework.md` and produce `{recommendation, reason, confidence}`.
8. Upsert the creator into the Notion Creators DB using `hashgifted-ops-manager/references/notion-creator-crm.md`. Store lifecycle state, location inference/eligibility evidence, metrics, visual feed properties, fit/risk signals, and campaign relation before or immediately after any Hashgifted mutation.
9. In `plan` or `dry_run`, record the proposed action and continue without clicking.
10. In `assist`, ask for approval before clicking Shortlist or Decline.
11. For strong fits, click `click_action("Shortlist creator")` and then `wait_for_change("next applicant loaded")`.
12. For hard gate failures or clear brand-safety mismatches, click `click_action("Decline creator")` only after approval, then `wait_for_change("next applicant loaded")`.
13. For incomplete evidence, ambiguous fit, or UI uncertainty, leave the creator in Applied and add a manual review warning.
14. Append action status, evidence, warnings, and Notion page ID to the audit record.

For large multi-campaign runs, batch Instagram/profile capture separately from mutation. Save per-batch artifacts and a progress/decision file before applying any shortlist actions. If background capture is used, make runners self-load the active Hermes env file (for example `/opt/data/.env`) so `BROWSERBASE_API_KEY`, `HASHGIFTED_EMAIL`, and `HASHGIFTED_PASSWORD` are present in foreground, background, and cron contexts.

## Decision Output

For each applicant, record:

```json
{
  "creator": {"name": "Name", "handle": "@handle"},
  "recommendation": "shortlist|decline|manual_review",
  "reason": "short human-readable reason",
  "confidence": "high|medium|low",
  "objective_fit": "audience_awareness|content_library|both|weak",
  "warnings": []
}
```

Use `manual_review` when evidence is incomplete or the creator may be a fit but needs human judgement. Do not use this skill to select a creator.

## Exit Conditions

Stop when any condition is true:

- Requested run limit or stop condition is reached.
- Review limit is reached.
- Applicants queue is empty.
- Remaining applicants visibly fail a hard gate.
- Authentication, rate limit, or page integrity issue appears.
- The adapter cannot unambiguously identify the active creator or action button.

Under-shortlisting is better than lowering the bar.

## Failure Handling

- Instagram unavailable: fall back to TikTok. If both fail, use `manual_review` unless another reliable signal justifies decline.
- Page resort lag: wait for `next applicant loaded`, then re-read the applicant before acting.
- Ambiguous identity or UI shift: stop and flag `manual_review_required`.
- Decline control missing or ambiguous: do not improvise; leave Applied and flag.
- Shortlist action appears to fail: verify the creator's status before clicking again.
- Background or Browserbase capture appears hung: inspect the batch directory for per-handle `capture.json`/thumbnails, the runner summary file, child Node/Python process state, and Browserbase running sessions before killing it. A slow final handle may still complete successfully; if retrying, skip batches whose `results.json` is complete and rerun only missing handles.
- Instagram contact sheet order can differ from the original batch prompt if sheets are built from sorted directories or stale partial directories. Use printed sheet labels plus `results.json` as canonical when recording decisions or applying mutations.

## Reporting

Return a concise summary:

- Shortlisted: count and names.
- Declined: count grouped by reason.
- Manual review: count and why.
- Run progress.
- Warnings and manual review items.
- Audit log location or inline audit record.
