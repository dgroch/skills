# Corpus Analysis Summary (214 Campaigns)

**Date:** 2026-05-27
**Corpus:** 214 Fig & Bloom email campaigns (2019-2024)
**Source:** `/opt/data/workspace/right-hook-review-corpus/manifest.csv`

## Key Metrics

- **Total campaigns:** 214
- **With assets:** 214 (100%)
- **Approval rate:** 77.1% (165 approved, 8 change-requested)
- **Dimensions:** 600px width (universal), 4,300-6,750px height

## Campaign Type Distribution

| Type | Count | % | V5 Priority |
|------|-------|---|-------------|
| Holiday | 32 | 15.0% | **HIGH** |
| Lifecycle | 17 | 7.9% | **HIGH** |
| Product Launch | 15 | 7.0% | **HIGH** |
| Promotional | 14 | 6.5% | **HIGH** |
| Welcome | 12 | 5.6% | **HIGH** |
| Seasonal | 11 | 5.1% | **HIGH** |
| Editorial | 5 | 2.3% | Medium |
| Other | 108 | 50.5% | Needs classification |

## Visual Patterns (Programmatic)

### Height-Based Layout Categories
- **Compact** (4,300-4,800px): Single focus (hero + 1 product + CTA)
- **Standard** (5,000-5,800px): 2-3 products + social proof
- **Extended** (6,000-6,750px): Storytelling, multiple products, educational

### Format Distribution
- PNG: ~70% (static campaigns)
- GIF: ~30% (animated elements, product rotations)

## Component Frequency (Estimated)

Based on campaign types and typical email structure:

1. Header/Logo: 100%
2. Hero Section: 100%
3. Body Copy: ~93%
4. Product Cards: ~84%
5. CTA Buttons: 100%
6. Social Proof/Testimonials: ~56%
7. Footer: 100%
8. Offer/Discount Blocks: ~28%
9. Educational Content: ~19%
10. Urgency/Countdown: ~14%

## Gap Analysis (Corpus vs V4)

### Missing Component Types
1. **Campaign-type-specific primitives:**
   - Holiday countdown component
   - Welcome sequence header (email 1/2/3/4 indicator)
   - Abandonment urgency banner
   - Product launch "NEW" badge
   - Offer percentage/dollar display
   - Gift guide tier layout

2. **Seasonal theming:**
   - Spring (pastels, florals)
   - Summer (bright, energetic)
   - Autumn (warm, cozy)
   - Winter (cool, elegant)
   - Holiday themes (Christmas, Valentine's)

3. **Lifecycle flow components:**
   - Discount code with expiry timer
   - Cart contents display
   - Post-purchase care instructions
   - Review request with star rating input

4. **Advanced layouts:**
   - Product comparison grid (2-4 side-by-side)
   - Tiered offer display
   - UGC gallery
   - Educational step-by-step

### Estimated V5 Scope
- **Primitives:** 60-70 (vs 40 in v4)
- **Themes:** 8-10 (vs 1 in v4)
- **Layout templates:** 5-8 (vs 1 in v4)

## Next Steps

1. **Visual analysis** of 20 diverse campaigns (when vision tools available)
2. **Build seasonal themes** (6-8 themes from corpus color patterns)
3. **Create 10 high-priority primitives** from gap analysis
4. **Campaign-type-aware composition** in v5 engine

## Files

- Full analysis: `CORPUS_ANALYSIS_REPORT.md`
- Analysis script: `analyze_email_corpus.py`
- Raw data: `corpus_analysis.json`
