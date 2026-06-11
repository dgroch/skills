---
name: blog-production-loop
description: >
  Drive a Fig & Bloom editorial calendar to published, critic-approved blog
  posts with zero human in the loop until escalation. For each post: write the
  copy, source or generate brand imagery, apply internal linking, publish a
  Shopify draft, have an independent critic score the rendered page against
  the bundled rubric, and refine until it passes or escalates. Use whenever
  the brief is "work through the editorial calendar", "produce the blog
  posts", "run the content loop", or any batch blog-production task that ends
  in published posts on figandbloom.com.
author: Daniel Groch
license: MIT
browser_operator_version: 1
related_skills:
  - blog-internal-linking
  - brand-photographer
  - photography-ugc-review
  - brand-cdn
---

# Blog Production Loop

Two nested loops. The **outer loop** holds the editorial calendar in an array
and runs until it is empty — no partial batches declared done. The **inner
loop** drives one post through maker → critic → refine until the critic's
verdict is PASS or the attempt cap forces an escalation.

## Operating principles — non-negotiable

1. **The maker never grades its own work.** The critic runs in a fresh,
   isolated context with no access to the maker's reasoning — only the
   rendered page, the rubric, and the exemplars.
2. **PASS is the only path to publish.** Everything else stays a Shopify
   draft. No exceptions, no "close enough".
3. **The critic reviews the rendered page**, not the source HTML. Judgement
   happens where the reader is.
4. **Owned imagery first, licensed lifestyle fallback second, generated third.**
   Product imagery belongs inside product callouts; editorial imagery should
   favour lifestyle, context, hands, rooms, tables, notes, delivery, care, and
   quiet human-scale scenes.
5. **Escalation is a success state.** A post parked with a clear reason after
   four attempts is the loop working, not failing.

## Roles (context-isolated agents)

| Role | Does | Must not |
|---|---|---|
| **Orchestrator** | Pulls the calendar, runs the loops, tracks state, writes the run report | Write copy or score quality |
| **Maker** | Drafts copy, assembles the post body, applies revision directives | See the rubric scores it "would get"; self-publish |
| **Image Sourcer** | Runs the imagery waterfall (below) | Embed anything unowned or placeholder |
| **Publisher** | Shopify draft creation/update; flips draft → published on PASS only | Act on anything but a critic verdict |
| **Critic** | Scores the rendered draft against `resources/blog-critic-rubric.md` | Rewrite copy; see maker context |

## Inputs

- **Editorial calendar** — Notion data source
  `collection://52c90ef6-8b29-4869-8a59-736282852773`
  (*Editorial Calendar — May/June 2026 v2*). Each row needs: working title,
  tier (Guide | Journal), occasion/persona, target keyword (Guides), status.
  Rows missing a tier are clarified with Dan before the run, not guessed.
  **Important:** calendar rows may be scheduling pointers only. If the row
  markdown says the draft lives in Blog Posts ▸ Month via a `mention-page`,
  follow that canonical page and treat it as the source of truth.
- **Rubric** — `resources/blog-critic-rubric.md` (bundled). The critic loads
  it fresh every review. Exemplar URLs inside it are re-read once per run.
- **Voice & structure authorities** — the Parent Editorial Framework and
  Guide System pages in the Fig & Bloom Notion Editorial space; Journal craft
  rules for Journal-tier rows.
- **Operational pitfalls reference** — `references/shopify-draft-spin-pitfalls.md`
  captures reusable Notion data-source, Shopify draft read-back, markdown
  conversion, and product-callout checks discovered during draft-only runs.

## The inner loop — one post, end to end

### P1 — Brief assembly *(Orchestrator → Maker)*

From the calendar row: tier, persona/occasion, target keyword, any notes.
Tier decides the rules pack: Guides get the six-part Guide structure;
Journal gets the craft rules (real byline, named human, ≥3 proper nouns,
≥1 disagreeable sentence, no funnel shape).

### P2 — Copy *(Maker)*

Write against the Parent Editorial Framework: emotional arc leads, craft and
delivery proof supports, product and practical detail closes. Australian
English. Banned-language list respected at draft time, not patched later.
On attempts ≥2, the maker receives **only** the critic's revision directives
and the prior draft — directives are instructions, not suggestions.

### P3 — Imagery *(Image Sourcer)* — the waterfall

For each image slot the post needs (hero + inline, per content):

1. **Asset Library first (owned imagery).** Semantic search:

   ```
   GET https://asset-library-u70t.onrender.com/api/search?q={natural language description}&limit=8
   ```

   Returns `{results: [{id, title, url, description, mediaType, driveLink}]}`.
   The `url` values are already on the brand CDN
   (`brand-cdn.figandbloom.workers.dev`) — embed directly, no re-hosting.
   Query with the *scene*, not keywords ("close-up hellebores soft neutral
   background", not "flowers"). Screen candidates against the post's needs
   and the visual pillars; when uncertain whether a candidate is on-brand,
   apply `photography-ugc-review` before committing it.

2. **Licensed lifestyle fallback via `licensed-lifestyle-image-sourcing`**
   when the article needs context rather than product truth and owned imagery
   cannot serve the scene. Use official Unsplash or Pexels APIs only; do not
   scrape/reverse-engineer private web endpoints. Allowed stock roles: room
   atmosphere, winter table, bedside/recovery context, hand-written card,
   candlelight, delivery/arrival mood, negative space. Disallowed stock roles:
   any bouquet/floral product pretending to be Fig & Bloom, competitor branding,
   obvious stock smiles, over-bright studio lifestyle, clichéd grief imagery,
   or anything that contradicts the copy.

3. **Generate via `brand-photographer` if neither owned nor licensed lifestyle
   imagery fits.** Brand: Fig & Bloom. The skill anchors to the Notion brand
   config and seed library and runs Higgsfield with its own critique loop — let
   it finish its loop; do not pull early iterations. Host the approved output
   via `brand-cdn` for a stable URL before embedding.

4. **Separate editorial imagery from product truth.** Product-callout images
   must be live Shopify product images. Editorial/lifestyle images may be
   owned, generated, or licensed fallback assets, clearly used as mood/context.

Write descriptive alt text and source metadata for every image at embed time.
Licensed fallback images must carry photographer/source/licence URL in run
state and, if mirrored to the Fig & Bloom CDN, in the upload manifest.

### P4 — Layout, linking & shopability *(Maker)*

Before Shopify upload, compose the article body with lightweight blog-safe
modules borrowed from the email-builder design language, not raw newsletter
markup:

- **Editorial intro block:** one or two quiet paragraphs with more breathing
  room; no button stack.
- **2-up vertical image block:** preferred default for inline editorial imagery.
  Pair two portrait/lifestyle images side by side (desktop) that stack on
  mobile. Use combinations such as detail + context, arrangement + room,
  handwritten card + flowers, table + candle. This is the main antidote to
  every article feeling like a single full-width product image.
- **Image-caption pair:** every editorial image block needs a caption that adds
  craft, care, delivery, or emotional context.
- **Care checklist / decision guide:** useful for Guide posts; keep bullets
  clean (`<li>` without literal hyphen artefacts) and never insert product
  callouts inside `<ul>`.
- **Product callout module:** one live Shopify product image, product name,
  price, and `Shop the [name] →`. This is the only place product photography
  should dominate.
- **Soft CTA band:** prose link, not a campaign button; no visible `CTA:` label.

Recommended imagery rhythm per post:

- Use a single full-width hero only when the image earns it.
- Prefer one **2-up vertical lifestyle block** near the first third of the post.
- Keep one product callout later in the article after the reader has context.
- Do not repeat the same product image as hero and product callout.

Apply `blog-internal-linking` in full: Linking Map lookups, density and
anchor rules, ≥1 commercial link + ≥1 related post + 1 product callout
verified live on Shopify (`status: ACTIVE`) at this moment, soft woven close.
Journal tier: a single quiet in-context product link only — skip the rest.

### P5 — Publish as draft *(Publisher)*

Shopify Admin GraphQL against `lechoixflowers.myshopify.com`. **Discover and
validate the mutation against the live schema** (`graphql_schema` /
`validate_graphql_codeblocks`) rather than trusting remembered field names.
Known notes from `blog-internal-linking`: article body is HTML via
`articleUpdate(id: $id, article: { body })` with `id` top-level; the theme
renders the title as H1 — never repeat it in the body. Create in **draft**
(unpublished) state. Record the article ID and preview URL in run state.

Before declaring the draft ready for critic, read it back from Shopify and
run render-level checks. Local source QA is not enough: previous runs passed
text checks while Shopify read-back still contained malformed list items,
product callouts nested inside `<ul>`, and literal `CTA:` scaffolding. Verify
summary, body length, image presence, link counts, no duplicate title H2, no
banned language, no public scaffolding, and explicit Guide-tier product
callout evidence (`Shop the [name] →`, price, product image). See
`references/shopify-draft-spin-pitfalls.md`.

### P6 — Critic review *(Critic, fresh context)*

Browser actions follow `reference-browser-operator` when a public or preview URL
is available:

1. `navigate(preview_url)` → `confirm_context("figandbloom.com/blogs/")` —
   bail to ESCALATE if false.
2. `screenshot()` at desktop width; where the adapter supports a narrow
   viewport, capture one for the D6 mobile check.
3. Read the rendered body for the gate scan and dimension scoring.
4. Score per `resources/blog-critic-rubric.md`: hard gates first, then the
   six weighted dimensions, then the verdict block in the rubric's exact
   output format. No false passes — uncertainty is REVISE or ESCALATE.

For **draft-only spins** where Shopify does not expose an agent-accessible
public preview, do not publish solely for QA. The critic may review Shopify
read-back HTML/metadata plus the publisher's explicit render-level checks,
and the run report must state that limitation. Draft-only status itself is
not a fail when the user asked for drafts.

### P7 — Gate *(Orchestrator + Publisher)*

- **PASS** → Publisher flips the article to published. Log scores. Next post.
- **REVISE** → attempt counter +1; directives go to the Maker (and Image
  Sourcer if D4 failed); loop to P2/P3.
- **ESCALATE** (4th REVISE, G6 hit, ambiguous tier, unreadable page) → leave
  in draft, park with full score history and the critic's final directives,
  continue the outer loop. **An escalated post never blocks the batch.**

## Stop conditions & budgets

- **Per post:** 4 attempts, then ESCALATE. Hard.
- **Per run:** stop when the calendar array is empty or a configured token
  budget is hit; if budget-stopped, the run report says exactly which rows
  remain.
- The pass-rate sanity check from the rubric applies: >~90% first-attempt
  passes across a batch → flag that the bar may be mis-set.

## Run report *(Orchestrator, end of run)*

```markdown
# Blog production run — {date}
- Calendar rows: N | Published: N | Escalated: N | Remaining: N
- Attempts histogram: 1st-pass: N, 2nd: N, 3rd: N, escalated: N

## Published
| Post | Tier | Attempts | Final score | URL |

## Needs Dan's eye
| Post | Tier | Blocking issue (critic's words) | Draft URL |

## Patterns
{Recurring failure modes across the batch — these are skill/rubric
improvement candidates, e.g. "5 of 8 first drafts failed D5 link density".}
```

## Running it

**As a Claude Code dynamic workflow (preferred for batches):**
`workflows/blog-production.workflow.js` is the orchestration **template** —
prompt Claude to treat it as a template to adapt, not a script to run
verbatim. Pair with `/goal` set to: *"every calendar row is either published
with a PASS verdict or escalated with a logged reason."* Set an explicit
token budget on exploratory runs.

**As a Paperclip agent routine:** follow the phases turn-by-turn; the role
isolation then maps to sub-agent spawns with fresh contexts. The Critic must
still be a separate spawn — never the same context as the Maker.

## What this skill does NOT cover

- Authoring the editorial calendar (it consumes the Notion DB)
- Writing or amending the rubric (versioned separately in `resources/`)
- Email, social cuts, or Pinterest distribution of finished posts
- SEO keyword research for new topics

## When in doubt

- Calendar row has no tier? → Ask Dan. Guides and Journal have different bars.
- Asset Library returns near-misses only? → Generate; never settle for
  off-brand owned imagery just because it's owned.
- Shopify schema surprises you? → Validate, don't guess. A failed mutation is
  recoverable; a malformed live post is a brand cost.
- Critic and rubric seem to disagree? → The rubric wins; flag the ambiguity
  in the run report so the rubric gets fixed.
