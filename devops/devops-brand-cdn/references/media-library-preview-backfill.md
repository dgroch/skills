# Media Library Preview Backfill

Use this when running a repo-local script that backfills Fig & Bloom Brand Asset Manifest `Preview URL` values from Google Drive originals into the brand CDN.

## Pattern

1. Run the script dry first to count affected rows.
2. Run `--yes --limit 5` as a smoke test.
3. Verify at least one written CDN URL with a normal GET, checking `HTTP 200`, `content-type: image/jpeg`, and JPEG first bytes (`ff d8 ...`). If a ranged GET returns 403, retry a normal GET before declaring failure.
4. Run the full `--yes` pass only after smoke success.
5. Re-run dry at the end. Remaining rows may be legitimate non-images/videos if the script only creates JPEG previews for images.

## Render + Google credential bridge

If the media library app already has the production Notion/R2 env in Render:

- Fetch env from Render service `asset-library` instead of copying secrets manually.
- Use `ASSET_R2_BUCKET` for the brand CDN bucket when present; Render may also have `R2_BUCKET` for a different asset-index bucket.
- Mint `GOOGLE_ACCESS_TOKEN` immediately before the run from local `gws` OAuth with `gws auth export --unmasked` and the Google OAuth token endpoint.
- Never print token or R2 secret values. Only log service ID, key names/presence, bucket name, counts, and public CDN URLs used for verification.

## Interpreting results

- `filled`: Notion row was patched with a public CDN preview.
- `skipped (non-image)`: expected for Drive originals that are `video/mp4`, `video/quicktime`, etc.; the JPEG preview script intentionally skips these.
- A post-run dry-run count that consists of video assets is not a failure of the image preview backfill. Video preview generation is a separate workflow.
