---
name: campaign-setup
description: Create Fig & Bloom ad campaign structure in Notion — page hierarchy, CDN-hosted creatives, flat Ads DB with performance fields. Follow this exact process for every new campaign.
tags: [fig-bloom, advertising, notion, cdn, campaigns]
---

# Campaign Setup Process

## When to use

Setting up a new ad campaign for Fig & Bloom. Produces a clean Notion structure with creatives, metadata, and performance tracking ready for platform sync.

## Architecture

```
Advertising (page)
└── Campaigns (page)
    ├── Ads (single flat DB — one row per ad concept)
    └── {Campaign Name} (page with all creatives embedded)
```

**One DB per campaign hierarchy, NOT per campaign.** All campaigns share the flat Ads DB. Each row is an ad concept (e.g. "Oops vs Wow — Anniversary"), not an aspect ratio variant.

## Rules (non-negotiable)

1. **ALWAYS use brand CDN for images** — load the `devops-brand-cdn` skill. Never embed Google Drive URLs in Notion (they break — Notion can't render them as external images). Upload to `figandbloom/campaigns/{campaign-slug}/{slug}.png`
2. **Flat DB, not relational** — one row per ad concept. Three aspect ratios = one ad with three CDN URLs in the "Creatives (CDN)" field. Meta loads them as creatives within the same ad.
3. **Campaign page links to DB, DB rows link to campaign page** — bidirectional navigation
4. **Include strategy fields** — Hypothesis, Angle, Campaign Type, Funnel, Target Audience. These are what make the DB useful for learning what works.

## Step-by-step

### 1. Extract & upload to CDN

```bash
# Unzip campaign assets
python3 -c "import zipfile; zipfile.ZipFile('campaign.zip').extractall('extracted/')"

# Upload each file to brand CDN (load devops-brand-cdn skill first)
/opt/data/workspace/dgroch-skills/devops/devops-brand-cdn/scripts/upload.sh figandbloom "campaigns/{slug}/{file}.png" "/path/to/file.png"
```

Key naming: `campaigns/{campaign-slug}/{occasion}-{ratio}.png`

### 2. Create Notion structure

- Find or create "Advertising" page at workspace root
- Find or create "Campaigns" page under Advertising
- Create campaign page under Campaigns with all creatives embedded via CDN URLs
- Create "Ads" DB under Campaigns (or reuse existing one)

### 3. Ads DB schema

| Property | Type | Notes |
|----------|------|-------|
| Ad | Title | "{Campaign} — {Occasion}" |
| Campaign | Select | Campaign name |
| Status | Select | Draft / Approved / Active / Paused / Killed |
| Occasion | Select | Campaign-specific |
| Platform | Multi-select | Meta / TikTok / Google |
| Hypothesis | Rich text | Why this will work |
| Angle | Rich text | Creative approach |
| Campaign Type | Select | Prospecting / Retargeting / Re-engagement / Brand Awareness |
| Funnel | Select | TOFU / MOFU / BOFU |
| Target Audience | Rich text | Who we're reaching |
| Headline | Rich text | Ad headline |
| Primary Text | Rich text | Ad body copy |
| CTA | Select | Shop Now / Sign Up / Learn More / Get Offer |
| Creatives (CDN) | Rich text | All CDN URLs, one per line |
| Campaign Page | URL | Link to campaign page with embedded creatives |
| Campaign ID | Rich text | Platform campaign ID |
| Adset ID | Rich text | Platform adset ID |
| Ad ID | Rich text | Platform ad ID |
| Budget ($/day) | Number (dollar) | Daily budget |
| Spend | Number (dollar) | From sync |
| Revenue | Number (dollar) | From sync |
| ROAS | Number | From sync |
| CPA | Number (dollar) | From sync |
| Conversions | Number | From sync |
| Clicks | Number | From sync |
| Impressions | Number | From sync |
| CTR (%) | Number (percent) | From sync |
| Start Date | Date | |
| End Date | Date | |
| Last Synced | Date | Updated by Meta sync cron |

### 4. Add rows

One row per ad concept. Fill in all strategy fields (hypothesis, angle, audience). Add all CDN URLs in "Creatives (CDN)". Link "Campaign Page" URL to the campaign page.

### 5. Meta Ads sync (when ready)

Once campaign goes live and has Ad IDs, set up a cron job to pull metrics from Meta Marketing API and write back to the DB. Needs: Meta Marketing API token, Ad Account ID, and the Ads DB ID.

## Google Ads static creative intake

When Daniel sends a zip of static ad creatives and asks to “index them to Google Ads”, treat it as a full campaign/ads intake, not just file extraction:

1. Unzip the archive to a temporary work folder and inventory file count, dimensions, and filename concepts.
2. Save originals to Synology Photos / Google Drive under a durable campaign-style folder, e.g. `SHARED DRIVE/Graphics/Promotional/Google Ads/<date> <campaign/intake name>/`.
3. Upload each creative to the Fig & Bloom brand CDN before embedding or storing creative URLs in Notion. Notion renders CDN URLs reliably; Google Drive URLs are for source-file access only.
4. Create one Manifest row per creative with Drive File ID/link, CDN Preview URL/file, dimensions, aspect ratio, source folder, content type such as `Google Ads Creative`, and filename-derived description/tags when no vision pass is required.
5. Create/update a Campaigns page under 📁 Campaigns with embedded CDN previews grouped by creative concept.
6. Create Ads DB rows grouped by concept, **not one row per size variant**. Store all CDN URLs for that concept in `Creatives (CDN)` and set Platform=`Google`.
7. Verify Drive file count, Notion campaign page, at least one Manifest row, and at least one Ads DB row by reading them back. Delete local extracted media after successful upload/indexing; keep only a small JSON audit file if useful.

## Pitfalls

- **Google Drive URLs don't work in Notion embeds** — Notion blocks them. Always CDN.
- **Don't create rows per aspect ratio** — in Meta and Google creative intake, multiple sizes/ratios are creative variants under one ad concept, not separate ad concepts.
- **Don't create separate DBs per campaign** — one flat DB, filterable by Campaign select. Cross-campaign comparison only works if everything's in one table.
- **Don't skip strategy fields** — the DB's value is sorting by ROAS and immediately seeing what hypothesis/angle/audience drove the winner.
- **CDN upload helper may print a valid URL despite non-zero exit** — if using the Fig & Bloom upload script in automation, parse stdout for the final `https://brand-cdn...` URL and verify it, rather than assuming non-zero always means the upload failed.
- **Notion DB creation API is fussy** — relation properties need `{"database_id": "...", "type": "single_property", "single_property": {}}` not just `{"database_id": "..."}`. Test with a small DB first.

## Notion IDs (current)

- Advertising page: `361fdc24-425f-80ef-ac57-d2e02628e574`
- Campaigns page: `36ffdc24-425f-814a-97c5-ca6dd3603795`
- Ads DB: `36ffdc24-425f-8120-8ced-ed816b12049a`
