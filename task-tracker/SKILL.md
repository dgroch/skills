---
name: task-tracker
description: Paperclip SEO workflow for Task Tracker. Use this skill when you need to run structured work for Task Tracker, including planning, monitoring, analysis, and execution handoffs.
---

# Task Tracker (Paperclip)

This skill was adapted from the CSTMR SEO specialist system for Paperclip AI.

Paperclip path mapping:
- Treat any `tracker/` paths below as relative to your Paperclip project workspace data directory.
- Keep file structures and schemas consistent across runs so other SEO skills can consume outputs.
- Replace any references to `agent.yaml` routing with your Paperclip notification or orchestration settings.


## Purpose

Manage the persistent state file (`tracker/state.json`). This is the agent's memory and coordination layer. Every cron run begins by reading state and ends by writing it.

Heavy data (crawl results, keyword universes, backlink inventories) lives in `tracker/data/{skill}/` — not in state.json. The state file holds only OKRs, tasks, alerts, and metadata timestamps.

## Tools Required

- File system (read/write JSON)
- `config/budgets.yaml` (for API usage tracking)

## Pre-conditions (Every Read)

1. Validate `tracker/state.json` against `tracker/schema/state.v2.schema.json`
2. If validation fails:
   a. Log corruption alert
   b. Scan `tracker/backups/` for most recent file that passes validation
   c. Restore it as `tracker/state.json`
   d. Add alert to restored state: `{ severity: "critical", type: "state_corruption", restored_from: "{backup_filename}" }`
3. If no valid backup exists, create fresh state from schema defaults and add critical alert

## Post-conditions (Every Write)

1. Validate the state about to be written against schema
2. Create backup: `tracker/backups/state_{ISO8601_timestamp}.json`
3. Write `tracker/state.json`
4. Prune backups to keep only 7 most recent
5. Release lock

## Modes

### `read`

Load and return the current state. Called at the start of every cron run.

**Steps:**
1. Acquire lock (`tracker/.lock`). If locked, wait up to 60s, then fail.
2. Read `tracker/state.json`
3. Validate against schema (see pre-conditions)
4. Return parsed state

### `write`

Persist updated state. Called at the end of every cron run.

**Steps:**
1. Validate state (see post-conditions)
2. Write backup, then state file
3. Release lock

### `init`

Bootstrap step 9. Populate initial OKRs and tasks from findings in steps 1–8.

**Steps:**
1. Read bootstrap findings from `tracker/data/{skill}/` directories
2. Create OKRs based on identified priorities (technical health, keyword coverage, content gaps)
3. Create tasks from actionable findings (critical issues, quick wins, strategic items)
4. Set all metadata timestamps from bootstrap step outputs
5. Write state

### `create_task`

Add a new task to the tracker.

**Required fields:**
- `id`: Auto-generated `task-{NNN}`
- `title`: What needs to be done
- `skill`: Which skill created this
- `type`: One of `audit`, `fix`, `research`, `brief`, `monitor`, `report`, `implement`
- `priority`: One of `critical`, `high`, `medium`, `low`
- `status`: Initial status (usually `pending`)
- `goal_id`: Which OKR this supports (nullable for ad-hoc tasks)

**Optional fields:**
- `impact_estimate`: Expected traffic/ranking impact
- `effort_estimate`: S/M/L
- `blocked_by`: Task ID or description
- `notes`: Context

**Invariants:**
- No duplicate task IDs
- Every task with a `goal_id` must reference a valid OKR
- `created_at` and `updated_at` set automatically

### `update_task`

Change task status or fields.

**Status transitions:**
```
pending → in_progress → completed
                ↓
             blocked (requires blocked_by reason)
                ↓
           escalated (triggers notification per OPERATOR.md)

Brief workflow:
pending → in_progress → handoff_copywriter → copy_review → approved | revision_needed

Dev workflow:
pending → in_progress → handoff_dev → completed | blocked
```

**Rules:**
- `updated_at` must change on every update
- Moving to `escalated` creates an alert
- Moving to `completed` updates the parent OKR's key result `current` value if applicable

### `query`

Filter tasks by skill, status, priority, goal, or type. Used by skills to find their relevant work.

### `create_alert`

Add an alert to `state.json → alerts[]`.

**Fields:**
- `id`: Auto-generated `alert-{NNN}`
- `severity`: `critical`, `high`, `medium`, `low`
- `type`: `anomaly`, `state_corruption`, `budget_warning`, `escalation`, `technical_issue`
- `description`: What happened
- `recommendation`: What to do about it
- `requires_action`: Boolean
- `created_at`: Timestamp
- `resolved_at`: Null until resolved

**Side effect:** If severity is `critical` or `high`, trigger notification per `agent.yaml → notifications.routing`.

### `log_api_call`

Append to `tracker/api_usage.json` and check budget.

**Steps:**
1. Read current usage from `tracker/api_usage.json`
2. Compute month-to-date spend for this API
3. Check against `config/budgets.yaml` thresholds:
   - Below circuit_breaker_pct → proceed
   - At circuit_breaker_pct → log warning, allow call but flag degradation mode
   - At hard_stop_pct → refuse call, return budget_exhausted error
4. If call proceeds, log: `{ api, endpoint, timestamp, estimated_cost_usd, response_status }`

### `prune`

Remove completed tasks older than 90 days. Archive to `tracker/data/task-tracker/archive_{quarter}.json`.
