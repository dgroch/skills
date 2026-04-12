---
name: local-seo
description: Paperclip SEO workflow for Local SEO. Use this skill when you need to improve local search visibility, local pack performance, and citation consistency.
---


# Local SEO (Paperclip)

This skill was adapted from the CSTMR SEO specialist system for Paperclip AI.

Paperclip path mapping:
- Treat any `tracker/` paths below as relative to your Paperclip project workspace data directory.
- Keep file structures and schemas consistent across runs so other SEO skills can consume outputs.
- Replace any references to `agent.yaml` routing with your Paperclip notification or orchestration settings.


## Purpose

Optimise the client's local search presence. Manage Google Business Profile, local citations, reviews, and geo-targeted content strategy. Market geo and local context from `config/client.yaml → market`.

## Tools Required

- Google Business Profile API (listing management, reviews, posts)
- SerpAPI (local pack results, geo-modified queries)
- Ahrefs (local keyword tracking)
- Firecrawl (citation discovery, competitor local pages)

## Data Storage

- `tracker/data/local/gbp_audit_{date}.json` — GBP audit results
- `tracker/data/local/citations.json` — citation inventory and consistency status
- `tracker/data/local/local_rankings_{date}.json` — local pack tracking

## Modes

### `audit`

**When:** Bootstrap step 6, monthly (15th).
**Pre-conditions:** GBP API accessible.

**Steps:**
1. **GBP completeness check:**
   - Business name (matches client name exactly)
   - Primary + secondary categories (relevant to business)
   - Address, phone, website URL (correct and consistent)
   - Hours (current, including holiday hours)
   - Description (contains keywords, under 750 chars)
   - Attributes (all relevant ones set)
   - Photos (recent, high quality, cover categories: exterior, interior, products, team)
   - Products/services listed
   - Q&A section (common questions answered)
2. **NAP consistency audit:**
   - Check client's Name, Address, Phone across top citation sources
   - Flag inconsistencies (old address, wrong phone, name variations)
   - Citation sources to check: Google, Apple Maps, Bing Places, Yellow Pages, True Local, Yelp, Facebook, Instagram, industry-specific directories
3. **Local ranking check** (SerpAPI):
   - Search top local keywords with geo modifier (from `config/client.yaml → market.serp_location`)
   - Check local pack presence (position 1–3, or not present)
   - Check organic position for same queries
4. **Review analysis:**
   - Total reviews, average rating, recent trend (last 30/90 days)
   - Sentiment of recent reviews
   - Response rate (are reviews being responded to?)
5. **Local schema verification:**
   - LocalBusiness schema on relevant pages
   - Correct address, geo coordinates, opening hours, phone
6. Write audit results
7. Create tasks for issues found

### `optimise`

**When:** Ad-hoc, after audit identifies improvements.
**Decision level:** Recommend for GBP changes, Autonomous for citation cleanup tasks.

**Steps:**
1. GBP recommendations: missing fields, better categories, updated description, photo needs
2. Citation cleanup: create tasks to fix inconsistencies (some may need manual operator action)
3. Review strategy:
   - If response rate <90%, recommend review response workflow
   - If rating declining, flag for operator attention
   - Suggest review generation tactics (post-purchase email, in-store signage)
4. Geo-targeted content opportunities:
   - Suburb-specific landing pages (e.g., "flower delivery {suburb}")
   - Only recommend if keyword data supports it (volume > threshold)
5. Local link building opportunities: chambers of commerce, local event sponsors, complementary businesses

### `review_response`

**When:** As part of monthly audit, or on-demand.
**Decision level:** Autonomous for positive/neutral, Escalate for negative.

**Steps:**
1. Fetch recent reviews via GBP API
2. Classify: positive (4–5 stars), neutral (3 stars), negative (1–2 stars)
3. Positive: draft warm, personalised thank-you (not generic). Recommend to operator for posting.
4. Neutral: draft acknowledging response. Recommend to operator.
5. Negative: **Escalate to operator immediately.** Draft suggested response but do not post. Include: review content, customer concern, suggested resolution approach.
