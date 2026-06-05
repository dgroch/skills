---
name: creative-design-discipline
description: >
  Think and work like a graphic designer when composing ANY visual creative —
  static ads, carousels, social posts, stories, banners, slide layouts, posters,
  email headers, thumbnails. Apply this whenever image, type, and brand elements
  are being arranged on a canvas, especially when spacing, proportion, hierarchy,
  or "it looks off / amateur" are in play. Use it even when not explicitly asked
  to "design" — any layout task counts. This is the craft layer; it sits on top
  of a brand's own guide (which supplies fonts, palette, logo, voice) and never
  overrides brand rules, but its discipline (grid, critique loop) always holds.
version: 1.0.0
author: Dan Groch
license: MIT
metadata:
  tags: [Creative, Design, Layout, Grid, Composition, Type, Brand]
  related_skills: [creative-brand-guidelines-manager, creative-brand-photographer, creative-add-creative-builder]
---

# Design Discipline

A layout is *designed* when every element sits on a system and earns its place.
It looks amateur when elements are placed by eye and shipped without looking.
This skill encodes the system and the looking.

## Operating principle

**System before elements. Never draft blind.**
Define the grid, margins, type scale and spacing rhythm *before* placing a single
element, then size and position everything relative to that system — not by
guessing coordinates. Then render at full size and critique against it before
showing anyone.

## 1. Build medium — relational, not pixel-stamped

Lay out in **HTML/CSS** (flex/grid, `rem`/`%`, `line-height`, `aspect-ratio`),
rendered to image via headless browser. Proportions become *relationships* that
hold across ratios. Avoid hand-placing elements with absolute pixel coordinates
in raster tools — that is the single biggest cause of drift and "wrong"
proportion. If a raster tool must be used, still derive every value from the
system below; never type a magic number.

## 2. The grid & margins (defaults — override only with a brand system)

- **Outer margin:** ~8% of the short edge, equal on all four sides. (1080px wide → **88px**.)
- **Columns:** 6, with a **24px** gutter. Align every edge to a column.
- Content lives inside the margin box. Full-bleed imagery may cross it; *type and logos never do.*

## 3. Type scale — modular, restrained

- Pick **one ratio** (default **1.5**) and build a small set of steps. Don't freestyle sizes.
- **Max 2–3 sizes per view.** Hierarchy comes from scale + weight + space, not from many sizes.
- A display headline may take a deliberate jump *above* the scale to own its space — that's allowed; ten slightly-different sizes are not.
- Example steps for a 1080-wide frame: kicker 26 · dek 34 · subhead 52 · **display 96–160** (size to the line count and the space it must fill).

## 4. Spacing rhythm

- All spacing from an **8px scale**: 8 / 16 / 24 / 40 / 64 / 96.
- **Proximity = relationship.** Related items sit close; unrelated items get real space. Even gaps between unrelated blocks read as accidental.
- Vertical rhythm should feel intentional top-to-bottom — no orphan gaps.

## 5. Hierarchy & focal point

- **Exactly one focal element per view.** Everything else is quieter by design.
- Secondary elements must never out-shout the message. A **logo is support, not the hero** — if it's the loudest thing on a cover, it's wrong.
- Lead the eye: entry (headline/focal) → support → exit (CTA/sign-off).

## 6. Proportion & negative space

- Negative space is composed, not leftover. If there's a gap, it should look *chosen*.
- Decide the image-to-type proportion deliberately (e.g. headline owns the top third, image the middle, footer the bottom band). State it before building.
- A timid headline floating in a big empty area is a proportion failure — either size it to own the space or move it to relate to the subject.

## 7. Alignment & optical adjustment

- Everything aligns to the grid. Left edges of kicker, headline, body and footer share a margin.
- Prefer **optical** alignment over mathematical when they disagree (large type, round shapes, punctuation hang).
- One alignment logic per view — don't mix centred and left-aligned without reason.

## 8. Safe zones (platform chrome)

- **Stories / Reels (9:16):** keep critical content and CTAs out of the **top ~14%** and **bottom ~20%** (UI overlays).
- **Feed (4:5, 1:1):** keep a **~8%** top/bottom buffer so nothing is jammed to the edge.
- Nothing important — never the logo or CTA — sits in a chrome band.

## 9. Logo & brand-mark discipline

- Respect clearance space; **cap size** (e.g. ≤ ~26% of frame width) so it supports, not dominates.
- **Never** crop, bleed off the edge, recolour, stretch, rotate, or add effects. Black or white only. Use master files; don't typeset the wordmark.
- Choose the right lockup for the space (horizontal vs stacked vs monogram) — don't force a tall lockup into a thin band.

## 10. Restraint

- Limited sizes, limited weights, disciplined colour. "Premium and considered," not loud.
- Let the **brand guide** supply fonts, palette, logo files and voice. This skill governs *how they're arranged*, and defers to brand rules — except the discipline here (grid, critique loop) always applies.

## 11. The critique loop — *the anti-regression mechanism*

Producing the file is step one, not the finish. Before showing anyone:

1. **Render at 100%** (full resolution). **Never approve from a thumbnail or contact sheet** — small previews hide proportion and spacing errors. (This is exactly how a too-big logo or a floating headline slips through.)
2. **Zoom into each region** — corners, edges, the footer, where type meets image.
3. **Run the QA checklist** (§12). Diagnose like a critic, naming specific faults.
4. **Iterate at least twice.** First render is a draft. Fix, re-render, re-check.

## 12. Pre-ship QA checklist

- [ ] Outer margins equal on all four sides (measure — don't eyeball).
- [ ] Exactly one clear focal point; secondary elements quieter.
- [ ] Logo within its size cap and clearance; not cropped, not bleeding; black/white only; correct lockup.
- [ ] All type sits on the grid; shared left/right margins.
- [ ] ≤ 3 type sizes, all from the scale.
- [ ] Spacing uses the rhythm tokens; gaps look intentional (proximity reflects relationship).
- [ ] Negative space is composed — no accidental dead zones.
- [ ] Critical content and CTA clear of platform safe zones.
- [ ] Nothing clipped at the edges.
- [ ] Checked at full size, not a thumbnail.

## Sensible defaults by format (1080 base)

| Format | Size | Margin | Headline | Safe zone |
|---|---|---|---|---|
| Story/Reel 9:16 | 1080×1920 | 88 | 120–160 | top 14% / bottom 20% |
| Feed 4:5 | 1080×1350 | 88 | 104–140 | ~8% top & bottom |
| Square 1:1 | 1080×1080 | 80 | 96–128 | ~8% top & bottom |
| Landscape 16:9 | 1200×675 | 72 | 72–104 | minimal |

---

*How to use this:* pair it with the brand brief/guide — that supplies the *what*
(fonts, palette, logo, voice); this supplies the *how* (composition). When the two
ever conflict, brand quality wins on taste; the grid-and-critique discipline
holds regardless.
