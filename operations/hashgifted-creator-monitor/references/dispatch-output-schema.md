# Dispatch Output Schema

Use this when emitting the monitor's dispatch plan. The plan is a list of items, one per creator, ordered by priority.

## Item Schema

```json
{
  "creator": {
    "name": "Creator Name",
    "handle": "@handle",
    "notion_id": "optional"
  },
  "campaign": {
    "name": "Campaign Name",
    "hashgifted_url": "https://brands.hashgifted.com/...",
    "notion_id": "optional"
  },
  "current_state": "Applied",
  "matched_rule": "Applied, not reviewed",
  "dispatch": "hashgifted-creator-shortlist",
  "priority": 5,
  "reason": "New applicant with strong aesthetic fit signals; needs qualification.",
  "confidence": "high",
  "evidence": [
    {"label": "campaign_context", "type": "screenshot", "ref": "path-or-runtime-url"},
    {"label": "thread_excerpt", "type": "text", "ref": "redacted excerpt"}
  ],
  "warnings": []
}
```

## Field Rules

- `creator.handle` must include the leading `@`. If unknown, set to `null` and add `creator_identity_ambiguous` to warnings.
- `current_state` is the monitor's interpretation, not necessarily the literal Hashgifted label. Use one of: `Applied`, `Shortlisted`, `Selected`, `AwaitingReply`, `PastDeadline`, `StoryPosted`, `Posted`, `Delivered`, `Ghosted`.
- `matched_rule` must quote a row label from `hashgifted-ops-manager/references/lifecycle.md` verbatim.
- `dispatch` must be one of: `hashgifted-creator-shortlist`, `hashgifted-creator-select`, `hashgifted-content-capture`, `hashgifted-story-capture`, `hashgifted-creator-close`, `nudge`, `manual_review`.
- `priority` is the numeric rank from the Dispatch Priority section in `SKILL.md`. Lower numbers are higher priority.
- `confidence` reflects how certain the monitor is about the state read, not the desirability of acting. Use `low` when evidence is incomplete.
- `evidence` should include at least one screenshot reference for any dispatch item that names a high-risk downstream action (`hashgifted-creator-select`, `hashgifted-creator-close`).
- `warnings` use the codes in `hashgifted-ops-manager/references/audit-log.md`.

## One Item Per Creator Per Cycle

If a creator matches more than one lifecycle row, emit only the highest-priority match. The next sweep will pick up subsequent states.

## Plan Wrapper

```json
{
  "run_id": "2026-05-10T09-45-00Z_hashgifted_monitor",
  "mode": "assist",
  "scope": "all_active",
  "caps": {"creators_per_run": 25, "actions_per_creator": 1},
  "campaigns_swept": [
    {"name": "Campaign A", "hashgifted_url": "https://...", "creators_evaluated": 12}
  ],
  "items": [
    /* dispatch items, sorted by priority then by deadline proximity */
  ],
  "manual_review": [],
  "warnings": [],
  "stopped_reason": "creators_cap_reached|list_exhausted|no_campaigns_in_scope|auth_required|notion_unreachable|adapter_gap|schema_gap"
}
```

## Consumer Contract

Downstream skills read the dispatch plan and must:

- Re-confirm creator identity from the live page before any high-risk action.
- Re-read campaign status to ensure the dispatched state is still current.
- Treat `confidence: low` as a stop-and-ask signal, not a green light.
- Honour their own run mode independently of the monitor's mode.
