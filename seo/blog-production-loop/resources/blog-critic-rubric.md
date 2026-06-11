# Fig & Bloom — Blog Critic Rubric

**Purpose:** The scorecard a critic agent uses to gate every blog post produced by the
editorial loop. The critic reviews the **rendered Shopify draft** (screenshot + extracted
body), not the raw source. The maker agent never scores its own work.

**Sources of truth:** Parent Editorial Framework (May/June 2026), Guide System,
Journal — Magazine-Tier Editorial, `blog-internal-linking` skill,
`photography-ugc-review` skill.

**Version:** 1.0 | **Owner:** Dan | **Voice authority:** Parent framework wins on any conflict.

---

## 0. Identify the tier first

Every post is one of two tiers. Score against the right one — a Guide judged as a
Journal piece (or vice versa) is a wasted cycle.

| Tier | Job | Tell |
|---|---|---|
| **Guide** | Search + conversion. A tasteful friend helping someone make the right gesture. | Occasion/relationship/mood/situation/product-pathway framing; follows the six-part Guide structure |
| **Journal** | Brand + culture. Magazine-tier feature. | Real byline, reported content, commissioned photography leads, no funnel shape |

If the brief says Journal but the draft reads like a Guide, that is itself a fail
(see Gate J1).

---

## 1. Hard gates — instant REVISE, no scoring

Check these first. Any hit stops the review; return the gate ID and move on.
Mirrors the hard-reject scan in `photography-ugc-review`.

### Universal gates (both tiers)

- **G1 — Banned language.** Any of: *stunning, gorgeous, breathtaking, elevate,
  curate, blooms* (as a noun), *spoil them/yourself, beautiful blooms, freshly
  picked, handcrafted with love, florist-grade, professional quality, say it with
  flowers, one-stop shop, perfect for every occasion, cheap, affordable,
  budget-friendly, order now, don't miss out, we've got you covered*.
- **G2 — Not Australian English.** US spellings (*color, coziness*),
  Americanisms (*y'all, super cute, obsessed*), UK affectations (*rather lovely,
  just the ticket*).
- **G3 — Urgency or discount-led selling.** Countdown framing, anxiety urgency,
  percentage-off as the hook, more than one hard CTA.
- **G4 — Title duplicated as H2/H1 in the body.** The theme renders the title;
  repeating it is a known defect.
- **G5 — Broken render.** Missing/broken images, dead links, malformed HTML
  visible on the page, headings out of hierarchy.
- **G6 — Dishonest imagery.** Product callout image is not the real product;
  watermarks; competitor branding; visible AI artefacts (warped hands,
  impossible reflections, uncanny texture).
- **G7 — Product callout placed directly after a grief/sympathy passage.**
- **G8 — Literal scaffolding in copy.** A printed "CTA:", placeholder text,
  internal notes, or prompt residue anywhere on the page.

### Guide-only gates

- **G9 — Recommends a product that isn't a real, live Fig & Bloom design.**
  Callout must be verified in-stock on Shopify at publish time.

### Journal-only gates

- **J1 — Funnel shape present.** CTA blocks, awareness-stage routing, or more
  than a single quiet in-context product link.
- **J2 — No real byline, or "By Fig & Bloom".** Byline must be Daniel, Kellie,
  or a named contributor.
- **J3 — Missing craft minimums.** Fewer than: 1 named human who is not the
  author, 3 proper nouns (varieties, suburbs, growers, markets, streets),
  1 sentence someone could disagree with.

---

## 2. Scored dimensions

If all gates pass, score each dimension **1–5**:

- **5** — A discerning editor would publish it untouched
- **4** — Publishable; minor polish would help but isn't required
- **3** — Right idea, execution falls short; specific fixes needed
- **2** — Misses the standard in a structural way
- **1** — Wrong on arrival

### D1 — Emotional arc & hierarchy *(weight ×2)*

The post leads with the feeling, not the stems, price, or logistics.

- First sentence makes the reader feel something; a full read tells them exactly
  what to do next.
- Order holds: emotional arc → craft/delivery proof → product and practical
  detail. Specifics never open; they close.
- The sender's unspoken question — *"Will this feel right?"* — is answered.
- **Guide:** the six-part structure is present and in order (moment context →
  emotional job → selection logic → recommended products → card language →
  next action).
- **Journal:** the piece stands alone as something a stranger would read for
  pleasure. Apply the test: **would The Design Files, Broadsheet, Gourmet
  Traveller or Vogue Living run this?** Score 5 only if the honest answer is yes.

### D2 — Voice & craft of the prose *(weight ×2)*

Premium not pretentious; thoughtful not precious; warm not gushing; clear not salesy.

- Specificity does the work: stem names, suburbs, delivery times, real
  occasions — at least one grounding detail per major section.
- Every adjective earns its place. If a phrase could appear on any florist
  website, it fails this dimension.
- Understatement over volume: no exclamation-mark warmth, no superlatives,
  no over-punctuation.
- Quietly confident close — present, guide, make it easy. Never push.
- **Journal:** more room is allowed — longer sentences, first person, humour —
  but the parent voice still governs.

### D3 — Usefulness *(weight ×1.5)*

Blog register is authoritative, generous, educational.

- A reader gets genuine value before being asked for anything.
- **Guide:** would a reader bookmark or share this? Does it remove choosing
  anxiety and give them language (card wording, selection logic) they can use?
- **Journal:** is it reported, not written? Does it carry a point of view —
  at least one sentence someone could disagree with — and proper nouns that
  prove someone left the desk?

### D4 — Imagery *(weight ×1.5)*

Score the rendered images per the `photography-ugc-review` standard.

- Real moments over studio stylings: the frame feels paused, not posed.
- Warm, slightly desaturated grade; linen, timber, candlelight territory.
  Never cool, never over-processed, never flat.
- Hands/process or delivery/arrival represented where the content calls for it.
- Composition: eye level or slightly above; shallow depth of field for
  emotional detail; negative space respected; no harsh studio light, pure
  white backdrops, catalogue isolation, or unrelated props.
- **Journal:** the lead image must be able to open the piece with no text.
  Library imagery may support but never lead.

### D5 — Internal linking & shopability *(weight ×1)*

Per the `blog-internal-linking` skill. *(Guide tier; for Journal, only the
"single quiet product link" rule applies — score 5 if honoured, 1 if violated.)*

- Density ~1 internal link per 120–150 words; spread, not clustered.
- One canonical target per concept; most specific match wins; no duplicate
  targets, no self-links.
- Descriptive anchors that read naturally; never "click here".
- Present: ≥1 commercial link, ≥1 related blog post, 1 product callout with
  the real product image and a "Shop the [name] →" link with price.
- Closing CTA is soft, woven prose — feeling first, then the gentle link.

### D6 — Page craft *(weight ×1)*

The rendered page, judged as a designer would.

- Heading hierarchy is clean and scannable; paragraphs breathe.
- Image placement creates rhythm — no orphaned images, no text walls.
- Mobile render holds up (check the narrow viewport screenshot).
- Nothing reads as templated filler; the page feels considered end to end.

---

## 3. Verdict logic

Weighted total = Σ (score × weight). Maximum = 45.

| Verdict | Condition |
|---|---|
| **PASS** | All gates clear, **no dimension below 4**, weighted total ≥ 38 |
| **REVISE** | Any gate hit, or any dimension ≤ 3, or total < 38 |
| **ESCALATE** | Critic is genuinely uncertain, or revision cap reached |

Rules of conduct (inherited from `photography-ugc-review`):

- **No false passes.** When in doubt, REVISE with notes — never wave it through.
- **No drift across the batch.** Post 12 gets the same rigour as post 1.
- If the pass rate across a calendar run exceeds ~90% on first attempt, the
  bar is probably set too low — flag it.
- Feedback is **directional, not prescriptive**: say *"the opening leads with
  logistics — the feeling needs to come first"*, not rewritten copy. The maker
  rewrites; the critic judges.

---

## 4. Critic output format

Return exactly this block so the maker can act on it programmatically:

```markdown
## [Post title] — attempt [n]

**Tier:** Guide | Journal
**Verdict:** PASS | REVISE | ESCALATE
**Gates:** CLEAR | [gate IDs hit, with the offending line quoted]

**Scores:**
- D1 Emotional arc & hierarchy: [1–5] — [note if <5]
- D2 Voice & craft: [1–5] — [note if <5]
- D3 Usefulness: [1–5] — [note if <5]
- D4 Imagery: [1–5] — [note if <5]
- D5 Linking & shopability: [1–5] — [note if <5]
- D6 Page craft: [1–5] — [note if <5]

**Weighted total:** [n]/45

**Revision directives:** [Only if REVISE. Max five items, ordered by impact.
Each names the dimension, the specific failure, and the direction of the fix.]
```

---

## 5. Loop stop conditions

- **Revision cap: 4 attempts per post.** On the fourth REVISE, verdict becomes
  ESCALATE: park the draft (do not publish), surface the post URL, the full
  score history, and the critic's final directives for Dan's eyes.
- A PASS flips the Shopify article from draft to published; anything else
  stays in draft. No exceptions.
- ESCALATE also fires immediately on: G6 (dishonest imagery), ambiguous tier,
  or any case where the critic cannot render/read the page.

---

## 6. Calibration exemplars

The critic anchors "what 5 looks like" against these published posts, not vibes.
Before each batch run, the critic should re-read at least the exemplar matching
the tier under review.

### Journal exemplar

**Against the Dozen Red Roses** — Kellie, June 2026
`https://figandbloom.com/blogs/journal/against-the-dozen-red-roses`

The master anchor for D1, D2 and D3 at Journal tier. What makes it a 5:

- **Opens with a thesis someone could disagree with** — "the dozen red roses
  is, most of the time, the wrong thing to send" — and argues it for the whole
  piece. Point of view, not content.
- **Reported, not written.** A real customer story (the thirtieth-birthday
  caller, the hellebores, the email two days later) carries the argument.
- **Proper nouns doing the work:** hellebores, ornamental kale, fragrant
  stock, the Epping wholesale flower market, deep plum stock. Specificity
  over adjectives, exactly as the framework demands.
- **The brand POV embodied, not stated as a slogan** — designer vs dispatcher
  is *shown* through the story before it's named.
- **Generosity of mind:** the carve-out paragraph (red roses as ritual)
  concedes the counter-argument, which makes the whole piece more credible —
  the framework's "trust the reader" principle in action.
- **One quiet product moment** (the Amour callout) placed *with* the
  carve-out, where it serves the argument rather than interrupting it. This
  is the model for J1 compliance.
- **The close sells nothing and everything:** "this week the stock is
  extraordinary, and the whole studio smells of it. Send that."

### Guide exemplars

**What to Write on a Flower Card** — May 2026
`https://figandbloom.com/blogs/news/what-to-write-on-flower-card`

The anchor for D1, D3 and D5 at Guide tier. What makes it a 5:

- **Textbook hierarchy:** opens on the feeling ("their ordinary Tuesday that
  suddenly feels less ordinary"), then immediately removes the reader's
  anxiety ("take the pressure off").
- **Gives usable language**, organised by occasion and relationship-distance
  (partner vs colleague vs someone you don't know well) — the Guide System's
  selection-logic and card-language sections done properly.
- **Products woven in-context** (Broome, Marseille, Savoie named where the
  occasion calls for them) with collection links on natural anchors — never
  a bolted-on shelf.
- **Handles sympathy with restraint:** "the card does not need to make the
  situation better. It cannot." Warm without gushing; names what to avoid
  ("everything happens for a reason") and why.

**Growing With the Seasons at Fat Magpie Farm** — December 2025
`https://figandbloom.com/blogs/news/fat-magpie-farm`

The anchor for D3 (reported usefulness) and D4 within the news blog. What
makes it the bar:

- **A real named human** (Trudi), quoted in her own voice, on a real visit —
  craft proof through someone else's craft.
- **Imagery is the story:** commissioned field photography and video lead;
  the frame feels paused, not posed, per the visual pillars.
- **Brand values shown through alignment, not assertion** — "those ideas were
  no longer language on a page" — with a single soft contextual link.

**The Gentle Art of Flower Arranging** — August 2025
`https://figandbloom.com/blogs/news/the-gentle-art-of-flower-arranging-for-wellness-and-presence`

The anchor for D3's evidence standard: claims are carried by cited research
(caregiver SFA programs, the blood-pressure study, the 12-week Korean
horticultural program), not florist clichés. The Flower Club close is a
model soft conversion — the product appears as the natural next step of the
argument.

> **Calibration caveat:** this post predates the current voice framework and
> contains usages today's gates would catch (e.g. "blooms" as a noun). The
> critic anchors on its *structure and evidence discipline only* — voice is
> anchored by the 2026 exemplars above. Current gates always win over any
> exemplar.

Re-calibrate exemplars when the catalogue or voice framework changes, and
re-version this rubric alongside the Internal Linking Map's monthly refresh.
