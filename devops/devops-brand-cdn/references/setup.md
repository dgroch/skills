# devops-brand-cdn — first-time setup

Anything that needs to happen once per user, per device, per agent profile, or after a credential rotation.

## Credentials

The skill reads from the first `.env` it finds, in this order:

1. `/home/claude/.env` — Claude Code Execution
2. `/opt/data/.env` — Hermes profile
3. `~/.env` — standard fallback

Either env file should contain:

```
WORKER_URL=https://brand-cdn.figandbloom.workers.dev
BRAND_CDN_UPLOAD_TOKEN=<the secret>     # preferred (namespaced)
# or
UPLOAD_TOKEN=<the secret>               # legacy / single-skill envs
```

The script accepts either var name. `UPLOAD_TOKEN` wins if both are set. Use the namespaced form when the `.env` is shared across multiple skills.

The token is generated when the Worker is deployed and stored as a Cloudflare Secret. To get or rotate it: Cloudflare → Workers → `brand-cdn` → Settings → Variables and Secrets → `UPLOAD_TOKEN`.

If the user pastes the token in chat, write it straight to the appropriate `.env` and don't echo it back. The transcript still contains the secret, but the blast radius is bounded — the token only grants upload to the configured buckets, not account-level access. Rotate in one click if it leaks.

## Network allowlist

The Worker host must be reachable from wherever the agent's code runs. Where you configure that depends on the runtime:

- **Claude Code Execution** → Settings → Capabilities → Code execution → Allowed domains. Add `brand-cdn.figandbloom.workers.dev`.
- **Hermes profile** → profile network / egress config. Add the same host.
- **Other runtimes** → ensure outbound HTTPS to `*.figandbloom.workers.dev` is permitted.

If the host is missing from the allowlist, every upload/health request returns HTTP 403 with `x-deny-reason: host_not_allowed`. Don't try to work around this by going through the Cloudflare MCP — the MCP doesn't expose object-write tools, the Worker is the upload path.

If a custom domain ever replaces the `*.workers.dev` URL (e.g. `cdn.figandbloom.com`), update both the `.env` and the allowlist.

## Smoke test

Run this as the first thing in any session that uses this skill:

```bash
bash <skill_path>/scripts/upload.sh --health
```

Expected output: `ok`. Anything else, surface to the user — don't proceed.

## Deploying the Worker (only needed once, or to update)

The Worker is already deployed. These steps are for re-deploying after edits or for a fresh account.

1. Cloudflare dashboard → Workers & Pages → Create → name `brand-cdn` → Deploy default
2. Edit code → paste contents of `worker-source.js` → Deploy
3. Settings → Bindings:
   - R2 bucket: variable `WHOOSH_BUCKET` → bucket `whoosh`
   - R2 bucket: variable `BOWER_BUCKET` → bucket `bower`
   - R2 bucket: variable `FIGANDBLOOM_BUCKET` → bucket `figandbloom`
   - Secret: `UPLOAD_TOKEN` → a long random string (`openssl rand -hex 32`)
4. Save and deploy
5. Visit the Worker URL — should return `ok`

When adding a new brand bucket later, only edit the `BUCKETS` map in `worker-source.js`, add an R2 binding, and redeploy. Existing brands keep working.

## Custom domain (optional)

The `*.workers.dev` URL works fine but isn't pretty in Notion. To use a custom domain like `cdn.figandbloom.com.au`:

1. Worker → Settings → Domains & Routes → Add Custom Domain
2. Enter the domain (the parent zone must already be on Cloudflare)
3. Cloudflare provisions DNS automatically
4. Update `WORKER_URL` in `.env` to the new domain
5. Update the runtime's network allowlist to the new domain
6. Existing object URLs continue to work at the old `*.workers.dev` host — both domains point at the same Worker

Don't migrate URLs already in Notion until you're ready to update them in bulk. Two URL hosts pointing at the same files is fine indefinitely.
