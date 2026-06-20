---
name: blog-magazine-layout
description: >
  Apply the Fig & Bloom "glossy magazine" editorial layout to any Journal blog
  post — scoped CSS, author card at top, italic standfirst, drop cap, hairline
  pull quote, wide establishing image, two-up image band, small-caps captions.
  Use whenever building, restyling, or elevating a blog post on figandbloom.com,
  or whenever someone says "make it look like a magazine", "elevate the layout",
  "use the Journal design", or "lay this post out". Owns the *look*; pairs with
  the editorial brand-voice framework (the words), blog-internal-linking (the
  links) and brand-photographer / licensed-lifestyle-image-sourcing (the images).
license: MIT
metadata:
  author: Daniel Groch
  related_skills:
    - blog-internal-linking
    - brand-photographer
    - licensed-lifestyle-image-sourcing
    - photography-ugc-review
---

# Blog Magazine Layout

The house editorial layout for Journal posts. The goal is a page a reader would
find in The Design Files or Vogue Living — generous white space, one strong
hero, type that carries the voice, images that earn their place. Restraint is
the whole aesthetic: a few deliberate moments, not a wall of widgets.

## Page architecture

Shopify renders the **featured image** and the **title** itself. The body is
everything below. So:

- **Featured image = the hero.** Set it on `article.image` (a horizontal /
  letterbox crop, ~3:2 or 2:1). **Never repeat the hero inside the body** — it
  renders twice.
- **Body order:** author card → standfirst → opening (drop cap) → article, with
  a pull quote and image moments woven through, closing on a hairline + final
  line.
- Wrap the whole body in `<div class="fb-foliage">` and ship a **scoped
  `<style>` block** inside it (Shopify preserves `<style>` and `<script
  type="application/ld+json">` in article body). Scoping by the wrapper class
  keeps styles off the rest of the theme.

## The scoped style block (paste verbatim, tweak sparingly)

**Base font is `px`, not `rem` — on purpose.** Some Shopify themes set a small
root (e.g. `html{font-size:62.5%}`), which makes rem-based body type render
tiny. The wrapper pins an absolute `18px`; everything inside scales in `em` off
that, so the post reads the same regardless of theme root.

```html
<div class="fb-foliage">
<style>
.fb-foliage{max-width:760px;margin:0 auto;color:#14110f;font-family:-apple-system,'Helvetica Neue',Helvetica,Arial,sans-serif;line-height:1.75;font-size:18px;}
.fb-foliage .fb-author{display:flex;flex-wrap:wrap;align-items:center;gap:16px;margin:0 0 2.2em;padding:0 0 1.6em;border-bottom:1px solid #d8ccbe;}
.fb-foliage .fb-author img{flex:0 0 auto;width:84px;height:84px;border-radius:50%;object-fit:cover;display:block;}
.fb-foliage .fb-author .meta{flex:1;min-width:220px;}
.fb-foliage .fb-author .name{font-family:'Hoefler Text','Didot','Bodoni MT',Georgia,serif;font-size:1.5em;line-height:1;margin:0 0 5px;color:#14110f;}
.fb-foliage .fb-author .role{margin:0 0 8px;font-size:0.74em;letter-spacing:0.15em;text-transform:uppercase;color:#9a9082;}
.fb-foliage .fb-author .bio{margin:0;font-size:0.94em;line-height:1.6;color:#5f574e;}
.fb-foliage .standfirst{font-family:'Hoefler Text','Didot','Bodoni MT',Georgia,serif;font-size:1.4em;line-height:1.5;font-style:italic;color:#6f665b;margin:0 0 1.8em;font-weight:400;}
.fb-foliage p{margin:0 0 1.3em;}
.fb-foliage p.lead:first-letter{float:left;font-family:'Hoefler Text','Didot','Bodoni MT',Georgia,serif;font-size:4em;line-height:0.74;padding:0.06em 0.14em 0 0;color:#14110f;}
.fb-foliage .pull{font-family:'Hoefler Text','Didot','Bodoni MT',Georgia,serif;font-size:1.6em;line-height:1.34;font-style:italic;text-align:center;color:#14110f;max-width:30ch;margin:2.4em auto;padding:1.5em 0;border-top:1px solid #d8ccbe;border-bottom:1px solid #d8ccbe;}
.fb-foliage figure{margin:0;}
.fb-foliage .wide{margin:2.2em 0;}
.fb-foliage .wide img{width:100%;height:auto;display:block;}
.fb-foliage .single{margin:2.2em auto;max-width:460px;}
.fb-foliage .single img{width:100%;height:auto;display:block;}
.fb-foliage .band{display:flex;flex-wrap:wrap;gap:14px;margin:2.2em 0;}
.fb-foliage .band figure{flex:1 1 280px;}
.fb-foliage .band img{width:100%;height:380px;object-fit:cover;display:block;}
.fb-foliage figcaption{margin-top:0.6em;font-size:0.72em;letter-spacing:0.14em;text-transform:uppercase;color:#9a9082;}
.fb-foliage .single figcaption{text-align:center;}
.fb-foliage .rule{border:0;border-top:1px solid #d8ccbe;width:56px;margin:2.2em auto 1.9em;}
.fb-foliage .callout{display:flex;flex-wrap:wrap;align-items:center;gap:16px;margin:2.2em 0;padding:14px;border:1px solid #d8ccbe;border-radius:4px;background:#faf7f2;}
.fb-foliage .callout > a{flex:0 0 auto;display:block;}
.fb-foliage .callout img{width:120px;height:150px;object-fit:cover;display:block;border-radius:2px;}
.fb-foliage .callout .ctext{flex:1;min-width:200px;}
.fb-foliage .callout .ctext .h{margin:0 0 4px;font-size:1.02em;font-weight:600;}
.fb-foliage .callout .ctext .s{margin:0;font-size:0.95em;color:#5f574e;}
</style>
  <!-- components go here -->
</div>
```

Palette is brand: Noir text `#14110f`, Clay hairlines `#d8ccbe`, muted
captions `#9a9082`. Display type uses a didone stack to echo Lust Display
(Lust isn't web-licensed). Body stays sans, per the brand guide.

## Components

**Author card — always at the TOP** (lands the byline before the read). Drop
the "Read more in the Journal" line here; that's an end-of-post CTA and reads
oddly at the top.

```html
<div class="fb-author">
  <img src="HEADSHOT_URL" alt="Kellie, co-founder of Fig & Bloom, in the studio" width="84" height="84">
  <div class="meta">
    <p class="name">Kellie</p>
    <p class="role">Co-founder, Fig &amp; Bloom</p>
    <p class="bio">Kellie is the co-founder of Fig &amp; Bloom and designs the range, bringing a background in fashion to how the studio works with colour and form.</p>
  </div>
</div>
```
Kellie headshot: `https://cdn.shopify.com/s/files/1/0657/8723/2489/files/kellie-signoff-headshot-v2.jpg`

**Standfirst** (the dek — one line, sets up the piece):
`<p class="standfirst">…</p>`

**Opening paragraph with drop cap** (only the first body paragraph):
`<p class="lead">When I…</p>`

**Pull quote** (lift one true line; place it away from where it sits in the body
so it doesn't read twice):
`<p class="pull">A bouquet isn't a collection of nice things gathered together. It's an edited object.</p>`

**Wide establishing image** (landscape only — context / scene-setting):
```html
<figure class="wide"><img src="URL" alt="…"><figcaption>Caption in small caps</figcaption></figure>
```

**Single image** (one portrait/standalone shot — centred and width-capped so a
portrait never goes full-bleed-tall; caption centres under it):
```html
<figure class="single"><img src="URL" alt="…"><figcaption>Centred caption</figcaption></figure>
```

**Two-up image band** (the workhorse for pairs/contrasts; fixed height means
portrait images never stack tall on mobile):
```html
<div class="band">
  <figure><img src="URL_A" alt="…"><figcaption>Left caption</figcaption></figure>
  <figure><img src="URL_B" alt="…"><figcaption>Right caption</figcaption></figure>
</div>
```

**Hairline divider** before the closing line: `<hr class="rule">`

**Product callout** — compact horizontal card (small image + name/price/link),
never full-bleed. Approved, ACTIVE designs only (see `blog-internal-linking`):
```html
<div class="callout">
  <a href="/products/HANDLE"><img src="PRODUCT_IMG" alt="…"></a>
  <div class="ctext">
    <p class="h">One-line hook.</p>
    <p class="s">Short line — from $XXX. <a href="/products/HANDLE">Shop the … →</a></p>
  </div>
</div>
```

## Imagery rules (enforced)

- **No AI-generated images. Ever.** Especially in Kellie's column. If an image's
  provenance is unknown, check it before use:
  `python3 -c "from PIL import Image,ExifTags; im=Image.open('f.jpg'); print({ExifTags.TAGS.get(k,k):v for k,v in im.getexif().items()})"`
  A real camera shot carries Make/Model/DateTimeOriginal/exposure. A stripped
  72-dpi header with an empty Exif IFD plus a studio-perfect look = treat as AI
  and reject.
- **Owned library first.** Then licensed editorial context (Unsplash/Pexels) for
  clearly-not-our-product scene-setting only (per licensed-lifestyle skill) —
  never stock florals passed off as our work.
- **Hero is horizontal.** Letterbox/3:2. Owned library assets are often 640px
  portrait, so a crisp wide hero usually needs a crop or a commissioned shot —
  flag when the hero will be soft full-bleed on desktop.
- **Never stack full-width portraits.** Use the two-up `band` (fixed height +
  `object-fit:cover`) so portraits crop to a consistent landscape on mobile.
- **Captions** are descriptive and honest; don't name a product as a link unless
  it's an approved, ACTIVE design (see blog-internal-linking).
- One hero + one or two interior moments is plenty for a ~1,000–1,500-word post.
  Let it breathe.

## Hosting images on Shopify (so they render reliably)

Body and featured images must be Shopify-hosted, not hotlinked.

- **External URL (brand-CDN, Unsplash already on a URL):** `fileCreate` accepts
  it directly as `originalSource` (`contentType: IMAGE`). Poll the MediaImage
  `node` until `fileStatus: READY`, then use `image.url`.
- **Local file (an upload, or a crop you made):** `stagedUploadsCreate`
  (`resource: IMAGE`, `httpMethod: POST`) → POST the bytes to the returned `url`
  with all `parameters` as form fields → `fileCreate(originalSource: resourceUrl)`
  → poll READY.
- Set the hero with `article.image = { url: SHOPIFY_CDN_URL, altText }`.

## Shopify mechanics (gotchas)

- `articleUpdate(id: ID!, article: ArticleUpdateInput!)` — **`id` is a top-level
  arg, NOT nested inside `article`.** Nesting fails silently.
- Scheduling needs BOTH `isPublished: true` and `publishDate` (UTC ISO 8601).
- Drafts: `isPublished: false`, no `publishDate`.
- **A draft carrying a past `publishedAt` will flip live on ANY edit.** If an
  article has a past publish date, a body-only `articleUpdate` makes Shopify
  recompute it as published — silently. To keep something a draft: send
  `isPublished: false` in the same update (this also nulls `publishedAt`), and
  re-query `isPublished`/`publishedAt` after editing a draft to confirm it
  stayed down.
- Journal blog is `gid://shopify/Blog/88398430441` (titled "Journal", handle
  `news`; there is no `journal`-handle blog). Kellie editorial → author
  `Kellie`; guide-tier → `Fig & Bloom`.

## Build checklist

1. Write/confirm the copy (voice framework). One intent, scannable.
2. Choose images per the rules above; verify provenance; host on Shopify.
3. Assemble body: author card → standfirst → lead → … → pull quote / band /
   wide image woven in → `hr.rule` → close.
4. **Render before you push.** Build the body in a local HTML wrapper and
   screenshot at ~820px (desktop) and ~430px (mobile) with headless Chromium;
   eyeball for jank (drop cap, band wrap, caption alignment, nothing dropped).
5. `articleUpdate`. Keep drafts unpublished until Dan approves going live.
6. Add internal links + product callout as a pre-publish pass
   (blog-internal-linking) — show before pushing if it changes approved copy.
