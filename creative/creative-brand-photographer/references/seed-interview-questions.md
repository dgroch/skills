### Interview Questions by Category

Each category has REQUIRED and OPTIONAL questions. Ask required
questions. Only ask optional questions if the answer isn't obvious
from the image itself.

#### Logo

Required:
- Which logo variant? (primary wordmark / secondary / monogram / sticker / favicon)
- Black or white? (or describe if neither)

Auto-filled by the skill:
- `format`: detected from file extension
- `background`: "transparent" if PNG with alpha, otherwise describe
- `use_for`: always ["overlay", "composite"]
- `never_use_for`: always ["style-reference"]

#### Bouquet

Required:
- What flowers are in this bouquet? (list the main varieties)

Optional (ask only if not obvious from image):
- What season? (spring/summer/autumn/winter/all-season)
- How would you describe the colour story in 3–4 words?

Auto-filled by the skill:
- `subcategory`: "wrapped" if tissue/ribbon visible, "arranged" if in vase, "loose" if no wrapping
- `tags`: derived from what's visible (ribbon, tissue, scale)
- `pairs_with`: default ["model-*"] for wrapped bouquets
- `use_for`: ["composite", "style-reference", "product-shot"]

#### Model

Required:
- Where is this photo from? (e.g. "Viktoria & Woods AW26 lookbook", "brand shoot March 2025")
- What season/collection? (so we can pair with right bouquets)

Optional (ask only if not obvious from image):
- What are the main outfit colours?

Auto-filled by the skill:
- `subcategory`: "fashion-editorial" (default for styled model shots)
- `tags`: derived from what's visible (framing, backdrop, gaze direction)
- `pairs_with`: default ["bouquet-*"]
- `use_for`: ["composite"]

#### Packaging

Required: none (the skill can see what it is)

Optional:
- Any specific name for this packaging element? (e.g. "the autumn box", "limited edition ribbon")

Auto-filled by the skill:
- `subcategory`: detected (tissue/ribbon/box/sticker/card/insert)
- `description`: written from what's visible
- `tags`: derived from content
- `use_for`: ["composite", "style-reference"]

#### Space

Required:
- What is this space? (store/warehouse/studio/workbench)
- Any name or location? (e.g. "Melbourne studio", "Collingwood warehouse")

Auto-filled by the skill:
- Everything else derived from the image

#### Lifestyle

Required:
- What type of scene? (tablescape/interior/doorstep/bedside)

Auto-filled by the skill:
- Everything else derived from the image

#### Product (non-floral)

Required:
- What is this product? (candle/card/styling kit/tea etc)
- Product name if it has one?

Auto-filled by the skill:
- Everything else derived from the image

### ID Generation

The skill generates IDs automatically using this pattern:

```
<category>-<descriptor>-<3-digit-sequence>
```

Examples:
- `bouquet-orchid-amber-001`
- `model-vw-autumn-cream-001`
- `logo-primary-black`
- `packaging-ribbon-detail-001`
- `space-melbourne-studio-001`

The descriptor is derived from the image content or user's answers.
Sequence numbers are auto-incremented within each category.

### Workflow: Auditing the Seed Library

When the user asks "what seeds do I have" or "what's missing":

**Report the current state:**

> **Fig & Bloom — Seed Library Status**
>
> | Category  | Count | Minimum | Status    |
> |-----------|-------|---------|-----------|
> | Logo      | 3     | 2       | ✓ Ready   |
> | Bouquet   | 2     | 5       | ✗ Need 3+ |
> | Packaging | 1     | 3       | ✗ Need 2+ |
> | Model     | 0     | 3       | ✗ Need 3+ |
> | Space     | 0     | 0       | Optional  |
> | Lifestyle | 0     | 0       | Optional  |
> | Product   | 0     | 0       | Optional  |
>
> **Modes available:** A (text-to-image) only.
> **To unlock Mode B (composite):** Add 3+ model seeds and 3+ more bouquet seeds.
> **To unlock Mode C (style-ref):** Add 3+ more bouquet seeds.
>
> **Gathering priority:**
> 1. Bouquet photos (3 more needed — different seasons/colour stories)
> 2. Packaging detail shots (2 more needed)
> 3. Model references (3 needed — source from current V&W collection)

### Workflow: Updating Existing Seeds

When the user asks to update or reclassify:

1. List the affected entries with their current metadata
2. Ask what needs to change
3. Show the updated JSON entry for confirmation
4. Write to the active backend (`seeds.json` in file mode; the seed row in Notion mode)

### Workflow: Removing Seeds

When the user asks to remove:

1. Confirm: "Remove `bouquet-orchid-amber-001` from the active seed registry? The local file stays on disk — this just deregisters it from the skill."
2. On confirmation, remove the entry from the active backend (`seeds.json` or the Notion seed row)
3. Report updated mode availability
