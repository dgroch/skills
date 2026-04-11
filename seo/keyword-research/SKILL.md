---
name: keyword-research
description: Paperclip SEO workflow for Keyword Research. Use this skill when you need to discover, cluster, and prioritize keyword opportunities by intent and impact.
---


# Keyword Research (Paperclip)

This skill was adapted from the CSTMR SEO specialist system for Paperclip AI.

Paperclip path mapping:
- Treat any `tracker/` paths below as relative to your Paperclip project workspace data directory.
- Keep file structures and schemas consistent across runs so other SEO skills can consume outputs.
- Replace any references to `agent.yaml` routing with your Paperclip notification or orchestration settings.


## Purpose

Discover, analyse, cluster, and map keywords. Feed into content strategy and on-page specs. All keyword tiers and market context come from `config/client.yaml`.

## Tools Required

- Ahrefs (keyword explorer, content gap, keyword difficulty)
- Google Search Console (existing query performance)
- SerpAPI (SERP feature detection, PAA)

## Data Storage

- `tracker/data/keywords/universe_{date}.json` — full keyword inventory
- `tracker/data/keywords/clusters.json` — current cluster definitions
- `tracker/data/keywords/tracked_clusters.json` — clusters configured for rank tracking
- `tracker/data/keywords/gaps_{date}.json` — content gap analysis results

## Modes

### `discovery`

**When:** Bootstrap step 3.
**Pre-conditions:** Crawl data (step 1) and GSC baseline (step 2) exist.

**Steps:**
1. **Seed extraction:**
   - Pull all ranking queries from GSC baseline (impressions >0)
   - Extract title/H1/meta keywords from crawl data
   - Load keyword tier examples from `config/client.yaml → keyword_tiers`
2. **Expansion** (Ahrefs):
   - For each seed keyword: related keywords, also rank for, questions
   - Apply market filters: country from `config/client.yaml → market.serp_gl`, language from `serp_hl`
   - De-duplicate
3. **Metrics collection** (Ahrefs):
   - Volume, keyword difficulty (KD), CPC, SERP features, parent topic
   - Batch calls where possible to conserve budget
4. **Clustering:**
   - Group by semantic similarity + SERP overlap (keywords with >3 shared top-10 URLs = same cluster)
   - Assign intent: transactional, commercial_investigation, informational, local, navigational
   - Label each cluster with a primary keyword (highest volume in cluster)
5. **Page mapping:**
   - Map each cluster to existing URL (from crawl data) or flag as `unmapped` (content gap)
   - Where multiple clusters map to same URL, check for cannibalisation risk
6. **Prioritisation:**
   - Score = (Volume × Intent_Weight × Relevance) / (KD × Effort_Estimate)
   - Intent weights: transactional=3, commercial_investigation=2.5, local=2, informational=1, navigational=0.5
   - Relevance: 1.0 for tier 1, 0.7 for tier 2, 0.4 for tier 3
7. **Configure rank tracking:**
   - Select top clusters (max 15 initially to control SerpAPI budget)
   - For each: primary keyword + up to 4 secondary keywords
   - Write to `tracker/data/keywords/tracked_clusters.json`
8. Write all data to `tracker/data/keywords/`
9. Create tasks for content gaps (unmapped clusters with priority score above threshold)

**Budget note:** Discovery is the most Ahrefs-intensive mode. Monitor usage via task-tracker `log_api_call`. If approaching circuit-breaker, reduce expansion depth (fewer related keywords per seed).

### `refresh`

**When:** 5th of month (monthly-keyword-refresh cron).
**Pre-conditions:** Discovery has run at least once.

**Steps:**
1. Load current keyword universe
2. Pull last 30 days of GSC query data — identify new queries not in universe
3. Ahrefs: check for volume/KD changes on existing keywords (batch, top priority clusters only)
4. Add new keywords, re-cluster if needed
5. Re-run gap analysis: new unmapped clusters → content opportunities
6. Update tracked_clusters.json if new high-priority clusters emerged
7. Create briefs for top new gaps (via content-strategy skill)
8. Write updated data

**Budget degradation:** At circuit-breaker, refresh only tier 1 keywords. At hard-stop, use GSC data only (no Ahrefs calls).

### `targeted`

**When:** Ad-hoc, triggered by other skills or operator request.
**Purpose:** Research a specific topic, URL, product, or keyword cluster.

**Steps:**
1. Accept input: keyword, URL, topic, or product name
2. Ahrefs: keyword explorer for the target + related keywords
3. SerpAPI: current SERP for target keyword (detect features, competitors, content types)
4. Map to existing clusters or create new one
5. Return findings (don't auto-create tasks — this is research)
