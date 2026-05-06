---
name: brand-asset-manifesting
description: Use when crawling Google Drive/shared-drive brand asset folders and manifesting videos/images into a reusable Notion database for AI content generation.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [brand-assets, google-drive, shared-drive, notion, gemini, video-analysis]
    related_skills: [google-workspace, gws-cli-workflows, notion, audio-content-processing]
---

# Brand Asset Manifesting

## Overview

This skill creates a searchable, reusable asset database for brand media stored in Google Drive or shared drives. It samples videos/images, asks a vision model such as Gemini to describe the asset as a whole, records timestamps/shot beats, and syncs the result into Notion as the working database.

The goal is to make future AI content generation easy: every asset gets a stable handle, Drive link, physical metadata, content tags, usage ideas, and reorganisation notes.

## When to Use

Use this when the user asks to:

- Crawl or manifest a Google Drive/shared-drive folder of brand assets.
- Analyse videos into timestamped beats/shots.
- Build a Notion asset library rather than a one-off spreadsheet.
- Preserve file handles for later shared-drive reorganisation.
- Capture metadata such as aspect ratio, duration, orientation, dimensions, MIME type, and Drive file ID.

Do not use for private/non-brand personal archives unless the user explicitly asks and has permission to process the media.

## Canonical Database Choice

Prefer **Notion** as the canonical human-facing database.

Local JSON remains the deterministic backup/source artifact for reruns, but Google Sheets should only be used for quick previews or exports. Notion is better for long-running curation because it supports rich properties, page-level notes, views, filtering, and editorial workflow.

## Required Environment and First-Run Setup

- Google Workspace auth available through `gws`.
- A Gemini access path:
  - `GEMINI_PROVIDER=openrouter` + `OPENROUTER_API_KEY`, or
  - `GEMINI_PROVIDER=google` + `GEMINI_API_KEY` / `GOOGLE_API_KEY`.
- `NOTION_API_KEY` for Notion sync.
- `ffmpeg` and `ffprobe` for video frame/thumbnail extraction.
- Public brand CDN for thumbnails that render directly in Notion file/media properties:
  - Preferred Worker/R2 upload mode: `BRAND_CDN_BASE_URL` + `BRAND_CDN_UPLOAD_TOKEN` + `BRAND_CDN_UPLOAD_BUCKET`.
  - Static/mount fallback: `BRAND_CDN_BASE_URL` + `BRAND_CDN_UPLOAD_DIR`.

The script is intentionally fail-fast on first run. If required access/config is missing, it prints setup instructions rather than guessing or writing secrets anywhere.

Copy the template and fill it in **outside the repo**:

```bash
cp templates/config.example.env /private/path/brand-asset-manifest.env
$EDITOR /private/path/brand-asset-manifest.env
set -a; . /private/path/brand-asset-manifest.env; set +a
```

Important: never commit real API keys, OAuth tokens, Notion IDs for private workspaces, or CDN credentials. The repo contains only templates/placeholders.

Key env vars:

```bash
export DRIVE_FOLDER_ID="<google-drive-folder-id>"
export MANIFEST_LIMIT=50                         # omit/0 for all files
export MANIFEST_RECURSIVE=true                   # crawl nested folders by default
export MANIFEST_RENAME_FILES=true                 # rename Drive files after analysis
export ASSET_TAXONOMY_VERSION=v0-discovery        # reviewed/evolving taxonomy label
export BRAND_CDN_BASE_URL="https://brand-cdn.figandbloom.workers.dev"
export BRAND_CDN_UPLOAD_TOKEN="<worker-upload-token>"
export BRAND_CDN_UPLOAD_BUCKET="figandbloom"       # public Worker bucket slug: figandbloom/whoosh/bower
export BRAND_CDN_UPLOAD_URL_TEMPLATE="${BRAND_CDN_BASE_URL}/upload/{bucket}/{key}"  # optional
# Static fallback only:
# export BRAND_CDN_UPLOAD_DIR="/srv/brand-cdn/public"
export GEMINI_PROVIDER=openrouter                # or google
export GEMINI_MODEL="google/gemini-3-flash-preview"  # OpenRouter example
export NOTION_BRAND_ASSET_DATABASE_ID="<existing-notion-db-id>"
export NOTION_BRAND_ASSET_PARENT_PAGE_ID="<page-id-to-create-db-if-missing>"
export MANIFEST_WORKDIR="/private/local/output/path"
```

If no Notion database ID is available, ask the user for a parent Notion page and make sure it is shared with the Hermes/Notion integration before creating a database.

## Notion Database Schema

Recommended properties:

- `Asset` — title; current intuitive filename after analysis.
- `Drive File ID` — rich text; stable dedupe key.
- `File Handle` — rich text; `drive:<id> | <filename>`.
- `Drive Link` — URL.
- `Preview URL` — URL; public CDN/thumbnail/proxy link for inline preview.
- `Preview` — files/media; external CDN thumbnail/preview when public URL is available.
- `Source Folder` — rich text.
- `Folder Path` — rich text.
- `Mime Type` — rich text.
- `Asset Type` — select: video, image, other.
- `Duration Seconds` — number.
- `Dimensions` — rich text.
- `Aspect Ratio` — select/rich text.
- `Orientation` — select: portrait, landscape, square, unknown.
- `Size MB` — number.
- `Overall Description` — rich text.
- `Content Type` — select/rich text.
- `Mood Tone` — multi-select.
- `Visual Tags` — multi-select.
- `People Present` — rich text.
- `Products / Flowers` — multi-select.
- `Contains Product` — AI select: yes/no; model-derived and not trusted as canonical.
- `Product Name` — AI-suggested product name from the controlled catalogue; use as a suggestion/training signal, not the source of truth.
- `Product Match Confidence` — AI confidence score; useful for sorting/calibration but not sufficient proof of correctness.
- `Human Product Name` — human-verified product name; use this as the canonical product field for downstream pulls when populated.
- `Product Match Review` — select: unreviewed, correct, incorrect, not a product, unclear/multiple.
- `Setting / Location` — rich text.
- `Usable For` — multi-select.
- `Reorg Notes` — rich text.
- `Timestamp Beats` — rich text or page body block; long JSON/readable beat breakdown.
- `Manifest Model` — rich text.
- `Taxonomy Version` — rich text; the taxonomy pass/version used for tags.
- `Taxonomy Candidates` — multi-select; candidate tags from this asset for later taxonomy review.
- `Original Filename` — rich text; filename before script renaming.
- `Renamed At` — date; set only when Drive file was renamed.
- `Manifested At` — date.

Keep multi-select values short: strip commas, truncate long phrases, and dedupe.

## Viewable Assets in Notion

Notion database URL properties are reliable but require clicking out. To make assets viewable inside Notion, prefer one of these approaches:

1. **Public CDN URL** — best option for reusable brand libraries. Publish a generated thumbnail/proxy rendition to the brand CDN and store it in both `Preview URL` and `Preview` file/media property. This gives inline viewing in Notion and keeps Drive originals private.
2. **Notion file upload** — useful for sampled thumbnails/contact sheets. Upload extracted JPEG thumbnails to Notion and add image blocks. This is good for quick visual scanning but duplicates media into Notion.
3. **External Drive link only** — simplest but not ideal. Private Google Drive links usually do not render as inline media in Notion for every viewer/session, so keep them as source handles, not previews.

For video assets, usually store:

- `Drive Link` — canonical/private source.
- `Preview URL` — public CDN thumbnail or proxy MP4 when available.
- `Preview` file/media property — public CDN thumbnail, so the database can show media inline.
- Page body — optional first frame/contact sheet plus timestamp beats.

## Workflow

1. **Verify Google Drive access**
   ```bash
   export PATH=/opt/data/npm-global/bin:/opt/data/home/.local/bin:$PATH
   export HOME=/opt/data/home
   gws drive files list --params '{"pageSize":10,"includeItemsFromAllDrives":true,"supportsAllDrives":true,"fields":"files(id,name,mimeType),nextPageToken"}' --format json
   ```

2. **List target folder contents**
   ```bash
   gws drive files list --params '{"q":"\"<FOLDER_ID>\" in parents and trashed=false","includeItemsFromAllDrives":true,"supportsAllDrives":true,"pageSize":100,"fields":"files(id,name,mimeType,parents,driveId,size,videoMediaMetadata,webViewLink),nextPageToken"}' --format json
   ```

3. **Run the reusable script**
   ```bash
   set -a; [ -f /opt/data/.env ] && . /opt/data/.env; set +a
   export PATH=/opt/data/npm-global/bin:/opt/data/home/.local/bin:$PATH
   export HOME=/opt/data/home
   export DRIVE_FOLDER_ID="<FOLDER_ID>"
   export MANIFEST_LIMIT=25
   export MANIFEST_RECURSIVE=true
   export MANIFEST_RENAME_FILES=true
   export BRAND_CDN_BASE_URL="<PUBLIC_CDN_BASE_URL>"
   export BRAND_CDN_UPLOAD_DIR="<LOCAL_OR_MOUNTED_CDN_PUBLIC_DIR>"
   export NOTION_BRAND_ASSET_DATABASE_ID="<DB_ID>"   # if already created
   python /opt/data/skills/productivity/brand-asset-manifesting/scripts/drive_video_manifest_to_notion.py
   ```

4. **Verify Notion sync**
   - Query by `Drive File ID` count.
   - Confirm no duplicates.
   - Spot-check a few pages for readable timestamp beat notes.
   - Confirm local JSON backup path from the script summary.

5. **Rename source files on first pass**
   - Do not reorganise folders during the first pass.
   - Rename each Drive file after analysis to a short, intuitive, content-based filename.
   - Keep `Drive File ID` as the canonical dedupe key and store `Original Filename` for audit/reversal.

6. **Taxonomy review at end of each run**
   - Treat tags from early batches as candidates, not final truth.
   - Write a taxonomy review JSON with top terms, one-off terms, and merge/synonym candidates.
   - Do not rewrite all historical records automatically unless the user approves a taxonomy migration.
   - When a taxonomy stabilises, bump `ASSET_TAXONOMY_VERSION` and run a deliberate update pass.

7. **Scale to entire drive**
   - Run in batches with `MANIFEST_LIMIT` and existing Notion DB.
   - Keep `Drive File ID` as the dedupe key.
   - Store failures in local JSON for retry instead of dropping them.

## Timestamp Beat Guidance

Each video should include:

- Whole-video description in 2–4 sentences.
- Shot/beat breakdown with `start_s`, `end_s`, `shot_description`, `shot_type`, and `ai_usefulness`.
- Practical reuse notes: ad hooks, product detail, texture/background, UGC, seasonal content, behind-the-scenes, delivery, founder/team, etc.

For very short videos, 3–5 beats is enough. For longer videos, sample 6–10 visual frames and ask Gemini to infer coherent beats; do not pretend frame sampling is a full frame-by-frame analysis.

## Product Classification Review Loop

Treat exact product tagging as a review/calibration layer, not as fully automated truth:

- Keep `Product Name`, `Contains Product`, and `Product Match Confidence` as AI-generated suggestion fields.
- Use `Human Product Name` as the canonical downstream product value whenever a human has reviewed the asset.
- Use `Product Match Review` to label the AI suggestion: `unreviewed`, `correct`, `incorrect`, `not a product`, or `unclear/multiple`.
- Automated reruns must not overwrite `Human Product Name` or `Product Match Review` on existing pages.
- Reviewed rows become an evaluation set for improving candidate filtering, prompts, thresholds, and later possible fine-tuning.

## Evolving Taxonomy Strategy

Asset tagging should be adaptive. During discovery runs, let Gemini produce rich candidate tags, but keep them bounded and versioned:

- Use `ASSET_TAXONOMY_VERSION=v0-discovery` while exploring the library.
- Store raw/candidate tags in Notion, but generate an end-of-run taxonomy review report.
- Review synonym clusters, over-specific one-off tags, and under-specified high-frequency tags.
- Promote stable categories only after enough assets have been ingested.
- Avoid automatic system-wide rewrites on every run; instead propose a migration plan, then run a controlled normalisation pass if approved.

Good taxonomy reports should answer:

- Which tags are common enough to become canonical?
- Which tags should be merged?
- Which content categories are missing?
- Which old rows need retagging if the taxonomy changes?

## Common Pitfalls

1. **Sampling too close to video EOF.** Sparse social videos can report a 20s duration but have frames only at whole seconds. Avoid final-millisecond seeks and retry earlier timestamps.
2. **Using Google Sheets as the long-term database.** Sheets are fine for exports, but Notion should be canonical for curation and AI asset retrieval.
3. **Creating duplicate Notion databases.** Search/pin one canonical DB. If the DB is inaccessible, ask the user to share it with the integration instead of creating another table.
4. **Losing stable handles.** Always store Drive file ID, original filename, source folder, folder path, MIME type, and Drive URL before any reorganisation.
5. **Overloading multi-selects.** Long phrases and commas create messy Notion options. Put long text in rich text/body blocks.
6. **Assuming shared-drive root equals folder ID.** A shared-drive root parent is usually the `driveId`, while a normal folder parent is the folder ID.
7. **Forgetting API versions.** If newer Notion versions behave differently, use the older database endpoints with `Notion-Version: 2022-06-28` for stable database/page sync.
8. **Reconstructing CDN URLs manually.** In Worker/R2 upload mode, always store the `url` returned by the `brand-cdn` Worker response. The current Worker endpoint uses public bucket slugs such as `figandbloom`, `whoosh`, and `bower` in `POST /upload/:bucket/:key`; do not use Cloudflare binding variable names like `FIGANDBLOOM_BUCKET` unless the Worker source has explicitly been changed to accept them.

## Verification Checklist

- [ ] Target Drive folder/shared drive was listed successfully.
- [ ] Files are deduped by `Drive File ID`.
- [ ] Local JSON backup and taxonomy review JSON were written.
- [ ] Notion database ID is captured/pinned for future runs.
- [ ] Notion row count and unique Drive File IDs match the processed count.
- [ ] At least 3 synced assets have useful descriptions, timestamp beats, CDN previews, and intuitive renamed filenames.
- [ ] Any failed assets are logged for retry.
