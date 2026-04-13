---
name: seo-technical-audit
description: Paperclip SEO workflow for Technical Audit. Use this skill when you need to audit crawl, indexation, and performance issues and prioritize technical fixes.
---


# Technical Audit (Paperclip)

This skill was adapted from the CSTMR SEO specialist system for Paperclip AI.

Paperclip path mapping:
- Treat any `tracker/` paths below as relative to your Paperclip project workspace data directory.
- Keep file structures and schemas consistent across runs so other SEO skills can consume outputs.
- Replace any references to `agent.yaml` routing with your Paperclip notification or orchestration settings.


## Purpose

Crawl the client site, identify technical SEO issues, and log them to the task tracker with severity, impact, and recommended fixes.

All client-specific details (domain, platform constraints) come from `config/client.yaml`.

## Tools Required

- Firecrawl (crawling, page extraction)
- Google Search Console (index coverage, manual actions)
- PageSpeed Insights (Core Web Vitals)
- Shopify Admin API (redirect management, meta verification)

## Data Storage

- `tracker/data/technical-audit/crawl_{date}.json` — raw crawl data
- `tracker/data/technical-audit/cwv_{date}.json` — CWV results
- `tracker/data/technical-audit/latest.json` — symlink/copy of most recent crawl summary

## Modes

### `baseline`

**When:** Bootstrap step 1.
**Pre-conditions:** Pre-flight validation passed. No prior crawl data exists.

**Steps:**
1. Fetch sitemap from `{domain}/sitemap.xml`
2. Full site crawl via Firecrawl — all discoverable pages
3. For each page, extract: URL, status code, title, meta description, H1, canonical, robots directives, internal links, external links, images (alt text presence), structured data
4. Run PageSpeed Insights on top 10 pages by type (homepage, top collections, top products, top blog posts)
5. Check GSC: index coverage status, manual actions, mobile usability
6. Classify issues by severity:
   - **Critical:** 5xx errors, noindex on key pages, manual actions, blocked by robots.txt, missing canonical
   - **High:** 4xx errors on linked pages, duplicate titles/H1s, missing meta descriptions on key pages, redirect chains >2 hops, CWV failures
   - **Medium:** Missing alt text, thin content (<300 words on key pages), orphan pages, non-HTTPS resources
   - **Low:** Suboptimal title length, missing schema where expected, minor CWV warnings
7. Write crawl data to `tracker/data/technical-audit/crawl_{date}.json`
8. Write CWV data to `tracker/data/technical-audit/cwv_{date}.json`
9. Create tasks in state.json for each issue found (grouped — not one task per URL)

**Output schema:**
```json
{
  "crawl_date": "ISO8601",
  "domain": "from config",
  "pages_crawled": 0,
  "summary": {
    "total_pages": 0,
    "by_status": { "200": 0, "301": 0, "404": 0, "500": 0 },
    "issues_by_severity": { "critical": 0, "high": 0, "medium": 0, "low": 0 }
  },
  "issues": [],
  "cwv": { "pages_tested": 0, "pass_rate": 0, "results": [] },
  "pages": []
}
```

### `weekly`

**When:** Monday 06:00 (weekly-crawl cron).
**Pre-conditions:** At least one prior crawl exists.

**Steps:**
1. Load previous crawl from `tracker/data/technical-audit/latest.json`
2. Crawl site via Firecrawl (use sitemap lastmod to prioritise changed pages if budget-constrained)
3. Delta analysis:
   - New pages (in current, not in previous)
   - Removed pages (in previous, not in current)
   - Status code changes
   - Title/meta/H1 changes
   - New/resolved issues
4. Write crawl data
5. Create/update tasks for new issues; close tasks for resolved issues
6. If any critical issue is new, create alert

**Budget degradation:** If Firecrawl budget at circuit-breaker, crawl only pages with changed lastmod in sitemap. If at hard-stop, skip crawl entirely and log.

### `deep`

**When:** 1st of month (monthly-technical-audit cron).
**Pre-conditions:** Weekly crawl data exists.

**Steps:**
1. Everything in `weekly` mode, plus:
2. Full CWV audit on top 20 pages
3. Internal link equity analysis (pages by inlink count, orphan detection)
4. Index bloat check (indexed pages vs. crawled pages vs. sitemap pages)
5. Redirect audit via Shopify API (chains, loops, 404 targets)
6. Canonical validation (self-referencing, cross-domain, conflicting signals)
7. Schema validation on all pages with structured data
8. Compute site health score: weighted average of (CWV pass rate × 0.3) + (critical issues × 0.3) + (index coverage × 0.2) + (internal linking score × 0.2)
9. Compare health score to previous month
10. Update monthly-technical-audit task with findings

### `emergency`

**When:** Triggered by traffic-anomaly event (>30% drop).
**Pre-conditions:** Anomaly alert exists in state.json.

**Steps:**
1. Check GSC for manual actions — if found, escalate immediately
2. Check GSC index coverage for sudden changes
3. Verify robots.txt hasn't changed (fetch and compare to cached version)
4. Check if site is up (HTTP status of homepage, key pages)
5. Scan for canonical changes on top traffic pages
6. Check for algorithm update signals (SERP volatility)
7. Determine scope: site-wide vs. specific pages/sections
8. Write findings to alert, recommend next action
9. If cause identified, create targeted fix task. If not, escalate to operator.
