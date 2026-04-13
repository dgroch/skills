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
4. COMPONENTS      → Select which sections to include
5. LAYOUT          → Choose layout recipe
6. DESIGN MOCKUP   → Interactive HTML preview for approval
7. REFINEMENT      → Human feedback loop
8. KLAVIYO DEPLOY  → Convert to email-client HTML, push to Klaviyo
```

Present each step for approval before proceeding.

---

## Step 1: Campaign Brief

The brief is structured text, not JSON. If provided by a brief-generator skill, parse it. If not, collect from the human:

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
3. Assign layout positions: full-width (hero + closer), two-column grid (mid-tier)
4. Present selection with rationale. Wait for human approval.

---

## Step 3: Copy Generation

Read `references/brand-voice.md` before writing any copy.

Generate: subject line, preheader, hero headline (Cervanttis, lowercase), hero subheadline, body paragraphs, product occasion headlines, CTA labels, upsell copy, promo copy, delivery cutoff copy.

---

## Step 4: Component Selection

| Component              | Include when...                     |
| ---------------------- | ----------------------------------- |
| Hero (text over image) | Always                              |
| Sensitivity opt-out    | Occasion can be painful             |
| Body copy              | Always                              |
| Product showcase       | Always (3–5 products)               |
| Testimonial            | Reviews exist for featured products |
| Promo code block       | Campaign has an offer               |
| Card/gift upsell       | Add-on products available           |
| Delivery cutoffs       | Hard deadline exists                |
| Trust bar              | Always                              |
| Footer                 | Always                              |

---

## Step 5: Layout & Design

Read `references/design-system.md` for the complete specification.

**Key rules:**

- Each email should feel visually distinct from recent sends
- Mix full-width and two-column product layouts
- One illustration per section max, tighter crop, larger size
- Hero: 30% black mask over lifestyle image
- Cervanttis: lowercase only, max 3 placements per email
- Lust: regular weight only, never italic
- Neuzeit-Grotesk: Light (body) and Bold (CTAs, labels, nav)

---

## Step 6: Design Mockup

Generate a complete HTML file as an interactive preview.

**Embedding assets for preview:**

- Fonts: base64 encode from `assets/fonts/`
- Logo: base64 encode from `assets/logo/F_B_Logo_Horizontal_BLK.png`
- Illustrations: base64 encode selected PNGs from `assets/illustrations/`. Use `_white.png` for dark sections, `_black.png` for light sections.
- Product images: use Shopify CDN URLs. If sandbox blocks external URLs, use colour gradient placeholders with product names.

Save preview to `/mnt/user-data/outputs/` for human review.

---

## Step 7: Refinement

Present mockup. Wait for feedback. Common areas: typography, illustration placement, layout balance, copy tone, product selection, section ordering. Iterate until approved.

---

## Step 8: Klaviyo Deployment

Once design is approved, convert and deploy. Read `references/klaviyo-html.md` for conversion spec.

### 8a. Convert to email-client HTML

- Table-based layout (not flexbox/grid)
- Inline styles
- Web-safe font fallback stacks
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
    },
    "relationships": {
      "campaign-messages": {
        "data": [{
          "type": "campaign-message",
          "id": "{message_id}"
        }]
      }
    }
  }
}
```

**Important:** After template creation, assign it to a campaign message. Wait 2–3 seconds before updating the cloned template (known Klaviyo 404 bug).

**Confirm with human before scheduling send.** Never auto-send.

---

## Assets (bundled with this skill)

```
assets/
├── fonts/
│   ├── Lust-Regular.otf          (display headlines)
│   ├── Cervanttis.ttf            (script accent)
│   ├── NeuzeitGro-Lig.otf        (body copy)
│   └── NeuzeitGro-Bol.otf        (CTAs, labels)
├── illustrations/                 (8 illustrations × 2 variants)
│   ├── Body_white.png / Body_black.png
│   ├── BodyFlower_white.png / BodyFlower_black.png
│   ├── Face1_white.png / Face1_black.png
│   ├── Face2_white.png / Face2_black.png
│   ├── FrontFace_white.png / FrontFace_black.png
│   ├── HandFlower_white.png / HandFlower_black.png
│   ├── HandPlant_white.png / HandPlant_black.png
│   └── HandRose_white.png / HandRose_black.png
└── logo/
    └── F_B_Logo_Horizontal_BLK.png
```

**Illustration usage:** `_white` variants for Noir backgrounds (25–35% opacity), `_black` variants for white/clay backgrounds (10–15% opacity). One per section, tighter crop, positioned at section edge.

---

## Reference Files

| File                              | Read before...                               |
| --------------------------------- | -------------------------------------------- |
| `references/brand-voice.md`       | Writing any copy                             |
| `references/design-system.md`     | Building any layout or mockup                |
| `references/product-selection.md` | Selecting products from Shopify              |
| `references/components.md`        | Assembling the email structure               |
| `references/klaviyo-html.md`      | Converting to email-client HTML or deploying |

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
