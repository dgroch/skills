---
name: creative-email-campaign-builder
description: Build complete Klaviyo email campaigns for Fig & Bloom using the v4 template library. Use this skill whenever someone asks to create an email campaign, email design, Klaviyo email, marketing email, promotional email, newsletter, or EDM for Fig & Bloom.
---

# Email Campaign Builder — Fig & Bloom (v4)

Builds production-ready Klaviyo emails by assembling pre-built, locked templates. The agent selects components and injects content. It does not write HTML or make design decisions.

## Core principle

**The agent is a content editor, not a designer or developer.**

Every layout decision, style rule, illustration, icon, and colour is already baked into the template files. The agent's only job is:
1. Select the right templates for this campaign
2. Write good copy for the token values
3. Assemble and validate

---

## Pipeline

```
1. BRIEF         → Campaign parameters
2. PRODUCTS      → Fetch from Shopify, select 3–5
3. COPY          → Write all token values (headlines, body, CTAs)
4. SELECT        → Choose components from references/manifest.json
5. ASSEMBLE      → Read templates, replace tokens, concatenate into shell
6. VALIDATE      → Check all tokens filled, no {{}} remain, pre-flight checks
7. PREVIEW       → Save preview HTML to outputs + Google Drive. Wait for approval.
8. PRODUCTION    → Re-assemble with shell-production (no base64 fonts)
9. KLAVIYO       → Upload template + create campaign. Wait for approval before scheduling.
```

**Every numbered step is a gate. Do not skip ahead.**

---

## Step 1: Campaign Brief

Collect or parse:
```
Campaign name, goal, audience, tone, products (Shopify collection URL),
promo code (if any), opt-out required (yes/no), delivery cutoffs, accent colour (if any)
```

Auto-infer opt-out requirement:
- **Required:** Mother's Day, Father's Day, Valentine's Day/Galentine's, pregnancy/baby, memorial
- **Not required:** seasonal, product launch, general promo, retention

---

## Step 2: Product Selection

Read `references/product-selection.md` before fetching.

Fetch the Shopify collection. Select 3–5 products optimising for price spread, visual variety, and type mix. Assign card layout per product:
- Hero/spotlight product → `card-lifestyle-studio` (one per email max)
- Equal-weight products → `card-horizontal` + `card-horizontal-reversed` (alternating)
- Product with strong review → `card-single-testimonial`

Present selection with rationale. Wait for approval.

---

## Step 3: Copy (Token Values)

Read `references/brand-voice.md` before writing any copy.

Write values for every token that will be used. Key rules:
- `HEADLINE` case **depends on the font used in the selected template** — check the template comment block:
  - **Cervanttis templates** (hero-a, hero-b, hero-c, hero-d, upsell-noir, opt-out) → **MUST be lowercase**. e.g. `"for the one who does it all"`
  - **Lust templates** (body-copy, section-headline, all product cards) → **Sentence case**. e.g. `"Some gestures speak before words do."`
- `OPT_OUT_HEADLINE` → always lowercase (Cervanttis)
- `UNSUBSCRIBE_URL` token value → `{{ unsubscribe_url }}` (single braces, spaces inside — exact Klaviyo syntax)
- `REVIEW_STARS` → use Unicode star characters: `★★★★★`
- `BODY_P2` → empty string `""` if only one paragraph needed

---

## Step 4: Component Selection

Read `references/manifest.json` to confirm component file paths and token names.

Standard component order:

```
header                       ← always first
hero (choose one variant)    ← always
opt-out                      ← if required (immediately after hero)
body-copy
divider (optional — max 1 non-line divider per email)
section-headline
products (1–5 cards, mixed types)
testimonial                  ← if review copy available
promo-code                   ← if campaign has offer
upsell-noir                  ← closing beat
delivery-cutoffs             ← if hard deadline
trust-bar                    ← always
footer                       ← always last
```

**Hero selection guide:**

| Variant | When to use |
|---|---|
| `hero-a` | Standard campaigns. Maximum photo impact. |
| `hero-b-white/clay/noir` | Photo must be seen unobscured. Editorial feel. |
| `hero-c1` / `hero-c2` × `white/clay/noir` | Portrait photography. Most editorial. |
| `hero-d-noir` | Launches, VIP, re-engagement. Maximum brand statement. |
| `hero-d-clay` / `hero-d-white` | Type-forward but warmer tone. |

---

## Step 5: Assembly

For each selected component in order:
1. Read the template file from `references/templates/[path].html`
2. Replace every `{{TOKEN}}` with its value from Step 3
3. Verify no `{{` or `}}` characters remain in the output

Shell files are at:
- Preview: `references/shell/shell-preview.html`
- Production: `references/shell/shell-production.html`

Inject assembled components into the shell between `<!-- COMPONENTS_START -->` and `<!-- COMPONENTS_END -->`.

Fill shell tokens:
- `{{CAMPAIGN_NAME}}` → campaign name / email subject
- `{{BODY_BG}}` → `#2c2825` (default — do not change without approval)
- `{{FONT_CDN_LINK}}` → leave empty for preview; add `<link>` tag for production if CDN is configured
- `{{COMPONENTS}}` → assembled component HTML

---

## Step 6: Validation

Run every check before presenting the preview:

**Token validation:**
- [ ] No `{{` or `}}` characters remain anywhere in the assembled HTML
- [ ] `{{ unsubscribe_url }}` appears exactly once in the footer with single braces and internal spaces

**Content checks:**
- [ ] All Cervanttis headlines (`HEADLINE` in hero, `OPT_OUT_HEADLINE`, upsell `HEADLINE`) are lowercase in their token values
- [ ] `REVIEW_STARS` uses `★` Unicode characters, not asterisks or text

**Image checks:**
- [ ] All `_IMAGE_URL` tokens are filled — no token placeholders remain
- [ ] Images are Klaviyo media library hosted URLs (not local paths)

**Font check (production only):**
- [ ] Grep the production HTML for `base64` inside `<style>` blocks — if found, the wrong shell was used. Strip it.

---

## Step 7: Preview

1. Assemble using `references/shell/shell-preview.html` (base64 fonts for correct browser rendering)
2. Save to `/mnt/user-data/outputs/{YYYY-MM-DD}-{campaign-slug}-preview.html`
3. Save to Google Drive — read `reference-google-drive` skill for conventions:
   - Folder: `03 - Marketing > Email Marketing > Campaign Drafts` (folder ID: `14SJXWGGrZAoJUmkEb0FlBDSHHNyf_bIj`)
   - Title: `{YYYY-MM-DD} {Campaign Name} — Design Preview`
   - mimeType: `text/html`, disableConversionToGoogleType: `true`

State: *"Preview assembled from locked templates. Styles, illustrations, icons, and layout are baked in. Please review at 600px (desktop) and 375px (mobile)."*

**Wait for explicit human approval before proceeding to Step 8.**

If edits are requested:
- Content/copy changes → update token values, re-assemble from Step 5
- Component changes → update selection, re-assemble from Step 5
- Design changes → these require a template file update, not token changes. Flag to human.

---

## Step 8: Production HTML

Re-assemble using `references/shell/shell-production.html`:
- No base64 font data
- `{{FONT_CDN_LINK}}` = `<link href="[CDN_URL]" rel="stylesheet" type="text/css">` if configured, otherwise empty string

Save to:
- `/mnt/user-data/outputs/{YYYY-MM-DD}-{campaign-slug}-production.html`
- Google Drive: `{YYYY-MM-DD} {Campaign Name} — Production HTML` in same Campaign Drafts folder

Run font check: grep for `base64` inside `<style>` blocks. If found → wrong shell used → fix before proceeding.

**Wait for explicit human approval before proceeding to Step 9.**

---

## Step 9: Klaviyo Deployment

Read `references/klaviyo-html.md` before making API calls.

**Create template:**
```
POST /api/templates/
{
  "data": {
    "type": "template",
    "attributes": {
      "name": "{Campaign Name} — {YYYY-MM-DD}",
      "editor_type": "CODE",
      "html": "{production_html}"
    }
  }
}
```

Assign template to campaign message. Set list/segment and scheduled send time.

Wait 2–3 seconds after template creation before any follow-up API call (known Klaviyo 404 bug).

**Confirm with human before scheduling send. Never auto-send.**

---

## Template library reference

All templates are in `references/templates/`. Always read the actual file — never reconstruct template HTML from memory.

Read `references/manifest.json` to confirm exact file paths and token names before assembly.

| Reference file | Read before... |
|---|---|
| `references/brand-voice.md` | Writing any copy (Step 3) |
| `references/product-selection.md` | Selecting products (Step 2) |
| `references/manifest.json` | Component selection and token names (Steps 4–5) |
| `references/klaviyo-html.md` | Klaviyo API calls (Step 9) |
| `reference-google-drive` skill | Google Drive uploads (Steps 7, 8) |

---

## What the agent does NOT do in v4

- Write HTML
- Choose colours, fonts, or spacing
- Resize or reposition illustrations
- Add, remove, or modify SVG icons
- Override any locked style in a template

If a campaign need cannot be met with the existing templates, escalate for template development. Do not improvise HTML.
