# Shoppable product banner — runbook

An "email-style" banner: a row of product tiles, each a composed image (4:5
photo + cream caption with occasion label, serif name, price), each wrapped in
its own product link. It looks designed, every tile is clickable, and the row
wraps to 2-up / 1-up on mobile because it's flex-wrap, not one wide image.

Use this when a post should push **several** products (a curated set of cards,
a few named bouquets). For a single hero product, the plain inline callout in
SKILL.md is enough — don't over-build.

## Why images, not native HTML product cards

The native option (text + photo cards in HTML) is lighter and editable in
Shopify's editor, but the type/spacing drifts with the theme and never looks as
considered. Dan's call is the composed-image route for this brand. Accept the
trade-offs and mitigate them: real text headings around the block (SEO), honest
photography, alt text on every tile, and a plain-text collection link alongside
so there's always a crawlable path.

## Pipeline (7 steps)

1. **Pick products.** Cards: curate to the post's actual sections (birthday →
   thank-you → sympathy → love/apology → new chapter). Bouquets: the ones the
   copy already names. Pull live data from Shopify — `status: ACTIVE`,
   `availableForSale: true` (a sold-out callout is worse than none), `handle`,
   `featuredImage.url`, and `priceRangeV2.minVariantPrice` for the "From $X".

2. **Build `products.json`** (see scripts/render_tiles.js header for the shape)
   and render: `node scripts/render_tiles.js products.json ./out`. Photos are
   locked to 4:5 — that's the native ratio of the product library (1000×1250),
   so nothing crops. Eyeball one card + one bouquet before uploading.

3. **Stage uploads (PUT).** Via the Shopify Admin GraphQL:
   ```graphql
   mutation Stage($input: [StagedUploadInput!]!) {
     stagedUploadsCreate(input: $input) {
       stagedTargets { url resourceUrl }
       userErrors { field message }
     }
   }
   ```
   One input per file: `{ filename, mimeType: "image/png", resource: IMAGE,
   httpMethod: PUT }`. PUT, not POST (see gotchas).

4. **Upload the bytes.** Build `put_targets.json`
   (`[{local, url, resourceUrl}]`) and run
   `python3 scripts/put_upload.py put_targets.json`. Expect HTTP 200.

5. **Register the files** from the staged resourceUrls:
   ```graphql
   mutation FileCreate($files: [FileCreateInput!]!) {
     fileCreate(files: $files) {
       files { alt fileStatus ... on MediaImage { id } }
       userErrors { field message }
     }
   }
   ```
   `{ originalSource: <resourceUrl>, contentType: IMAGE, alt: "<honest alt>" }`.
   Alt with no ampersand (write "Fig and Bloom", or skip the brand) so it's
   clean inside an HTML attribute.

6. **Poll for the CDN URL.** fileCreate returns `fileStatus: UPLOADED` and
   `image: null`. Wait ~6s, then read the nodes until `READY`:
   ```graphql
   query($ids:[ID!]!){ nodes(ids:$ids){ ... on MediaImage { id fileStatus image { url } } } }
   ```
   Those `image.url` (cdn.shopify.com/...) are what go in the body.

7. **Embed + publish.** Build the banner HTML (below), splice it into the body,
   and `articleUpdate(id: $id, article: { body })`. Re-fetch to confirm.

## Banner HTML (responsive, no media queries)

Real `<h2>`/`<h3>` heading + lead `<p>` in body text (crawlable), then the
tile grid, then a plain-text collection link. Each tile is `<a><img></a>`.

```html
<div style="display:flex;flex-wrap:wrap;gap:14px;margin:26px 0;justify-content:center;">
  <a href="https://figandbloom.com/products/<handle>" style="flex:1 1 150px;max-width:210px;text-decoration:none;">
    <img src="<cdn url>" alt="<honest alt>" style="width:100%;height:auto;display:block;border-radius:2px;">
  </a>
  <!-- …one <a> per product… -->
</div>
```

- Cards: `flex:1 1 150px; max-width:210px`. Bouquets (bigger): `flex:1 1 200px;
  max-width:300px`. flex-wrap does the responsive work — tiles reflow to fit.
- Product URLs absolute (`https://figandbloom.com/products/<handle>`).
- Place the bouquet block near the close; never a product push straight after a
  grief/sympathy passage.

## Brand tokens (locked)

Background `#FAF6F0` · ink `#26221E` · gold eyebrow `#B08D57` · muted
`#6E655C`. Names in Cormorant Garamond 600; labels/price in Jost. Premium and
restrained — never loud. (All encoded in render_tiles.js; change there.)

## Gotchas — what a junior gets wrong

- **POST staging.** Don't. POST targets return ~9 long signed form fields
  (policy + signature); transcribe one base64 char wrong and GCS 400s with no
  useful message. **Use `httpMethod: PUT`** — signature lives in the URL,
  curl PUTs the file, done.
- **No Fig & Bloom R2 bucket.** brand-cdn only has `whoosh`/`bower`. Host blog
  imagery on **Shopify Files** (same CDN the blog already serves from) — don't
  invent a bucket.
- **articleUpdate body escaping.** The body is large HTML full of `"`. Before
  putting it in a GraphQL variable, render it **single-line with single-quoted
  attributes** (`html.replace('"',"'").replace('\\n','')`). Zero double quotes,
  zero newlines → drops straight into the variable with no escaping war. Em
  dashes / curly quotes stay as literal UTF-8 (valid).
- **`fileCreate` is async.** It returns `UPLOADED` with `image: null`. You must
  poll the node for `READY` to get `image.url`. Using the null url = broken img.
- **4:5, not square/landscape.** The product photos are 1000×1250. Anything
  else crops the card art or the stems. Lock the photo box to 4:5.
- **Duplicate title H2.** The theme renders the article title as H1. If the
  body opens with an `<h2>` repeat of the title, strip it.
- **Re-rendering?** Upload as new files, repoint the body, then `fileDelete`
  the old MediaImage ids so Files doesn't fill with orphans.
- **Sold-out products.** Filter `availableForSale: true`. Featuring a sold-out
  design is worse than featuring nothing.
