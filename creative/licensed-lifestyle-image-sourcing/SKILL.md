---
name: licensed-lifestyle-image-sourcing
description: Source licensed lifestyle/supporting imagery via official Pexels and Unsplash APIs as the second step after owned Fig & Bloom assets, before generated brand photography. Use for editorial context images in blogs, emails, social, and design comps — not for pretending stock florals are Fig & Bloom products.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [fig-bloom, imagery, stock-photos, pexels, unsplash, licensing, lifestyle]
    related_skills: [blog-production-loop, creative-brand-photographer, devops-brand-cdn, photography-ugc-review]
required_environment_variables:
  - PEXELS_API_KEY
  - UNSPLASH_ACCESS_KEY
---

# Licensed Lifestyle Image Sourcing

Use this skill when a project needs **context/lifestyle imagery** and the owned
Fig & Bloom asset library cannot provide the right scene in time.

This is a fallback workflow, not a replacement for Fig & Bloom imagery.

## Source priority

1. **Owned Fig & Bloom asset library**
   - Search `https://asset-library-u70t.onrender.com/api/search?q={scene}&limit=8`.
   - Prefer real Fig & Bloom product, studio, delivery, process, card, table,
     home, hands, and UGC assets.
2. **Licensed lifestyle fallback** using official APIs only:
   - Pexels API: `https://api.pexels.com/v1/search`
   - Unsplash API: `https://api.unsplash.com/search/photos`
3. **Generated brand photography**
   - Use `creative-brand-photographer` / Higgsfield when the scene must look
     like Fig & Bloom and neither owned nor licensed lifestyle imagery fits.

Do **not** scrape provider websites or reverse-engineer private web APIs. Use
the documented APIs, preserve source metadata, and follow the provider licence.

## Allowed vs disallowed stock roles

Allowed:

- warm home interior
- winter table or candlelight
- bedside / recovery context
- hand-written card or envelope
- delivery/arrival mood
- linen, timber, ceramic, negative space
- human-scale context where the flowers are not the product claim

Disallowed:

- stock bouquets used as if they were Fig & Bloom arrangements
- competitor-style florist product photography
- visible third-party branding
- obvious stock smiles / staged wellness clichés
- grief clichés, hospital clichés, melodrama
- over-bright, cool, glossy, or generic studio lifestyle
- any image whose details contradict the article copy

## Query strategy

Search by **scene**, not keyword stuffing.

Good queries:

- `warm winter table candle linen home interior vertical`
- `hand writing sympathy card neutral desk vertical`
- `bedside table get well card flowers soft morning vertical`
- `ceramic vase linen table soft window light vertical`

Poor queries:

- `flowers`
- `birthday bouquet`
- `sympathy flowers`
- `luxury florist arrangement`

Add provider parameters that bias toward portrait/lifestyle:

- Pexels: `orientation=portrait`, `per_page=12`
- Unsplash: `orientation=portrait`, `per_page=12`, `content_filter=high`

## Selection criteria

For every candidate, score quickly:

- **Licence/source clear:** provider, photo ID, photographer, source URL,
  download URL where required.
- **Role fit:** mood/context/supporting image, not product truth.
- **Brand fit:** warm, slightly desaturated, tasteful, quiet, human scale.
- **Composition:** portrait crop works; enough negative space; no awkward crop.
- **Risk:** no fake Fig & Bloom product, no competitor branding, no clichés.
- **Pairability:** can form a 2-up vertical block with another image.

Reject any candidate that fails product-truth boundaries even if it is pretty.

## Output contract

Return candidates as JSON-ready objects:

```json
{
  "provider": "pexels|unsplash",
  "provider_id": "...",
  "photographer": "...",
  "source_url": "https://...",
  "image_url": "https://...",
  "download_tracking_url": "https://...",
  "licence_url": "https://...",
  "width": 0,
  "height": 0,
  "orientation": "portrait",
  "recommended_role": "hero|inline|2-up-left|2-up-right|background-reference",
  "alt_text": "Plain, descriptive alt text.",
  "selection_notes": "Why it fits and what risk was checked."
}
```

For Unsplash, trigger/download-track the provider `links.download_location`
when an image is selected, as required by Unsplash API guidelines.

## Blog image composition guidance

When used with `blog-production-loop`:

- Prefer a **2-up vertical lifestyle block** over repeated full-width images.
- Pair context + detail:
  - winter care: vase/table + hand/care/detail
  - get-well: bedside/home context + gentle card/detail
  - sympathy: negative-space interior + handwritten card/detail
  - birthday: warm table/gift context + candle/room/detail
- Keep product photography only in the Shopify product callout.
- Add captions that carry useful craft or emotional context.
- Record the image source metadata in the run report or upload manifest.

## API usage

Use the bundled helper script when available:

```bash
python scripts/search_lifestyle_images.py \
  --query "warm winter table candle linen home interior vertical" \
  --providers pexels,unsplash \
  --limit 8 \
  --out /tmp/lifestyle-candidates.json
```

Environment variables Daniel will provide:

- `PEXELS_API_KEY`
- `UNSPLASH_ACCESS_KEY`

If neither key is available, return a structured blocker and fall back to owned
assets or generated brand photography. Do not invent images or silently use
unlicensed web URLs.

## CDN handoff

If an image is selected for production and the licence permits mirroring:

1. Download the selected image.
2. Preserve provider metadata in a sidecar JSON manifest.
3. Upload through `devops-brand-cdn` / R2 with a stable path.
4. Embed the CDN URL in the final asset, not a hotlinked provider URL, unless
   the provider's terms or the project explicitly prefer hotlinking.
5. Keep photographer/source/licence metadata in the run report.

If licence or API terms are uncertain, do not mirror; use the provider URL and
source attribution metadata until reviewed.
