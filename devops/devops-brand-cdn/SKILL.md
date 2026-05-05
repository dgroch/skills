---
name: devops-brand-cdn
description: Upload files to the Fig & Bloom Cloudflare R2 CDN and get back a public URL ready to drop into Notion, an email, an ad creative, or anywhere else a permanent image link is needed. Use whenever an image, video, or asset needs a stable public URL — including hosting Higgsfield-generated outputs, attaching seed images to Notion brand databases, hosting Figma exports for review, or pulling any local file or remote URL into a brand-scoped bucket. Trigger on phrases like "upload this", "host this image", "put this in R2", "give me a public URL", "save to whoosh bucket", "attach to Notion", or any time a downstream tool needs a URL Notion or another system can fetch.
author: Daniel Groch
license: MIT
---

# DevOps Brand CDN

Upload assets to the Fig & Bloom Cloudflare R2 CDN, get back a public URL. One bucket per brand. Used by `creative-brand-photographer`, `creative-add-creative-builder`, `photography-ugc-review`, and anything else that needs to host files publicly.

## Architecture

A single Cloudflare Worker (`brand-cdn`) handles both upload and public read. R2 buckets stay private — all access flows through the Worker.

- **Upload:** `POST /upload/:bucket/:key` with `Authorization: Bearer ${UPLOAD_TOKEN}` → file lands in R2, Worker returns the public URL
- **Public read:** `GET /:bucket/:key` (no auth, cached forever) → that's the URL to put in Notion or anywhere else
- **Buckets:** one per brand teamspace. Currently `whoosh`, `bower`, and `figandbloom`. Adding a new brand = create the bucket, add an R2 binding to the Worker, add one line to the Worker's `BUCKETS` map.

## When to use this skill

- A `creative-brand-photographer` generation finished and the output needs to live somewhere stable so it can be attached to Notion
- A user dragged a reference photo into chat and wants it added to the Characters/Locations/Products database
- A `creative-add-creative-builder` rendered a creative and the team needs a shareable URL
- Any Notion `File` property where you'd otherwise hit the "I can only attach existing file IDs, not URLs" wall — Notion accepts external URLs in `cover` and `icon`, and the public Worker URLs work seamlessly there
- Anywhere else you need a permanent, cacheable, public URL for a file

## When NOT to use this skill

- For ephemeral output the user just needs to see once → use `present_files` instead
- For files that should remain private → R2 has no public-read enabled; only the Worker's GET path is public, but it's unauthenticated, so don't put anything sensitive in these buckets
- For static brand assets that already live on the brand's own domain (logos at `figandbloom.com.au/assets/...`) → use the existing URL

## Prerequisites

Two things must be true before any upload works. If either fails, fix it before proceeding — don't try to work around it.

### 1. Credentials in `.env`

The skill looks in three places, in order:

1. `/home/claude/.env` — Claude Code Execution convention
2. `/opt/data/.env` — Hermes profile convention
3. `~/.env` — standard fallback

The file should contain at minimum a Worker URL and an upload token. Either var name works for the token:

```
WORKER_URL=https://brand-cdn.figandbloom.workers.dev
BRAND_CDN_UPLOAD_TOKEN=<the secret>     # preferred (namespaced)
# or
UPLOAD_TOKEN=<the secret>               # legacy / single-skill envs
```

The namespaced form (`BRAND_CDN_UPLOAD_TOKEN`) is preferred when the `.env` holds secrets for multiple skills. The script accepts either; if both are set, `UPLOAD_TOKEN` wins.

If no `.env` exists or the keys are missing, **stop and ask the user for the token**. The token is rotatable in Cloudflare → Workers → brand-cdn → Settings → Variables and Secrets. Never echo the token back into chat after writing it.

### 2. Worker host reachable from the runtime

`brand-cdn.figandbloom.workers.dev` must be reachable from wherever the agent's code runs. The exact location depends on the runtime:

- **Claude Code Execution:** Settings → Capabilities → Code execution → Allowed domains
- **Hermes profile:** profile's network allowlist / egress config
- **Other runtimes:** outbound HTTPS to `*.figandbloom.workers.dev`

Symptom of a missing allowlist: HTTP 403 with header `x-deny-reason: host_not_allowed`. If you see that, **stop and tell the user** — don't keep retrying.

Run the smoke test below as the first thing in any session that uses this skill.

## Quickstart

```bash
# Smoke test the Worker (always do this first)
bash scripts/upload.sh --health

# Upload a local file
bash scripts/upload.sh whoosh characters/maya.png /tmp/maya.png

# Upload a remote URL (e.g. Higgsfield output)
bash scripts/upload.sh figandbloom generations/2026-05-03_doorstep-v1.png \
  https://platform.higgsfield.ai/.../some-output.png

# Or via Python (handles both, returns just the URL on stdout)
python scripts/upload.py whoosh characters/maya.png /tmp/maya.png
```

Output on success is a single line — the public URL. Pipe it into whatever needs it next.

## Key naming conventions

Keep the structure consistent so the bucket stays browsable and Notion attachments stay legible.

```
<brand>/characters/<slug>.<ext>           e.g. whoosh/characters/maya.png
<brand>/locations/<slug>.<ext>            e.g. whoosh/locations/apartment-doorstep.png
<brand>/products/<slug>.<ext>             e.g. whoosh/products/piccolo-pistachio-pop.png
<brand>/generations/<date>_<slug>.<ext>   e.g. whoosh/generations/2026-05-03_maya-doorstep_v1.png
<brand>/uploads/<date>_<slug>.<ext>       e.g. whoosh/uploads/2026-05-03_user-photo.jpg
```

Slugs are lowercase, hyphen-separated, no spaces, no special characters. Date is `YYYY-MM-DD`. Versioning suffix (`_v1`, `_v2`) is fine for iteration.

The brand prefix in the key matches the bucket name — that's redundant in the URL but it makes bucket browsing in the Cloudflare dashboard much cleaner if a brand ever needs to be migrated.

## Common workflows

### Hosting a Higgsfield generation

After a Higgsfield job completes and returns a URL, push it to R2 so the public URL is stable and Notion-safe (Higgsfield URLs are subject to their CDN policies).

```bash
HIGGS_URL="https://platform.higgsfield.ai/.../output.png"
KEY="generations/2026-05-03_doorstep-maya_v1.png"
PUBLIC_URL=$(python scripts/upload.py whoosh "$KEY" "$HIGGS_URL")
echo "Hosted at: $PUBLIC_URL"
```

That URL goes straight into Notion via `notion-update-page` (page cover or content embed) or `notion-create-pages` (cover field).

### Attaching to a Notion `File` property

Notion's `File` property type accepts external URLs via the API, but the current Notion MCP `create-pages` / `update-page` tools serialize file properties differently — many of them only accept previously-uploaded Notion file IDs, not external URLs. If you hit that wall:

1. Upload through this skill, get the public URL
2. Set the page's `cover` to the URL (cover always accepts external URLs)
3. Or embed the image inline in the page body via Markdown: `![alt](https://brand-cdn.figandbloom.workers.dev/whoosh/characters/maya.png)`
4. Mention the URL in the relevant property if the field is a URL or text type

If the user really needs the image in the `File` property specifically, tell them — they can drag the file onto the row in Notion's UI manually using the public URL from this skill.

## Adding a new brand

1. Create the R2 bucket: name = brand slug (lowercase, no spaces). Use Cloudflare MCP `r2_bucket_create` or the dashboard.
2. In the Worker (Cloudflare → Workers → brand-cdn → Edit code), add the brand to the `BUCKETS` map at the top:
   ```js
   const BUCKETS = {
     whoosh: 'WHOOSH_BUCKET',
     bower: 'BOWER_BUCKET',
     figandbloom: 'FIGANDBLOOM_BUCKET',
     newbrand: 'NEWBRAND_BUCKET',  // ← add this line
   };
   ```
3. In Worker → Settings → Bindings, add an R2 binding: variable name `NEWBRAND_BUCKET`, bucket `newbrand`.
4. Deploy the Worker.

Reference copy of the deployed Worker code is in `worker-source.js` for diff'ing or re-deploying.

## When in doubt

- Smoke test fails? → Read the response. `host_not_allowed` is allowlist; `401` is bad token; `404` from a GET is just "key doesn't exist yet"; anything else, surface to the user.
- User pasted a token? → Write it straight to the appropriate `.env`, don't echo it back.
- Bucket doesn't exist? → Create it via Cloudflare MCP, add the binding, redeploy. Don't silently fall back to a different bucket.
- A different agent session is asking? → Same skill, same Worker. The skill is brand-agnostic; the bucket name is the per-brand part.

See `references/setup.md` for first-time setup on a new device or after credential rotation.
