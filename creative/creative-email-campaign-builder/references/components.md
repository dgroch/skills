# Component Library — Fig & Bloom Email (v2)

## Component Decision Matrix

| Component | Always | Conditional | Condition |
|---|---|---|---|
| Header (logo) | ✓ | | |
| Hero | ✓ | | Choose variant A/B/C/D based on campaign tone |
| Sensitivity opt-out | | ✓ | Occasion can be painful |
| Body copy | ✓ | | |
| Section divider | | ✓ | Between sections where visual rhythm needs a break |
| Section headline | ✓ | | When products follow |
| Product showcase (3–5) | ✓ | | Mix card layouts — see Product Layout Selection |
| Testimonial | | ✓ | Reviews exist for featured products |
| Promo code block | | ✓ | Campaign has an offer |
| Card/gift upsell | | ✓ | Add-on products available |
| Partner cross-promo | | ✓ | Active partner deal (rare) |
| Delivery cutoffs | | ✓ | Hard delivery deadline |
| Trust bar | ✓ | | |
| Footer (nav + social) | ✓ | | |

---

## Hero Variant Selection

| Variant | When to use |
|---|---|
| A — Text Over Image | Standard campaigns; maximum photo impact |
| B — Text Above Image | When photo must be seen unobscured; editorial feel |
| C1 — Image Left / Text Right | Portrait photography; most editorial |
| C2 — Text Left / Image Right | As C1; use when flipping for visual variety |
| D — Dark Noir (type-forward) | Launches, VIP, re-engagement, high-intent sends |

Each hero has approved colour variants (White / Clay / 50% Clay / Noir). See design-system.md.

---

## Product Layout Selection

Choose card types based on product count, price tier, and available photography:

| Layout | Products | Best for |
|---|---|---|
| Full-width | 1 | Hero product, highest price point |
| Lifestyle + studio stacked | 1 | Editorial spotlight; requires both photo types |
| Single + testimonial | 1 | When strong review copy available |
| Horizontal card | 3–4 | Equal-weight products; alternates image L/R |
| Two-column grid | 2–4 | Mid-tier; efficient use of vertical space |

**Mixing layouts:** A well-composed product section varies layouts. Example: open with full-width hero product → horizontal card stack for mid-tier → two-column grid for remaining.

---

## Section Divider Selection

| Divider | Weight | When to use |
|---|---|---|
| Line (1px) | None | Default between all sections |
| Whitespace (48px) | Silence | Most editorial; between two text-heavy sections |
| Illustration strip (120px) | Medium | Between product and copy sections; brand texture moment |
| Full-bleed image (180px) | High | Mid-email pause; requires strong lifestyle photography |

**Rules:**
- Use max one non-line divider per email
- Full-bleed image strip: lifestyle photography only (studio shots too static at this crop)
- Illustration strip: BodyFlower, 100% width, 35% vertical crop, background matches adjacent section tone

---

## Sensitivity Opt-Out Triggers

Include opt-out block for these occasions:
- Mother's Day
- Father's Day
- Valentine's Day / Galentine's Day
- Pregnancy / baby-related
- Memorial / sympathy campaigns

Do NOT include for:
- Seasonal campaigns (autumn, winter, etc.)
- Product launches
- Flower of the month
- General promotions
- Retention/loyalty flows

---

## Component Ordering

Standard ordering (adjust based on campaign needs):

```
1.  Header
2.  Hero (A/B/C/D)
3.  Opt-out (if required — always immediately after hero)
4.  Body copy
5.  [Divider — optional]
6.  Section headline
7.  Products (mixed layouts)
8.  [Divider — optional]
9.  Testimonial
10. Promo code
11. Upsell (dark section)
12. Delivery cutoffs
13. Trust bar
14. Footer
```

**Flexible rules:**
- Opt-out MUST be position 3 when included — never buried
- Testimonial between products and promo (social proof before purchase nudge)
- Upsell (Noir section) near bottom — closing beat
- Promo code can move to position 4 if campaign is offer-led
- Never use the same section divider type twice in one email

---

## Component HTML Patterns

### Header
```html
<div style="text-align:center;padding:28px 24px 22px;border-bottom:1px solid #e8e2da;">
  <img src="{LOGO_URL}" alt="Fig & Bloom" style="height:24px;width:auto;">
</div>
```

### Hero A — Text Over Image
```html
<div style="position:relative;width:600px;height:450px;overflow:hidden;">
  <img src="{HERO_IMAGE}" style="width:100%;height:100%;object-fit:cover;display:block;" alt="">
  <div style="position:absolute;inset:0;background:rgba(0,0,0,.30);display:flex;
    flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:40px;">
    <p style="font-family:'NeuzeitGro',sans-serif;font-weight:700;font-size:10px;
      letter-spacing:.14em;text-transform:uppercase;color:rgba(255,255,255,.8);margin-bottom:14px;">
      {SUBHEADING}
    </p>
    <h1 style="font-family:'Cervanttis',cursive;font-weight:400;font-style:normal;
      font-synthesis:none;font-size:56px;color:#fff;line-height:1.0;margin-bottom:16px;">
      {HEADLINE_LOWERCASE}
    </h1>
    <p style="font-family:'NeuzeitGro',sans-serif;font-weight:300;font-size:13px;
      color:rgba(255,255,255,.92);max-width:320px;line-height:1.7;margin-bottom:28px;">
      {SUB_COPY}
    </p>
    <a href="{CTA_URL}" style="font-family:'NeuzeitGro',sans-serif;font-weight:700;font-size:10px;
      letter-spacing:.16em;text-transform:uppercase;background:#fff;color:#000;
      text-decoration:none;padding:14px 40px;display:inline-block;">{CTA_TEXT}</a>
  </div>
</div>
```

### Hero B — Text Above Image
```html
<!-- Text band -->
<div style="background:{BAND_BG};padding:48px 64px 44px;text-align:center;
  position:relative;overflow:hidden;min-height:280px;">
  <img src="{ILLUSTRATION_BLACK}" style="position:absolute;right:0;bottom:-30px;
    width:220px;height:auto;opacity:.13;display:block;" alt="">
  <p style="font-family:'NeuzeitGro',sans-serif;font-weight:700;font-size:9px;
    letter-spacing:.18em;text-transform:uppercase;color:{SUPER_COLOR};
    margin-bottom:18px;position:relative;z-index:1;">{SUBHEADING}</p>
  <h1 style="font-family:'Cervanttis',cursive;font-weight:400;font-style:normal;
    font-synthesis:none;font-size:54px;color:{HEADLINE_COLOR};line-height:1.0;
    margin-bottom:18px;position:relative;z-index:1;">{HEADLINE_LOWERCASE}</h1>
  <p style="font-family:'NeuzeitGro',sans-serif;font-weight:300;font-size:13px;
    color:{SUB_COLOR};max-width:340px;margin:0 auto 28px;line-height:1.75;
    position:relative;z-index:1;">{SUB_COPY}</p>
  <a href="{CTA_URL}" style="font-family:'NeuzeitGro',sans-serif;font-weight:700;
    font-size:10px;letter-spacing:.16em;text-transform:uppercase;background:{BTN_BG};
    color:{BTN_TEXT};text-decoration:none;padding:14px 40px;display:inline-block;
    position:relative;z-index:1;">{CTA_TEXT}</a>
</div>
<!-- Photo below — no overlay -->
<div style="width:600px;height:360px;overflow:hidden;">
  <img src="{LIFESTYLE_IMAGE}" style="width:100%;height:100%;object-fit:cover;
    object-position:center;display:block;" alt="">
</div>
```

### Hero C — Split (50/50)
```html
<div style="display:flex;width:600px;height:440px;">
  <!-- Photo col (swap order for C2) -->
  <div style="width:300px;height:440px;position:relative;overflow:hidden;flex-shrink:0;">
    <img src="{PRODUCT_IMAGE}" style="width:100%;height:100%;object-fit:cover;display:block;" alt="">
  </div>
  <!-- Text col -->
  <div style="width:300px;height:440px;background:{COL_BG};display:flex;
    flex-direction:column;align-items:flex-start;justify-content:center;
    padding:40px 36px 40px 40px;position:relative;overflow:hidden;
    border-left:1px solid #e8e2da;">
    <img src="{ILLUSTRATION}" style="position:absolute;right:-16px;bottom:-20px;
      height:262px;width:auto;opacity:.11;display:block;" alt="">
    <p style="font-family:'NeuzeitGro',sans-serif;font-weight:700;font-size:9px;
      letter-spacing:.18em;text-transform:uppercase;color:{SUPER_COLOR};
      margin-bottom:20px;position:relative;z-index:1;">{SUBHEADING}</p>
    <h1 style="font-family:'Cervanttis',cursive;font-weight:400;font-style:normal;
      font-synthesis:none;font-size:44px;color:{HEADLINE_COLOR};line-height:1.0;
      margin-bottom:18px;position:relative;z-index:1;">{HEADLINE_LOWERCASE}</h1>
    <p style="font-family:'NeuzeitGro',sans-serif;font-weight:300;font-size:12px;
      color:{SUB_COLOR};line-height:1.75;margin-bottom:28px;
      position:relative;z-index:1;max-width:190px;">{SUB_COPY}</p>
    <a href="{CTA_URL}" style="font-family:'NeuzeitGro',sans-serif;font-weight:700;
      font-size:10px;letter-spacing:.16em;text-transform:uppercase;background:{BTN_BG};
      color:{BTN_TEXT};text-decoration:none;padding:13px 24px;display:inline-block;
      position:relative;z-index:1;">{CTA_TEXT}</a>
  </div>
</div>
```

### Hero D — Dark Noir
```html
<div style="background:{HERO_BG};height:500px;display:flex;flex-direction:column;
  align-items:center;justify-content:center;text-align:center;padding:0 64px;
  position:relative;overflow:hidden;">
  <img src="{ILLUSTRATION_L}" style="position:absolute;left:-16px;bottom:-60px;
    height:410px;width:auto;opacity:.30;display:block;" alt="">
  <img src="{ILLUSTRATION_R}" style="position:absolute;right:-16px;bottom:-60px;
    height:410px;width:auto;opacity:.25;display:block;transform:scaleX(-1);" alt="">
  <p style="font-family:'NeuzeitGro',sans-serif;font-weight:700;font-size:9px;
    letter-spacing:.22em;text-transform:uppercase;color:{SUPER_COLOR};
    margin-bottom:24px;position:relative;z-index:1;">{SUBHEADING}</p>
  <h1 style="font-family:'Cervanttis',cursive;font-weight:400;font-style:normal;
    font-synthesis:none;font-size:62px;color:{HEADLINE_COLOR};line-height:.95;
    margin-bottom:20px;position:relative;z-index:1;">{HEADLINE_LOWERCASE}</h1>
  <div style="width:40px;height:1px;background:{RULE_COLOR};margin:20px auto;
    position:relative;z-index:1;"></div>
  <p style="font-family:'NeuzeitGro',sans-serif;font-weight:300;font-size:13px;
    color:{SUB_COLOR};max-width:300px;margin:0 auto 32px;line-height:1.75;
    position:relative;z-index:1;">{SUB_COPY}</p>
  <a href="{CTA_URL}" style="font-family:'NeuzeitGro',sans-serif;font-weight:700;
    font-size:10px;letter-spacing:.16em;text-transform:uppercase;background:{BTN_BG};
    color:{BTN_TEXT};text-decoration:none;padding:14px 40px;display:inline-block;
    position:relative;z-index:1;">{CTA_TEXT}</a>
</div>
```

### Product Card — Horizontal
```html
<div style="display:flex;width:600px;border-top:1px solid #e8e2da;">
  <div style="width:280px;height:350px;flex-shrink:0;overflow:hidden;">
    <img src="{PRODUCT_IMAGE}" style="width:100%;height:100%;object-fit:cover;
      object-position:center top;display:block;" alt="{PRODUCT_NAME}">
  </div>
  <div style="flex:1;display:flex;flex-direction:column;justify-content:center;
    padding:32px 36px 32px 32px;">
    <p style="font-family:'NeuzeitGro',sans-serif;font-weight:700;font-size:9px;
      letter-spacing:.18em;text-transform:uppercase;color:#aaa;margin-bottom:8px;">{LABEL}</p>
    <h3 style="font-family:'Lust',Georgia,serif;font-weight:normal;font-size:22px;
      color:#000;line-height:1.15;margin-bottom:8px;">{PRODUCT_NAME}</h3>
    <p style="font-family:'NeuzeitGro',sans-serif;font-weight:300;font-size:12px;
      color:#666;line-height:1.6;margin-bottom:12px;font-style:italic;">{OCCASION_HEADLINE}</p>
    <p style="font-family:'NeuzeitGro',sans-serif;font-weight:700;font-size:13px;
      color:#000;letter-spacing:.04em;margin-bottom:20px;">{PRICE}</p>
    <a href="{CTA_URL}" style="font-family:'NeuzeitGro',sans-serif;font-weight:700;
      font-size:9px;letter-spacing:.16em;text-transform:uppercase;background:#000;
      color:#fff;text-decoration:none;padding:10px 24px;display:inline-block;">Shop Now</a>
  </div>
</div>
<!-- Mirror for alternating cards: swap flex-direction to row-reverse, adjust padding -->
```

### Product Card — Single + Testimonial
```html
<div style="display:flex;width:600px;align-items:stretch;border-top:1px solid #e8e2da;">
  <!-- Product col -->
  <div style="width:340px;flex-shrink:0;border-right:1px solid #e8e2da;">
    <div style="width:340px;height:425px;overflow:hidden;">
      <img src="{PRODUCT_IMAGE}" style="width:100%;height:100%;object-fit:cover;
        object-position:center top;display:block;" alt="{PRODUCT_NAME}">
    </div>
    <div style="padding:28px 28px 32px;">
      <p style="font-family:'NeuzeitGro',sans-serif;font-weight:700;font-size:9px;
        letter-spacing:.18em;text-transform:uppercase;color:#aaa;margin-bottom:8px;">{LABEL}</p>
      <h3 style="font-family:'Lust',Georgia,serif;font-weight:normal;font-size:22px;
        color:#000;line-height:1.15;margin-bottom:8px;">{PRODUCT_NAME}</h3>
      <p style="font-family:'NeuzeitGro',sans-serif;font-weight:300;font-size:12px;
        color:#666;line-height:1.6;margin-bottom:12px;font-style:italic;">{OCCASION_HEADLINE}</p>
      <p style="font-family:'NeuzeitGro',sans-serif;font-weight:700;font-size:13px;
        color:#000;margin-bottom:20px;">{PRICE}</p>
      <a href="{CTA_URL}" style="font-family:'NeuzeitGro',sans-serif;font-weight:700;
        font-size:9px;letter-spacing:.16em;text-transform:uppercase;background:#000;
        color:#fff;text-decoration:none;padding:10px 24px;display:inline-block;">Shop Now</a>
    </div>
  </div>
  <!-- Testimonial col -->
  <div style="flex:1;background:#EBE5DF;display:flex;flex-direction:column;
    align-items:center;justify-content:center;padding:36px 28px;text-align:center;
    position:relative;overflow:hidden;">
    <img src="{FACE2_ILLUSTRATION}" style="position:absolute;right:-30px;bottom:-30px;
      height:calc(30% + 30px);width:auto;opacity:.12;display:block;" alt="">
    <span style="font-size:12px;color:#C8A888;letter-spacing:.1em;margin-bottom:18px;
      display:block;position:relative;z-index:1;">★★★★★</span>
    <p style="font-family:'NeuzeitGro',sans-serif;font-weight:300;font-size:13px;
      font-style:italic;color:#333;line-height:1.8;margin-bottom:16px;
      position:relative;z-index:1;max-width:200px;">{QUOTE_TEXT}</p>
    <cite style="font-family:'NeuzeitGro',sans-serif;font-weight:700;font-size:10px;
      letter-spacing:.08em;color:#999;font-style:normal;display:block;
      position:relative;z-index:1;">— {REVIEWER_NAME}</cite>
  </div>
</div>
```

### Section Divider — Illustration Strip
```html
<div style="width:600px;height:120px;background:{BG_COLOR};position:relative;overflow:hidden;">
  <img src="{BODYFLOWER_VARIANT}"
       style="position:absolute;top:50%;left:50%;transform:translate(-50%,-35%);
         width:100%;height:auto;opacity:{OPACITY};display:block;" alt="">
</div>
<!-- BG / variant / opacity: Clay #D8CCBE / black / .20 · 50%Clay #EBE5DF / black / .16
     White #fff / black / .13 (add 1px borders) · Noir #000 / white / .32 -->
```

### Section Divider — Full-Bleed Image Strip
```html
<div style="width:600px;height:180px;overflow:hidden;">
  <img src="{LIFESTYLE_IMAGE}"
       style="width:100%;height:100%;object-fit:cover;object-position:center 25%;display:block;"
       alt="">
</div>
<!-- Lifestyle photography only. No text. No overlay. -->
```

### Promo Code Block
```html
<div style="text-align:center;padding:36px 48px;border-top:1px solid #e8e2da;">
  <p style="font-family:'NeuzeitGro',sans-serif;font-weight:700;font-size:10px;
    letter-spacing:.14em;text-transform:uppercase;color:#888;margin-bottom:12px;">{PROMO_LABEL}</p>
  <div style="display:inline-block;border:2px dashed #000;padding:12px 32px;margin-bottom:12px;">
    <span style="font-family:'Lust',Georgia,serif;font-weight:normal;font-size:20px;
      letter-spacing:.08em;">{CODE}</span>
  </div>
  <p style="font-family:'NeuzeitGro',sans-serif;font-weight:300;font-size:12px;
    color:#666;margin-bottom:20px;">{TERMS}</p>
  <a href="{CTA_URL}" style="font-family:'NeuzeitGro',sans-serif;font-weight:700;
    font-size:10px;letter-spacing:.16em;text-transform:uppercase;background:#000;
    color:#fff;text-decoration:none;padding:14px 40px;display:inline-block;">{CTA_TEXT}</a>
</div>
```

### Dark Upsell Section
```html
<div style="background:#000;text-align:center;padding:48px;position:relative;overflow:hidden;">
  <img src="{ILLUSTRATION_WHITE}" style="position:absolute;left:-16px;bottom:-60px;
    height:410px;width:auto;opacity:.30;display:block;" alt="">
  <img src="{ILLUSTRATION_WHITE_R}" style="position:absolute;right:-16px;bottom:-60px;
    height:410px;width:auto;opacity:.25;display:block;transform:scaleX(-1);" alt="">
  <h2 style="font-family:'Cervanttis',cursive;font-weight:400;font-style:normal;
    font-synthesis:none;font-size:32px;color:#fff;position:relative;z-index:1;
    margin-bottom:14px;">{HEADLINE_LOWERCASE}</h2>
  <p style="font-family:'NeuzeitGro',sans-serif;font-weight:300;font-size:13px;
    color:rgba(255,255,255,.7);max-width:340px;margin:0 auto 24px;line-height:1.75;
    position:relative;z-index:1;">{BODY}</p>
  <a href="{CTA_URL}" style="font-family:'NeuzeitGro',sans-serif;font-weight:700;
    font-size:10px;letter-spacing:.16em;text-transform:uppercase;background:#fff;
    color:#000;text-decoration:none;padding:14px 40px;display:inline-block;
    position:relative;z-index:1;">{CTA_TEXT}</a>
</div>
```

### Testimonial — Full-width
```html
<div style="text-align:center;padding:44px 64px;border-top:1px solid #e8e2da;
  background:#EBE5DF;position:relative;overflow:hidden;">
  <img src="{FACE1_OR_FACE2_ILLUSTRATION}" style="position:absolute;right:-16px;
    bottom:-20px;height:200px;width:auto;opacity:.11;display:block;" alt="">
  <span style="font-size:12px;color:#C8A888;letter-spacing:.1em;margin-bottom:18px;
    display:block;position:relative;z-index:1;">★★★★★</span>
  <p style="font-family:'NeuzeitGro',sans-serif;font-weight:300;font-size:14px;
    font-style:italic;line-height:1.75;color:#333;max-width:360px;margin:0 auto 14px;
    position:relative;z-index:1;">{QUOTE_TEXT}</p>
  <cite style="font-family:'NeuzeitGro',sans-serif;font-weight:700;font-size:11px;
    letter-spacing:.06em;color:#888;font-style:normal;position:relative;
    z-index:1;">— {REVIEWER_NAME}</cite>
</div>
```

---

## Mobile HTML Patterns (v3 additions)

When generating email HTML, apply the class naming convention from design-system.md to all layout elements. The mobile CSS block must be included in every email's `<style>` tag.

### Table-based stacking for Klaviyo production HTML

In table-based email, stacking is achieved by setting `display:block` on `<td>` elements via media queries. Apply width attributes on `<td>` at desktop size; media queries override to 100%.

**Hero C — table-based split:**
```html
<table width="600" cellpadding="0" cellspacing="0" border="0">
  <tr class="split-row">
    <td class="split-col-photo" width="300" valign="top"
        style="width:300px;height:440px;overflow:hidden;">
      <img src="{IMAGE}" width="300" style="display:block;width:300px;
        height:440px;object-fit:cover;" class="fluid-img" alt="">
    </td>
    <td class="split-col-text" width="300" valign="middle"
        style="width:300px;padding:40px 36px 40px 40px;
        border-left:1px solid #e8e2da;vertical-align:middle;">
      <!-- text content -->
    </td>
  </tr>
</table>
```

**Horizontal card — table-based:**
```html
<table width="600" cellpadding="0" cellspacing="0" border="0"
       class="h-card" style="border-top:1px solid #e8e2da;">
  <tr>
    <td class="h-card-img" width="280"
        style="width:280px;height:350px;overflow:hidden;vertical-align:top;">
      <img src="{IMAGE}" width="280" style="display:block;width:280px;
        height:350px;object-fit:cover;object-position:center top;"
        class="fluid-img" alt="{PRODUCT_NAME}">
    </td>
    <td class="h-card-info"
        style="padding:32px 36px 32px 32px;vertical-align:middle;">
      <!-- product info -->
    </td>
  </tr>
</table>
```

**Single + testimonial — table-based:**
```html
<table width="600" cellpadding="0" cellspacing="0" border="0"
       class="prod-testi-split" style="border-top:1px solid #e8e2da;">
  <tr>
    <td class="prod-testi-prod" width="340"
        style="width:340px;border-right:1px solid #e8e2da;vertical-align:top;">
      <!-- product image + info -->
    </td>
    <td class="prod-testi-testi"
        style="background:#EBE5DF;padding:36px 28px;
        text-align:center;vertical-align:middle;position:relative;">
      <!-- testimonial content -->
    </td>
  </tr>
</table>
```

### Outlook fallback note

Outlook desktop ignores media queries. All emails must be legible and functional at 600px fixed width without any responsive rules applied — this is guaranteed by the table-based base layout. Mobile optimisation is an enhancement, not a dependency.
