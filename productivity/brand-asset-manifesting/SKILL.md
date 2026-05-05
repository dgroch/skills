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
- `ffmpeg` and `ffprobe` for video frame extraction.

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
export GEMINI_PROVIDER=openrouter                # or google
export GEMINI_MODEL="google/gemini-3-flash-preview"  # OpenRouter example
export NOTION_BRAND_ASSET_DATABASE_ID="<existing-notion-db-id>"
export NOTION_BRAND_ASSET_PARENT_PAGE_ID="<page-id-to-create-db-if-missing>"
export MANIFEST_WORKDIR="/private/local/output/path"
```

If no Notion database ID is available, ask the user for a parent Notion page and make sure it is shared with the Hermes/Notion integration before creating a database.

## Notion Database Schema

Recommended properties:

- `Asset` — title; original filename or human label.
- `Drive File ID` — rich text; stable dedupe key.
- `File Handle` — rich text; `drive:<id> | <filename>`.
- `Drive Link` — URL.
- `Preview URL` — URL; public CDN/thumbnail/proxy link for inline preview.
- `Preview` — files/media; external preview image/video when public URL is available.
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
- `Setting / Location` — rich text.
- `Usable For` — multi-select.
- `Reorg Notes` — rich text.
- `Timestamp Beats` — rich text or page body block; long JSON/readable beat breakdown.
- `Manifest Model` — rich text.
- `Manifested At` — date.

Keep multi-select values short: strip commas, truncate long phrases, and dedupe.

## Viewable Assets in Notion

Notion database URL properties are reliable but require clicking out. To make assets viewable inside Notion, prefer one of these approaches:

1. **Public CDN URL** — best option for reusable brand libraries. Use the brand CDN workflow to publish a thumbnail/proxy rendition and store it in a `Preview URL` property. Add the same URL as an image/video block in the asset page body. This gives inline viewing and keeps Drive permissions private.
2. **Notion file upload** — useful for sampled thumbnails/contact sheets. Upload extracted JPEG thumbnails to Notion and add image blocks. This is good for quick visual scanning but duplicates media into Notion.
3. **External Drive link only** — simplest but not ideal. Private Google Drive links usually do not render as inline media in Notion for every viewer/session, so keep them as source handles, not previews.

For video assets, usually store:

- `Drive Link` — canonical/private source.
- `Preview URL` — public CDN thumbnail or proxy MP4 when available.
- Page body — first frame/contact sheet plus timestamp beats.

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
   export NOTION_BRAND_ASSET_DATABASE_ID="<DB_ID>"   # if already created
   python /opt/data/skills/productivity/brand-asset-manifesting/scripts/drive_video_manifest_to_notion.py
   ```

4. **Verify Notion sync**
   - Query by `Drive File ID` count.
   - Confirm no duplicates.
   - Spot-check a few pages for readable timestamp beat notes.
   - Confirm local JSON backup path from the script summary.

5. **Scale to entire drive**
   - Run in batches with `MANIFEST_LIMIT` and existing Notion DB.
   - Keep `Drive File ID` as the dedupe key.
   - Store failures in local JSON for retry instead of dropping them.

## Timestamp Beat Guidance

Each video should include:

- Whole-video description in 2–4 sentences.
- Shot/beat breakdown with `start_s`, `end_s`, `shot_description`, `shot_type`, and `ai_usefulness`.
- Practical reuse notes: ad hooks, product detail, texture/background, UGC, seasonal content, behind-the-scenes, delivery, founder/team, etc.

For very short videos, 3–5 beats is enough. For longer videos, sample 6–10 visual frames and ask Gemini to infer coherent beats; do not pretend frame sampling is a full frame-by-frame analysis.

## Common Pitfalls

1. **Sampling too close to video EOF.** Sparse social videos can report a 20s duration but have frames only at whole seconds. Avoid final-millisecond seeks and retry earlier timestamps.
2. **Using Google Sheets as the long-term database.** Sheets are fine for exports, but Notion should be canonical for curation and AI asset retrieval.
3. **Creating duplicate Notion databases.** Search/pin one canonical DB. If the DB is inaccessible, ask the user to share it with the integration instead of creating another table.
4. **Losing stable handles.** Always store Drive file ID, original filename, source folder, and Drive URL before any reorganisation.
5. **Overloading multi-selects.** Long phrases and commas create messy Notion options. Put long text in rich text/body blocks.
6. **Assuming shared-drive root equals folder ID.** A shared-drive root parent is usually the `driveId`, while a normal folder parent is the folder ID.
7. **Forgetting API versions.** If newer Notion versions behave differently, use the older database endpoints with `Notion-Version: 2022-06-28` for stable database/page sync.

## Verification Checklist

- [ ] Target Drive folder/shared drive was listed successfully.
- [ ] Files are deduped by `Drive File ID`.
- [ ] Local JSON backup was written.
- [ ] Notion database ID is captured/pinned for future runs.
- [ ] Notion row count and unique Drive File IDs match the processed count.
- [ ] At least 3 synced assets have useful descriptions and timestamp beats.
- [ ] Any failed assets are logged for retry.
