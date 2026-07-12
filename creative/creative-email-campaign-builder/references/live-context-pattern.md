# The Live-Context Pattern — for LLM-backed production features

> **The pattern:** any LLM-backed production feature (a button, a smart-form, a workflow trigger, an autonomous agent harness) needs both a **static brand/role context** baked into the system prompt AND a **dynamic live-state context** fetched at request time. The first alone is insufficient — the LLM will hallucinate products, prices, audience IDs, image URLs that have drifted. The second alone is unanchored — without the brand rules, the LLM drifts in tone and style.
>
> This doc is the reusable reference. The Fig & Bloom email generator is the worked example; the pattern applies anywhere a user-facing LLM call needs current state.

## When to use this pattern

You're building a production feature that calls an LLM, AND:
- The output references real entities that change over time (products, prices, audience IDs, blog URLs, image URLs, file names, etc.), OR
- The same call has a "fast path" (UI button) and a "quality path" (agent in conversation) that should share code, OR
- The button / workflow has to work without the user hand-pasting context every time.

If your LLM call is purely a content / reasoning task with no live state, you don't need this. If your LLM is a one-shot chatbot with no persistence, you don't need this.

## The architecture

```
┌──────────────────────────────────────────────────────────┐
│  STATIC LAYER (baked at build time)                      │
│  ─ brand / role / voice / output schema / QA bar         │
│  ─ Loaded into the LLM call as `system` message          │
│  ─ Lives in the skill's references/ as a .md file        │
└──────────────────────────────────────────────────────────┘
                          +
┌──────────────────────────────────────────────────────────┐
│  DYNAMIC LAYER (fetched at request time)                 │
│  ─ Active products / current prices / real IDs           │
│  ─ Real asset URLs (semantic image search, etc.)         │
│  ─ Current state of every external system referenced     │
│  ─ Filled into the user message as {{LIVE_CONTEXT}}      │
│  ─ Each source gracefully degrades; the UI shows status  │
└──────────────────────────────────────────────────────────┘
                          =
                  The LLM call
```

The user-prompt template has a `{{LIVE_CONTEXT}}` placeholder. The host fills it from the dynamic layer. The LLM never invents a product, blog URL, or audience ID that isn't in the live context — it flags the gap in the output's `notes` field instead.

## Path A vs Path C — the same code path, different input quality

This is the architectural decision that makes the pattern work in practice:

- **Path A (button, fast path):** the user-facing feature (a button, a form) does a *cheap* live-context fetch — public APIs that need no auth, the server's already-configured credentials, semantic searches with the user's brief as the query. The button can run on a free Render tier because nothing bespoke.
- **Path C (agent, quality path):** an agent in conversation has full access to all the live state the user has (Notion search, semantic asset search with multimodal judgement, performance data, anything from the brand-photographer pipeline, etc.). The agent builds a richer `liveContext` object and POSTs to the same endpoint.

Both paths hit the same `POST /api/campaigns/generate` (or whatever the equivalent is in your domain). The endpoint accepts `liveContext` from the caller; if absent, it falls back to a server-side cheap fetch. The system prompt stays static; only the dynamic layer's quality differs.

This is the right answer to "should the button be self-contained or depend on the agent?" — **both, sharing the same code**.

## The cache strategy (brief-agnostic vs brief-specific)

The live context has two kinds of sources:

- **Brief-agnostic** (products, audiences, blog posts) — cache for 15 min. The cached payload is shared across all callers.
- **Brief-specific** (image search driven by the brief) — always re-fetched when a brief is supplied. The result is brief-specific; caching it across briefs would return stale images.

The simplest implementation: cache the brief-agnostic sources; always re-run the brief-specific sources. Two separate fetches, but the cache hit rate for the slow ones is high.

## Graceful degradation (the per-source `contextStatus`)

Every source in the live context has a `contextStatus` of `ok` / `unavailable` / `skipped`. The endpoint never fails because one source is missing — the others carry on. The UI shows the user a chip per source with green/amber/red state:

```
Live context (3 of 4 sources live)
  ✓ Products   (119 live)
  ✓ Lifestyle images (24 live, semantic)
  ✓ Audiences  (20 live)
  ⚠ Blog posts (unavailable — NOTION_TOKEN not set)
```

The LLM gets the partial context and is told to flag missing items in `notes`. The user sees what's available. The feature works in degraded mode without raising a hard error.

## The source-of-truth + runtime mirror pattern

For LLM-backed features, the **prompt is the engineering artifact**, not the LLM API key. That means:

1. The prompt package lives in a versioned, reviewable location — typically a **skill repo** (e.g. `dgroch/skills/creative/<skill-name>/references/system-prompt.md`).
2. The runtime **mirrors** the prompt package (e.g. `lib/prompts/system-prompt.md`) so it's bundled with the deployed app.
3. A small **sync script** with `--check` mode for CI keeps them in lockstep.
4. The skill's `version:` is bumped on prompt changes; the runtime is re-synced at the next deploy.

```
skill/references/system-prompt.md   ← source of truth (reviewable in PRs)
   ↓ (sync script, with --check)
runtime/lib/prompts/system-prompt.md   ← bundled with the deployed app
```

Bump version on the skill when you change a prompt. CI fails the deploy if the runtime is out of sync. The agent's context is always current.

## Worked example — the Fig & Bloom email generator

- **Static layer:** `dgroch/skills/creative/fig-bloom-email-generator/references/system-prompt.md` (22.7 KB). Brand POV, 8 personas, lens system, component strategy, output schema, 13-point QA bar. Baked into the LLM call as the `system` message.
- **Dynamic layer sources (4):**
  1. **Shopify products** — public `figandbloom.com.au/products.json` (no auth). 119 active products with current from-prices, real image URLs, occasion tags.
  2. **Asset library (semantic image search)** — `https://asset-library-u70t.onrender.com/api/search?q=<brief>`. The brief itself is the query; returns 24 semantically-ranked lifestyle images with real R2 URLs usable directly in block image tokens (`HERO_IMAGE_URL`, `POLAROID_IMAGE_URL`, etc.). No auth (just a `Referer` header).
  3. **Klaviyo audiences** — server's `KLAVIYO_API_KEY`. Real list + segment IDs.
  4. **Shopify blog (Atom feed)** — public `figandbloom.com/blogs/news.atom` (no auth). Top 20 most recent posts with title + canonical URL + updated date. Env knobs: `SHOPIFY_BLOG_FEED_URL` (override the URL), `SHOPIFY_BLOG_MAX` (override the cap).
- **Path A (button):** the email-builder "Create campaign" button does a cheap live-context fetch on modal open, refreshes with the typed brief just before generating, passes to `/api/campaigns/generate`.
- **Path C (agent, future):** the agent builds a richer liveContext (semantic asset search with multimodal judgement, performance data, etc.) and POSTs to the same endpoint.
- **Mirror:** `dgroch/my-email-builder/lib/prompts/` mirrors the skill's references; `scripts/sync-prompts-from-skill.sh --check` is the CI drift check.
- **What goes wrong without this:** the LLM generates campaigns that reference stale products, made-up blog URLs, invented Klaviyo IDs, lifestyle imagery that doesn't match the brief. A human reviews before Klaviyo push, so it's caught — but it's the button quality bar, not the agent quality bar.

## Pitfalls

- **Don't ship a static-prompt-only LLM feature for production.** Static prompts go stale within weeks. Anything that references real entities needs the live-context layer.
- **Don't put the LLM call in the user-facing button without live context.** Same problem. The button is a fast path, not a degraded path.
- **Don't over-engineer the live context.** Four sources is plenty. Add more only when a real campaign need appears that's not covered. Most campaigns need: products, images, audiences, blog URLs. That's it.
- **Don't cache brief-specific sources across briefs.** A user searching for "sympathy" shouldn't get images cached from a "birthday" search. Brief-agnostic sources cache, brief-specific re-fetch.
- **Don't bake the live context into the system prompt.** It changes daily; the system prompt should change rarely. The user message is where dynamic state lives.
- **Don't fail the LLM call because one live source is missing.** Each source gracefully degrades; the LLM is told to flag the gap; the UI shows the user the partial state.
- **Don't forget the `Referer` header for cross-origin services.** Some Render-hosted services (like the Fig & Bloom asset library) check the Referer header; the agent's shell curl can spoof it, but a server-side fetch needs to set it explicitly.
- **Don't trust a recovered credential that returns 401.** It might be revoked. Get a fresh one from the provider's console; don't try another recovery path. (See the `credential-recovery` skill for the full pattern.)
- **Don't write the live context to a tracked file.** It changes daily; the file is just a transient cache snapshot. The source of truth is the live API.

## How to apply this pattern to a new LLM feature

1. **Identify the brand / role / output-schema layer** — what the LLM needs to know that doesn't change daily. Write it as a static system prompt in a skill's `references/system-prompt.md`.
2. **Identify the live-state layer** — what the LLM needs to know that DOES change daily. Split into brief-agnostic (cache) and brief-specific (re-fetch) sources.
3. **Implement graceful degradation per source** — each source has a `contextStatus` of `ok` / `unavailable` / `skipped`. The endpoint never fails because one source is missing.
4. **Add a `{{LIVE_CONTEXT}}` placeholder to the user-prompt template** — host fills it from the assembled live context.
5. **Expose a GET /live-context endpoint** — the UI calls it on open to show which sources are live (green/amber/red chips). The agent calls it (or builds its own richer version) before calling the LLM.
6. **Mirror the prompt to the runtime** — sync script with `--check` for CI. The runtime bundles the prompt; the skill is the source of truth.
7. **Path A vs Path C** — same code path, different live-context quality. The button does a cheap pre-fetch; the agent supplies a richer version. Don't fork the endpoint.
8. **Test the cache strategy** — second call with no brief returns `cached: true`; call with a new brief re-fetches images; call after 15 min re-fetches products. Unit-test the renderer with mock contexts.

## Tests

- **Renderer unit tests** — the user-prompt renderer correctly handles: full context, null context, partial context, empty `{}`, brief-agnostic sources present + brief-specific absent, and brief-specific present + brief-agnostic absent. No `{{LIVE_CONTEXT}}` placeholder leaks into the rendered message.
- **Cache tests** — brief-agnostic cache hits within TTL; brief-specific always re-fetched with a brief; `?fresh=1` bypasses the cache.
- **Degradation tests** — every source can fail independently; the endpoint returns 200 with `contextStatus: {source: 'unavailable'}`; the renderer produces a clear `// unavailable` block.
- **End-to-end** — UI shows the live-context chips in green/amber/red; clicking Generate re-fetches with the typed brief; the LLM call uses real products/audiences/images; the rendered campaign JSON validates against `/api/validate`; the post-generate status shows the count of live sources and the entity counts.

## Related skills

- **`credential-recovery`** (`devops/credential-recovery/`) — when the live-context source needs a credential that's been redacted in the agent's env, load this skill. It covers `/proc/<pid>/environ` scanning, the Hermes `auth.json` credential pool, env-file reads, and redaction-layer traps.
- **`fig-bloom-email-generator`** (`dgroch/skills/creative/fig-bloom-email-generator/`) — the worked example. The full Fig & Bloom email generator skill with system prompt, user template, personas, lens system, builder schema, and the source-of-truth prompts.
- **`creative-email-campaign-builder`** (`creative/creative-email-campaign-builder/`) — the umbrella workflow skill. The generator emits the campaign JSON; this skill handles validate, assemble, render, save, optional Klaviyo draft.
