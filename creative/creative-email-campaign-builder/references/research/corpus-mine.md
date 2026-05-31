# Right Hook Email Corpus — Mine & Findings

Analysis of the **Fig & Bloom Right Hook Email Design Corpus** (Notion DB
`Right Hook Email Design Corpus DB`, data source
`collection://35ffdc24-425f-8132-af59-000bcf50f921`). This is the "214 email
mine": ingest the real send history, quantify what the designs actually do, and
feed the findings back into this skill so generated emails match the house style
*and* vary without feeling same-y.

Machine-readable tables live alongside this file in **`freq.json`**.

---

## Method

**Enumeration (metadata mine — all rows).**
The Notion MCP available in this environment exposes only `fetch` and
(semantic) `search` — there is **no bulk query / row-count / SQL tool**, and no
Notion API token is present in the environment. So the full row set was
harvested by running ~30 saturating semantic searches scoped to the data
source, unioning and de-duplicating the returned page IDs until new queries
stopped yielding new rows. That produced **212 unique rows** (the DB is stated
as "~214"; the last ~2 could not be surfaced semantically — 98.6% coverage).
Every one of the 212 pages was then fetched individually for its authoritative
properties (Name, Campaign, Subject, Preview, MIME, CDN URL, dimensions where
present).

**Visual mine (stratified sample).**
The renders are single 600px-wide columns but extremely tall (median ~5,000px),
so 212 full pixel reads are not tractable. A **stratified sample of 41 emails**
was drawn to span both MIME types (PNG/GIF) and every campaign type, downloaded
from the brand CDN, and analysed two ways (later **widened to 157 unique emails
/ 74%** for the block-taxonomy review — see *Expanded visual review* below):
- **Dimensions + animation** parsed directly from file headers (PNG `IHDR`;
  GIF logical-screen descriptor + frame/`0x2C` count) — no PIL/ImageMagick
  needed.
- **Layout / colour / type / illustration / above-the-fold** classified from
  two **Chromium-rendered contact sheets** (a top-700px "above-fold" grid and a
  deeper thumbnail grid).

Frequencies from the visual sample are labelled as estimates; the metadata
figures (count, MIME, taxonomy, subject/preview) are exact over all 212 rows.

---

## Metadata findings (n = 212)

### MIME / animated-GIF prevalence
| MIME | n | % |
|---|---|---|
| `image/png` (static) | 146 | 68.9% |
| `image/gif` (animated) | 66 | **31.1%** |

**Every** sampled GIF (20/20) was genuinely multi-frame (2–18 frames) — so
`image/gif` reliably means *animated hero*, and roughly **one email in three
ships one**. This is a first-class capability the corpus depends on, and the
single biggest gap in the current skill (which slices static PNG only).

### Dimensions
- **Width is locked at 600px** (40/41 sampled = 600; one 599 rounding artefact).
- **Height (sample): min 2,395 · median 4,984 · mean 5,058 · max 7,440 px.**
  27/41 are >4,500px. These are long vertical scrolls — the **above-the-fold
  window is only the top ~700px**, a small fraction of the whole.

### Campaign-type taxonomy (parsed from Name)
| Type | n | % |
|---|---|---|
| newsletter / editorial | 54 | 25.5% |
| promo (sale / BF / giveaway / free-ship / rewards) | 35 | 16.5% |
| launch / new-product | 18 | 8.5% |
| welcome | 13 | 6.1% |
| abandoned-cart (cart / checkout / browse / site) | 13 | 6.1% |
| occasion:Valentines | 10 | 4.7% |
| occasion:Xmas | 9 | 4.2% |
| post-purchase | 7 | 3.3% |
| occasion:Easter | 6 | 2.8% |
| winback | 5 | 2.4% |
| occasion:MD | 4 | 1.9% |
| occasion:FD | 2 | 0.9% |
| birthday | 2 | 0.9% |
| occasion:other (LNY / Halloween / IWD / Friendship / Kindness …) | 14 | 6.6% |
| other (rewards-tier / LTV / forms / apology / SMS) | 20 | 9.4% |

The corpus is **editorial-led**: the single largest bucket is content/editorial
sends (flower-of-the-month, care guides, founder stories, UGC), not hard promo.
That matters for variation — most sends are *story* moments, not *offer*
moments.

### Subject / preview patterns
- **Emoji in subject lines: 95.0%** (and 84.4% of rows carry an emoji somewhere).
  Emoji-leading subjects are effectively the house style.
- **Personalization: 24.5%** of rows use `{{ first_name|default:'…' }}` —
  **always with a default fallback** (e.g. `'friend'`, `'Moment Maker'`,
  `'Psst'`). Never a bare token.
- Avg subject **41.8 chars**, avg preview **43.3 chars** — short, punchy.
- 33 rows (15.6%) have no Subject — these are flow/SMS/form assets where the
  rendered design is the deliverable.

---

## Visual findings (stratified sample, n = 41)

### Recurring designed-block taxonomy
Share of sampled emails containing at least one instance (rounded; not mutually
exclusive). "Built" = already a component in `references/templates/`.

| Block | freq | built? | notes |
|---|---|---|---|
| header (logo) | 100% | ✓ | centred wordmark, universal |
| photo/type **hero** | 95% | ✓ | maps to `editorial-hero` / `hero-*` / `caption-bar-hero` |
| **editorial-hero** | ~62% | ✓ | photo + Lust headline + Cervanttis accent + button on overlapping plate |
| **designed-product-card** | ~48% | ✓ | product spotlight with designed name/price/occasion + optional badge (bestseller/scarcity) — richer than plain `card-*` |
| **caption-bar-hero** | ~40% | ✓ | full-bleed photo with a thin caption / super-label bar; common editorial & occasion opener |
| testimonial / review | ~30% | ✓ | stars + quote |
| **polaroid-collage** | ~24% | ✓ | tilted overlapping photos + pull-quote (UGC / reviews / multi-occasion) |
| **feature-list** | ~22% | ✓ | polaroid + reasons-to-believe bullets |
| **story block** | ~18% | ✓ | founder/editorial: portrait + narrative + signature (Dan & Kellie / Penny) |
| **offer-panel** | ~17% | ✓ | bold display %-off + dashed code + rotated sticker; promo/sale/free-ship/rewards + giveaway mode |
| **howto-steps** | ~6% | ✓ | vertical numbered 3-step how-to / care sequence, one photo per step |
| **comparison-vs** | ~2% | ✓ | side-by-side us-vs-them / before-after with central "vs" badge |
| trust-bar | ~90% | ✓ | |
| footer | 100% | ✓ | |

**Taxonomy verdict.** The mine **confirms the proposed 6-type designed-block
taxonomy**, all six built (editorial-hero, feature-list, polaroid-collage,
caption-bar-hero, story, designed-product-card). The **7th block — a designed
offer/promo panel** (`blocks/offer-panel`) — is also built: promo is the
second-largest bucket (16.5%) and those panels are visually distinct (huge Lust
offer value + dashed code box + rotated sticker). The expanded 74% review (below)
then surfaced two more on-system blocks, both now built: **`howto-steps`** (8th,
~6%) and **`comparison-vs`** (9th, ~2%) — bringing the library to **nine
designed-block types**.

### Expanded visual review (74% of the corpus)

After the initial 41-image stratified pass, the review was widened to **157
unique emails (74%)** — deduped by content hash across a second 116-email pass —
specifically to confirm the offer-panel and to check for any *new* candidate
blocks. Findings:

- **`offer-panel` (7th) — confirmed and built.** Recurs across every
  sale / Black Friday / flash / free-shipping / rewards send (~17%). Giveaways
  are *not* a separate block — they're the offer-panel in **GIVEAWAY MODE**
  (no code; prize in the offer value).
- **`howto-steps` (8th) — built.** A *vertical* numbered how-to / care
  sequence with an image per step (refresh, dry, make-last, eucalyptus,
  arranging, home-spots), ~6%. Genuinely distinct from the existing horizontal
  `three-column-steps-*` (a compact partner-flow) and from `feature-list` (RTB
  bullets beside one polaroid).
- **`comparison-vs` (9th) — built.** Side-by-side us-vs-them / bought-vs-got /
  before-after with a central "vs" badge, ~2%. Low-frequency but on-system.

No other new block types surfaced across all 157 — the house vocabulary is
stable and on-system. All three reviewed candidates (offer-panel, howto-steps,
comparison-vs) are now built, for **nine designed-block types** total.

### On-brand consistency (confirmed from pixels)
- **Palette:** monochrome **Noir #000 / White / Clay #D8CCBE** dominates every
  send; seasonal accent colour appears only in ~15–20% of emails (occasion &
  promo) and only as panel/accent — exactly the locked rule. Outer gutter is
  the **#2c2825** body background.
- **Type:** **Lust** sentence-case display + **Cervanttis** lowercase script
  accents + **Neuzeit Grotesk** sans body, consistently.
- **Buttons:** **square black** (never pills) — confirmed.
- **Illustration:** faint brand botanical **line-art** as low-opacity section
  accents — present and subtle, matching `design-system.md`.

### Animated GIF heroes — what they animate
- ~31% of the corpus. Three patterns: **reveal mechanics** (flower-of-the-month
  / product reveals, 2–4 frames), **UGC / review photo carousels** (8–18
  frames), and **sale / urgency flashes** (4–5 frames). The GIF is always the
  hero (top of email).

### Above-the-fold CTA
With median height ~5,000px and a logo-header → photo/type-hero opening, the
**primary CTA lands below the ~700px fold in the majority of emails** (sample
estimate: ≈⅓ have a button above the fold). A skimmer often can't click without
scrolling. This is the clearest actionable gap and drives the new layout rule +
pre-flight check below.

---

## What this changes in the skill

The mine maps directly onto the five requirements:

1. **Variation without visual repetition** — nine designed-block types + a
   rotation scheme (see `manifest.json → variation_rules`) so consecutive sends
   don't repeat the same opening/affirm/close beats.
2. **On-brand consistency** — every variation stays inside the locked
   Noir/Clay/White + Lust/Cervanttis/Neuzeit + square-black-button system;
   accent colour only where the corpus uses it (occasion/promo).
3. **Parametrised components** — each designed block exposes `palette`,
   `layout`, and `illustration` token variants so variations are generatable,
   not bespoke.
4. **Procedural image-creation workflows** — documented per block in SKILL.md
   Step 5, including the **animated-GIF hero** produce/slice path.
5. **Animated GIF hero** — promoted to a first-class slice path (the slicer now
   emits a GIF when the source/flag is animated, instead of a static PNG).
6. **CTA above the fold** — a layout rule (primary CTA within the first ~700px)
   plus a Step 6 pre-flight validation check.

See `freq.json` for the machine-readable tables these decisions are based on.
