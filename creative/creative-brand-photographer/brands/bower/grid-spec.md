# Bower — Instagram Grid Specification

Extracted from: bower-art-direction.pdf → Grid Logic tab

---

## 9-Post Composition Pattern

The grid reads as a single warm colour story when viewed as a whole.
No single post should break the tonal consistency of the grid.

```
┌──────────────────┬──────────────────┬──────────────────┐
│  Product close-up │  Lifestyle wide  │  Texture detail  │
├──────────────────┼──────────────────┼──────────────────┤
│ Lifestyle doorstep│  Product hero    │  Packaging flat  │
├──────────────────┼──────────────────┼──────────────────┤
│  Texture petal   │  Lifestyle table │  Product full    │
└──────────────────┴──────────────────┴──────────────────┘
```

### Content Types (3 lanes)

| Type      | Description                                        |
|-----------|----------------------------------------------------|
| Product   | Hero shots, close-ups, full arrangements in vessel  |
| Lifestyle | Kitchen table, doorstep arrival, living room scenes |
| Detail    | Petal textures, packaging flat-lays, stem close-ups |

> **Note:** The 9-post grid above covers Instagram only. The
> `hero-editorial` shot type (see "Website-only lanes" below) is a
> separate lane for the homepage hero rotation. It does **not** sit
> within the Instagram grid and must not be slotted into any of the
> nine positions.

### Grid Rules

**Colour consistency:** Every image on the grid should share the same warm
colour grade. If a single image feels cooler or more saturated than its
neighbours, it breaks the whole grid. Batch-grade, never individually.

**Rhythm:** No more than 2 consecutive posts of the same type. The sequence
should feel like a considered editorial layout — product, lifestyle, detail,
repeat with variation.

**Text posts:** Rare. Maximum 1 per 12 posts. When used: Linen background,
Espresso text, Instrument Serif italic for the quote, Plus Jakarta Sans for
attribution. No coloured backgrounds for text posts.

**Reels cover frames:** Must be designed to sit harmoniously in the grid.
Extract a still frame from the reel that matches the brand colour grade, or
design a custom cover in the brand palette.

### Stories vs Feed

**Feed:** Curated, considered, slow. Every post earns its place. The feed
is the brand's portfolio — it should look like a single editorial spread.

**Stories:** Warmer, more spontaneous, behind-the-scenes energy. Studio prep,
arrangement close-ups, packing boxes. Can use Sandstone or Linen backgrounds
for text frames.

---

## Shot Types by Grid Position

### Product Lane (3 per 9-post cycle)

| Slot             | Shot type         | Aspect ratio | Notes                                    |
|------------------|-------------------|--------------|------------------------------------------|
| Product close-up | Tight crop        | 1:1          | Single flower or arrangement detail      |
| Product hero     | Full arrangement  | 4:5 (→3:4)  | Eye-level, linen surface, hero vase      |
| Product full     | Wide frame        | 4:5 (→3:4)  | Full arrangement with generous neg space |

### Lifestyle Lane (3 per 9-post cycle)

| Slot               | Shot type        | Aspect ratio | Notes                                  |
|--------------------|------------------|--------------|----------------------------------------|
| Lifestyle wide     | Scene-setting    | 4:5 (→3:4)  | Broader room context, person optional  |
| Lifestyle doorstep | Delivery moment  | 4:5 (→3:4)  | Box arriving, hands reaching           |
| Lifestyle table    | Kitchen/dining   | 4:5 (→3:4)  | Morning light, arrangement as centrepiece|

### Detail Lane (3 per 9-post cycle)

| Slot           | Shot type        | Aspect ratio | Notes                                    |
|----------------|------------------|--------------|------------------------------------------|
| Texture detail | Macro/close-up   | 1:1          | Petal texture, dewdrop, stem detail      |
| Packaging flat | Unboxing moment  | 4:5 (→3:4)  | Tissue reveal, box contents              |
| Texture petal  | Extreme close-up | 1:1          | Shallow DOF, single bloom               |

---

## Website-only lanes

These shot types are produced for the website and do **not** appear in
the 9-post Instagram rotation. They have their own art direction and
their own scoring criteria — keep them out of the grid plan.

### Hero Editorial (website hero, weekly rotation)

The homepage hero image rotates weekly with the current drop. The shot
is **editorial, not product** — the arrangement appears within a scene
rather than being the subject of it. See `art-direction.md` →
"Hero Editorial" for direction and `rubric.md` for scoring.

| Slot          | Shot type        | Aspect ratio              | Notes                                                                                  |
|---------------|------------------|---------------------------|----------------------------------------------------------------------------------------|
| Hero editorial | Scene with arrangement | 16:9 primary, 4:5 secondary | Desktop hero is 16:9; mobile crop is 4:5. Higgsfield 4:5 → 3:4 mapping constraint applies. |

**Why it's outside the grid:** The Instagram grid is curated for tonal
consistency across nine tiles. A hero-editorial shot is wider, more
atmospheric, and intentionally crops the arrangement off-centre or
partially out of frame — choices that would break grid rhythm if
slotted into a 1:1 or 3:4 feed tile.
