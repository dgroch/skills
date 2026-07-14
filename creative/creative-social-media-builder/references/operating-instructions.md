# Fig & Bloom Social Builder — Operating Instructions

Project instructions for generating social posts (carousels and single cards) via the **hosted social builder**. Two layers: the **grid layer** (how screens of 9 are sequenced) and the **post layer** (how each tile is produced). This captures how to get the result first time — the judgment layer that sits on top of this skill's `SKILL.md`, not a replacement for it.

- **Builder:** `my-social-builder.onrender.com` (JSON-first API)
- **Skill:** `creative-social-media-builder` in `dgroch/skills` (main branch)

---

## Invocation contract — the screen is the unit of work

The deliverable is a **cohesive screen of 9**, not a pile of single assets. Every invocation resolves to one of three modes, in this order of preference:

### Mode A — Screen (default)

Canonical invocation:

> "Plan the next screen — 9 tiles, following the grid system. Here's what's ready: [reflexed roses content, quiet arts #2, …]"

Input: the list of ready content — sources, campaigns, assets, themes. Output, in order:

1. The 9-tile plan as three rows against the composition maps below (tile class, slot, ground, source asset per tile).
2. Builder payloads and copy for every type-led card and callout; deliberate photo picks for every silent tile.
3. All 9 tiles rendered and inspected per the core operating loop.
4. The contact sheet (3×3, square-cropped covers) for review — the approval artifact.
5. The posting order (reverse row order) once approved.

If the supplied content can't fill 9 slots, fill the remaining **silent** slots from the asset library / evergreen pool — never deliver a partial screen. If the content overfills, hold the surplus for the next screen and say so.

### Mode B — Row (3 tiles) — requires grid state

A row can be produced alone (completing a screen in progress, absorbing a reactive post), but a row is only plannable against **what it will sit above** — adjacency, tone, and spine continuity all depend on the current top of the grid. Acquire grid state in this order:

1. **User-supplied screenshot** of the current grid (top row minimum; top two rows preferred). This is the reliable path — ask for it when it isn't offered.
2. **Browser screenshot** — `node references/scripts/grid-snapshot.js --handle <handle> --output /tmp/grid.png` drives headless Chromium (the `puppeteer` skill is already a dependency) to the public profile and screenshots the grid. Best-effort only: Instagram frequently login-walls logged-out views. The script detects the wall and reports `gated: true` in its `__GRID_MANIFEST__` block — when gated, treat grid state as unknown and fall back to asking for a screenshot. Never attempt to log in or bypass the wall.
3. **No grid state → no row.** Do not plan a row blind. Either escalate to a full screen (Mode A, which is self-contained) or wait for the screenshot.

With grid state in hand, read the top row for: which column carries the spine card nearest the top, the ground of the last spine card (to alternate), dark-tile positions (adjacency), and the scale mix of the adjacent row. Then plan the new row of 3 against the placement and rhythm rules.

### Mode C — Single tile (constrained)

Single tiles are produced only as (a) a fill for a named slot in an already-approved screen plan, or (b) evergreen silent padding for the queue. A bare one-off request ("make a quote card") is fine to render, but deliver it with its grid constraints stated — centre column only, non-consecutive rows, row-mates silent — and do not schedule it outside a row or screen plan.

---

## The grid layer — the editorial spine

Batches are planned in **screens of 9** before any tile is produced. This section governs where tiles go and what mix a screen carries; everything below it governs how each tile is made. Applies **below the pinned journal row** — that strip is fixed.

### First principles

- Photography is the grid; designed type is punctuation. The grid reads as considered when quiet outnumbers voice.
- The grid only ever sees **cover frames**. Reel, carousel, static — format is invisible. These rules govern covers, not formats.
- Plan in rows of 3 and screens of 9, **never in tile intervals** ("every 7th tile") — intervals drift across columns and eventually collide.
- Silence is the scarce resource. Type earns attention only because most tiles carry none.

### Tile classes — split by which element leads

1. **Type-led** — builder cards where type is the tile: `card-quote-lineart`, `card-statement-split`, `card-statement-bars`, `card-note`. The spine.
2. **Photo-led with callout** — photography carrying designed copy: journal covers, `story-overlay`, captioned cards, reel covers with type. The luminance rule (below) applies to every one.
3. **Silent photography** — a clean image or reel cover, no type. The base layer.

### Column roles

- **Centre column — voice.** Type-led cards live here and only here. Default spine down the column: card / silent photo / card. The row-2 centre slot stays silent — it is the breath between the cards.
- **Outer columns — craft.** Photography and photo-led callouts only. Type-led cards never touch the outer columns.

### Screen composition (per 9)

Default screen — two cards:

```
silent        TYPE-LED      silent
callout?      silent        callout?
silent        TYPE-LED      silent
```

Reel-heavy screen — one card:

```
silent        TYPE-LED      silent
callout?      silent        callout?
silent        callout?      silent
```

Counts that fall out: **type-led 1–2** (two is the default) · **callouts ≤2** on a two-card screen, **≤3** on a one-card screen · **silent ≥4** — the four card-flankers at minimum.

### Placement rules

- A type-led card's row-mates are silent — the card owns its row's voice.
- Type-led cards never sit in consecutive rows.
- No two type-carrying tiles (card or callout) **orthogonally adjacent** — sharing an edge. Diagonal contact is fine; diagonals read as separation on the grid.
- The two cards per screen alternate roles — one **voice** (quote / statement), one **commerce** (launch card / journal cover) — and alternate grounds down the spine: light, clay, light…

### Photography rhythm

- **Scale:** every photo row mixes distances — one detail, one mid, one full. Never three of the same.
- **Tone:** max one dark tile per row; no two dark tiles adjacent in any direction.
- **Colour:** warm-neutral base; at most one saturated moment per row.
- **Story test:** every image reads as floristry and craft — bouquet, bench, delivery, detail of an arrangement. Catalogue shots (a lone houseplant, bare product-on-white) fail even when technically on-palette.

### Reels & carousels

- A reel enters the grid plan only with a **qualifying cover**: composed, graded, no burned-in captions or UI text. No qualifying cover → design one in the builder before it is scheduled.
- A carousel is judged by its **cover slide**, like any other tile of its class.

### Planning & posting workflow

1. Plan the screen of 9 as three rows against the maps above.
2. Assemble a **contact sheet** — square-crop every cover, lay out 3×3 — and look. Never approve a batch from a list. Check: column roles, counts, adjacency, scale/tone/colour per row, luminance on every callout, spine grounds alternating.
3. Post in **reverse row order** — Instagram fills newest-leftmost.
4. Keep **two evergreen silent tiles** rendered and queued as padding, so an unplanned reel or reactive post completes a row instead of breaking the spine.

---

## Core operating loop (per tile)

Treat every step as a gate. Do not skip ahead, do not improvise HTML.

1. **Schema** — `GET /api/schema`. Always fetch first. It is versioned; read the version and the current design/slide/token/lever spec. Things move (the `font` lever arrived in v3.3.0) — never assume last session's shape still holds.
2. **Library** — `GET /api/library`. Copy a preset row verbatim for the slide you want, then fill only the copy tokens. Presets are the known-good baseline.
3. **Validate** — `POST /api/validate` with `{post:{...}}`. Clear every error before rendering.
4. **Render** — `POST /api/render`, same `{post:{...}}` shape. Returns `{slices:[{index, slide, pngBase64, w, h, overflow, failedAssets}]}`.
5. **Inspect** — decode the PNGs and actually look. Green validation is necessary, not sufficient — legibility and whitespace are eyeball calls.

### Payload shape — the gotchas

- **One tokens bag per slide.** Content tokens and levers (`theme`, `surface`, `font`) all live inside `slides[n].tokens`. There is **no separate `levers` key**. This trips people up every time.
- **`{post:{...}}` wrapper** on both validate and render. Not the bare object.
- Check `overflow` and `failedAssets` on **every slice**, not just the HTTP 200.

### Levers & fonts

- `font` (interior slides):
  - `editorial` → Lust pills + Neuzeit Grotesk body. **This is the house look — default to it.**
  - `script` → Neuzeit pills + Cervanttis body. Older default; only when the softer signature feel is wanted.
- **Cervanttis always renders lowercase.** Any script set in title/sentence case is wrong — force lowercase in the copy.
- Fonts in play: Lust (serif), Neuzeit Grotesk (sans), Cervanttis (script).

---

## Photo & caption legibility (where it breaks)

The single biggest source of rework. Caption ink must follow the **actual luminance of the band it sits on**:

- White ink over dark or mid-tone bands.
- Dark ink over light bands.
- A band must be **shadow-free and uniform** — "nominally light" is not enough. Dark script crossing a shadow, or dark ink on a mid-tone wall, will be rejected.

**Fallback ladder** when a clean caption band doesn't exist — climb it in order, stop as soon as it reads:

1. Anchor the caption to an existing clean band in the shot.
2. Reframe via `PHOTO_POS` to bring clean negative space under the text.
3. Serif-box or scrim behind the text.
4. Outpaint to manufacture negative space (Higgsfield Nano Banana 2 Edit) — last resort. Needs the full-res original via Drive File ID, not the manifest preview URL. Save the result back to R2 and log it as a new manifest row.

---

## The 4:5 overflow gate

- Feed posts render at 1080×1350 (4:5) and Stories at 1080×1920.
- The 4:5 crop is where text overflow and photo-template failures hide. Photo templates (captioned, feature card, poll) and long-form are the high-risk ones.
- Render **both ratios**, confirm `overflow: false` on all slices before calling it done.

---

## Asset sourcing (owned-first)

- Semantic asset library: `https://asset-library-u70t.onrender.com/api/search?q=<url-encoded>&limit=8`.
- Asset manifest (Notion): DB `357fdc24-425f-81a2-8785-000b04ce37e3` — real image URLs live here.
- CDN: `brand-cdn.figandbloom.workers.dev`. The CDN 403s Python's urllib — fetch with `curl -s`. (Higgsfield `media_import_url` handles its own requests, so pass CDN URLs to it directly.)
- Ground the cover in a **specific, real image** — the hero from the source blog/product, chosen deliberately. Don't let the builder pick a generic plate.

---

## Brand voice guardrails (non-negotiable)

- No exclamation marks. Australian English. Flower names lowercase in prose.
- Banned words: blooms, gorgeous, stunning, luxury, exquisite, elevate, curate.
- Palette: warm clay (`#D8CCBE`), plum, lilac.
- Tone: a florist is a designer, not a dispatcher. Restraint is the point.

---

## Corrections log — lessons paid for in iteration

Things that had to be fixed last time. Do them right the first time:

- Cover was too generic → use the specific source hero image.
- Too much whitespace on intro slides → raise body-copy density; the intro slide especially reads thin at default.
- Script in wrong case → Cervanttis lowercase, always.
- Wrong font pairing shipped → default interior to `editorial` (Lust + Neuzeit), not `script`.
- Caption lost on a busy band → apply the luminance rule and the fallback ladder **before** rendering, not after.
- Detail tile read as plant catalogue → run the story test: every image reads as floristry and craft, not product-on-white.

---

## Definition of done

**Per tile:**

- Validation green on both ratios: correct dimensions, `overflow: false`, no `failedAssets`.
- Every caption passes the luminance rule by eye.
- Copy passes brand voice (no banned words, no exclamation marks, lowercase flowers, Cervanttis lowercase).
- Cover is a deliberate, specific image — not a default pick.

**Per screen (grid layer):**

- Type-led cards: correct count, centre column, non-consecutive rows, roles and grounds alternating.
- Callout count and adjacency clean; every callout passes the luminance rule by eye.
- ≥4 silent tiles; every photo passes the story test; scale, tone and colour rhythm hold per row.
- Contact sheet reviewed at full size before the first post is scheduled.

---

## Working style

Act decisively. Make the strong creative call and flag the decision rather than asking for pre-approval on every step. Surface the two or three genuine forks; drive the rest.
