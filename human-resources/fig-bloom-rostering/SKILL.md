---
name: fig-bloom-rostering
description: Paperclip operations workflow for Fig Bloom Rostering. Use this skill when you need to build or optimize weekly staff rosters using Deputy and Shopify inputs within labour budget constraints.
---


# Fig & Bloom Rostering

## Context

Fig & Bloom runs three flower studios. Weekly rosters must stay within **8.5% of projected gross revenue** for labour spend. Revenue comes from Shopify. Scheduling is done in Deputy.

See `references/roster-rules.md` for staff rules, budget formula, and cutting priority.
See `references/deputy-workflow.md` for Deputy API concepts and publishing.

## Credentials (environment variables)

| Variable | Source | Used by |
|---|---|---|
| `DEPUTY_SUBDOMAIN` | env | fetch_roster_inputs.py |
| `DEPUTY_TOKEN` | env | fetch_roster_inputs.py |
| `SHOPIFY_STORE` | env | fetch_revenue.py |
| `SHOPIFY_TOKEN` | env | fetch_revenue.py |

Deputy credentials are already configured. Shopify credentials must be added before revenue fetching works.

## Execution Workflow

### Step 1 — Fetch revenue forecast

```bash
python scripts/fetch_revenue.py
```

Returns: `gross_revenue`, `labour_budget` (= gross × 0.085), and the 7-day period covered.

### Step 2 — Fetch roster inputs from Deputy

```bash
python scripts/fetch_roster_inputs.py [YYYY-MM-DD]
```

Pass the Monday of the target week, or omit to default to next Monday.

Returns: all active employees (with employment type), and approved leave for the week.

### Step 3 — Build the roster

Using the data from steps 1 and 2, build the roster in this order:

1. **Full-timers** (employment_type=1) — fixed 38h/week, schedule as-is
2. **Part-timers** (employment_type=2) — meet each worker's minimum hours
3. **Casuals** (employment_type=3) — fill remaining gaps within budget

Respect availability and remove anyone on approved leave for that week.

Track running labour cost as shifts are added. Compare against `labour_budget`.

### Step 4 — Cut if over budget

If total committed labour > labour_budget:
- Trim casual hours first (never zero out entirely)
- Trim part-timer hours next (only down to minimum commitment)
- Never cut full-timers

### Step 5 — Publish via Deputy API

Once the roster is within budget, publish via Deputy. Staff receive in-app notification.

For publishing API details, refer to `references/deputy-workflow.md` and the deputy-connector skill.

## Key Constraints

- Respect each worker's availability (days unavailable)
- Some staff flagged **"no solo Saturday"** — never roster alone on Saturdays
- Never cut part-timers below their minimum hour commitment
- Keep casuals with at least some hours every week (retention)

## What Good Looks Like

- All three studios covered all trading days
- Labour ≤ 8.5% of forecasted gross revenue
- No availability conflicts, no leave conflicts
- Casuals and part-timers both have meaningful hours
