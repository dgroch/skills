# Design System — Fig & Bloom Email

## Colour Palette

| Name | Hex | Usage |
|---|---|---|
| Noir | #000000 | Primary text, CTAs, dark section backgrounds, logo |
| Silk White | #FFFFFF | Primary email background |
| Clay | #D8CCBE | Secondary backgrounds, borders, dividers, body background |
| 50% Clay | #EBE5DF | Tertiary backgrounds (opt-out, testimonial, promo sections) |
| Campaign accent | Varies | Seasonal — must complement brand palette. Approved per campaign. |

**Rules:**
- Brand is monochromatic — black and white for maximum impact
- Borders/dividers: 1px solid #e8e2da (slightly lighter than Clay)
- Campaign accent colours are permitted per the brand guidelines but should be used sparingly (e.g. CTA background, section border accent)

## Typography

### Lust (Display)
- **Role:** Section headlines, product names, promo code text, large quotes
- **Weight:** Regular only — NEVER italic
- **Case:** Title Case for headlines, mixed for product names
- **Sizes:** 28px (section headlines), 22px (product names), 20px (promo codes)
- **Fallback stack:** Georgia, 'Times New Roman', serif

### Cervanttis (Script Accent)
- **Role:** Hero headlines, opt-out headings, upsell headings — MAX 3 placements per email
- **Weight:** Normal only
- **Case:** ALWAYS lowercase
- **Sizes:** 44px (hero headline), 26–32px (section accents)
- **Usage:** Sparingly. If you're considering a 4th Cervanttis placement, use Lust instead.
- **Fallback stack:** cursive

### Neuzeit-Grotesk (Body)
- **Role:** Body copy, CTAs, labels, navigation, preheader text, prices, captions
- **Weights:** Light (300) for body, Bold (700) for CTAs/labels/navigation
- **Sizes:** 14px (body), 12–13px (secondary copy), 10–11px (labels, nav, fine print), 9px (grid labels)
- **Letter spacing:** Body: normal. CTAs/labels: 0.12–0.18em. Navigation: 0.1em
- **Fallback stack:** 'Gill Sans', 'Helvetica Neue', sans-serif

## Button Styles

| Variant | Background | Text | Border | Usage |
|---|---|---|---|---|
| Primary | #000 | #fff | none | Main CTAs |
| Primary White | #fff | #000 | none | CTAs on dark backgrounds |
| Outline | transparent | #000 | 1.5px solid #000 | Secondary actions (opt-out) |
| Outline White | transparent | #fff | 1.5px solid #fff | Secondary on dark backgrounds |
| Small | #000 | #fff | none | Product cards |

**All buttons:** Neuzeit-Grotesk Bold, uppercase, letter-spacing 0.16em, padding 14px 40px (primary) or 10px 24px (small)

## Illustrations

8 brand illustrations available in white-on-transparent and black-on-transparent:
- Body, BodyFlower, Face1, Face2, FrontFace, HandFlower, HandPlant, HandRose

**Usage rules:**
- ONE illustration per section maximum
- Tighter crop preferred — zoom into the detail rather than showing the full image
- White variant: for Noir background sections (opacity 25–35%)
- Black variant: for white/clay background sections (opacity 10–15%)
- Position: right or left edge, vertically centred, partially bleeding off-edge
- Purpose: texture and brand signature, not decoration. Should feel incidental, not focal.

**Recommended pairings:**
- Hero/body copy: BodyFlower, HandFlower
- Upsell/dark sections: HandRose, HandFlower
- Testimonial/quote: Face1, Face2
- Product sections: generally no illustration (let product photography speak)

## Photography Guidelines

From brand guidelines:
- Floral arrangements should be the main subject
- Light, airy, simple backgrounds
- People: not engaging camera, not the focal point, used for scale and warmth
- No distracting text overlays on photography
- Product shots: clean white/light backgrounds, product as sole subject

## Hero Component

- **Layout:** Text overlaid on lifestyle image
- **Image mask:** 30% black overlay (rgba(0,0,0,.30)) to ensure text contrast
- **Text:** White, centred, layered: subheading (Neuzeit Bold uppercase 10px) → headline (Cervanttis 44px lowercase) → subheadline (Neuzeit Light 13px) → CTA (white button)
- **Aspect ratio:** approximately 4:3
- **Photography brief for AI generation:** Hands holding bouquet, kraft paper wrap, subject not engaging camera, warm natural light, Australian setting

## Section Spacing

- Section padding: 32–48px horizontal, 32–44px vertical
- Between paragraphs: 12–14px
- After headline to content: 24–32px
- Border between sections: 1px solid #e8e2da

## Layout Recipes (v1)

### Product Layouts
- **Full-width:** Product image spans 600px, info centred below. Use for hero product or premium/high-impact items.
- **Two-column grid:** Two products side by side (300px each), square images, info below each. Use for mid-tier products.

### Section Backgrounds
- White (#fff): default for product sections, body copy
- 50% Clay (#EBE5DF): opt-out, testimonials, promo blocks
- Noir (#000): upsell sections, occasional opt-out variant

### Email Rhythm
A well-designed email alternates visual density:
```
Dense  (hero image + text overlay)
Light  (opt-out — minimal text, beige bg)
Medium (body copy with illustration accent)
Dense  (full-width product image)
Dense  (two-column product grid)
Dense  (full-width product image)
Light  (testimonial — beige bg, centered quote)
Medium (promo code block)
Dense  (upsell — dark bg, illustration)
Light  (cutoffs — small text)
Light  (trust bar — icons)
Light  (footer)
```

## Promo Code Styling

- Container: dashed border (2px dashed #000), padding 12px 32px
- Code text: Lust, 20px, letter-spacing 0.08em
- Supporting text: Neuzeit Light, 12px, colour #666
- Section background: white (not clay — code should pop)

## Testimonial Styling

- Large opening quotation mark: Lust, 48px, colour Clay (#D8CCBE)
- Quote text: Neuzeit Light 14px, italic, colour #333, max-width 360px
- Attribution: Neuzeit Bold 11px, colour #666, preceded by em dash
- Section background: 50% Clay (#EBE5DF)

## Trust Bar

5 items in a single row: Fresh Daily Flowers, Perfect for Every Occasion, Australia-Wide Service, Same Day Delivery, Order Before 1pm. SVG icons (stroke only, 26px), Neuzeit Bold 8px labels.
