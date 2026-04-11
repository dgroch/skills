---
name: on-page-specs
description: Paperclip SEO workflow for On-Page Specs. Use this skill when you need to run structured work for On-Page Specs, including planning, monitoring, analysis, and execution handoffs.
---

# On-Page Specs (Paperclip)

This skill was adapted from the CSTMR SEO specialist system for Paperclip AI.

Paperclip path mapping:
- Treat any `tracker/` paths below as relative to your Paperclip project workspace data directory.
- Keep file structures and schemas consistent across runs so other SEO skills can consume outputs.
- Replace any references to `agent.yaml` routing with your Paperclip notification or orchestration settings.


## Purpose

Define and audit on-page SEO elements for every page. Produce specifications — not copy. The Copywriter agent writes actual text to these specs. Platform-specific constraints (URL structure, theme-managed schema) from `config/client.yaml → shopify`.

## Tools Required

- Firecrawl (current page state)
- Google Search Console (query/page performance)
- Ahrefs (keyword data, competitor on-page analysis)
- SerpAPI (SERP feature analysis, competitor titles/descriptions)
- Shopify Admin API (meta tag verification)

## Data Storage

- `tracker/data/on-page-specs/specs/` — individual spec files per URL
- `tracker/data/on-page-specs/audit_{date}.json` — audit results

## Modes

### `audit`

**When:** Part of monthly deep audit or quarterly strategy review.
**Pre-conditions:** Crawl data exists.

**Checks per page:**

| Element | What to check |
|---------|--------------|
| Title tag | Unique? Contains target keyword? Correct length (50–60 chars)? Brand suffix present? |
| Meta description | Unique? Contains keyword? Correct length (150–160 chars)? Has CTA? |
| H1 | Present? Unique? Matches page intent? |
| Heading hierarchy | H1 → H2 → H3 logical? No skipped levels? |
| Image alt text | Present on all images? Descriptive? Contains keyword where natural? |
| Internal links | Sufficient (≥2 per content page)? Relevant anchor text? Links to pillar/cluster? |
| Schema markup | Present? Correct type for page type? Valid? |

**Title format conventions** (derived from client config):
- Product: `{Product Name} — {Category} | {Brand}`
- Collection: `{Collection Name} — {Geo} {Service} | {Brand}`
- Blog: `{Post Title} | {Brand}`
- Homepage: `{Brand} — {Tagline}`

**Output:** Issues grouped by severity, with specific URLs and recommendations.

### `spec`

**When:** New page created, or triggered by content-strategy/keyword-research.
**Purpose:** Produce a complete on-page specification for a specific URL.

**Steps:**
1. Identify target keyword and cluster from keyword data
2. SerpAPI: analyse current SERP for target keyword
   - Top 5 results: title format, meta description style, heading structure, content length, schema types, SERP features present
3. Produce spec:

```json
{
  "url": "/collections/example",
  "page_type": "collection",
  "target_keyword": { "keyword": "...", "volume": 0, "kd": 0 },
  "title_tag": { "spec": "format rule", "example": "concrete example" },
  "meta_description": { "spec": "format rule", "example": "concrete example" },
  "h1": "recommended H1 text",
  "heading_structure": ["H2: ...", "H3: ...", "H2: ..."],
  "schema": { "type": "Product|Collection|Article|LocalBusiness|FAQPage", "required_fields": [] },
  "internal_links": { "link_to": [], "link_from": [] },
  "content_notes": "any specific guidance for the copywriter"
}
```

4. Save to `tracker/data/on-page-specs/specs/{url_slug}.json`

### `optimise`

**When:** Ad-hoc, for underperforming pages (ranking 11–20).
**Purpose:** Quick-win improvements to push a page into top 10.

**Steps:**
1. Pull GSC data for the page: queries driving impressions, current positions
2. Compare current on-page elements to spec (or create spec if none exists)
3. Identify gaps: title not optimised, meta description not compelling, missing schema, weak internal linking
4. Produce prioritised list of changes with expected impact
5. Create task (type: `fix` for simple changes, `brief` if content rewrite needed)
