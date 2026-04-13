# Product Selection — Fig & Bloom Email Campaigns

## Source: Shopify Storefront

Fetch products from the campaign-relevant Shopify collection.

### Finding the right collection
- Map campaign occasion to collection handle:
  - Mother's Day → `/collections/mothers-day`
  - Valentine's Day → `/collections/valentines-day`
  - General/seasonal → `/collections/flowers` (bestsellers)
  - New product launch → specific collection handle from brief
- Fetch via: `web_fetch` on `figandbloom.com/collections/{handle}`
- Parse product names, prices, review counts, and image URLs from the collection page HTML

### If no campaign-specific collection exists
Fall back to `/collections/flowers` and filter by:
- Seasonal appropriateness
- Current availability (check for "sold out" indicators)
- Bestseller status

## Selection Criteria

Select 3–5 products. Optimise across these dimensions:

### 1. Price Spread
Ensure the selection covers at least 3 price tiers:
- Entry: $80–110
- Mid: $120–160
- Premium: $180–250+

This ensures the email serves both budget-conscious and premium buyers.

### 2. Visual Variety
Selected products should have distinct colour stories:
- Don't select 3 pink bouquets
- Mix warm tones (pink, coral, peach) with cool (white, green, purple)
- Include at least one "clean/white" option and one "colourful" option

### 3. Social Proof Density
Prioritise products with:
- Higher review counts (>10 reviews = strong signal)
- Higher ratings (4.0+)
- Products with reviews create more buyer confidence in email

### 4. Type Mix
Include variety in product format:
- At least one bouquet (most popular category)
- At least one vase arrangement or bundle (higher AOV, gifting-ready)
- Consider add-ons: candle bundles, chocolates, greeting cards

## Layout Assignment

After selection, assign products to layout positions:

| Position | Layout | Best for |
|---|---|---|
| Position 1 | Full-width | Entry price point or highest visual impact |
| Position 2–3 | Two-column grid | Mid-tier products, visual contrast pair |
| Position 4 | Full-width | Premium/top-end product (aspirational close) |

This creates a visual rhythm: big → small small → big.

## Presentation to Human

Present the selection as a table:

```
| Product | Price | Reviews | Layout | Rationale |
|---|---|---|---|---|
| Monaco Pink | From $97 | 5 ★ | Full-width | Entry price, pink/feminine |
| Osaka Bouquet | From $139 | 34 ★★★★ | Grid left | Bestseller, highest reviews |
| Marseille | From $150 | 33 ★★★★ | Grid right | Pastel contrast to Osaka |
| Osaka + Vase | From $220 | 12 ★★★ | Full-width | Premium, gifting-ready upsell |
```

Wait for human approval before proceeding to copy.
