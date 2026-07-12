# Social Media Ad Campaign Manifesting

## When to Use
When manifesting frames from social media ad campaigns (Instagram, TikTok, Facebook ads) that are typically provided as multiple image/video variations.

## Naming Convention
For multi-frame campaigns, use descriptive suffixes:
- `<CampaignName>-Frame<N>-<DistinguishingFeature>.<ext>`

Examples:
- `Seen-Felt-Frame1-MaroonDoor.jpg`
- `Seen-Felt-Frame2-BlueDoor.jpg`
- `Seen-Felt-Frame3-FullThread.jpg`

## Split-Composition Ad Analysis

Split-composition ads (e.g., iMessage screenshot + product photo side-by-side) require capturing both narrative elements:

### Vision Prompt Pattern
```
Split composition social ad: left shows [message context] with [text overlay].
Right shows [product description] in [setting].
Brand tagline [tagline text]. Part of [campaign name] campaign.
```

### Key Fields to Capture
- **content_type**: "Ad Creative" (not "Social Media Post" or "UGC")
- **visual_tags**: Include layout descriptors like "split-composition", "imessage", "screenshot"
- **mood_tone**: Campaign emotional intent (e.g., "empathetic", "comforting", "warm")
- **setting**: Delivery/purchase context (e.g., "doorstep", "home interior")

### Campaign Organization
Create campaign-specific subfolder:
```
Ad Creative/
  └── <CampaignName> Campaign/
      ├── Frame1.jpg
      ├── Frame2.jpg
      └── Frame3.jpg
```

## Fig & Bloom Specific Patterns

### Product Identification
When analyzing bouquets, look for:
- **Specific varieties**: roses, hydrangea, statice, lisianthus, ranunculus, eucalyptus
- **Arrangement style**: white paper wrap + black ribbon (standard Fig & Bloom packaging)
- **Brand elements**: "FOR MOMENT MAKERS" tagline, logo placement

### Emotional Context
Fig & Bloom ads often pair:
- Digital communication (iMessage, email) with physical delivery
- Emotional triggers (sympathy, celebration, apology) with product imagery
- "Seen. Felt." campaign structure: message context → delivery moment

### Drive Folder ID
Ad Creative folder: `11fUAxgDGaEu0ovBbOIhkVAmo-Ksghocd`
