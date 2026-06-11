/**
 * blog-production.workflow.js — TEMPLATE
 *
 * Orchestration template for the blog-production-loop skill, written for
 * Claude Code dynamic workflows. Per Anthropic's guidance, treat this as a
 * template Claude adapts in-session — NOT a script to run verbatim. The
 * concrete spawn/agent API surface should be confirmed against the current
 * dynamic-workflows runtime when the harness is generated.
 *
 * Invariants that MUST survive any adaptation:
 *   1. Critic runs in a FRESH context — never the maker's.
 *   2. Only a PASS verdict publishes. Everything else stays draft.
 *   3. Attempt cap = 4, then ESCALATE (park, log, continue the batch).
 *   4. The calendar is held in this script's state — the goal never lives
 *      in a model context that can compact and drift.
 */

const CONFIG = {
  calendarDataSource: "collection://52c90ef6-8b29-4869-8a59-736282852773",
  rubricPath: "resources/blog-critic-rubric.md",
  assetLibrary: "https://asset-library-u70t.onrender.com/api/search",
  shopDomain: "lechoixflowers.myshopify.com",
  maxAttemptsPerPost: 4,
};

// ---------------------------------------------------------------------------
// Outer loop — loop-until-done over the editorial calendar
// ---------------------------------------------------------------------------
async function run() {
  const rows = await spawnAgent("orchestrator/pull-calendar", {
    prompt: `Query ${CONFIG.calendarDataSource} for rows with status
             ready-to-produce. Return JSON: [{title, tier, persona,
             keyword, notes}]. If any row lacks a tier, return it under
             "needs_clarification" instead of guessing.`,
  });

  if (rows.needs_clarification?.length) escalateToDan(rows.needs_clarification);

  const report = { published: [], escalated: [], attempts: {} };

  for (const post of rows.ready) {           // holds ALL rows — no partial done
    const result = await producePost(post);  // inner loop
    report[result.status === "PASS" ? "published" : "escalated"].push(result);
    report.attempts[post.title] = result.attempts;
  }

  return writeRunReport(report);             // format per SKILL.md
}

// ---------------------------------------------------------------------------
// Inner loop — one post: maker → publish draft → critic → refine
// ---------------------------------------------------------------------------
async function producePost(post) {
  let directives = null;
  let draft = null;

  for (let attempt = 1; attempt <= CONFIG.maxAttemptsPerPost; attempt++) {
    // P2 — copy. On retries, the maker sees ONLY prior draft + directives.
    const copy = await spawnAgent("maker", {
      freshContext: attempt === 1,
      prompt: makerPrompt(post, draft, directives), // tier rules pack inside
    });

    // P3 — imagery waterfall: owned (asset library) → brand-photographer.
    const images = await spawnAgent("image-sourcer", {
      prompt: imageSourcerPrompt(post, copy.imageSlots, CONFIG.assetLibrary),
    });

    // P4 — internal linking (skipped to single-quiet-link for Journal tier).
    const body = await spawnAgent("maker/linking", {
      prompt: linkingPrompt(post.tier, copy, images), // blog-internal-linking
    });

    // P5 — Shopify draft. Schema validated in-session, never from memory.
    draft = await spawnAgent("publisher", {
      prompt: publishDraftPrompt(CONFIG.shopDomain, post, body, draft?.articleId),
    });

    // P6 — critic. FRESH context. Rubric + rendered page only.
    const verdict = await spawnAgent("critic", {
      freshContext: true, // <- the invariant
      prompt: criticPrompt(CONFIG.rubricPath, draft.previewUrl, post.tier, attempt),
    });

    if (verdict.verdict === "PASS") {
      await spawnAgent("publisher", {
        prompt: `Flip article ${draft.articleId} from draft to published.
                 Verify it resolves publicly, then return the live URL.`,
      });
      return { status: "PASS", attempts: attempt, ...verdict, url: draft.liveUrl };
    }

    if (verdict.verdict === "ESCALATE") {
      return { status: "ESCALATE", attempts: attempt, history: verdict };
    }

    directives = verdict.revisionDirectives;  // REVISE → feed the maker
  }

  // Cap reached — park it, don't block the batch.
  return { status: "ESCALATE", attempts: CONFIG.maxAttemptsPerPost,
           reason: "attempt cap", lastDirectives: directives };
}
