
## Legacy v4 engine (reference only)

The 10-step v4 pipeline (Brief → Products → Copy → Select → Render → Validate → Preview → Upload → Production → Klaviyo) is **superseded** by the v5 engine + the JSON-first workflow above. It is preserved in `references/v4-legacy-pipeline.md` for historical reference, debugging old campaigns, and understanding the rendering internals the builder API wraps. **Do not follow it for new work.**

## What the agent does NOT do in v4

- Write HTML
- Choose colours, fonts, or spacing
- Resize or reposition illustrations
- Add, remove, or modify SVG icons
- Override any locked style in a template

If a campaign need cannot be met with the existing templates, escalate for template development. Do not improvise HTML.

---

### Companion: `fig-bloom-email-generator` (and the live-context pattern)

> A new companion skill — **`fig-bloom-email-generator`** (lives in `dgroch/skills/creative/fig-bloom-email-generator/`, NOT the local skills registry) — packages the brand + persona + lens-routing + schema context into a single LLM call, so a brief (from the email-builder "Create Campaign" button or an agent conversation) produces a complete, validated campaign JSON in one shot.

### Render free-tier 30s timeout on `/api/campaigns/generate` — fall back to direct authoring

The live email builder is on Render's `free` plan, which kills any HTTP request that takes longer than 30s with a 502. LLM calls to Anthropic Sonnet 4 typically take 50–60s end-to-end (system prompt + live context + generation + JSON extraction + validation retry), so the LLM call is reliably killed mid-flight. The error surface is misleading: the server returns `{"error":"Validation still failing after retry.","raw":null}` even though the real cause is a Render-level timeout, not a validation failure.

**When the live builder's generator times out, write the campaign directly** using the brand-voice guidance baked into the system prompt + the live context fetched from `/api/live-context`. Workflow:

1. **Fetch live context** with the brief as the `q=` param: `GET /api/live-context?q=<brief>`. This is fast (1-2s) and gives you real products, audiences, blog posts, and 24 semantically-ranked lifestyle images.
2. **Compose the campaign JSON by hand**, using the brand-voice rules from the system prompt: lowercase Cervanttis hero, sentence-case Lust headlines, Australian English, no urgency/countdown/discount framing, "more not off" for the 20% more stems offer, etc.
3. **Save the JSON to disk** (e.g. `/tmp/<slug>-campaign.json`) so it's not lost if the next step fails.
4. **Validate against the live builder**: `POST /api/validate` with the JSON body. Expect `{"ok": true}` with no errors. If validation fails, fix the JSON and re-validate. The validator is fast (<1s).
5. **Assemble to HTML for QA**: `POST /api/assemble`. Returns 250KB+ of clean HTML with no unfilled tokens.
6. **Render to PNG (if needed)**: `POST /api/render`. **Currently broken on Render** with `'height' in 'clip' must be positive` — see the "Render /api/render height pitfall" below.

This manual workflow is what the system prompt is calibrated for — it's a brand-voice spec, not an LLM oracle. A human pass is always warranted, but the system prompt's 13-point QA bar is rigorous enough that a careful hand-write lands in the same quality bucket as a generator run.

### Anthropic model name gotcha — only `claude-sonnet-4-20250514` is known-good on this account

`mcp_render_update_environment_variables` accepts `CAMPAIGN_LLM_MODEL`. As of 9 Jun 2026, the following names **return 404 from the API account that the Render service uses**:

- `claude-3-5-haiku-20241022` — 404
- `claude-sonnet-4-5` — 404 (no date suffix)
- `claude-haiku-4-5`, `claude-haiku-4-5-20251001` — 404

**The known-good default is `claude-sonnet-4-20250514`** (the hardcoded fallback in `lib/campaignGenerator.js`). When the LLM is unreachable, restore the env var to that value via the Render MCP tool and let the next deploy come up. Don't try to "swap to haiku for speed" without verifying the model name first — every variant tried returned 404.

### Render `/api/render` height pitfall

`POST /api/render` returns `'height' in 'clip' must be positive` (Puppeteer `CdpPage.screenshot` error) for some campaign JSONs. The error is independent of `renderOptions.height` in the request body — passing `{"height": 2400}` does not bypass it. This is a Render-side Chromium / Puppeteer version drift, not a campaign JSON issue. Workaround: open the campaign in the builder UI, which uses a different render code path. Filed as a follow-up; not blocking the assembly + validate flow.

### The two-layer architecture (the key insight)

A static system prompt is **necessary but not sufficient** for a production LLM feature. The system prompt carries *brand foundations* (voice, personas, lens routing, output schema, QA bar) that change rarely. The *live state* — active products, current from-prices, real Klaviyo list/segment IDs, today's blog URLs, lifestyle imagery that semantically matches the brief — changes daily. The generator uses a **two-layer model**:

1. **Static layer** — the system prompt in `fig-bloom-email-generator/references/system-prompt.md`. Baked in at build time.
2. **Dynamic layer** — the LIVE CONTEXT block in the user message, filled at request time from four sources: Shopify (products), the asset library (semantic image search via brief), Klaviyo (audiences), Notion (blog index). Each source gracefully degrades; the UI shows which sources are live.

Without the dynamic layer, the LLM generates campaigns that reference stale or invented products, blog URLs, and audience IDs. The button works only if the runtime fetches and threads live context on every call.

### Path A vs Path C — same code path, different live-context quality

- **Path A (button, fast path):** the email-builder button does a cheap live-context fetch (Shopify public feed, server's Klaviyo key, asset library with the brief as the search query), passes the result to `/api/campaigns/generate`. Good enough for most campaigns.
- **Path C (agent, quality path, future):** an agent in conversation builds a richer live context (semantic asset search with multimodal judgement, performance data, anything from Notion it can see) and POSTs to the same endpoint. Same code path; richer inputs. The button is the fast path; the agent is the quality path.

### Source-of-truth pattern

The generator's prompt files are the **source of truth** in `dgroch/skills/`. The email-builder runtime **mirrors** them under `lib/prompts/` via `scripts/sync-prompts-from-skill.sh` (CI-friendly with `--check` mode). Bump the skill's `version:` on prompt changes; sync to runtime.

See **`references/live-context-pattern.md`** for the reusable pattern doc — applicable beyond email to any LLM-backed production feature (a smart-form, a workflow button, an autonomous agent harness).
