---
name: creative-ad-brief-architect
description: Build a prospecting-video ad brief for Fig & Bloom using the Winning Ads Framework (Pattern Interrupt → Proof). Use when planning, briefing, or kicking off a paid social/prospecting VIDEO ad (or the static stills spun from it) — selects one avatar, routes the persuasion lenses, picks the offer, names the real design, lays out the five-step beat sheet, tags AI-draft vs real-hero shots, and emits an Ads Database row + hypothesis. Triggers on "brief an ad", "new prospecting video", "winning ads brief", "pattern interrupt ad", "ad concept for [occasion]". This is the strategy head; the script itself is written by creative-ad-scriptwriter.
---

# Ad Brief Architect — Fig & Bloom

The strategy head for prospecting **video** ads. This skill turns an occasion and
an intent into a complete, framework-true brief that `creative-ad-scriptwriter`
can render without further questions — and that logs cleanly into the Ads
Database.

It owns: avatar choice, lens routing, offer selection, the named hero design, the
five-step beat sheet, the AI-draft vs real-hero-shot split, and the hypothesis.
It does **not** write the script (that's `creative-ad-scriptwriter`), assemble
statics (`creative-ad-creative-builder`), or produce footage (`creative-ugc-photo-generation`,
`creative-video-transformation`).

> Companion to the email-focused `creative-campaign-brief-generator`. Use this one
> whenever the deliverable is a **prospecting video ad**, not an email.

## When to use this skill

- "Brief an ad", "new prospecting video", "ad concept for [occasion]"
- "Run the Winning Ads framework on [idea]"
- Any request to plan a paid-social video (Meta/TikTok) or the stills cut from it

One occasion, one intent, one avatar per brief. If asked to cover two, split it
into two briefs.

## Read first (every intake)

Load these before asking anything, and pre-fill confident defaults silently:

- `references/winning-ads-framework.md` — the five steps, the hook principle, the
  Whoosh keep/drop list, the pre-ship checklist. The non-negotiable spine.
- `references/lens-routing.md` — the ten persuasion lenses and the occasion →
  lead-lens defaults. Produce a weighted routing string.
- `references/offers.md` — the canonical offers and which occasion gets which.
- `references/ads-db-row.md` — the Ads Database fields and valid select values.
- `../creative-campaign-brief-generator/references/personas.md` — the avatar
  (sender) definitions. **Reuse these; do not invent new avatars.**

Canonical voice lives in `creative-brand-guidelines-manager`; the Whoosh/voice
gate is enforced by `creative-copy-qa`. This skill defers to both rather than
restating them.

## Intake (2–3 exchanges, conversational — never a form)

Collect the fields below. Where `references/` or context gives a confident
default, apply it silently and surface it for confirmation. Don't ask cold for
what you can infer.

| Field | Source / default |
|---|---|
| **Occasion** | From the request. Map to the Ads DB `Occasion` select (see ads-db-row.md). |
| **Avatar (the sender)** | Pick **one** persona from personas.md and commit. Default by occasion (e.g. milestone occasions → Milestone Sender). Name the specific moment ("the long-distance partner who second-guesses"). |
| **Named design** | A **real** Fig & Bloom design (Osaka, Marseille, Lucerne, Umbria, Monaco…). Never generic flowers. Confirm the design exists; if unsure, ask. |
| **Lens routing** | Weighted blend across the ten lenses (e.g. `Ziglar 40 / Robbins 35 / Hormozi 25`). Default by occasion from lens-routing.md. |
| **Offer** | From offers.md. Default stack: Free Size Upgrade behind the 7-Day Freshness Promise. **Value, never discount.** |
| **CTA** | Default `Shop Now`. Only DB-valid values: Shop Now / Sign Up / Learn More / Get Offer. |
| **Funnel / Campaign Type** | Prospecting video → `TOFU` / `Prospecting` by default. |
| **Platform** | Default `Meta`; add TikTok/Google if requested. |

For tender occasions (Sympathy / Condolences / Get Well): lead with Ziglar,
let **presence be the proof**, and hold the guarantee as a quiet closing
reassurance — not a super. Flag the brief as high-sensitivity.

## Build the five-step beat sheet

Lay the brief out as the five framework beats. For each beat give: the intent,
the on-screen idea, and an **asset tag**. Do not write final spoken lines —
that's the scriptwriter's job; give direction the writer can voice.

1. **Pattern interrupt (0–~2s)** — the recognition line aimed at the avatar +
   the named bouquet visible by ~second 2. Asset: usually `AI-draft OK`.
2. **Self-recognition** — the one avatar, drilled. (Fires together with step 1.)
3. **Problem articulation** — the avatar's real doubt; the category enemy is
   *careless gifting* (arrives small, tired, nothing like the photo). Never name
   a rival, never a clinical list. Any falling-short gift shown here is
   deliberately **not** a Fig & Bloom design. Asset: `AI-draft OK`.
4. **Unique mechanism** — the named design: designed-not-assembled, hand-tied,
   arrives looking exactly like the photo, still beautiful in seven days.
   Asset: **`REAL HERO SHOT REQUIRED`** — the hero design must be real product
   photography before ship (the mechanism *is* "arrives like the photo"; an AI
   bouquet here breaks the promise). AI is fine for the draft/animatic only.
5. **Proof** — the **message back** (the call, the photo on the table) as social
   proof of the moment after, plus risk reversal (the offer stack). Asset:
   `AI-draft OK` for the moment-after; **no fabricated testimonials or review
   counts**.

End on one clear CTA (Shop Now).

### Asset-split rule (hybrid)

Tag every beat `AI-draft OK` or `REAL HERO SHOT REQUIRED`. AI (via the
Higgsfield skills) carries ideation, avatar, and moment-after B-roll; **any frame
where the named design is the focus must be swapped to real product photography
before ship.** Carry these tags into the scriptwriter and the pre-ship checklist.

## Write the hypothesis

One sentence, in the house form: *"[Hook] stops the [avatar]; [mechanism] +
message-back resolve the sender's doubt that [specific fear]."* This is the row's
`Hypothesis` and the thing the Ads DB measures against.

## Emit the Ads Database row

Produce a fenced block with the fields from `references/ads-db-row.md` filled:
`Occasion`, `Avatar/Target Audience`, `Angle`, `Lens routing` (in Hypothesis or
Angle), `Offer`, `CTA`, `Funnel`, `Campaign Type`, `Platform`, `Status: Draft`,
`Hypothesis`. Leave performance fields (Spend, ROAS, CPA…) empty — they're filled
post-flight.

## Deliver

In this order, clearly labelled:

1. **Brief header** — occasion · avatar · named design · lens routing · offer · CTA.
2. **Five-step beat sheet** — each beat with intent, screen idea, asset tag.
3. **Hypothesis** — one line.
4. **Ads DB row** — fenced, ready to paste.
5. **Hand-off** — "Pass to `creative-ad-scriptwriter` to write the script."

Then run the pre-ship checklist from `references/winning-ads-framework.md` and
note any beat that fails (especially: real-hero-shot tag set, value-not-discount,
one avatar, no named rival, passes the Whoosh test).

## The one test that governs everything

> If a hook or line would also work on a Whoosh ad, it isn't ours yet.

Emotionally exact, calm, premium-but-human. Feeling leads; logistics support.
The interrupt is **recognition, not noise**.

## When NOT to use this skill

- Email campaign brief → `creative-campaign-brief-generator`.
- Writing the actual script → `creative-ad-scriptwriter`.
- Assembling static/carousel creative → `creative-ad-creative-builder`.
- Generating the imagery/video → `creative-ugc-photo-generation`, `creative-video-transformation`.
