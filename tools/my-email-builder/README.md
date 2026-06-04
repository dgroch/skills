# Fig & Bloom — Email Builder (canonical source lives elsewhere)

The Fig & Bloom email builder is a standalone application with its **own repository
and deployment**. It is intentionally **not vendored into this repo** — a partial copy
previously lived at `tools/my-email-buider/` and drifted badly out of sync with the
running service, so it was removed.

## Where it actually lives

| | |
|---|---|
| **Source repo** | https://github.com/dgroch/my-email-buider |
| **Live deploy** | https://my-email-builder.onrender.com (Render, free plan — cold start after idle) |
| **Deploys from** | `main` of the source repo (autoDeploy) |

> Note the source repo is spelled `my-email-buider` (historical typo); the live URL is
> `my-email-builder`.

## What it is

A JSON-first builder for on-brand Fig & Bloom campaign emails. Agents and the human UI
both drive it through the same HTTP API: generate campaign JSON → assemble/render →
save (Notion-backed) → optionally push a Klaviyo draft. Designed blocks are rasterised
to PNG via Puppeteer because their layout (rotate/overlap/script-over-serif) does not
survive as live email HTML.

Live API (verified): `GET /api/schema`, `POST /api/assemble`, `POST /api/render`,
`POST /api/render-slices`, `POST /api/export`, `GET|POST /api/designs`,
`GET|PUT|DELETE /api/designs/:id`, `POST /api/designs/:id/clone`,
`GET /api/klaviyo-audiences`, `POST /api/klaviyo-draft`.

## How this relates to the skill

The agent-facing contract — JSON-first workflow, group-prefixed component names,
component-selection strategy, the live API table — is documented in the skill:

- `creative/creative-email-campaign-builder/SKILL.md` (the **CANONICAL WORKFLOW** block)
- `creative/creative-email-campaign-builder/references/component-strategy.md`

The builder's `design-system/` (templates, shells, assets, manifest) is a copy of the
skill's `creative/creative-email-campaign-builder/references/`. That library is the
**single source of truth for the design system**; the builder repo mirrors it. Make
template/manifest changes in the skill's `references/`, then sync them into the builder
repo — never the other way around.

## Working on the builder itself

Clone and deploy from the source repo, not from here:

```bash
git clone https://github.com/dgroch/my-email-buider.git
```

Changes to the builder application (server, render pipeline, persistence, Klaviyo,
client UI) belong in that repo and deploy through its own Render blueprint.
