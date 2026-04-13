# Component Library — Fig & Bloom Email

## Component Decision Matrix

| Component | Always | Conditional | Condition |
|---|---|---|---|
| Header (logo) | ✓ | | |
| Hero (text over image) | ✓ | | |
| Sensitivity opt-out | | ✓ | Occasion can be painful |
| Body copy | ✓ | | |
| Section headline | ✓ | | When products follow |
| Product showcase (3–5) | ✓ | | |
| Testimonial | | ✓ | Reviews exist for featured products |
| Promo code block | | ✓ | Campaign has an offer |
| Card/gift upsell | | ✓ | Add-on products available |
| Partner cross-promo | | ✓ | Active partner deal (rare) |
| Delivery cutoffs | | ✓ | Hard delivery deadline |
| Trust bar | ✓ | | |
| Footer (nav + social) | ✓ | | |

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

## Component Ordering

Standard ordering (adjust based on campaign needs):

```
1. Header
2. Hero
3. Opt-out (if required — always immediately after hero)
4. Body copy
5. Section headline
6. Products (mixed layouts)
7. Testimonial
8. Promo code
9. Upsell (dark section)
10. Delivery cutoffs
11. Trust bar
12. Footer
```

**Flexible rules:**
- Opt-out MUST be early (position 3) when included — don't bury it
- Testimonial works best between products and promo (social proof before purchase nudge)
- Upsell (dark section) creates a visual "moment" — place near bottom as a closing beat
- Promo code can move earlier if the campaign is offer-led

## Component HTML Patterns

### Header
```html
<div style="text-align:center;padding:28px 24px 22px;border-bottom:1px solid #e8e2da">
  <img src="{LOGO_URL}" alt="Fig & Bloom" style="height:24px;width:auto">
</div>
```

### Hero (text over image)
```html
<div style="position:relative;width:100%">
  <img src="{HERO_IMAGE}" style="width:100%;display:block" alt="">
  <div style="position:absolute;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.30);
    display:flex;flex-direction:column;align-items:center;justify-content:center;
    text-align:center;padding:40px">
    <p style="font-family:'NeuzeitGro',sans-serif;font-size:10px;font-weight:700;
      letter-spacing:.14em;text-transform:uppercase;color:rgba(255,255,255,.8)">
      {SUBHEADING}
    </p>
    <h1 style="font-family:'Cervanttis',cursive;font-size:44px;color:#fff;
      line-height:1.05;text-shadow:0 2px 24px rgba(0,0,0,.25)">
      {HEADLINE_LOWERCASE}
    </h1>
    <p style="font-size:13px;color:rgba(255,255,255,.92);max-width:320px">
      {SUB_COPY}
    </p>
    <a href="{CTA_URL}" style="{BTN_WHITE_STYLES}">{CTA_TEXT}</a>
  </div>
</div>
```

### Promo Code Block
```html
<div style="text-align:center;padding:36px 48px;border-top:1px solid #e8e2da">
  <p style="font-size:10px;font-weight:700;letter-spacing:.14em;
    text-transform:uppercase;color:#888">{PROMO_LABEL}</p>
  <div style="display:inline-block;border:2px dashed #000;padding:12px 32px;margin:12px 0">
    <span style="font-family:'Lust',Georgia,serif;font-size:20px;
      letter-spacing:.08em">{CODE}</span>
  </div>
  <p style="font-size:12px;color:#666">{TERMS}</p>
  <a href="{CTA_URL}" style="{BTN_PRIMARY_STYLES}">{CTA_TEXT}</a>
</div>
```

### Dark Upsell Section
```html
<div style="background:#000;text-align:center;padding:48px;position:relative;overflow:hidden">
  <!-- Optional: illustration at 25-35% opacity, positioned right -->
  <img src="{ILLUSTRATION_WHITE}" style="position:absolute;right:-20px;top:50%;
    transform:translateY(-50%);height:260px;opacity:.3" alt="">
  <h2 style="font-family:'Cervanttis',cursive;font-size:32px;color:#fff;
    position:relative;z-index:1">{HEADLINE_LOWERCASE}</h2>
  <p style="font-size:13px;color:rgba(255,255,255,.7);max-width:340px;margin:14px auto 24px;
    position:relative;z-index:1">{BODY}</p>
  <a href="{CTA_URL}" style="{BTN_WHITE_STYLES};position:relative;z-index:1">{CTA_TEXT}</a>
</div>
```

### Testimonial
```html
<div style="text-align:center;padding:36px 48px;border-top:1px solid #e8e2da;background:#EBE5DF">
  <span style="font-family:'Lust',Georgia,serif;font-size:48px;color:#D8CCBE;
    display:block;line-height:.6;margin-bottom:8px">"</span>
  <p style="font-size:14px;font-style:italic;line-height:1.7;color:#333;
    max-width:360px;margin:0 auto 10px">{QUOTE}</p>
  <cite style="font-size:11px;font-weight:700;letter-spacing:.06em;color:#666;
    font-style:normal">— {NAME}</cite>
</div>
```
