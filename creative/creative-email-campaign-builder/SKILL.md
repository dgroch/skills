---
name: creative-email-campaign-builder
description: Build complete Klaviyo email campaigns for Fig & Bloom — from campaign brief through copy, design, and deployment to Klaviyo. Use this skill whenever someone asks to create an email campaign, email design, email template, Klaviyo email, marketing email, promotional email, newsletter, or EDM for Fig & Bloom. Also triggers for requests to design email layouts, generate email copy, build email HTML, or create campaign assets. If the request involves email and Fig & Bloom in any combination, use this skill.
---

# Email Campaign Builder — Fig & Bloom

Generates complete, on-brand Klaviyo email campaigns. Walks through a structured pipeline from brief to deployed campaign, with human-in-the-loop approval at each stage.

## Pipeline

```
1. BRIEF           → Campaign parameters (structured text)
2. PRODUCTS        → Fetch Shopify collection, select products
3. COPY            → Subject, preheader, body, CTAs
4. COMPONENTS      → Select which sections and layouts to use
5. LAYOUT          → Choose hero variant, product card mix, dividers, section backgrounds
6. DESIGN MOCKUP   → Interactive HTML preview for approval
7. REFINEMENT      → Human feedback loop
8. KLAVIYO DEPLOY  → Convert to email-client HTML, push to Klaviyo
```

Present each step for approval before proceeding.

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

---

## Step 4: Component Selection

Read `references/components.md` — Component Decision Matrix and Section Divider Selection.

| Component           | Include when...                                                               |
| ------------------- | ----------------------------------------------------------------------------- |
| Hero                | Always — choose A/B/C/D based on campaign tone                                |
| Sensitivity opt-out | Occasion can be painful (see triggers list)                                   |
| Body copy           | Always                                                                        |
| Section divider     | When visual rhythm benefits from a break (max one non-line divider per email) |
| Product showcase    | Always (3–5 products, mixed layouts)                                          |
| Testimonial         | Reviews exist for featured products                                           |
| Promo code block    | Campaign has an offer                                                         |
| Card/gift upsell    | Add-on products available                                                     |
| Delivery cutoffs    | Hard deadline exists                                                          |
| Trust bar           | Always                                                                        |
| Footer              | Always                                                                        |

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

**Section dividers** — Line default. One non-line divider max per email. Illustration strip (BodyFlower, 100% width, 35% crop) or full-bleed lifestyle image (180px). See design-system.md.

**Key typography rules:**

- Cervanttis: always `font-weight:400; font-synthesis:none` — never bold
- Lust: regular weight only, never italic
- Neuzeit-Grotesk: Light (body), Bold (CTAs, labels, nav)
- Cervanttis max 3 placements per email

**Illustration sizing formula:** CSS height = (container_height × visibility_pct) + bleed_offset. Width always `auto`. See design-system.md for per-context values.

---

## Step 6: Design Mockup

Generate a complete HTML file as an interactive preview.

**Embedding assets for preview:**

- Fonts: base64 encode from `assets/fonts/`
- Logo: base64 encode from `assets/logo/F_B_Logo_Horizontal_BLK.png`
- Illustrations: base64 encode from `assets/illustrations/` — use hi-res exports (≥500px wide). `_white.png` for dark sections, `_black.png` for light sections.
- Product images: use Shopify CDN URLs at 4:5 crop (1000×1250px source). If sandbox blocks external URLs, use colour gradient placeholders with product names.

Save preview to `/mnt/user-data/outputs/` for human review.

---

## Step 7: Refinement

Present mockup. Wait for feedback. Common areas: hero variant, illustration placement/sizing, product card layout mix, section backgrounds, divider choice, copy tone, product selection, section ordering. Iterate until approved.

---

## Step 8: Klaviyo Deployment

Once design is approved, convert and deploy. Read `references/klaviyo-html.md` for conversion spec.

### 8a. Convert to email-client HTML

- Table-based layout (not flexbox/grid)
- Inline styles
- Web-safe font fallback stacks (Lust → Georgia serif; Cervanttis → cursive; NeuzeitGro → Gill Sans, Helvetica Neue, sans-serif)
- VML fallback for Outlook background images
- Images as hosted URLs (upload illustrations and hero to Klaviyo media library)
- Klaviyo template tags: `{{ first_name|default:'Moment Maker' }}`, `{% unsubscribe %}`

### 8b. Push to Klaviyo

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
├── illustrations/                 (8 illustrations × 2 variants — LOW RES, use hi-res for production)
│   ├── Body_white.png / Body_black.png
│   ├── BodyFlower_white.png / BodyFlower_black.png  ← primary divider illustration
│   ├── Face1_white.png / Face1_black.png            ← testimonial
│   ├── Face2_white.png / Face2_black.png            ← testimonial (product+testimonial card)
│   ├── FrontFace_white.png / FrontFace_black.png
│   ├── HandFlower_white.png / HandFlower_black.png  ← hero D, upsell
│   ├── HandPlant_white.png / HandPlant_black.png
│   └── HandRose_white.png / HandRose_black.png      ← hero D (right), upsell
└── logo/
    └── F_B_Logo_Horizontal_BLK.png
```

**Hi-res illustration exports required for production** (≥500px wide, ideally 800px). Low-res bundle will appear pixelated on retina screens.

**Illustration usage by context:**

- Hero B text band: BodyFlower or HandFlower, width:220px, bottom-right, bottom:-30px
- Hero C text col: BodyFlower or HandFlower, height:262px, bottom-right, right:-16px, bottom:-20px
- Hero D flanking: HandFlower (left) + HandRose (right, mirrored), height:410px, bottom:-60px
- Body/copy sections: BodyFlower or HandFlower, height:200–220px, edge-anchored, bottom:-20px
- Testimonial full-width: Face1 or Face2, height:200px, bottom-right
- Testimonial alongside product: Face2, height:calc(30%+30px), right:-30px, bottom:-30px
- Illustration strip divider: BodyFlower, width:100%, 35% vertical crop

---

## Reference Files

| File                              | Read before...                                        |
| --------------------------------- | ----------------------------------------------------- |
| `references/brand-voice.md`       | Writing any copy                                      |
| `references/design-system.md`     | Building any layout or mockup                         |
| `references/product-selection.md` | Selecting products from Shopify                       |
| `references/components.md`        | Assembling structure, choosing layouts, HTML patterns |
| `references/klaviyo-html.md`      | Converting to email-client HTML or deploying          |

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
