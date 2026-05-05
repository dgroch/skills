# Notion + Google Drive Brand Asset Manifesting Lessons

## Session-specific facts worth reusing

- A Notion URL that looks like `https://www.notion.so/Asset-Manifest-<id>` may be a **page**, not a database. First try `/v1/databases/<id>`; if Notion returns “Provided ID ... is a page, not a database”, use `/v1/pages/<id>` and create a child database under that page if the integration has access.
- For this user's current Fig & Bloom asset manifest, the created database was `357fdc24-425f-81ed-805c-c4f9aff0665f` under Asset Manifest page `357fdc24-425f-804a-9660-fc8322a5ae75`; it is pinned locally as `NOTION_BRAND_ASSET_DATABASE_ID`.
- Initial verified Notion sync processed 10 videos from Drive folder `1SAfYZUaP7pnMen_D7eT59fbKwqHx6-6_`: 10 created, 0 failed, 10 unique Drive File IDs, 10 rows with preview file metadata.

## Git/reference skill hygiene

- When adding this as a reference skill to `dgroch/skills`, keep repo content generic and secret-free. Use `templates/config.example.env` with comments/placeholders; never commit filled `.env` files, API keys, Notion tokens, OAuth tokens, or private CDN credentials.
- Running `python -m py_compile` may create `__pycache__` under the skill scripts directory. Remove it before committing and ensure `.gitignore` covers `__pycache__/` and `*.py[cod]`.
- Do a simple static secret scan before commit for obvious OpenRouter, Notion, Google API key, and private-key markers. Do not include real credential prefixes in committed examples.

## Notion preview strategy

- Notion URL properties are reliable but require click-out.
- For inline/browsable previews, prefer a public CDN thumbnail/proxy URL stored in both `Preview URL` and a `Preview` files/media property.
- Private Google Drive links are canonical source handles but are inconsistent as inline Notion media; keep them in `Drive Link`, not as the primary preview UX.
- For videos, a CDN poster/contact sheet or proxy MP4 is usually better than attaching full originals to Notion.
- If `BRAND_CDN_BASE_URL` and `BRAND_CDN_UPLOAD_DIR` are configured, generated thumbnails should be copied into the CDN tree and used in Notion `Preview`.

## Rename-on-manifest policy

- First pass should **not** reorganise Drive folders.
- It may rename each Drive file to a short, intuitive, content-based name after analysis.
- Store `Original Filename`, `Drive File ID`, and `Renamed At` so renames are auditable and reversible.
- Keep filenames short and simple; use descriptions/tags as inputs, not long SEO-style names.

## Evolving taxonomy

- Treat discovery-run tags as candidates, not canonical truth.
- Store `Taxonomy Version` and write a taxonomy review JSON after each run with top terms and one-off merge candidates.
- Do not automatically rewrite system-wide historical tags after every run. Propose taxonomy migrations, then run controlled update passes when the user approves.

## Whole-drive crawling

- Whole shared-drive crawling needs recursive traversal: list children, queue folders, and collect `video/*` and `image/*` files. Preserve `folderPath` alongside Drive ID/name before any reorganisation.
- Keep `Drive File ID` as the dedupe key and write a local JSON backup for retry/audit.
