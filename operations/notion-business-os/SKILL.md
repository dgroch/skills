---
name: notion-business-os
description: "Notion as Fig & Bloom's business operating system — workspace map, database schemas, operating workflows, and agent orchestration patterns."
version: 1.0.0
author: agent
platforms: [linux]
metadata:
  hermes:
    tags: [notion, business-os, fig-bloom, bower, whoosh, orchestration, databases, campaigns, assets, trading]
---

# Notion Business OS

Notion is the central nervous system for all Fig & Bloom operations. Every agent profile reads from and writes to Notion databases as their primary state store. This skill is the authoritative map.

## When to Use

- Any task that touches Fig & Bloom, Bower, or Whoosh business data
- Creating, querying, or updating Notion databases
- Routing work between agent profiles based on Notion state
- Understanding how data flows between databases
- Operating the campaign pipeline, asset lifecycle, or trading system

## Prerequisites

```
NOTION_API_KEY=ntn_...  # in ~/.hermes/.env
```

All API calls use:
```bash
curl -s -X POST "https://api.notion.com/v1/..." \
  -H "Authorization: Bearer *** \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json"
```

**Rate limit:** ~3 requests/second average. Add 0.4s sleep between calls in loops.

---

## Workspace Map

### Top-Level Pages

| Page | ID | Purpose |
|------|----|---------|
| **🌸 Bower Brand OS** | `356fdc24-425f-8071-8dac-f93e052a19b3` | Bower brand identity, art direction, seed DBs |
| **Brand** (Whoosh) | `354fdc24-425f-802e-b6b1-f757a15cf4e0` | Whoosh brand identity, colour, voice, seed DBs |
| **Projects** | `366fdc24-425f-80ce-8151-c1b7dcf35b5a` | Fig & Bloom ops: recipes, pricing, gift cards |
| **Product** | `36dfdc24-425f-80d3-b7b0-f3614ce9aff7` | Floral recipes + BOMs (Purchasing sub-page holds Recipes + Materials) |
| **Systematic Portfolio (Beta)** | `369fdc24-425f-802b-8d83-c1f5e935174b` | Investment system: trading, rebalances, reports |

### Nested Under Fig & Bloom (some pages not shared with integration)

These pages exist under parent `36dfdc24` which returns 404 — the integration may not have access to all sub-pages:

| Section | Known Child Pages/Databases |
|---------|---------------------------|
| **Assets** | Manifest, Characters, Shots, Products, Brand Photographer Backend |
| **Advertising** | Meta Ads Creative Framework → Social Media Ads, UGC |
| **Creative Research** | Fig & Bloom Creative Research, Comms Calendar |
| **Product Research** | Oddly Viral Product Research |
| **Customer Research** | Review Research — Raw Reviews |

---

## Database Registry

### Asset & Brand Databases

| Database | ID | Items | Parent Page |
|----------|----|-------|-------------|
| **Manifest** | `357fdc24425f81ed805cc4f9aff0665f` | 7,100+ | Assets |
| **Products** (Fig & Bloom) | `358fdc24425f81949979dc3ee44c7ed5` | 425 | Assets |
| **Shots** (Assets) | `358fdc24425f81a2a9e4e76c472cdcf7` | 0 | Assets |
| **Characters** (Assets) | `53fa365a5153481db1d29bfb039e8dcc` | 1 | Assets |
| **Brand Photographer Artifacts** | `b1ecf2b1-2f4e-413c-bee6-49758a14d3d2` | 101 | Brand Photographer Backend |

### Product / Recipes (Floral Operations)

Found via Notion search 7 Jun 2026. Lives under workspace-root `Product` page (`36dfdc24-425f-80d3-b7b0-f3614ce9aff7`) → `Purchasing` sub-page (`36bfdc24-425f-80d7-b249-f60573eff27f`). The parent `Product` page 404s via the API (same access limitation as other top-level pages), but the child databases are queryable directly. **When the user asks "what's the cost of Osaka?" or "what's in the recipe for X?"** — these are the tables to hit.

| Database | ID | Purpose |
|----------|----|---------|
| **Recipes** | `db009442-de01-4459-a5a9-6d9961f08334` | One row per floral recipe (e.g. "Osaka Signature", "Marseille Statement"). Has `Name` (title), `Design` (select: Osaka/Marseille/Broome), `Tier` (Signature/Statement), `Customer Tier` (Member/Non-member), `Stem Count`, `Total Stem Cost`, `Sheet RRP`, `Retail Price`, `Shopify Handle`, `Shopify SKUs`, and a relation to Materials. |
| **Materials** | `906339d2-3f2d-4bc7-b8c4-77755e26c738` | One row per flower stem / bunch. Has `Name` (title), `Stem Cost`, `Bunch Cost`, `Stem RRP`, `Notes`, and a back-relation to Recipes. |

The Recipes↔Materials relation is bidirectional: query Recipes to get the BOM of a single arrangement, or query Materials to find which recipes use a given stem. **Margin = `Retail Price` − `Total Stem Cost`** is the simplest cost-engineering query. Verify live schema before bulk writes — see pitfall #11 below.

### Campaign & Advertising Databases

| Database | ID | Items | Parent Page |
|----------|----|-------|-------------|
| **Creators** | `b5e1059f-543b-488b-ae19-3a3055dbc672` | 74 | User Generated Content |
| **Campaigns** | `ab1819ee-4236-4105-b091-d2d0640509a3` | 5 | User Generated Content |
| **Briefs** | `f0275d2e-80d3-4be6-b2f4-6d069d49e89a` | 6 | User Generated Content |
| **Social Media Ads** | `361fdc24-425f-80ab-b393-e583a5d9b339` | 45 | Meta Ads Creative Framework |

### Research Databases

| Database | ID | Items | Parent Page |
|----------|----|-------|-------------|
| **Fig & Bloom Creative Research** | `351fdc24425f81be976ec417a1b9c365` | 99 | Creative Research |
| **Oddly Viral Product Research** | `359fdc24425f81f88777d9888c79d473` | 29 | Product Research |
| **Review Research — Raw Reviews** | `357fdc24425f8123a9e0d413eab168f1` | 1,000+ | Review Research |

### Trading Databases

| Database | ID | Items | Parent Page |
|----------|----|-------|-------------|
| **Trade Executions** | `36afdc24425f8198bfedd4f0482f9ee8` | 18 | Trade Execution Monitor |
| **Rebalance Audits** | `36afdc24425f816c9c94fbf53dbc4bcb` | — | Trade Execution Monitor |
| **Scheduled Rebalances** | `36afdc24425f810a800adeb862c5865e` | 1 | Rebalance Calendar |
| **Summary Stats** | `36afdc24425f815b8f5adddbd71a2b98c` | — | Reports & Performance |
| **Equity Curve** | `36afdc24425f812b835fc2cc558e2ee0` | — | Reports & Performance |
| **Monthly Returns** | `36afdc24425f819392f9d6b06ef7bdf6` | — | Reports & Performance |
| **Daily Returns** | `36afdc24425f81c7a582e12685857b7b` | — | Reports & Performance |
| **Holdings Snapshots** | `36afdc24425f810781f5e43869ec351a` | — | Reports & Performance |

### PR & Media Databases

| Database | ID | Items | Parent Page |
|----------|----|-------|-------------|
| **Press Releases** | `2cb1957d-b140-4f32-8cac-8a7c4bc4ac6c` | 7 | Press Releases page (`38efdc24-425f-801e-9652-c90afe0fe979`) |
| **Journalist Contacts & Coverage** | `685b6a39-534d-4fb4-bb06-cd63747cdc2a` | 17 | Journalists page (`38efdc24-425f-8086-a224-c90951a4d52c`) |

**Press Releases** — Data source ID: `3df591e8-385c-4e6d-a7ac-6f9939797dea`
Schema: Name (title), Approval Status (select: Draft/Pending Approval/Approved/Revisions Needed/Rejected), Sent Status (select: Not Sent/Sending/Sent/Failed/Partial Send), Author (rich_text), Release Date (date), Approved By (rich_text), Approved Date (date), Sent Date (date), PR Type (select: Data Story/Product Launch/Seasonal Campaign/Company Announcement/Partnership/Award), Outlet Targets (multi_select: Lifestyle/News/Trade/Local Metro/National/Gifting/Womens/Food Hospitality), Mentions (rich_text), Embargo Date (date), Coverage URL (url), Published URL (url), Notes (rich_text).

Approval workflow: Draft → Pending Approval → Daniel reviews page body (full email copy in blocks) → Approved → cron sends via IMAP/SMTP from media@figandbloom.com → Sent. Content gate: cron checks page has body blocks before sending. Managed by the `digital-pr-outreach` skill.

**Journalist Contacts & Coverage** — Data source ID: `3cacb1d2-fc05-4bba-b524-0a9938145f3c`
Schema: Name (title), Outlet, Role/Beat, Email, Phone, Twitter/X (url), LinkedIn (url), Location, Status (select: Not Contacted/Pitched/Responded/Coverage Secured/Declined/No Reply), Last Contact Date (date), Coverage Type (multi_select: Feature Article, News Mention, Round-up, Interview, Social Post, Podcast, TV/Radio), Coverage URL (url), Coverage Date (date), Notes.

Managed by the `digital-pr-outreach` skill. Used to track journalist contacts across campaigns and log coverage secured.

### Operational Databases

| Database | ID | Items | Parent Page |
|----------|----|-------|-------------|
| **Gift Cards Register** | `36afdc24425f816fa315ced08f6dcd71` | 10 | Gift Cards |
| **Projects** | `354fdc24425f801e9567e8a402db0222` | 1 | Top-level |

### Brand Seed Databases (Bower)

| Database | ID | Parent Page |
|----------|----|-------------|
| **👥 Characters** | `35efdc24-425f-8116-a0b1-f33454032fa2` | Bower Brand OS |
| **💐 Products** | `35efdc24-425f-816a-b577-f1352d079301` | Bower Brand OS |
| **📍 Locations** | `35efdc24-425f-813a-9182-c3c8738ea732` | Bower Brand OS |
| **📸 Shots** | `35efdc24-425f-81df-9243-d7be382496d5` | Bower Brand OS |

### Brand Seed Databases (Whoosh)

| Database | ID | Parent Page |
|----------|----|-------------|
| **Characters** | `354fdc24-425f-803e-ab23-fce6aeefd7f4` | Brand (Whoosh) |
| **Products** | `354fdc24-425f-803e-ab23-fce6aeefd7f4` | Brand (Whoosh) |
| **Locations** | `354fdc24-425f-808f-aae9-f90b7dbf67ba` | Brand (Whoosh) |
| **Shots** | `83c4d220-2d42-4b9a-8156-30539567d2f2` | Brand (Whoosh) |

---

## Key Database Schemas

### Manifest (7,100+ items)
The central asset registry. Every image/video on the Synology Photos drive gets a row here.

**Critical properties:**
- `Asset` (title) — filename or descriptive name
- `Drive File ID` (rich_text) — Google Drive file ID
- `Content Type` (select) — 200+ options including: product showcase, lifestyle/social media, influencer promotion, user-generated content, etc.
- `Product Name` (rich_text) — named product
- `Visual Tags` (multi_select) — 160+ tags
- `Setting / Location` (rich_text)
- `People Present` (rich_text)
- `Folder Path` (rich_text)
- `Overall Description` (rich_text) — AI-generated via vision manifesting
- `Mime Type` (rich_text)
- `CDN URL` (url, implied) — brand CDN at `brand-cdn.figandbloom.workers.dev`
- `Canonical Product Name` (relation) → Products DB

### Creators (74 items)
Hashgifted influencer pipeline. Rich qualification data.

**Key properties:**
- `Creator Name` (title)
- `Hashgifted Stage` (select): Applied → Manual Review → Shortlisted → Outreach Sent → Qualified → Selected → Content Posted → Captured
- `Decision` (select): Shortlist, Manual Review, Decline, Reserve, Selected, Complete, Pass
- `Status` (select): Active, Preferred, Excluded, Archived
- `Campaigns` (relation) → Campaigns DB
- `Followers` (number), `Engagement Rate` (number)
- `Metro Area` (select): Melbourne, Sydney, Brisbane, Other, Unknown
- `Brand Fit` (select): Strong, Good, Maybe, Weak, Unsafe
- `Visual Style` (multi_select): 42+ options
- `Content Themes` (multi_select): 37+ options
- `Tier` (select): Nano, Micro, Mid, Macro

### Social Media Ads (45 items)
4×3×3 creative matrix. Each ad is tagged on three axes.

**Key properties:**
- `Name` (title) — format: `PRODUCT_Angle_Format_HookType`
- `Angle` (select): Pain, Transformation, Social Proof, Authority
- `Creative Format` (select): Founder, UGC, Demo
- `Hook Type` (select): Question, Stat, Contrarian
- `Status` (select): Draft, In Review, Approved, Scheduled, Published, Needs changes
- `Platform` (multi_select): Instagram, Facebook, TikTok, Meta
- `Objective` (select): Purchase, Lead, AOV lift, Retargeting, Awareness
- `Brand QA` (select): Pending, Approved, Needs changes
- `Campaign Concept` (select): Same-day gesture rescue, Objects worth keeping, etc.

### Review Research (1,000+ items)
Competitor and customer review analysis.

**Key properties:**
- `Brand` (select) — competitor brand name
- `Source` (select) — ProductReview, etc.
- `Job To Be Done` (select) — romance, sympathy, birthday, etc.
- `Raw Text` (rich_text) — original review text
- `Delight Drivers` / `Complaints` / `Purchase Drivers` (rich_text)
- `Operational Issue` (select)

### Products (425 items)
Fig & Bloom product catalogue synced from Shopify + DataFeedWatch.

**Key properties:**
- `Product Name` (title)
- `Product Type` (select): Bouquet, Candle, Vase, etc.
- `Handle` (rich_text) — Shopify handle
- `Price AUD` (number)
- `Tags` (multi_select): hero, gift, mothers-day, etc.
- `Source` (select): Shopify, DataFeedWatch
- `Shopify Product ID` / `Shopify Legacy ID` (rich_text)

---

## Operating Workflows

### 1. Campaign Pipeline (Hashgifted UGC)

```
Briefs → Campaigns → Creators → Content Posted → Social Media Ads
```

**Flow:**
1. **Create Brief** in Briefs DB (concept hook, public link, status)
2. **Create Campaign** in Campaigns DB, link to Briefs, set target creator count
3. **Source Creators** via Hashgifted platform → import to Creators DB
4. **Qualify Creators** — agents run visual review, brand fit scoring, metro eligibility
5. **Shortlist & Outreach** — update Hashgifted Stage through pipeline
6. **Track Content** — once posted, update stage to "Content Posted" → "Captured"
7. **Create Ads** — from captured UGC, create rows in Social Media Ads DB tagged with 4×3×3 grid axes

**Agent roles:**
- `operator` — creator qualification, visual review, outreach
- `creative` — ad creative generation from captured UGC
- `director` — campaign strategy, brief creation, performance review

### 2. Asset Lifecycle

```
Raw file on Drive → Vision Manifest → Organized → Used in Creative
```

**Flow:**
1. **Upload** to Synology Photos shared drive (`0AOMVrKhhWKIwUk9PVA`)
2. **Vision Manifest** — Gemini/Qwen VL analyzes image → creates Manifest row with description, tags, content type
3. **CDN Upload** — image uploaded to Cloudflare R2 (`brand-cdn.figandbloom.workers.dev`)
4. **Organize** — file moved to correct folder based on manifest classification
5. **Use** — agents query Manifest for assets matching criteria (product, visual tags, content type)

**Query patterns:**
```json
// Find product photography for a specific bouquet
{"filter": {
  "and": [
    {"property": "Content Type", "select": {"equals": "product showcase"}},
    {"property": "Product Name", "rich_text": {"contains": "Osaka"}}
  ]
}}

// Find lifestyle UGC content
{"filter": {
  "and": [
    {"property": "Content Type", "select": {"contains": "user-generated"}},
    {"property": "Visual Tags", "multi_select": {"contains": "lifestyle"}}
  ]
}}
```

### 3. Brand OS Pattern

Each brand (Bower, Whoosh, Fig & Bloom) follows the same structure:

```
Brand Page (identity, voice, colours)
├── Art Direction (photography principles, scenes, avoid list)
├── Colour System (tokens, usage ratios, grading rules)
├── Critic Dimensions (quality rubric, pass/fail criteria)
├── Grid Spec (social media layout patterns)
├── Prompt Construction (AI image prompt recipes)
├── Voice & Copy (tone examples, pass/fail)
└── Seed Databases (Characters, Locations, Products, Shots)
```

**How agents use this:**
- Before generating any creative for a brand, load the Brand Page and relevant sub-pages
- Use Critic Dimensions as the quality gate for all generated content
- Use Colour System tokens for any visual work
- Use Seed Databases as reference data for AI image prompts
- Voice & Copy governs all text generation for that brand

### 4. Trading Operations (Systematic Portfolio)

```
Scheduled Rebalances → Rebalance Audits → Trade Executions → Reports
```

**Flow:**
1. **Schedule** — monthly rebalance row created in Scheduled Rebalances DB
2. **Dry Run** — system generates audit file, computes approval SHA, sets status to "Awaiting Approval"
3. **Review** — Daniel inspects orders in Trade Executions (ticker, side, quantity, limit price)
4. **Approve** — set Status = "Approved" + check "Execute Requested"
5. **Execute** — armed runner submits to Tastytrade
6. **Monitor** — Reports & Performance Dashboard updates with equity curve, returns

**Safety rules:**
- Never approve with blank Audit File or Approval SHA
- Execute Requested must be checked (not just Status change)
- Runner requires `NOTION_TRADING_APPROVALS_ENABLED=1`

### 5. Research Pipelines

**Creative Research:**
- Scrape viral content (TikTok, Instagram) → score by hook type, engagement, relevance
- Query by category, hook type, score threshold
- Feed winners into campaign briefs and ad creative

**Review Research:**
- Crawl competitor reviews (ProductReview.com.au, etc.)
- Code by Job To Be Done, delight drivers, complaints
- Extract patterns for Fig & Bloom positioning

**Product Research (Oddly Viral):**
- Track viral product trends → score by territory, moonpig logic, sourcing terms
- Feed into product development pipeline

---

## Agent Profile Routing

| Profile | Primary Notion Surfaces | Read/Write |
|---------|------------------------|------------|
| **director** | All — routing, strategy, cross-domain | R/W all |
| **operator** | Creators, Campaigns, Briefs, Manifest | R/W |
| **creative** | Social Media Ads, Brand OS pages, Shots, Characters | R/W |
| **investor** | Scheduled Rebalances, Trade Executions, Reports | R/W |
| **seo-expert** | Creative Research, Review Research | R |
| **engineer** | Manifest, Brand Photographer Artifacts | R/W |
| **librarian** | Manifest, Products, all research DBs | R/W |

---

## Cross-Database Relations

```
Creators ←→ Campaigns (many-to-many via relation)
Campaigns ←→ Briefs (many-to-many via relation)
Manifest.Canonical Product Name → Products (relation)
Shots.Character → Characters (relation)
Shots.Website Product → Products (relation)
Shots.Brand Seed Product → Products (relation)
```

---

## Query Patterns (Quick Reference)

### Paginate large databases
```python
import requests, time

def query_all(db_id, filter_obj=None, page_size=100):
    results = []
    cursor = None
    while True:
        body = {"page_size": page_size}
        if filter_obj:
            body["filter"] = filter_obj
        if cursor:
            body["start_cursor"] = cursor
        resp = requests.post(
            f"https://api.notion.com/v1/databases/{db_id}/query",
            headers=HEADERS, json=body
        )
        data = resp.json()
        results.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data["next_cursor"]
        time.sleep(0.4)
    return results
```

### Create a database row
```python
resp = requests.post(BASE + "/pages", headers=HEADERS, json={
    "parent": {"database_id": "DB_ID_HERE"},
    "properties": {
        "Name": {"title": [{"text": {"content": "New Item"}}]},
        "Status": {"select": {"name": "Draft"}},
        "Notes": {"rich_text": [{"text": {"content": "Created by agent"}}]}
    }
})
```

### Update a row
```python
resp = requests.patch(BASE + "/pages/PAGE_ID", headers=HEADERS, json={
    "properties": {
        "Status": {"select": {"name": "Approved"}}
    }
})
```

### Read page as markdown
```bash
curl -s "https://api.notion.com/v1/pages/PAGE_ID/markdown" \
  -H "Authorization: Bearer *** \
  -H "Notion-Version: 2022-06-28"
```

---

## Pitfalls

1. **Parent page 36dfdc24 returns 404** — The main Fig & Bloom workspace page isn't shared with the integration. Child pages/databases under it may also 404. **BUT** the Recipes (`db009442-de01-4459-a5a9-6d9961f08334`) and Materials (`906339d2-3f2d-4bc7-b8c4-77755e26c738`) databases under it ARE queryable by ID — they don't share their parent. Use database IDs directly (they work even if parent page is inaccessible).

2. **Mime Type is rich_text, not select** — Despite appearing as a dropdown in the UI, the API returns it as rich_text. Filter with `rich_text.contains` not `select.equals`.

3. **Manifest pagination is expensive** — 7,100+ items = 72 pages. Cache results to `/tmp/manifest_full.json` and refresh only when needed.

4. **Notion API versions** — The `2022-06-28` version works for all basic operations (query, create pages, update properties). The `2025-09-03` version renamed databases to "data sources" and added new endpoints (`/data_sources/{id}/query`, `/pages/{id}/markdown`). Use `2025-09-03` when you need: data source queries, the markdown endpoint, or database creation with properties (two-step: create + PATCH data source). Use `2022-06-28` for simple page/database queries against existing IDs. The two versions coexist — pick based on the endpoint, not a global default.

5. **Select options are case-sensitive** — "Active" ≠ "active". Always match exact option names from the schema.

6. **Relation properties return page IDs only** — To get the related page's properties, you must fetch each page separately.

7. **Multi-select filter uses `contains`** — `{"multi_select": {"contains": "tag_name"}}` checks if the tag exists in the array.

8. **Date properties need ISO format** — `{"date": {"start": "2026-05-28"}}` not "May 28, 2026".

9. **Title property format** — Always `[{"text": {"content": "..."}}]`, never a plain string.

10. **Rate limiting** — 3 req/s average. In loops, use `time.sleep(0.4)` between calls. For batch operations (manifest pulls), this adds up — plan accordingly.
