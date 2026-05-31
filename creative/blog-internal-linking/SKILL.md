---
name: blog-internal-linking
description: >
  Add internal links and product merchandising to any Fig & Bloom blog post,
  the "Wikipedia way" — every concept points to the single best page for it.
  Use whenever drafting, editing, or publishing a blog post on figandbloom.com,
  or whenever someone says "add internal links", "link this post up", "optimise
  internal linking", "make this post shoppable", or "add a product banner /
  shoppable tiles". Pairs with the brand-photographer skill (imagery) and the
  editorial brand-voice framework.
---

# Blog Internal Linking

Make every blog post build topical authority and move readers from visitor to
shopper, without ever reading as stuffed or salesy.

## Two layers

1. **Internal Linking Map** — the *stable* layer. The canonical page for each
   topic we write about (collections, evergreen posts, key landing pages),
   each with target keyword + approved anchor variants. This is the lookup
   table for what to link to.
   - Notion DB: https://www.notion.so/e9626cf56e1040b789267e5d2a8d523c
   - Data source (query this): `collection://45a5bae1-338c-47c0-8453-05ed68487879`
   - Process & rules page: https://www.notion.so/36efdc24425f81d3bcc0d1e80e65898d
2. **Products** — the *live* layer. Never stored (they sell out / change).
   Search Shopify at publish time for the product the post should feature.
   - Store: `lechoixflowers.myshopify.com` (public domain figandbloom.com)
   - Use the Shopify MCP `graphql_query` → `products(query: "...")`, filter to
     `status: ACTIVE` and `availableForSale: true`, grab `handle`,
     `featuredImage.url`, and `priceRangeV2.minVariantPrice` (for "From $X").

## Rules (link like Wikipedia)

- **One canonical target per concept.** Most specific match wins
  (e.g. "recovery" → Get Well Soon, not generic Bouquets). Never link one idea
  to two pages.
- **Moderate density:** ~1 internal link per 120–150 words. Editorial, not
  stuffed.
- **Descriptive anchors:** use an anchor variant from the Map that matches the
  target's keyword; vary wording; never "click here".
- **Every post needs:** ≥1 commercial link (collection/landing page) + ≥1
  related blog post + product merchandising (a single callout *or* a banner).
- **Never:** self-link, repeat a target, or print a literal "CTA:" label.
- **Priority drives eagerness:** Core links freely; Secondary when clearly
  relevant; Situational only on a strong match.

## Product merchandising — two modes

- **Single callout** (default): one in-stock product the post features/implies.
  Embed its real image linked to the product page + a short "Shop the [name] →"
  text link with price. Place near the close — never directly after a
  grief/sympathy passage.
- **Shoppable banner** (multiple products): email-style row of composed image
  tiles (4:5 photo + cream caption: occasion label, serif name, price), each
  its own product link, wrapping responsively. Use when pushing a curated set
  (e.g. occasion-matched cards, the bouquets the post names).
  → Full pipeline, GraphQL mutations, HTML template and gotchas:
  **`references/shoppable-banner.md`**. Renderer: **`scripts/render_tiles.js`**;
  uploader: **`scripts/put_upload.py`**.

## Procedure — applying links to a post

1. List the concepts in the draft: topics, palettes, occasions, recipients,
   care/longevity, seasonality, geography.
2. For each concept, find its row in the Map (match on `When to Link` /
   `Topic / Keyword`). Insert a link using an approved anchor variant, woven
   into existing copy.
3. Apply density + priority. Spread links across the post; don't cluster.
4. **Merchandising:** pick single-callout or banner per the section above.
   Real product imagery only (honest); in-stock only; placed near the close.
5. **Closing CTA:** soft, woven prose linked to the best-fit commercial
   collection. Land on the feeling first, then the gentle link.
6. **QA before publish:** no self-links; no duplicate targets; anchors read
   naturally; density not stuffed; imagery honest + in-stock; alt text on every
   tile; no literal "CTA:"; no duplicated H1/title in the body.

## Procedure — refreshing the Map (monthly, or when the catalogue changes)

1. Pull live sitemaps from `https://figandbloom.com/sitemap.xml` → the
   collections, pages, and blogs child sitemaps.
2. Diff against the Map. Add new canonical pages; retire any that 404.
3. Keep canonical targets only. Skip noise: `*-old`, duplicate slugs,
   one-off seasonal campaign collections, and system collections
   (`frontpage`, `members-only`, `all_collection`, image-URL artefacts).
4. Refresh keyword / anchor variants from each page's current SEO title.

## Shopify edit notes (publishing)

- Article body is HTML via `articleUpdate(id: $id, article: { body })` —
  `id` is **top-level**, a sibling of `article` (not inside it).
- The theme renders the article title as H1; do **not** repeat the title as an
  H2 at the top of the body.
- `Collection` has no `onlineStoreUrl` (build `/collections/{handle}`);
  `Article` has no `seo` field and `articles()` takes no `sortKey`.
- Big body edits: render the HTML **single-line, single-quoted attributes**
  before putting it in a GraphQL variable — no double quotes / newlines means
  no escaping war. (Detail in `references/shoppable-banner.md`.)
- Host blog imagery on **Shopify Files** (stagedUploadsCreate → fileCreate),
  not R2 — there's no Fig & Bloom R2 bucket, and Files is the CDN the blog
  already uses.
