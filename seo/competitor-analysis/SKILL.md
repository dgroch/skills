---
name: competitor-analysis
description: Paperclip SEO workflow for Competitor Analysis. Use this skill when you need to run structured work for Competitor Analysis, including planning, monitoring, analysis, and execution handoffs.
---

# Competitor Analysis (Paperclip)

This skill was adapted from the CSTMR SEO specialist system for Paperclip AI.

Paperclip path mapping:
- Treat any `tracker/` paths below as relative to your Paperclip project workspace data directory.
- Keep file structures and schemas consistent across runs so other SEO skills can consume outputs.
- Replace any references to `agent.yaml` routing with your Paperclip notification or orchestration settings.


## Purpose

Monitor and analyse SEO competitors. Identify their strategies, strengths, weaknesses, and opportunities to outperform. Competitor tiers from `config/client.yaml → competitors`.

## Tools Required

- Ahrefs (domain comparison, keyword gap, backlink gap, content explorer)
- SerpAPI (SERP share analysis, local pack)
- Firecrawl (competitor page analysis for deep dives)

## Data Storage

- `tracker/data/competitors/inventory.json` — competitor list with baseline metrics
- `tracker/data/competitors/monthly_{date}.json` — monthly comparison snapshots
- `tracker/data/competitors/deep_dive_{domain}_{date}.json` — individual deep dives

## Modes

### `discovery`

**When:** Bootstrap step 5.
**Pre-conditions:** Keyword clusters (step 3) and backlink data (step 4) exist.

**Steps:**
1. **Ahrefs organic competitors:** domains competing for the same keywords
2. **SERP analysis** (SerpAPI): for top 10 tier_1 keywords, who appears consistently?
3. **Local pack analysis:** for geo-modified keywords, who appears in local 3-pack?
4. **Select top competitors:** 3–5 most relevant, classified by tier (from `config/client.yaml → competitors`)
5. **Baseline each:**
   - Ahrefs: DR, estimated organic traffic, keywords in top 10, referring domains
   - Content: page count, blog frequency, content types
   - Backlinks: referring domain count, top linking domains
6. **Populate `config/client.yaml → competitors` tiers** with discovered domains
7. Write to `tracker/data/competitors/inventory.json`

**Competitor data schema:**
```json
{
  "competitor_id": "comp-001",
  "domain": "example.com",
  "name": "Example Florist",
  "tier": "tier_1_direct",
  "metrics": {
    "dr": 0,
    "organic_traffic_est": 0,
    "keywords_top_10": 0,
    "referring_domains": 0,
    "updated_at": "ISO8601"
  },
  "metrics_history": [],
  "top_pages": [],
  "top_keywords": [],
  "content_gap_keywords": [],
  "backlink_gap_domains": [],
  "notes": ""
}
```

### `monthly`

**When:** 10th of month.
**Pre-conditions:** Competitor inventory exists.

**Steps:**
1. For each tracked competitor:
   - Ahrefs: current DR, traffic, keywords, referring domains
   - Compare to previous month (from metrics_history)
   - Flag significant changes: DR ↑/↓3+, traffic ↑/↓20%, new keywords in top 10
2. **New content detection:** Ahrefs content explorer — recent pages from each competitor
   - Identify new topics they're targeting that the client isn't
3. **New backlink sources:** referring domains gained by competitors in last 30 days
   - Cross-reference with client's backlink gap — new link building opportunities?
4. **SERP share analysis:** for tracked keyword clusters, count how often each competitor appears in top 10
   - Trend: is the client gaining or losing SERP share relative to competitors?
5. **Strategic insights:**
   - Competitor launched new content type? (e.g., suburb pages, guides)
   - Competitor gained significant links from a source we could target?
   - Competitor's traffic spiked? What drove it?
6. Write monthly snapshot
7. Feed insights into content-strategy and backlink-management as applicable

**Budget degradation:** At Ahrefs circuit-breaker, check only tier_1 competitors. At hard-stop, skip entirely and note gap in monthly report.

### `deep_dive`

**When:** Quarterly, or when a competitor makes a significant move (detected in monthly check).
**Purpose:** Full analysis of a single competitor.

**Steps:**
1. Firecrawl: crawl competitor site (key sections, not exhaustive — budget-aware)
2. Content audit: page types, content length, topic coverage, publishing frequency
3. Keyword overlap: shared keywords, keywords they rank for that client doesn't
4. Backlink comparison: top linking domains, anchor text strategy, link velocity
5. Technical comparison: site speed, mobile experience, schema usage, site structure
6. Produce competitive brief:
   - Their strengths (what to learn from)
   - Their weaknesses (what to exploit)
   - Specific opportunities for the client
7. Create tasks from opportunities
