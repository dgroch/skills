---
name: creative-email-campaign-builder
description: Build complete Klaviyo email campaigns for Fig & Bloom — from campaign brief through copy, design, and deployment to Klaviyo. Use this skill whenever someone asks to create an email campaign, email design, email template, Klaviyo email, marketing email, promotional email, newsletter, or EDM for Fig & Bloom. Also triggers for requests to design email layouts, generate email copy, build email HTML, or create campaign assets. If the request involves email and Fig & Bloom in any combination, use this skill.
---

# Email Campaign Builder — Fig & Bloom (v3)

Generates complete, on-brand, mobile-optimised Klaviyo email campaigns. Walks through a structured pipeline from brief to deployed campaign, with human-in-the-loop approval at each stage.

## Pipeline

```
1. BRIEF              → Campaign parameters (structured text)
2. PRODUCTS           → Fetch Shopify collection, select products
3. COPY               → Subject, preheader, body, CTAs
4. COMPONENTS         → Select which sections and layouts to use
5. LAYOUT             → Choose hero variant, product card mix, dividers, section backgrounds
6. DESIGN MOCKUP      → Flexbox HTML preview — visual design approval
7. REFINEMENT         → Human feedback loop on design mockup
8. PRODUCTION HTML    → Convert to table-based + mobile media queries — final HTML approval
9. KLAVIYO DEPLOY     → Push approved HTML to Klaviyo, schedule send
```

**Each step requires explicit human approval before proceeding. Never skip a gate — especially between steps 8 and 9.**

---

## Step 1: Campaign Brief

The brief is structured text. If provided by a brief-generator skill, parse it. If not, collect from the human:

```
Campaign: Mother's Day 2026
Goal: Drive gift purchases before delivery cutoff
Audience: Moment Makers (primary), Self-care Enthusiasts (secondary)
Tone: Warm, understated, quietly confident
Products: From Shopify collection /collections/mothers-day
Promo: Free delivery code MUMDAY25, orders over $130, valid until May 5
Opt-out required: Yes (sensitive occasion)
Delivery cutoffs: Metro May 8, regional May 5
Accent colour: None (standard palette)
```

**Auto-infer where possible:**
- Mother's Day / Father's Day / Valentine's → opt-out required
- Product launch → no opt-out
- If promo not specified → ask
- If accent colour not specified → use standard palette

---

## Step 2: Product Selection

Read `references/product-selection.md` for methodology.

1. Fetch the campaign collection from Shopify (e.g. `figandbloom.com/collections/mothers-day`)
2. Select 3–5 products optimising for price spread, visual variety, social proof density, and type mix
3. Assign layout positions using the Product Layout Selection guide in `references/components.md`
4. Present selection with rationale. Wait for human approval.

---

## Step 3: Copy Generation

Read `references/brand-voice.md` before writing any copy.

Generate: subject line, preheader, hero headline (Cervanttis, lowercase), hero subheadline, body paragraphs, product occasion headlines, CTA labels, upsell copy, promo copy, delivery cutoff copy.

**Klaviyo personalisation variables** — use only for subscriber profile attributes. All product content, pricing, and campaign details are resolved at generation time from live Shopify data, not injected by Klaviyo.

Approved variables:
- `{{ first_name|default:'Moment Maker' }}` — personalised greeting
- `{% unsubscribe %}` — mandatory unsubscribe link
- `{{ email }}` — if needed for preference management links

---

## Step 4: Component Selection

Read `references/components.md` — Component Decision Matrix and Section Divider Selection.

| Component | Include when... |
|---|---|
| Hero | Always — choose A/B/C/D based on campaign tone |
| Sensitivity opt-out | Occasion can be painful (see triggers list) |
| Body copy | Always |
| Section divider | When visual rhythm benefits from a break (max one non-line divider per email) |
| Product showcase | Always (3–5 products, mixed layouts) |
| Testimonial | Reviews exist for featured products |
| Promo code block | Campaign has an offer |
| Card/gift upsell | Add-on products available |
| Delivery cutoffs | Hard deadline exists |
| Trust bar | Always |
| Footer | Always |

---

## Step 5: Layout & Design

Read `references/design-system.md` for the complete specification.

**Hero selection:**
- A (text over image): standard campaigns, maximum photo impact
- B (text above image): when photo must be seen unobscured; editorial
- C1/C2 (split 50/50): portrait photography; most editorial
- D (dark noir): launches, VIP, re-engagement, high-intent

**Product card mix** — vary layouts within the product section:
- Open with full-width or lifestyle+studio for hero product
- Horizontal cards for mid-tier equal-weight products
- Two-column grid for remaining products

**Section backgrounds** — White default; Clay/50%Clay for warm or soft moments; Noir for upsell and Hero D. Campaign accent: section bg OR border/CTA detail — never both.

**Section dividers** — Line default. One non-line divider max per email. Illustration strip (BodyFlower, 100% width, 35% crop) or full-bleed lifestyle image (180px).

**Key typography rules:**
- Cervanttis: always `font-weight:400; font-synthesis:none` — never bold
- Lust: regular weight only, never italic
- Neuzeit-Grotesk: Light (body), Bold (CTAs, labels, nav)
- Cervanttis max 3 placements per email

**Illustration sizing formula:** CSS height = (container_height × visibility_pct) + bleed_offset. Width always `auto`. See design-system.md for per-context values.

---

## Step 6: Design Mockup

Generate a complete HTML file as an interactive preview. The preview uses flexbox layout (acceptable for browser preview) but must apply the full class naming convention and mobile media query block — this ensures the mobile preview is accurate.

**Required in every mockup `<style>` block:**
1. `@font-face` declarations for all four fonts (base64 embedded)
2. Standard mobile CSS block from design-system.md (verbatim)
3. Any campaign-specific overrides

**Required class names on all layout elements** — see design-system.md Class Naming Convention. Every split row, card, image, and headline must carry its class.

**Embedding assets for preview:**
- Fonts: base64 encode from `assets/fonts/`
- Logo: base64 encode from `assets/logo/F_B_Logo_Horizontal_BLK.png`
- Illustrations: base64 encode hi-res exports (≥500px wide). `_white` for dark sections, `_black` for light sections.
- Product images: resolved at generation time from live Shopify CDN URLs at 4:5 crop (1000×1250px). If sandbox blocks external URLs, use colour gradient placeholders.

Save preview to `/mnt/user-data/outputs/` for human review. Note in the preview that it is best reviewed at both full width and at 375px (iPhone) width.

**Preview background colour:** Use `#2c2825` (warm dark brown) as the `body` background in all previews. This creates clear visual separation from the email content without competing with the brand palette.

---

## Step 7: Refinement

Present mockup. Wait for feedback. Iterate until approved. Common refinement areas: hero variant, illustration sizing, product card mix, section backgrounds, divider choice, copy tone, mobile layout behaviour.

---

## Step 8: Production HTML

Once the design mockup is approved through Steps 6–7, convert it to production email HTML. **Do not proceed to Klaviyo until the human has explicitly approved this output.**

Read `references/klaviyo-html.md` for the full conversion spec.

### 8a. Save design mockup to Google Drive

Before converting to production HTML, save the approved design mockup HTML file to Google Drive as a persistent record. Read the `reference-google-drive` skill before making any Drive calls.

**Folder:** `03 - Marketing > Email Marketing > Campaign Drafts`
- Email Marketing folder ID: `1aAekejfgl4q_ea8j4q2IfXTiJfUVX9Kg`
- If `Campaign Drafts` subfolder doesn't exist, create it first (mimeType `application/vnd.google-apps.folder`)

**File details:**
- Title: `{YYYY-MM-DD} {Campaign Name} — Design Mockup`  ← lead with date per Drive conventions
- mimeType: `text/html`
- disableConversionToGoogleType: `true`  ← keep as HTML, don't convert to Doc
- Content: base64-encoded full flexbox HTML mockup from Step 6 (approved version after refinement)
- parentId: Campaign Drafts folder ID

This file is the human-reviewable design record. If edits are required after the production HTML is built, regenerate from this mockup rather than rebuilding from scratch.

**Do not proceed to production HTML conversion until the Google Drive upload is confirmed successful.**

### What changes in production HTML vs the design mockup

The design mockup uses flexbox for ease of preview in a browser. Production HTML must work in email clients — including Outlook desktop, which ignores CSS layout entirely.

- All layout via `<table>`, `<tr>`, `<td>` — no flexbox, no grid
- All styles inline on elements (not in `<style>` block, except media queries)
- Apply class names to `<td>` and `<table>` elements (same convention as mockup — media queries target these)
- Include standard mobile CSS block in `<style>` tag in `<head>`
- VML fallback for Outlook background images
- Images as hosted Klaviyo media library URLs — upload all illustrations and the hero image to Klaviyo media library before generating the HTML, then reference those URLs
- Klaviyo template variables for personalisation only (see Step 3)

**Outlook note:** Outlook desktop ignores media queries. The table-based base layout must be fully legible at 600px fixed width without any responsive rules applied — responsive behaviour is an enhancement, not a dependency.

---

### Known production failure modes — must check before every deploy

These are confirmed issues from production emails. Check each before generating the production HTML.

#### ① Font rendering

Custom `@font-face` fonts embedded via base64 are stripped by Gmail and Outlook. Use a two-layer strategy:

**Layer 1 — Hosted font URL (renders in Apple Mail, iOS, Samsung Mail):**
```html
<link href="https://[fig-bloom-cdn]/fonts/fonts.css" rel="stylesheet" type="text/css">
```
Until a CDN is configured, omit Layer 1 and rely on Layer 2 only.

**Layer 2 — Optimised fallback stacks (renders everywhere):**
```css
Lust      → font-family: Georgia, 'Times New Roman', serif;
Cervanttis → font-family: 'Palatino Linotype', Palatino, Georgia, cursive;
NeuzeitGro → font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
```

Size compensation when falling back: increase Cervanttis headline sizes by ~10% since Georgia/Palatino renders smaller than the script font at the same px value.

Do NOT embed fonts as base64 in production HTML — they inflate file size and are stripped by major clients anyway.

#### ② Illustration resolution

**Always use hi-res exports, never the original low-res bundle.**
- Low-res bundle: 274–400px native — will appear pixelated on retina screens
- Hi-res required: ≥ 500px wide for edge-anchored sections; ≥ 800px wide for full-width illustration strips
- Source: `/assets/illustrations/hi-res/` or re-export from the original vector files at the required dimensions
- Upload hi-res PNGs to Klaviyo media library before building production HTML

#### ③ Klaviyo unsubscribe tag

The unsubscribe link **must** use the exact Klaviyo template tag syntax. A common failure is the tag being escaped or wrapped in quotes during string construction.

**Correct:**
```html
<a href="{{ unsubscribe_url }}" style="color:#aaa;text-decoration:underline;">Unsubscribe</a>
```

**Also accepted (block tag form):**
```html
{% unsubscribe %}
```

**Never do this** (causes literal text to render):
```html
href="{{% unsubscribe %}}"   ← double-braced or escaped
href="{% unsubscribe %}"     ← only valid as standalone block, not inside href
```

After generating the production HTML, grep for `unsubscribe` and verify the tag is syntactically correct before uploading to Klaviyo.

#### ④ Product image ratio

All product images must be 4:5 in production HTML. In table-based layout, enforce via `width` and `height` attributes on `<img>` tags as well as inline styles:

```html
<img src="{PRODUCT_URL}" width="280" height="350"
     style="display:block;width:280px;height:350px;object-fit:cover;object-position:center top;"
     alt="{PRODUCT_NAME}">
```

Never leave height as `auto` on product images in production HTML — email clients may not respect CSS-only aspect ratio control.

#### ⑤ Social icons

The footer must use inline SVG icons, not text links. Plain text renders when the agent omits SVGs or when a template engine strips them. Always include the full SVG markup inline — do not reference external icon files. The five required icons (Facebook, Instagram, YouTube, TikTok, Email) with their correct SVG paths are defined in `references/components.md` footer specification.

If SVG rendering is uncertain in the target client, use a hybrid: SVG with an `<img>` fallback via VML — but never plain text alone.

#### ⑥ Section illustrations missing

Every body copy section and upsell section must include an edge-anchored illustration. A common agent failure is including illustrations in the flexbox mockup but omitting them during table-based conversion.

Checklist before finalising production HTML:
- Body copy section → HandFlower or BodyFlower, black variant, bottom-right or bottom-left, ~200–220px height
- Upsell/noir section → HandFlower (left) + HandRose (right, mirrored), white variant, ~360px height
- Testimonial section → Face2, black variant, bottom-right, ~200px height

Illustrations are `position:absolute` inside a `position:relative` container. In table-based HTML use `position:relative` on the `<td>` and `position:absolute` on the `<img>`. Always set `overflow:hidden` on the container `<td>`.

#### ⑦ Hero rendering errors

Three distinct errors that commonly occur together:

**a) Cervanttis case** — Cervanttis must ALWAYS be lowercase. Write the copy in lowercase. Do not rely on `text-transform:lowercase` alone — write the content string in lowercase in the HTML source. Never title case or sentence case.

**b) Hero image mask** — Hero A must have a `rgba(0,0,0,0.30)` overlay div positioned absolutely over the image. Without it text is illegible. This is frequently omitted in production HTML. The overlay must be a separate `<div>` with `position:absolute; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.30)`.

**c) Hero text hierarchy** — The correct element stack inside the hero overlay is:
```
① Super label    → Neuzeit-Grotesk Bold, 9–10px, uppercase, letter-spacing .20em, rgba(255,255,255,.65)
② Headline       → Cervanttis, 52–58px, lowercase, color #fff
③ Subheadline    → Neuzeit-Grotesk Light (300), 13px, rgba(255,255,255,.88)   ← NOT Lust
④ CTA button     → Neuzeit-Grotesk Bold, 10px, uppercase, background #fff, color #000
```
Lust is never used inside the hero. If Lust appears in the hero, it is wrong.

#### ⑧ Lust font weight rendering too heavy

In production HTML, `<h1>`, `<h2>`, `<h3>` tags default to `font-weight:bold` in email clients. This makes Lust render as a heavy/bold slab rather than its intended elegant regular weight.

**Every** Lust element must have `font-weight:normal` inlined explicitly:

```html
<!-- WRONG — browser will bold this -->
<h2 style="font-family:'Lust',Georgia,serif;font-size:28px;color:#000;">

<!-- CORRECT -->
<h2 style="font-family:'Lust',Georgia,serif;font-weight:normal;font-size:28px;color:#000;">
```

Apply to: section headlines, product names, promo code text, testimonial quote marks.

#### ⑨ Text colour consistency

Only use colours from the approved palette. Common agent errors: using #333, #555, or #777 for body copy instead of the defined values.

| Element | Correct colour |
|---|---|
| Primary headlines (Lust) | #000000 |
| Body copy (NeuzeitGro Light) | #444444 |
| Secondary/caption copy | #666666 |
| Fine print, footer copy | #aaaaaa |
| Super labels (uppercase) | #aaaaaa |
| CTA buttons | #000000 bg, #ffffff text |
| Stars rating | #C8A888 |
| Clay decorative elements | #D8CCBE |

Never use #333, #555, #777, #888 (except attribution in testimonials: #999). When in doubt, use #000 for primary and #444 for body.

### Output

Save the production HTML file to `/mnt/user-data/outputs/` and present it to the human for review.

Also save the production HTML to Google Drive in the same `Campaign Drafts` folder:
- Title: `{YYYY-MM-DD} {Campaign Name} — Production HTML`
- mimeType: `text/html`, disableConversionToGoogleType: `true`

State clearly: *"This is the production HTML that will be pushed to Klaviyo. Please review at both desktop and mobile widths before approving. Design mockup and production HTML are both saved to Google Drive under 03 - Marketing > Email Marketing > Campaign Drafts."*

### Pre-deploy self-check (run before presenting to human)

Before presenting the production HTML, verify each item:

- [ ] Cervanttis headlines are lowercase in the HTML source (not just via CSS)
- [ ] Hero A has `rgba(0,0,0,0.30)` mask div over the image
- [ ] Hero subheadline uses Neuzeit-Grotesk Light, not Lust
- [ ] Every Lust element has `font-weight:normal` inlined
- [ ] All body copy sections include an edge-anchored illustration
- [ ] Footer contains inline SVG icons, not text links
- [ ] `{% unsubscribe %}` / `{{ unsubscribe_url }}` tag is syntactically correct — grep for it
- [ ] All product images have explicit `width` and `height` attributes (4:5 ratio)
- [ ] All hi-res illustration URLs are Klaviyo media library hosted URLs, not local paths
- [ ] Text colours match approved palette (#000, #444, #666, #aaa only)
- [ ] No `#333`, `#555`, `#777`, `#888` colour values present (except #999 for testimonial attribution)
- [ ] Background colour of email `<body>` or wrapper is `#2c2825`

**Wait for explicit approval. Do not proceed to Step 9 until confirmed.**

---

## Step 9: Klaviyo Deployment

Only begin this step after the human has explicitly approved the production HTML from Step 8.

Read the `klaviyo-api` skill before making API calls.

**Create template:**
```
POST /api/templates/
{
  "data": {
    "type": "template",
    "attributes": {
      "name": "{Campaign Name} — {Date}",
      "editor_type": "CODE",
      "html": "{converted_html}"
    }
  }
}
```

**Create campaign:**
```
POST /api/campaigns/
{
  "data": {
    "type": "campaign",
    "attributes": {
      "name": "{Campaign Name}",
      "audiences": {
        "included": ["{list_or_segment_id}"],
        "excluded": []
      },
      "send_strategy": {
        "method": "static",
        "options_static": {
          "datetime": "{scheduled_send_time_iso8601}"
        }
      }
    }
  }
}
```

**Important:** After template creation, assign it to a campaign message. Wait 2–3 seconds before updating the cloned template (known Klaviyo 404 bug).

**Confirm with human before scheduling send. Never auto-send.**

---

## Assets (bundled with this skill)

```
assets/
├── fonts/
│   ├── Lust-Regular.otf          (display headlines)
│   ├── Cervanttis.ttf            (script accent — always weight:400, font-synthesis:none)
│   ├── NeuzeitGro-Lig.otf        (body copy)
│   └── NeuzeitGro-Bol.otf        (CTAs, labels, nav)
├── illustrations/                 (8 illustrations × 2 variants — LOW RES preview only)
│   ├── Body_white.png / Body_black.png
│   ├── BodyFlower_white.png / BodyFlower_black.png  ← primary divider illustration
│   ├── Face1_white.png / Face1_black.png            ← testimonial full-width
│   ├── Face2_white.png / Face2_black.png            ← testimonial alongside product
│   ├── FrontFace_white.png / FrontFace_black.png
│   ├── HandFlower_white.png / HandFlower_black.png  ← hero D left, upsell
│   ├── HandPlant_white.png / HandPlant_black.png
│   └── HandRose_white.png / HandRose_black.png      ← hero D right (mirrored), upsell
└── logo/
    └── F_B_Logo_Horizontal_BLK.png
```

**Hi-res illustration exports required for production** (≥800px wide source). Low-res bundle will appear pixelated on retina screens.

**Illustration usage by context:**
- Hero B text band: BodyFlower or HandFlower, width:220px, bottom-right, bottom:-30px
- Hero C text col: BodyFlower or HandFlower, height:262px, bottom-right, right:-16px, bottom:-20px
- Hero D flanking: HandFlower (left) + HandRose (right, mirrored), height:410px, bottom:-60px
- Body/copy sections: BodyFlower or HandFlower, height:200–220px, edge-anchored, bottom:-20px
- Testimonial full-width: Face1 or Face2, height:200px, bottom-right, opacity:.11
- Testimonial alongside product: Face2, height:calc(30%+30px), right:-30px, bottom:-30px, opacity:.12
- Illustration strip divider: BodyFlower, width:100%, transform:translate(-50%,-35%), opacity per bg

---

## Reference Files

| File | Read before... |
|---|---|
| `references/brand-voice.md` | Writing any copy |
| `references/design-system.md` | Building any layout, mockup, or mobile CSS |
| `references/product-selection.md` | Selecting products from Shopify |
| `references/components.md` | Assembling structure, choosing layouts, HTML patterns, table-based conversion |
| `references/klaviyo-html.md` | Converting to production email HTML or deploying |

---

## Footer Specification

**Navigation:**
- Bouquets → `figandbloom.com/collections/bouquets`
- Vase Arrangements → `figandbloom.com/collections/vase-arrangements`
- Plants → `figandbloom.com/collections/plants`
- Gifts → `figandbloom.com/collections/gifts`
- Events → `figandbloom.com/collections/events`
- Store Finder → `figandbloom.com/pages/store-finder`

**Social:**
- Facebook → `facebook.com/figbloom`
- Instagram → `instagram.com/fig_and_bloom/`
- YouTube → `youtube.com/@figandbloom`
- TikTok → `tiktok.com/@fig_and_bloom`
- Email → `service@figandbloom.com`
