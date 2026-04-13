---
name: seo-analytics-reporting
description: Paperclip SEO workflow for Analytics Reporting. Use this skill when you need to monitor organic performance, detect anomalies, and produce SEO reports with actionable insights.
---


# Analytics & Reporting (Paperclip)

This skill was adapted from the CSTMR SEO specialist system for Paperclip AI.

Paperclip path mapping:
- Treat any `tracker/` paths below as relative to your Paperclip project workspace data directory.
- Keep file structures and schemas consistent across runs so other SEO skills can consume outputs.
- Replace any references to `agent.yaml` routing with your Paperclip notification or orchestration settings.


## Purpose

Track, analyse, and report on organic search performance. Detect anomalies early. Provide actionable insights, not data dumps. Notification routing from `agent.yaml`.

## Tools Required

- Google Search Console (search analytics)
- GA4 Data API (traffic, conversions)
- Ahrefs (domain metrics for monthly/quarterly context)

## Data Storage

- `tracker/data/analytics/pulse_{date}.json` — daily pulse snapshots
- `tracker/data/analytics/baselines.json` — rolling averages and benchmarks
- `tracker/reports/weekly_{date}.json` — weekly summaries
- `tracker/reports/monthly_{date}.json` — monthly reports
- `tracker/reports/dashboard.json` — latest status for dashboard notification channel

## Modes

### `baseline`

**When:** Bootstrap step 2.
**Pre-conditions:** GSC and GA4 credentials validated.

**Steps:**
1. Pull 90 days of GSC data: clicks, impressions, CTR, average position — by day, by query (top 500), by page (all)
2. Pull 90 days of GA4 data: organic sessions, users, conversions, revenue — by day, by landing page
3. Compute baselines:
   - 7-day rolling averages (for daily anomaly detection)
   - 30-day averages (for monthly comparison)
   - 90-day totals (for quarterly comparison)
4. Identify historical patterns: weekday vs weekend variance, seasonal trends if visible
5. Write to `tracker/data/analytics/baselines.json`
6. Store raw data for trend analysis

### `pulse`

**When:** Daily at 07:00.
**Pre-conditions:** Baseline exists.

**Steps:**
1. GSC: yesterday's clicks, impressions, CTR, avg position (note: 2–3 day data lag — use most recent available)
2. GA4: yesterday's organic sessions, conversions, revenue
3. Compare to 7-day rolling average from baselines
4. **Anomaly detection:**
   - Warning: >15% deviation from 7-day average
   - Critical: >30% deviation from 7-day average
5. If anomaly detected:
   - Quick diagnosis: site-wide or specific pages? Specific queries? Device-specific?
   - Check GSC for manual actions
   - Create alert in state.json
   - If critical, trigger traffic-anomaly event (→ technical-audit emergency mode)
6. If no anomaly: write pulse data, update rolling averages, no alert
7. Update `tracker/reports/dashboard.json` with latest metrics

**Budget note:** This mode uses only free APIs (GSC + GA4). No budget constraint.

### `weekly_summary`

**When:** Friday 14:00.
**Pre-conditions:** Daily pulse data for the week exists.

**Steps:**
1. Aggregate week's data:
   - Organic clicks/impressions/CTR/position (GSC, WoW change)
   - Organic sessions/conversions/revenue (GA4, WoW change)
2. Pull from other skills' recent outputs:
   - Technical audit: new/resolved issues (from weekly-crawl)
   - Rank tracking: movements summary (from weekly-ranks)
   - Backlinks: new/lost links (from weekly-backlinks)
   - Content: pipeline status, briefs in progress (from weekly-content-review)
3. Compose summary for operator:

```
## Week of {date}

### Headlines
- {3 biggest wins or positive movements}
- {3 biggest issues or risks}

### Traffic
| Metric | This week | Last week | Change |
|--------|-----------|-----------|--------|
| Clicks | ... | ... | +/-% |
| Impressions | ... | ... | +/-% |
| Sessions | ... | ... | +/-% |
| Conversions | ... | ... | +/-% |

### Rankings
- {movements summary from rank-tracking}

### Issues
- {open critical/high issues from task tracker}

### Content Pipeline
- {briefs pending/in-progress/review/approved}

### Next Week Priorities
- {top 3 tasks by priority}
```

4. Write to `tracker/reports/weekly_{date}.json`
5. Send via notification channel (Slack/dashboard per routing rules)

### `monthly_report`

**When:** Last day of month.
**Pre-conditions:** Full month of pulse data, weekly summaries.

**Steps:**
1. Full month aggregation:
   - GSC: clicks, impressions, CTR, avg position — MoM and YoY
   - GA4: organic sessions, users, conversions, revenue — MoM and YoY
   - Ahrefs: domain rating, referring domains, organic keywords (monthly snapshot)
2. Content performance: top 10 pages by traffic, top 10 by growth, bottom 10 declining
3. Technical health: site health score trend, open issues by severity
4. Backlink profile: DR change, new/lost referring domains, anchor distribution
5. Competitor snapshot: relative position changes (from competitor-analysis)
6. OKR progress: current vs target for each key result
7. Recommendations: top 3 priorities for next month with rationale
8. Write to `tracker/reports/monthly_{date}.json`
9. Send via notification channel (email + dashboard per routing rules)

### `baseline_report`

**When:** Bootstrap step 10.
**Pre-conditions:** All bootstrap steps 1–9 completed.

**Steps:**
1. Compile findings from all bootstrap steps into a single report
2. Structure: current state, key issues, opportunities, 90-day priorities
3. Include baseline metrics that future reports will compare against
4. Write to `tracker/reports/baseline_report.json`
5. Notify operator that bootstrap is complete and agent is operational
