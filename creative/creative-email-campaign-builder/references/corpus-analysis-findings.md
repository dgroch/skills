# Corpus Analysis Findings — v5 Email Design System

**Date:** 2026-05-28
**Sample:** 50 emails across 19 campaign types, analyzed via vision_analyze (qwen-vl-plus)
**Full reports:** `VISUAL_CORPUS_ANALYSIS.md`, `VISUAL_CORPUS_SYNTHESIS.md` in right-hook-review-corpus

## Hero Design Patterns (corpus-validated)

| Pattern | Frequency | Description | Primitives |
|---------|-----------|-------------|------------|
| Text-on-Photo | 60% | Large lifestyle photo + bold headline overlay + CTA | hero-a, hero-b-* |
| Photo + Text Band Below | 20% | Full-bleed photo top, white/clay/noir band below | hero-c* |
| Text-Forward / No Photo | 10% | Type-only hero, noir/clay/white bg | hero-d-* |
| Split Layout | 5% | Photo left/text right (or vice versa) | hero-c* |
| Multi-Image Collage | 5% | 2-4 photo grid as hero | hero-image-only + custom |

## Product Display Styles

| Style | Frequency | Description | Primitive |
|-------|-----------|-------------|-----------|
| Horizontal Cards | 55% | Image left, text+CTA right, one per row | card-horizontal* |
| Product Grid | 20% | 2-4 products side-by-side with badges | product-grid (new) |
| Single Product Focus | 15% | One large product image, centered | card-lifestyle-studio |
| Mixed Grid + Horizontal | 10% | Grid for main, horizontal for featured | product-grid + card-* |

## CTA Language by Flow Type (corpus-validated)

| Flow Type | CTA Examples | Primitive |
|-----------|-------------|-----------|
| Campaign | "GIFT NOW", "SPOIL HER", "SEND A SMILE" | cta (standard) |
| Sale | "SAVE NOW", "SHOP NOW", "MAKE IT HAPPEN" | cta (standard) |
| Abandonment | "TAKE ME BACK", "SEND IT NOW", "BRING IT TO LIFE" | cta-emotional (new) |
| Welcome | "SAVE NOW", "CLAIM MY CREDIT" | cta-emotional |
| LTV/Loyalty | "REDEEM REWARDS", "USE YOUR POINTS" | cta-emotional |
| Launch | "DISCOVER", "SEE WHAT'S NEW" | cta-exploratory (new) |
| Giveaway | "ENTER NOW", "SHOP TO ENTER", "TRY YOUR LUCK" | cta (standard) |
| Post-Purchase | "JOIN THE GROUP", "SHARE YOUR THOUGHTS" | community-invite (new) |

## Section Count by Campaign Type

| Type | Sections | Notes |
|------|----------|-------|
| Campaign | 8-10 | Standard flow |
| Sale/BFCM | 10-12 | Extra: promo code, T&C blocks |
| Abandonment | 6-8 | Short, focused on single product |
| Welcome | 8-10 | Intro + product range showcase |
| LTV/Loyalty | 10-12 | Countdown, points display, promo code |
| Launch | 8-10 | Storytelling + product showcase |
| Giveaway | 10-12 | Prize display, countdown, mechanics |
| Educational | 10-14 | Text-heavy, multiple info blocks |
| Christmas | 12-16 | Gift guide, multiple categories |

## Background Color Palettes

| Campaign | Hero BG | Section BGs | Accent |
|----------|---------|-------------|--------|
| Standard | White | White, light gray | Noir (#000) |
| Christmas | Dark red (#8B0000) or deep green | Dark red, gold | Gold (#FFD700) |
| Valentine's | Dark red or white+pink overlay | Light pink (#FFB6C1) | Burgundy (#800020) |
| Easter | White or soft peach | Light pink, soft peach | Orange (#FF8C00) |
| Earth Day | Light green | Green (#228B22), white | Forest green |
| Autumn | Warm amber/terracotta | Clay (#D8CCBE) | Burnt orange |
| Winter | Cool blue/silver | Light blue, white | Silver |

## Decorative Elements (consistent across corpus)

1. **Floral line illustrations** — Delicate leaf/flower line art as section dividers
2. **Service icons** — 5-6 line icons at bottom (Fresh Daily Flowers, Every Occasion, Australia-Wide, Same Day, Order Before 1pm)
3. **Brand logo** — Centered at top and bottom

## Confirmed Missing Primitives (built this session)

1. promo-code-display — Dashed border, bold code (30% of Sale/LTV/Welcome)
2. countdown-timer — DAYS/HOURS/MINUTES circles (20% of LTV/Giveaway/Easter)
3. urgency-headline — Bold urgent headlines with accent bar (25% of Sale/Holiday)
4. personalized-greeting — Hi {{ first_name }} (15% of LTV/Welcome)
5. cta-emotional — "BRING IT TO LIFE" style (100% of Abandonment)
6. cta-exploratory — "Discover" style (80% of Product Launch)
7. terms-conditions-block — Light gray T&C box (40% of Sale/BFCM)
8. community-invite — Facebook group link (Post-purchase)
9. card-upsell — Greeting card add-on (20% of Holiday)
10. discount-badge — "20% OFF" image overlay (30% of Sale)
11. feedback-request — Email feedback CTA (Post-purchase)
12. product-grid — 2-4 col grid with badges (20% of emails)
13. comparison-pairs — "What I Bought vs What I Got" (UGC)
14. sentiment-product-row — Product + emotional copy (15% of Holiday)
15. giveaway-banner — Prize display with value (100% of Giveaway)

## White Space Standards

- Between sections: 48-64px
- Within sections: 24-32px
- Around CTAs: 32px padding
- Around product cards: 16-24px
- Email width: 600px max-width container
