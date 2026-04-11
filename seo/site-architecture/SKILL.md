---
name: site-architecture
description: Paperclip SEO workflow for Site Architecture. Use this skill when you need to design or optimize URL hierarchy, internal linking, and redirect strategy.
---


# Site Architecture (Paperclip)

This skill was adapted from the CSTMR SEO specialist system for Paperclip AI.

Paperclip path mapping:
- Treat any `tracker/` paths below as relative to your Paperclip project workspace data directory.
- Keep file structures and schemas consistent across runs so other SEO skills can consume outputs.
- Replace any references to `agent.yaml` routing with your Paperclip notification or orchestration settings.


## Purpose

Define and maintain the optimal URL hierarchy, internal linking structure, and information architecture. Platform constraints from `config/client.yaml → shopify`.

## Tools Required

- Firecrawl (page inventory, internal link extraction)
- Shopify Admin API (redirect management, navigation structure)
- Google Search Console (crawl stats, index coverage)
- Ahrefs (internal link equity, page authority)

## Data Storage

- `tracker/data/architecture/sitemap_{date}.json` — URL hierarchy
- `tracker/data/architecture/internal_links_{date}.json` — link graph
- `tracker/data/architecture/redirects.json` — current redirect inventory

## Modes

### `mapping`

**When:** Bootstrap step 7, quarterly review.
**Pre-conditions:** Crawl data exists (step 1).

**Steps:**
1. **URL inventory:** Extract all URLs from crawl data, classify by type (product, collection, blog, page, utility, other)
2. **Hierarchy map:** Build tree from URL paths. Identify:
   - Depth: how many clicks from homepage to each page
   - Orphan pages: no internal links pointing to them
   - Deep pages: >3 clicks from homepage
3. **Internal link graph:**
   - For each page: outbound internal links, inbound internal links
   - Compute internal PageRank / link equity distribution
   - Identify pages receiving disproportionate equity vs. their importance
4. **Navigation audit:** Crawl main nav, footer nav, sidebar nav
   - Are key pages (collections, pillars) in main nav?
   - Is nav depth appropriate?
5. **Structural issues:**
   - Orphan pages (0 internal links)
   - Thin hub pages (collection/category pages with <3 products/posts)
   - Duplicate paths (product accessible via /products/ and /collections/x/products/)
   - Missing breadcrumbs
6. Write to `tracker/data/architecture/`
7. Create tasks for structural issues

### `restructure`

**When:** Ad-hoc, when architecture changes are warranted.
**Decision level:** Recommend — operator approves before implementation.

**Steps:**
1. Propose URL hierarchy changes with rationale
2. Plan pillar page structure (based on content-strategy pillar definitions)
3. Internal linking strategy:
   - Every blog post links to ≥1 relevant collection
   - Collections link to related collections
   - Products link to parent collection
   - Pillar pages link to all cluster pages and vice versa
   - Footer includes top-level collections and pillar pages
   - Breadcrumbs reflect hierarchy
4. Map all required redirects (old URL → new URL)
5. Risk assessment: which URLs have backlinks or rankings that could be lost?
6. Present plan to operator for approval
7. If approved, create implementation tasks (type: `handoff_dev` for theme changes, direct Shopify API for redirects)

### `redirect_management`

**When:** Part of restructure, or when crawl detects 404s on previously-linked URLs.
**Decision level:** Autonomous for fixing broken redirects, Recommend for new redirect rules.

**Steps:**
1. Audit existing redirects via Shopify API:
   - Chains (A→B→C) — should be A→C
   - Loops (A→B→A)
   - Targets that are 404
   - Unnecessary redirects (old URL no longer linked anywhere)
2. For broken redirects: fix via Shopify API (autonomous)
3. For new redirects: create task with recommendation (requires approval if URL has traffic/rankings)
4. Verify after implementation: crawl redirect targets, confirm 200 status
