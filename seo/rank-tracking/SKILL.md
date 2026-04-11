---
name: rank-tracking
description: Paperclip SEO workflow for Rank Tracking. Use this skill when you need to run structured work for Rank Tracking, including planning, monitoring, analysis, and execution handoffs.
---

# Rank Tracking (Paperclip)

This skill was adapted from the CSTMR SEO specialist system for Paperclip AI.

Paperclip path mapping:
- Treat any `tracker/` paths below as relative to your Paperclip project workspace data directory.
- Keep file structures and schemas consistent across runs so other SEO skills can consume outputs.
- Replace any references to `agent.yaml` routing with your Paperclip notification or orchestration settings.


## Purpose

Monitor keyword ranking positions and SERP feature presence for priority keywords. Detect movements early and trigger appropriate responses.

## Tools Required

- SerpAPI (real-time SERP checks)
- Google Search Console (position data — free fallback)
- Ahrefs (broad position changes for deep mode)

## Data Storage

- `tracker/data/keywords/tracked_clusters.json` — cluster definitions and tracking config
- `tracker/data/rankings/weekly_{date}.json` — weekly ranking snapshots
- `tracker/data/rankings/trends.json` — rolling position history per cluster

## Configuration

Tracked clusters are defined in `tracker/data/keywords/tracked_clusters.json`:

```json
{
  "clusters": [
    {
      "cluster_id": "cluster-001",
      "primary_keyword": "flower delivery melbourne",
      "check_keywords": ["flower delivery melbourne", "flowers delivered melbourne", "melbourne florist delivery"],
      "target_url": "/collections/flower-delivery",
      "priority": "tier_1",
      "current_position": null,
      "best_position": null,
      "serp_features": [],
      "our_serp_features": []
    }
  ]
}
```

**SerpAPI parameters** (from `config/client.yaml → market`):
- engine: google
- location: `config/client.yaml → market.serp_location`
- gl: `config/client.yaml → market.serp_gl`
- hl: `config/client.yaml → market.serp_hl`
- device: `config/client.yaml → market.primary_device`
- num: 20

**Call volume per weekly run:** `count(clusters) × avg(check_keywords per cluster) × devices`. With 15 clusters × 3 keywords × 1 device = ~45 calls. Monitor against `config/budgets.yaml → apis.serpapi`.

## Modes

### `weekly`

**When:** Tuesday 06:00.
**Pre-conditions:** tracked_clusters.json exists with ≥1 cluster.

**Steps:**
1. For each tracked cluster, for each check_keyword:
   - SerpAPI: search with configured parameters
   - Find client domain in results (position 1–20, or "not found")
   - Record SERP features present (featured snippet, PAA, local pack, images, video, shopping)
   - Record which SERP features the client owns
   - Record top 3 competitors for this query
2. Classify movements vs previous week:
   - ↑5+ = **big win** (celebrate in weekly summary)
   - ↑1–4 = **improvement**
   - ±0 = **stable**
   - ↓1–4 = **monitor** (note in weekly summary)
   - ↓5+ = **investigate** (create investigation task)
   - Dropped out of top 20 = **critical** (create alert, trigger investigation)
   - New entry in top 20 = **new ranking** (note in weekly summary)
3. Cannibalisation detection: if a different URL ranks for a keyword than the target_url, flag it
4. Write to `tracker/data/rankings/weekly_{date}.json`
5. Update `tracker/data/rankings/trends.json` with position history
6. Update cluster `current_position` and `best_position` in tracked_clusters.json
7. Create tasks/alerts for significant movements

**Budget degradation:** At SerpAPI circuit-breaker (80%), check only tier_1 priority clusters. At hard-stop (95%), skip SerpAPI entirely — use GSC average position data as fallback (less precise, 2–3 day lag, but free).

### `deep`

**When:** Monthly (alongside monthly-keyword-refresh), or triggered by algorithm-update event.
**Pre-conditions:** Weekly data exists.

**Steps:**
1. Everything in `weekly` mode, plus:
2. Desktop rankings in addition to mobile (doubles SerpAPI calls — budget-check first)
3. Check secondary keywords in each cluster (beyond the main check_keywords)
4. Ahrefs: broad position changes for domain (new keywords in top 50, lost from top 50)
5. Update tracked_clusters.json: add new high-priority clusters if discovered, remove irrelevant ones
6. If triggered by algorithm update: compare pre/post movements, assess impact by tier, recommend response

### `investigation`

**When:** Triggered by significant decline (↓5+ or dropped out).
**Purpose:** Diagnose why a specific keyword/cluster declined.

**Steps:**
1. Check ranking URL: is it still live? Status code? Has content changed?
2. Check for cannibalisation: is a different URL now ranking?
3. SerpAPI: who moved up? New competitor or existing competitor improved?
4. GSC: query-level data for the keyword (clicks, impressions, CTR trend)
5. Check for algorithm update correlation
6. Produce diagnosis with recommended action:
   - Content issue → create brief for refresh/rewrite
   - Technical issue → create fix task
   - Competitor improvement → assess competitive response
   - Algorithm shift → monitor and assess broader impact
