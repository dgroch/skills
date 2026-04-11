---
name: content-strategy
description: Paperclip SEO workflow for Content Strategy. Use this skill when you need to plan and prioritize an SEO content roadmap and publishing pipeline.
---


# Content Strategy (Paperclip)

This skill was adapted from the CSTMR SEO specialist system for Paperclip AI.

Paperclip path mapping:
- Treat any `tracker/` paths below as relative to your Paperclip project workspace data directory.
- Keep file structures and schemas consistent across runs so other SEO skills can consume outputs.
- Replace any references to `agent.yaml` routing with your Paperclip notification or orchestration settings.


## Purpose

Plan, prioritise, and manage the content pipeline. Produce content briefs for the Copywriter agent. Monitor published content performance. Seasonal calendar and segment context from `config/client.yaml`.

## Tools Required

- Ahrefs (content gap, competitor content)
- Google Search Console (page performance)
- GA4 (traffic, conversions by landing page)
- Shopify Admin API (product/collection metadata)

## Data Storage

- `tracker/data/content-strategy/calendar.json` — editorial calendar
- `tracker/data/content-strategy/inventory_{date}.json` — content audit results
- `tracker/data/content-strategy/gaps.json` — current content gaps

## Modes

### `plan`

**When:** Bootstrap step 8, or after major keyword refresh.
**Pre-conditions:** Keyword clusters, competitor intel, and site architecture data exist.

**Steps:**
1. **Ingest gaps:**
   - Load unmapped keyword clusters from `tracker/data/keywords/clusters.json`
   - Load competitor content intel from `tracker/data/competitors/`
   - Identify topics competitors cover that the client doesn't
2. **Map content types:**
   - Blog post: informational keywords, how-to, guides
   - Landing page: commercial investigation keywords, service pages
   - Product page: transactional keywords (existing products)
   - Collection page: category-level keywords (existing collections)
   - Pillar page: high-volume head terms with cluster of supporting content
3. **Pillar-cluster architecture:**
   - Identify 3–5 pillar topics from tier 1 keywords
   - Map supporting cluster content (blog posts, guides) that link to each pillar
   - Ensure every cluster page has a clear internal link path to its pillar
4. **Seasonal overlay:**
   - Load `config/client.yaml → seasonal_calendar`
   - For each upcoming event within `lead_weeks`, check if content exists
   - If not, add to calendar with deadline = event date minus lead_weeks
5. **Prioritise:**
   - **Critical:** Revenue keyword gap + seasonal event <6 weeks away
   - **High:** Top-50 keyword gap, underperforming rewrite candidate
   - **Medium:** Authority/informational content, lower-volume gaps
   - **Low:** Nice-to-have, backlog
6. Build editorial calendar with: content_id, type, target_keyword, cluster_id, priority, deadline, status, assigned_to
7. Create content briefs for top-priority items (via copywriter-handoff skill)
8. Write calendar to `tracker/data/content-strategy/calendar.json`

### `review`

**When:** Thursday 06:00 (weekly-content-review cron).
**Pre-conditions:** Calendar exists, GSC/GA4 accessible.

**Steps:**
1. **Performance check (last 30 days):**
   - GSC: clicks, impressions, CTR, position for content pages
   - GA4: sessions, conversions, bounce rate for content pages
   - Flag underperformers: pages ranking 11–20 (striking distance), pages with declining traffic (>20% MoM drop)
2. **Pipeline status:**
   - Check brief statuses in `tracker/briefs/`
   - Count: pending, in_progress, handoff_copywriter, copy_review, approved, revision_needed
   - Flag stale briefs (handoff_copywriter for >7 days with no progress)
3. **Upcoming needs:**
   - 2-month lookahead on seasonal calendar
   - Identify content that needs to be started now to meet deadlines
4. **Content freshness:**
   - Flag pages not updated in >6 months that are ranking but declining
   - Create refresh briefs for candidates
5. Update calendar statuses, create/update tasks

### `audit`

**When:** Quarterly (quarterly-strategy cron).
**Pre-conditions:** Full crawl data, keyword universe, competitor data.

**Steps:**
1. Full content inventory from crawl data (every page with content)
2. Classify: product, collection, blog, landing page, utility, other
3. Map to keyword clusters — coverage analysis
4. Cannibalisation detection: multiple pages targeting same cluster
5. Internal linking audit: are pillar-cluster links in place?
6. Competitor content comparison: what do they cover that we don't?
7. Pruning candidates: pages with zero traffic, no keywords, no internal links for >6 months
8. Produce quarterly content strategy document with recommendations
9. Revise OKRs if warranted (recommend to operator)
