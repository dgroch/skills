---
name: blog-post-builder
description: >
  Build and publish a Fig & Bloom Shopify blog post end-to-end from a brief in
  Notion. Reads the post brief (Marketing → Editorial → Blog Posts → {Month}),
  drafts it through the brand voice + Thought-Leader Lens workflow, applies
  internal links and product merchandising, then publishes the article to the
  Shopify blog. Use whenever someone says "write the May blog post", "build the
  blog post from the brief", "draft and publish this Notion blog brief", or
  "turn this editorial brief into a live blog post". Pairs with the
  blog-internal-linking skill (links + shoppable products), the
  creative-brand-photographer skill (imagery) and the editorial brand-voice
  framework.
---

# Blog Post Builder — Fig & Bloom

Turn an editorial brief in Notion into a published, on-brand, internally-linked
Shopify blog post. The skill owns the **whole pipeline**: brief → draft →
links/merchandising → publish → QA. It does not invent topics — it executes a
brief that already exists in Notion.

## The two source-of-truth systems

| What | Where | Use for |
|---|---|---|
| **Brief + brand voice** | Notion (Editorial workspace) | What to write, the moment, the voice, the month's direction |
| **Where to link / what to sell** | Internal Linking Map (Notion) + live Shopify | Internal links + the product callout/banner |

The Notion map (IDs, brief tree, how a brief inherits) is in
**`references/notion-brief-map.md`**. A self-contained copy of the brand voice
rules + the 7-lens drafting workflow is in **`references/brand-voice-and-lens.md`**
— read it so the skill still works if Notion is slow or unreachable.

## Inputs

- A **blog post brief**: a child page under `Blog Posts → {Month}` (e.g. May's
  *"What to Write on a Flower Card When You Want It to Feel Personal"*).
- It **inherits** two parents, which you must also read:
  1. the **month Creative Direction** doc (tone, palette, messaging pillars,
     headline bank, body-copy direction, the weekly content map), and
  2. the **Parent Editorial Framework** (brand voice, messaging hierarchy,
     tone guardrails). IDs in `references/notion-brief-map.md`.

## Procedure

### 1. Read the brief (Notion)
Fetch, in order: the **Parent Editorial Framework** → the **month Creative
Direction** → the **specific post page**. From them extract: the moment
(occasion + sender/recipient + the fear of getting it wrong), the messaging
pillar, the headline bank, required example messages, the palette/visual world,
and any success markers. If the post page is thin (title + a line of intent),
the month doc supplies the rest — that is by design.

### 2. Draft through the Thought-Leader Lens workflow
Run the 7-step workflow (full text in `references/brand-voice-and-lens.md`) as
**editorial machinery behind the piece — never named in the copy**:
1. **Identify the moment** — occasion, sender role, recipient state, the fear,
   the good outcome.
2. **Pick reader awareness (Schwartz)** — product- / problem- / feeling- /
   lifestyle-aware. This sets the headline and opening.
3. **Make it useful (Holmes)** — the post must reduce one real anxiety or teach
   one practical decision. If it can't answer *"what should I do now?"*, it's
   not ready.
4. **Add Moment-Maker identity (Godin)** — the quiet "people like us mark
   moments with intention" idea.
5. **Humanise (Ziglar)** — sincere, plain-spoken; a thoughtful friend, not a
   marketer.
6. **Specificity pass (Ogilvy)** — named bouquets, palette/composition,
   delivery reality, card/vase/add-on pathway, florist craft. No "premium
   beautiful bouquet" filler.
7. **Choose CTA by intent** — match the close to the awareness state.

### 3. Apply brand voice + structure
- **Messaging hierarchy:** emotional arc **leads**; craft + delivery proof
  **support**; product + practical details **close** — never lead. A reader who
  reads only the first sentence should *feel* something; one who reads it all
  should know exactly what to do.
- **Australian English**, warm understatement. Honour the tone guardrails
  (avoid "stunning/gorgeous", "spoil them", "order now", discount-leading,
  florist clichés) — see `references/brand-voice-and-lens.md`.
- Educational months (e.g. May) **require ≥2–3 real example messages** showing
  generic-vs-specific. Treat card-message examples as a distinct object, not
  body prose.
- Headline matched to awareness; open with the moment, not the product; soft,
  woven closing direction.

### 4. Internal links + product merchandising
Hand the draft to the **`blog-internal-linking`** skill (in this repo). It:
- maps each concept (occasion, palette, recipient, care, season, geography) to
  the single best canonical page via the **Internal Linking Map**, at
  ~1 link / 120–150 words, descriptive anchors, no duplicate/self links;
- guarantees **≥1 commercial link + ≥1 related blog post + product
  merchandising** (single callout by default, or a shoppable banner for a
  curated set);
- searches **live Shopify** for the in-stock product the post features (real
  imagery only), placed near the close — never right after a sympathy passage.

### 5. Publish to the Shopify blog
- Create/update the article via Shopify Admin GraphQL. Body is HTML via
  `articleUpdate(id: $id, article: { body })` — **`id` is top-level**, a sibling
  of `article`. The theme renders the title as H1, so **do not repeat the title
  as an H2** at the top of the body.
- Host blog imagery on **Shopify Files** (`stagedUploadsCreate` → `fileCreate`),
  not R2. For large bodies, render the HTML **single-line with single-quoted
  attributes** before putting it in a GraphQL variable (no escaping war).
- Store: `lechoixflowers.myshopify.com` (public domain `figandbloom.com`). Full
  Shopify edit notes + the banner pipeline live in the `blog-internal-linking`
  skill's `references/shoppable-banner.md`.

### 6. QA before publish (combined gate)
- **Useful before it sells?** Headline matches the awareness state? Feels Fig &
  Bloom, not generic florist SEO? Clear next action?
- **Voice:** Australian English; emotional arc leads; specific detail (a stem
  name, a delivery time, a real occasion) present; no banned phrases / discount
  language / over-selling.
- **Links:** no self-links, no duplicate targets, anchors read naturally,
  density not stuffed; ≥1 commercial + ≥1 related post + merchandising present.
- **Honesty:** product real and in-stock; real product image; alt text on every
  tile; no literal "CTA:" label; **title not duplicated** as a body heading.

## Guardrail
The lenses and frameworks are machinery — the reader should feel clarity, taste,
and usefulness, never a framework. Help before you sell. When in doubt, return to
the campaign promise: *Fig & Bloom helps customers send the right feeling, with
craft and delivery certainty behind it.*

## Related skills
- **`blog-internal-linking`** — links + shoppable products + Shopify publishing
  notes (this repo).
- **`creative-brand-photographer`** — on-brand imagery for the post.
- **`creative-copy-qa`** — independent brand-voice QA pass before publish.
