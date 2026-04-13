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

## Cervanttis Rendering Rule

Always set `font-synthesis:none` and explicit `font-weight:400` on every Cervanttis element to prevent browser faux-bold:

```css
font-family: 'Cervanttis', cursive;
font-weight: 400;
font-style: normal;
-webkit-font-smoothing: antialiased;
font-synthesis: none;
```

## Illustration Sizing Formula

**CSS height = (container_height × visibility_pct) + bleed_offset**

The bleed offset hides the origin of the linework below the section edge. Width is always `auto` — never constrain width directly.

| Context | Container height | Visibility | Bleed | Total CSS height |
|---|---|---|---|---|
| Hero B text band | auto (min 280px) | — | 30px | width:220px, height:auto |
| Hero C text col | 440px | 55% = 242px | 20px | 262px |
| Hero D noir | 500px | 70% = 350px | 60px | 410px |
| Body/copy sections | auto | — | 20px | 200–220px |

**Illustration source files:** Use hi-res exports (≥500px wide). Do not use the original low-res bundle (274–400px native) — these will appear pixelated on retina screens.

**Illustration opacity by background:**
- Noir background → white variant, 25–30% left / 20–25% right (slightly less for visual balance)
- White background → black variant, 18% left / 14% right
- Clay (#D8CCBE) background → black variant, 18% / 14%; or white variant, 35% / 28%
- 50% Clay (#EBE5DF) background → black variant, 14% / 11%

**Non-repetition rule:** Never use the same illustration in consecutive sections. Vary across HandFlower, BodyFlower, HandRose, FrontFace etc. within a single email.

## Hero Variants (v2 — Approved)

All heroes share: header (logo centred, 24px height), section border `1px solid #e8e2da`, body copy section below.

### Hero A — Text Over Image
- Full-width lifestyle image (600×450px), 30% black mask overlay
- Text centred over image: super label → Cervanttis headline 56px → subheadline → white CTA
- **Use for:** standard campaigns, maximum visual impact

### Hero B — Text Above Image
- Text band (top) + full-bleed photo (bottom, 600×360px, no overlay)
- Text band backgrounds: White / 50% Clay (#EBE5DF) / Clay (#D8CCBE) / Noir
- Illustration: width:220px, height:auto, anchored right:0, bottom:-30px (base bleeds off)
- Text/CTA colour: black on light bands, white on Noir
- **Use for:** when the photo should be seen unobscured; editorial feel

### Hero C — Split (50/50)
- Left 300px + right 300px, fixed height 440px
- **C1:** Photo left / Text right  **C2:** Text left / Photo right
- Text col backgrounds: White / Clay (#D8CCBE) / Noir
- Illustration: height:262px (55% visible + 20px bleed), bottom-right of text col, width:auto
- Text aligned left within col; CTA left-aligned
- **Use for:** portrait-crop photography; most editorial layout

### Hero D — Dark Noir (Type-forward)
- No photography. Full Noir (#000) background, fixed height 500px
- Two illustrations flanking: left + mirrored right, height:410px (70% visible + 60px bleed), bottom-anchored
- Cervanttis headline 62px; horizontal rule divider; white CTA
- Background variants: Noir / White / Clay / 50% Clay (with matching illo colour and opacity)
- **Use for:** high-intent sends, re-engagement, VIP, product launches; maximum brand statement

## Section Spacing

- Section padding: 32–48px horizontal, 32–44px vertical
- Between paragraphs: 12–14px
- After headline to content: 24–32px
- Border between sections: 1px solid #e8e2da

## Product Image Aspect Ratio

All product images use **4:5** (1000×1250px source). This matches the standard product photography format.

| Display context | CSS dimensions |
|---|---|
| Full-width | 600×750px |
| Two-column grid | 300×375px each |
| Horizontal card | 280×350px |
| Single + testimonial product col | 340×425px |
| Lifestyle + studio — lifestyle | 600×400px (3:2 crop from square, `object-position:center 25%`) |
| Lifestyle + studio — studio | 600×500px (`object-position:center top`) |

## Layout Recipes (v2)

### Hero Layouts
See Hero Variants above.

### Product Layouts (v2)

**Full-width** — Product image 600×750px (4:5), info centred below. Use for hero product or high-impact items.

**Two-column grid** — Two products side by side (300×375px each). Use for mid-tier products.

**Horizontal card** — Image left 280×350px (4:5), info right 320px, total height 350px. Alternate image-left / image-right between consecutive cards for rhythm. Use for 3–4 equal-weight products.

**Single product + testimonial** — Product col 340px (image 340×425px, info below) + testimonial col 260px (50% Clay bg). Illustration: Face2, bottom-right, `height:calc(30%+30px)`, `right:-30px`, `bottom:-30px`, `width:auto`, `opacity:.12`. No quote mark. Stars rating above quote text. Use when strong review copy is available.

**Lifestyle + studio stacked** — Lifestyle image 600×400px (`object-position:center 25%`) above studio shot 600×500px (`object-position:center top`), info centred below. Reserve for one hero/spotlight product per email — the most editorial format.

### Section Backgrounds (v2)

| Background | Hex | Illustration variant | Illustration opacity | Primary use |
|---|---|---|---|---|
| White | #ffffff | Black | 10–18% | Default — body copy, products |
| 50% Clay | #EBE5DF | Black | 11–16% | Opt-out, testimonials, fine print |
| Clay | #D8CCBE | Black or White | 13–20% | Warm hero bands, promo, rich moments |
| Noir | #000000 | White | 20–30% | Upsell, Hero D, high-impact closing beat |
| Campaign accent | e.g. #C4857A | White | 20–25% | Promo band OR border/CTA detail — never both in same email |

**Full-bleed image as background/divider:**
- Narrow strip (180px): lifestyle photography only, `object-fit:cover`, use as visual pause — no text
- Taller panel (340px): can carry optional text overlay (28% black mask, white Lust headline, outline white CTA)
- Studio shots too static at strip height — lifestyle photography only

### Section Dividers (v2)

**Line** — `1px solid #e8e2da`. Default. No visual weight. Use between all standard sections.

**Illustration strip** — 120px tall container, `overflow:hidden`. BodyFlower at `width:100%`, `position:absolute`, `transform:translate(-50%,-35%)` (35% crop shows blooms, not stems). Match illo variant to background: black on light, white on Noir. Opacities: Clay 20%, 50% Clay 16%, White 13% (add 1px borders top+bottom), Noir 32%.

**Full-bleed image** — 180px tall, lifestyle photography, `object-fit:cover`, `object-position:center 25%`. Pure visual pause — no text, no overlay. Studio photography does not work at this crop height.

**Whitespace** — 48px `<div>` with matching background colour. Most editorial option. Requires strong content on both sides.

### Email Rhythm
A well-designed email alternates visual density:
```
Dense  (hero — A/B/C/D based on campaign tone)
Light  (opt-out — 50% Clay bg, if required)
Medium (body copy with illustration accent)
[divider — illustration strip or whitespace]
Dense  (full-width or lifestyle+studio product)
Dense  (horizontal card stack or two-column grid)
Dense  (full-width or single+testimonial product)
[divider — line or full-bleed image strip]
Light  (testimonial — 50% Clay bg)
Medium (promo code block)
Dense  (upsell — Noir bg, illustrations)
Light  (cutoffs — small text)
Light  (trust bar — icons)
Light  (footer)
```

## Promo Code Styling

- Container: dashed border (2px dashed #000), padding 12px 32px
- Code text: Lust, 20px, letter-spacing 0.08em
- Supporting text: Neuzeit Light, 12px, colour #666
- Section background: white (not clay — code should pop)
- On accent background: dashed border `rgba(255,255,255,.6)`, code text white

## Testimonial Styling — Full-width

- Background: 50% Clay (#EBE5DF)
- No quote mark
- Stars: ★★★★★, colour #C8A888, 12px, letter-spacing 0.1em, above quote
- Quote text: Neuzeit Light 14px, italic, colour #333, max-width 360px, line-height 1.7
- Attribution: Neuzeit Bold 11px, colour #666, preceded by em dash
- Illustration: Face1 or Face2, bottom-right, low opacity (10–12%), `height:200–220px`

## Testimonial Styling — Alongside Product (Single + Testimonial card)

- Col width: 260px, background #EBE5DF
- No quote mark
- Stars above quote text
- Illustration: Face2, `height:calc(30%+30px)`, `right:-30px`, `bottom:-30px`, `width:auto`, `opacity:.12`

## Trust Bar

5 items in a single row: Fresh Daily Flowers, Perfect for Every Occasion, Australia-Wide Service, Same Day Delivery, Order Before 1pm. SVG icons (stroke only, 26px), Neuzeit Bold 8px labels.
