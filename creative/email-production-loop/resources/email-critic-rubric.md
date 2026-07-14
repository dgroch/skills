# Fig & Bloom — Email Critic Rubric

**Purpose:** The scorecard a critic agent uses to gate every campaign produced by the
email production loop. The critic reviews the **rendered email** — the full-email PNG
(`POST /api/render`) for layout, imagery and designed-block quality, plus the assembled
HTML (`POST /api/assemble`) for copy, links, tokens, subject and preview — never the
campaign JSON or the maker's reasoning. The maker agent never scores its own work.

**Sources of truth:** `creative-email-campaign-builder` (`references/brand-voice.md`,
`component-strategy.md`, the visual-QA loop, the above-fold pre-flight), the
`fig-bloom-email-generator` system prompt (§11 self-check, §6 lens system, §5 personas,
§8 objective taxonomy), the project playbook (domain rule, product source of truth,
gotchas, sign-off rules), and `photography-ugc-review`.

**Version:** 1.0 | **Owner:** Dan | **Voice authority:** `brand-voice.md` wins on any conflict.

---

## 0. Identify the objective first

Every send has one primary objective from the taxonomy. Score against the right one — a
`product_spotlight` judged as an `editorial_digest` (or vice versa) is a wasted cycle.

| Objective | Job | Tell |
|---|---|---|
| `occasion_gifting` | Help someone make the right gesture for a date | Occasion framing, persona-led, single hero gift |
| `range_launch` | Introduce a new range | News register, the range *is* the story |
| `product_spotlight` | One hero product, one decision | Single-product narrowing, confident default |
| `value_prop` | Why we're different | Proof-led, no discount |
| `social_proof` | The recipient's reaction / belonging | Real testimonial or "be the one who remembers" |
| `lifecycle` | Welcome / re-engage / post-purchase | Relationship register, low ask |
| `editorial_digest` | Recurring journal-led newsletter | Editorial leads, products woven, not shelved |
| `discount_offer` | Promotional offer | **Requires sign-off — see EG4** |

The objective sets the expected **block beat** (§ED2). If the brief says one objective but
the email reads as another, that mismatch is itself a fail.

---

## 1. Hard gates — instant REVISE, no scoring

Check these first. Any hit stops the review; return the gate ID with the offending element
quoted, and move on. Mirrors the hard-reject scan in `photography-ugc-review`.

- **EG1 — Banned language.** Any of: *elevate, curate, stunning, gorgeous, pop of colour,
  blooms* (as a noun), *spoil them/yourself, beautiful blooms, handcrafted with love,
  florist-grade, professional quality, say it with flowers, perfect for every occasion,
  cheap, affordable, budget-friendly, order now, don't miss out, last chance*. Exclamation
  marks in any headline. Emoji anywhere in body copy. (`brand-voice.md` is the authority;
  flag novel offenders.)
- **EG2 — Not Australian English.** US spellings (*color, organize, customize*),
  Americanisms (*obsessed, super cute, y'all*).
- **EG3 — Wrong domain.** Any CTA, link or destination on `figandbloom.com.au`,
  `.myshopify.com`, or anything other than **`figandbloom.com`**. Hard rule, zero tolerance.
- **EG4 — Unapproved commercial claim.** Discount/percentage-off framing, a delivery
  cut-off time, or a city-specific same-day promise **without MarketingManager /
  ShopifyAdmin sign-off**. Until approved, claims stay general ("available in many areas",
  "choose your day and time at checkout").
- **EG5 — Broken render.** Broken or missing images; leftover `{{ … }}` tokens visible in
  copy; a blank black button box (empty `CTA_TEXT`/`CTA_URL`); malformed layout; headings
  out of hierarchy; **missing `{{ unsubscribe_url }}` in the footer**.
- **EG6 — Dishonest or unrights-cleared imagery.** A product image that is not the real
  live product; watermark; competitor branding; visible AI artefacts (warped hands,
  impossible reflections, uncanny texture); any UGC / person-bearing photo whose `rights`
  are not cleared in the asset library. (Known excluded assets stay excluded.)
- **EG7 — Fabricated product or price.** A named bouquet not live on the store at build
  time, or any invented price. Every product traces to a live Shopify SKU with a current
  from-price (verified via `figandbloom.com/products/{slug}.js`).
- **EG8 — Literal scaffolding in the email.** A printed "CTA:", placeholder text, internal
  notes, or prompt residue rendered anywhere on the email.
- **EG9 — Urgency- or discount-led selling / multiple primary CTAs.** Countdown framing,
  manufactured scarcity, or more than one hard CTA competing for the click.
- **EG10 — Subject line breaks the rules.** Over 50 characters, caps lock, emoji,
  exclamation mark, or phrased as a command. Must be a question or a statement.
- **EG11 — Sensitivity opt-out missing.** A painful-occasion send (Mother's / Father's Day,
  Valentine's, sympathy, pregnancy/baby) with no gentle opt-out block placed early
  (immediately after the hero).
- **EG12 — Sibling-brand bleed.** Whoosh / Bower tone — terse Sunday-drop cadence,
  "Forgot? Fixed."-style lines. Fig & Bloom is editorial, not transactional.

---

## 2. Scored dimensions

If all gates pass, score each dimension **1–5**:

- **5** — A discerning editor would send it untouched
- **4** — Sendable; minor polish would help but isn't required
- **3** — Right idea, execution falls short; specific fixes needed
- **2** — Misses the standard in a structural way
- **1** — Wrong on arrival

### ED1 — Subject + preview line *(weight ×2)*

The open decision. Scored as a pair, because that's how the inbox shows them.

- Subject earns the open without hype — curiosity or a clear benefit, in the brand's
  quiet register; under 50 characters; a question or statement, never a command.
- Preview **extends** the subject's promise; it never repeats it and is never left to
  default to body text.
- Together they set an honest expectation the email then keeps.
- Note for the run report (not scored here): subject + preview must be set in the **Klaviyo
  campaign editor**, not just the builder — the builder value does not sync.

### ED2 — Emotional arc, hierarchy & block beat *(weight ×2)*

The email leads with the feeling or the usefulness, not the stems, price, or logistics.

- The lead block reduces one real anxiety or teaches one decision before it sells.
- Order holds: hook → proof/craft → product → single next action. Specifics close; they
  never open. Delivery framed as reassurance, never admin.
- The expected beat for the stated objective (§0) is present and in order.
- The subscriber is framed as someone who notices and marks moments with intention —
  identity-affirming, not transactional.

### ED3 — Voice & craft of the copy *(weight ×2)*

Premium not pretentious; warm not gushing; minimal not sparse; clear not salesy.

- Every word earns its place; no line that could sit on any florist's website.
- Australian English throughout. Understatement over volume — no superlatives, no
  exclamation warmth, no over-punctuation.
- Occasion headlines follow the **[Verb/Gerund] + [Emotional Act]** pattern where used —
  love letters to the recipient's qualities, not product descriptions.
- CTA copy is 2–3 words, active verb first (SEND LOVE, MAKE A MOMENT).
- The chosen lens (Robbins / Ziglar / Cialdini …) is coherent, not bolted on; a strong
  default opens Ziglar (disarm hesitation), closes Robbins (future memory).

### ED4 — Imagery & designed-block quality *(weight ×1.5)*

Score the rendered images and every designed `blocks/*` to the `photography-ugc-review`
standard and the producer's visual-QA rubric.

- **Owned imagery first** (asset library), licensed lifestyle only as editorial support,
  AI brand photography last — never stock florals passed off as product.
- Warm, slightly desaturated grade; linen / timber / candlelight territory. Never cool,
  never over-processed, never flat or catalogue-isolated.
- Each designed block passes: **composition balance** (nothing crammed or stranded),
  **type contrast** (Lust display vs NeuzeitGro body vs Cervanttis accent distinct),
  **focal clarity** (one obvious focal point), **brand restraint** (locked Noir/Clay/White,
  monochrome type, square black button — no off-brand colour or clearance-y loudness).

### ED5 — Above-the-fold & CTA discipline *(weight ×1)*

The skimmer must be able to click without scrolling.

- Primary CTA falls within the first ~700px (a CTA-bearing hero passes by construction; a
  bare `hero-image-only` opener that pushes the CTA past the fold fails).
- Exactly one primary CTA; any secondary action is clearly subordinate.
- Button is the square black brand button; destination is correct and resolves live.

### ED6 — Product truth & shopability *(weight ×1)*

- Every named product is live and shoppable (confirmed on the live collection page, not
  Shopify admin search) with a real current from-price.
- Every link resolves to a live page — no `-archived` handles, no dead slugs; domain is
  `figandbloom.com`.
- If the email links a blog post, that post is **live on Shopify before send** (most sit
  as drafts at build time — confirm published status).

### ED7 — Render & email-client integrity *(weight ×1)*

The rendered email, judged as a build engineer would.

- Renders clean as both PNG and HTML: no broken images, no leftover tokens, no orphaned
  or stacked designed blocks without a divider.
- Footer carries `{{ unsubscribe_url }}`; personalisation uses
  `{{ first_name|default:'Moment Maker' }}`.
- Mobile width holds up; designed-block PNGs are legible at email scale.
- `HEADLINE` casing matches the component font (Cervanttis = lowercase; Lust = Sentence
  case); `REVIEW_STARS` use `★`.

---

## 3. Verdict logic

Weighted total = Σ (score × weight). Maximum = **50**.

| Verdict | Condition |
|---|---|
| **PASS** | All gates clear, **no dimension below 4**, weighted total ≥ **42** |
| **REVISE** | Any gate hit, or any dimension ≤ 3, or total < 42 |
| **ESCALATE** | Critic is genuinely uncertain, or the revision cap is reached |

Rules of conduct (inherited from `photography-ugc-review`):

- **No false passes.** When in doubt, REVISE with notes — never wave it through. A live
  send is a brand cost; a parked draft is free.
- **No drift.** Attempt 4 gets the same rigour as attempt 1.
- If first-attempt pass rate across a batch of sends exceeds ~90%, the bar is probably too
  low — flag it.
- Feedback is **directional, not prescriptive**: say *"the opening leads with delivery —
  the feeling needs to come first"*, not rewritten copy. The maker rewrites; the critic
  judges.

---

## 4. Critic output format

Return exactly this block so the maker (and orchestrator) can act on it programmatically:

```markdown
## [Campaign name] — attempt [n]

**Objective:** [taxonomy id]
**Verdict:** PASS | REVISE | ESCALATE
**Gates:** CLEAR | [gate IDs hit, with the offending element quoted]

**Scores:**
- ED1 Subject + preview: [1–5] — [note if <5]
- ED2 Arc, hierarchy & beat: [1–5] — [note if <5]
- ED3 Voice & craft: [1–5] — [note if <5]
- ED4 Imagery & block quality: [1–5] — [note if <5]
- ED5 Above-fold & CTA: [1–5] — [note if <5]
- ED6 Product truth & shopability: [1–5] — [note if <5]
- ED7 Render & client integrity: [1–5] — [note if <5]

**Weighted total:** [n]/50

**Revision directives:** [Only if REVISE. Max five items, ordered by impact. Each names the
dimension, the specific failure, and the direction of the fix — not the rewrite.]
```

---

## 5. Loop stop conditions

- **Revision cap: 4 attempts per campaign.** On the fourth REVISE, verdict becomes
  ESCALATE: park the **saved builder design** (do not create a Klaviyo draft), surface the
  design id, the full score history, and the critic's final directives for Dan.
- **PASS is the only path to a Klaviyo draft** — and the draft is created **unsent**.
  Scheduling and sending always stay with Dan. Everything short of PASS stays a saved
  design only.
- ESCALATE also fires immediately on: EG6 (dishonest imagery), an ambiguous objective the
  brief can't resolve, or any case where the critic cannot render/read the email.

---

## 6. Calibration

The critic anchors "what 5 looks like" against approved work, not vibes. Before each review:

1. **Pull the objective-matched exemplar** from the builder:
   `GET https://my-email-builder.onrender.com/api/examples?objective=<objective>` —
   returns approved campaign JSON for that objective. Assemble/render it if a visual
   anchor is needed. This is the durable, self-updating exemplar source.
2. **Cross-check the producer's own bar** — the generator's §11 13-point self-check. A PASS
   here should imply all 13 are met, but judged independently and on the *rendered* email.

> Re-calibrate when the catalogue, component library, or `brand-voice.md` changes, and
> re-version this rubric alongside them. If the critic and a producer reference disagree,
> `brand-voice.md` wins on voice and `/api/schema` wins on structure — flag the conflict in
> the run report so the rubric gets fixed.
