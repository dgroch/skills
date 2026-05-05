---
name: florist-review-intelligence
description: Use when crawling, normalising, analysing, and syncing public customer reviews for Fig & Bloom and Australian florist competitors to extract voice-of-customer insights, complaints, purchase drivers, delight moments, and competitive positioning.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research, florist, reviews, voice-of-customer, competitive-intelligence, notion, australia]
    related_skills: [notion, social-creative-research-pipeline, seo-competitor-analysis]
---

# Florist Review Intelligence

## Overview

This skill builds a repeatable review-intelligence operation for **Fig & Bloom** and key Australian florist competitors. It collects publicly available reviews and review-like comments, stores raw evidence locally as JSONL, classifies customer language, and syncs structured insights into Notion for human review.

Default competitors and markets:

- Brands: `Fig & Bloom`, `Daily Blooms`, `LVLY`
- Geographies: `Melbourne`, `Sydney`, `Brisbane`
- Sources: Google Business/Profile surfaces where accessible, ProductReview.com.au, Trustpilot, Facebook public reviews/comments, Yelp/Tripadvisor where relevant, Reddit/social mentions, website testimonials, and public review widgets.

The main output is a voice-of-customer dataset: exact customer phrasing, complaints, purchase reasons, delight drivers, objections, failure modes, and brand-by-brand opportunity gaps.

## When to Use

Use this skill when the user asks to:

- research what consumers say about Fig & Bloom or florist competitors
- scrape/crawl public reviews for Daily Blooms, LVLY, or other florists
- extract customer complaints, praise, purchase drivers, and emotional language
- build a Notion review intelligence database
- run recurring daily/weekly competitor review monitoring
- compare florist brands across Melbourne, Sydney, and Brisbane

Do **not** use this skill for private/customer-service inboxes, login-gated communities, payment-gated data, or data that cannot be legally or operationally accessed by the running environment.

## Compliance Boundary

Operate with a permissive, evidence-first posture:

**Collect what is publicly accessible.** Public review widgets, review platform pages, Google Business profiles, and other indexable surfaces are within scope. Use Playwright with stealth mode to render JavaScript-heavy pages and extract the full public review corpus — including what is behind lightweight bot-protection layers (Cloudflare challenge pages, DataDome, PerimeterX) that a headless browser can typically bypass without misrepresentation.

**Use bot-evasion tools freely** when they do not require false credentials or account impersonation:
- Playwright + playwright-stealth (primary — masks navigator.webdriver, navigator.plugins, and other automation fingerprints)
- Puppeteer as fallback
- Realistic browser fingerprints, viewport, locale, and timezone settings
- Polite rate limits between requests (~1–2 req/s per domain) to avoid triggering abuse thresholds
- Resource blocking for telemetry/tracking scripts that serve no data purpose

**Do not:**
- Provide false credentials or impersonate a logged-in user
- Circumvent paywalls or paid-gated content
- Attempt to solve CAPTCHAs (log as `blocked_source` and move on)
- Reverse-engineer or abuse private/internal APIs that are not publicly documented
- Represent the collector as a human user

**Evidence preservation:**
- Store source URL, date collected, and extraction method for every item.
- Keep personally identifying details out of summaries; prefer reviewer display names only when already public and useful for deduplication.
- Quote exact customer language for insight, but avoid republishing large copyrighted review corpora verbatim.

If a source is blocked, save a `blocked_source` event with the URL and reason, then move to other sources.

## Data Model

Use local JSONL as the source of truth. One object per review/comment/mention:

```json
{
  "id": "stable-sha256-id",
  "brand": "Daily Blooms",
  "brand_alias": "dailyblooms",
  "market": "Melbourne",
  "source": "Google|ProductReview|Trustpilot|Facebook|Reddit|Website|Yelp|Tripadvisor|Other",
  "source_url": "https://...",
  "review_url": "https://...",
  "reviewer": "display name or null",
  "rating": 4.0,
  "review_date": "YYYY-MM-DD or null",
  "collected_at": "YYYY-MM-DDTHH:MM:SSZ",
  "title": "optional review title",
  "text": "raw public review/comment text",
  "language": "en",
  "sentiment": "positive|mixed|negative|unknown",
  "themes": ["delivery", "product_quality", "customer_service"],
  "complaints": ["late delivery"],
  "delight_drivers": ["beautiful arrangement"],
  "purchase_drivers": ["same-day delivery"],
  "objections": ["expensive"],
  "emotion_words": ["stunning", "disappointed"],
  "customer_phrases": ["looked exactly like the photo"],
  "job_to_be_done": "birthday|sympathy|romance|apology|corporate|same_day|other|unknown",
  "operational_issue": "delivery|quality|communication|refund|website|none|unknown",
  "competitor_opportunity": "what Fig & Bloom can exploit or defend",
  "confidence": 0.75,
  "status": "new|analysed|synced|rejected|blocked_source"
}
```

## Taxonomy

### Themes

- `delivery_speed`
- `delivery_accuracy`
- `same_day_delivery`
- `product_quality`
- `photo_match`
- `freshness_longevity`
- `value_price`
- `customer_service`
- `refund_resolution`
- `website_checkout`
- `packaging_presentation`
- `premium_design`
- `gift_recipient_reaction`
- `subscription_repeat_purchase`
- `corporate_service`
- `local_trust`

### Purchase Drivers

- same-day / urgent delivery
- beautiful/premium design
- trusted local florist
- easy ordering
- good price/value
- reliable for special occasions
- recipient reaction
- brand aesthetic
- sympathy/occasion confidence
- subscription/convenience

### Complaints / Failure Modes

- late or missed delivery
- wrong date/time/address
- poor communication
- flowers not fresh
- arrangement did not match photo
- smaller than expected
- expensive for perceived value
- website/checkout issues
- refund or complaint handling
- damaged packaging
- substitution disappointment

### Customer Language to Extract

Prioritise phrases that sound like a real customer and can guide copy/creative:

- “looked exactly like the photo”
- “arrived on time”
- “made her day”
- “for the price I expected...”
- “couldn’t get through to anyone”
- “last minute and they still delivered”
- “not what was pictured”
- “fresh for over a week”
- “embarrassing gift”
- “saved me when I forgot...”

## Source Discovery Queries

Run broad and source-specific search passes. Examples:

```text
Fig & Bloom reviews Melbourne florist
Fig & Bloom reviews Sydney florist
Daily Blooms reviews Melbourne
Daily Blooms florist reviews Brisbane
LVLY reviews Melbourne flowers
LVLY flowers reviews Sydney
site:productreview.com.au Daily Blooms flowers reviews
site:productreview.com.au LVLY flowers reviews
site:trustpilot.com Daily Blooms reviews
site:trustpilot.com LVLY reviews
site:facebook.com Daily Blooms reviews flowers
site:reddit.com.au florist reviews Melbourne Daily Blooms
"Daily Blooms" "late delivery"
"LVLY" "not fresh" flowers
"Fig & Bloom" "looked like the photo"
```

For each brand/market, search both brand-only and problem-intent queries:

- `<brand> florist reviews <market>`
- `<brand> flowers reviews <market>`
- `<brand> complaints flowers`
- `<brand> late delivery`
- `<brand> refund flowers`
- `<brand> not fresh flowers`
- `<brand> photo did not match`

## Collection Workflow

1. Get the live date/time.
2. Generate a query plan for each brand × market × source family.
3. Search the web and collect candidate review URLs.
4. Visit public pages and extract review text, rating, date, source, and source URL.
5. Save raw extracts to `data/raw/YYYY-MM-DD.jsonl`.
6. Deduplicate by canonical URL + reviewer + date + text hash.
7. Analyse each item into the schema above.
8. Save analysed rows to `data/analysed/YYYY-MM-DD.jsonl`.
9. Write a daily summary to `reports/YYYY-MM-DD.md`:
   - top complaints by brand
   - top delight drivers by brand
   - language customers use
   - purchase drivers
   - operational risks
   - Fig & Bloom opportunities
   - source coverage gaps
10. Sync analysed rows to Notion if configured.
11. Verify JSONL is valid and Notion sync counts match expected row counts.

## Recommended Local Layout

```text
/opt/data/florist-review-intelligence/
  config.json
  data/
    raw/YYYY-MM-DD.jsonl
    analysed/YYYY-MM-DD.jsonl
    notion-sync-state.json
  reports/YYYY-MM-DD.md
  exports/YYYY-MM-DD.csv
  logs/YYYY-MM-DD.log
```

For Paperclip portability, keep scripts inside this skill and pass paths explicitly.

## Notion Database

Create or reuse a Notion database called:

`Fig & Bloom Review Intelligence`

Recommended properties:

- `Name` — title, format `<Brand> · <Source> · <short phrase>`
- `Brand` — select: Fig & Bloom, Daily Blooms, LVLY
- `Market` — select: Melbourne, Sydney, Brisbane, National, Unknown
- `Source` — select: Google, ProductReview, Trustpilot, Facebook, Reddit, Website, Yelp, Tripadvisor, Other
- `Source URL` — url
- `Review URL` — url
- `Rating` — number
- `Review Date` — date
- `Collected At` — date
- `Sentiment` — select: positive, mixed, negative, unknown
- `Themes` — multi-select
- `Complaints` — rich text
- `Delight Drivers` — rich text
- `Purchase Drivers` — rich text
- `Customer Phrases` — rich text
- `Job To Be Done` — select
- `Operational Issue` — select
- `Opportunity` — rich text
- `Raw Text` — rich text
- `Local ID` — rich text
- `Status` — select: new, analysed, synced, rejected, blocked_source

Environment variables:

- `NOTION_API_KEY` — required for Notion sync
- `NOTION_FLORIST_REVIEW_DATABASE_ID` — database ID for page creation
- `NOTION_FLORIST_REVIEW_DATA_SOURCE_ID` — data source ID for querying/upserts on newer Notion API versions
- Optional: `NOTION_FLORIST_REVIEW_PARENT_PAGE_ID` — parent page for database creation

## Scripts

This skill ships with:

- `scripts/review_intel_pipeline.py` — stdlib CLI for query generation, URL harvesting, analysis heuristics, CSV export, and Notion sync.
- `scripts/playwright_stealth_collector.js` — **primary** browser-backed collector using Playwright + playwright-stealth for JavaScript-heavy public review pages with bot-detection evasion.
- `scripts/test_playwright_stealth_collector.js` — parser smoke tests for the Playwright collector (run: `npm test`).
- `scripts/puppeteer_review_collector.js` — **fallback** browser collector using Puppeteer. Use when Playwright is unavailable.
- `scripts/test_puppeteer_review_collector.js` — parser smoke tests for the Puppeteer collector (run: `npm run test:puppeteer`).
- `scripts/firecrawl_collector.js` — autonomous Firecrawl-backed ProductReview collector. Uses `/v0/scrape` raw markdown (`skipExtract`, no LLM extraction) plus deterministic parsing for ProductReview short-review strips and full review cards. Writes JSONL to `data/firecrawl/` and deduplicates by review ID/content.
- `scripts/run_firecrawl.sh` — cron-safe wrapper for the Firecrawl collector with log capture and optional callback.
- `package.json` — Node/Playwright + playwright-stealth dependency manifest. Also includes Puppeteer as optional fallback.
- `templates/review_record_schema.json` — JSON schema for one analysed review item.
- `templates/config.example.json` — default Fig & Bloom / Daily Blooms / LVLY config.

Typical usage:

```bash
cd /opt/data/skills/research/florist-review-intelligence

# Install Playwright browsers if not already present.
# On Debian/Ubuntu: sudo apt install -y libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2
npx playwright install --with-deps chromium

# Run smoke tests.
npm test

# Primary browser-backed collection for JS-heavy review pages (Playwright + stealth).
# Uses stealth mode by default to mask automation fingerprints.
node scripts/playwright_stealth_collector.js \
  --brand "Daily Blooms" \
  --market Melbourne \
  --source Reviews.io \
  --url "https://www.reviews.io/company-reviews/store/dailyblooms.com.au" \
  --out /opt/data/florist-review-intelligence/data/raw/browser-$(date +%F).jsonl \
  --max-reviews 500 \
  --wait-ms 3000 \
  --load-more-clicks 10 \
  --screenshot /opt/data/florist-review-intelligence/screenshots/dailyblooms-reviewsio-$(date +%F).png

# Fallback: Puppeteer collector (for environments where Playwright is unavailable).
node scripts/puppeteer_review_collector.js \
  --brand "Daily Blooms" \
  --market Melbourne \
  --source Reviews.io \
  --url "https://www.reviews.io/company-reviews/store/dailyblooms.com.au" \
  --out /opt/data/florist-review-intelligence/data/raw/browser-$(date +%F).jsonl \
  --max-reviews 500

# Stdlib pipeline steps.
python3 scripts/review_intel_pipeline.py seed-queries \
  --config templates/config.example.json \
  --out /opt/data/florist-review-intelligence/queries.txt

python3 scripts/review_intel_pipeline.py harvest-url \
  --brand "Daily Blooms" \
  --market Melbourne \
  --source ProductReview \
  --url "https://example.com/public-review-page" \
  --out /opt/data/florist-review-intelligence/data/raw/$(date +%F).jsonl

python3 scripts/review_intel_pipeline.py analyse \
  --in /opt/data/florist-review-intelligence/data/raw/$(date +%F).jsonl \
  --out /opt/data/florist-review-intelligence/data/analysed/$(date +%F).jsonl \
  --report /opt/data/florist-review-intelligence/reports/$(date +%F).md

python3 scripts/review_intel_pipeline.py sync-notion \
  --in /opt/data/florist-review-intelligence/data/analysed/$(date +%F).jsonl
```

## Analysis Guidance

Use LLM analysis when available, but preserve deterministic heuristics as a fallback. For every review, classify:

- What is the customer complaining about?
- Why did they choose this provider?
- What made them happy?
- What made them unhappy?
- What exact language did they use?
- What operational or positioning opportunity exists for Fig & Bloom?

When using an LLM, ask for strict JSON using the schema above and keep the raw text attached. When using heuristics, set `confidence` lower and make that visible in Notion.

## Competitive Summary Format

Daily/weekly summaries should include:

```markdown
# Florist Review Intelligence — YYYY-MM-DD

## Coverage
- Brands covered:
- Sources covered:
- New reviews:
- Blocked/gap sources:

## Executive Takeaways
- ...

## Brand: Daily Blooms
### What customers choose them for
### What customers complain about
### Customer phrases
### Fig & Bloom opportunity

## Brand: LVLY
...

## Brand: Fig & Bloom
...

## Cross-category language bank
- "..."

## Next crawl targets
- ...
```

## Scheduling

For daily monitoring, schedule a Hermes/Paperclip routine with web/browser/file/terminal tools. The routine should:

1. Load this skill.
2. Generate query plan.
3. Search and crawl public results.
4. Save JSONL.
5. Analyse and summarize.
6. Sync to Notion.
7. Report counts: searched, captured, analysed, synced, failed, blocked.

Suggested cadence: daily at 7:30am local time for fresh monitoring; weekly summary every Monday.

## Common Pitfalls

1. **Only collecting star ratings.** Ratings are weak without the actual customer language. Always extract text.
2. **Over-indexing on one source.** Google and ProductReview may tell different stories. Track source coverage.
3. **Mixing markets.** Melbourne, Sydney, and Brisbane have different delivery expectations and competitors. Preserve market.
4. **Copying raw reviews into marketing.** Use reviews to infer language and needs; do not plagiarise customer text wholesale.
5. **Losing blocked-source evidence.** Log blocked pages so the next operator knows what was attempted.
6. **No dedupe key.** Review pages are syndicated and scraped by multiple sources. Use stable IDs.
7. **Notion as source of truth.** Keep JSONL as canonical. Notion is the human dashboard.
8. **Using plain fetcher on JavaScript review widgets.** If `harvest-url` returns only `blocked_source` or empty records for Reviews.io, ProductReview, Birdeye, or similar widgets, switch to `scripts/playwright_stealth_collector.js` (primary) or `scripts/puppeteer_review_collector.js` (fallback) and save a screenshot for evidence. Both support `--load-more-selector` for pagination.
9. **Missing Chromium/Playwright.** Run `npx playwright install --with-deps chromium` in the skill directory. If the environment already has system Chromium, set `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium`. For Puppeteer fallback: set `CHROMIUM_PATH=/usr/bin/chromium`.

## Verification Checklist

- [ ] Config includes `Fig & Bloom`, `Daily Blooms`, and `LVLY`
- [ ] Markets include `Melbourne`, `Sydney`, and `Brisbane`
- [ ] JSONL validates with one object per line
- [ ] Every record has `brand`, `market`, `source`, `source_url`, `text`, and `id`
- [ ] Analysis adds sentiment, themes, customer phrases, complaints, and opportunity
- [ ] Notion database properties match the expected schema
- [ ] Sync reports created/updated/failed counts
- [ ] Daily report includes source coverage gaps and next crawl targets
