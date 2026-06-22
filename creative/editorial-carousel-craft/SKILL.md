---
name: editorial-carousel-craft
description: >
  Editorial standard + critic for Fig & Bloom social carousels and statics. This skill does
  NOT render — it sets the bar a multi-slide editorial carousel must clear and scores it.
  Use whenever building, reviewing, or elevating an editorial carousel — "make the [post]
  carousel", "critique these slides", "elevate this carousel", "why does our carousel look
  like a template", "turn this Journal post into a carousel". Carries the publisher benchmark,
  a slide-by-slide seven-axis critique rubric (incl. an Honesty/proof axis), the editorial
  arc + pacing standards, and a worked example. Rendering, templates, fonts, ratios, asset
  sourcing, and persistence are owned by the my-social-builder app and its writer skill
  (social-post-builder); this skill targets the builder's editorial lanes (carousel-journal,
  story-editorial), critiques the rendered PNG set, and returns feedback through the campaign
  loop. Defers to brand-guidelines-manager for fonts, palette, and voice. Never generates AI
  photography.
license: MIT
metadata:
  author: Dan Groch
  related_skills:
    - social-post-builder
    - ad-creative-builder
    - brand-guidelines-manager
    - copy-qa
---

# Editorial Carousel Craft

Make carousels that read like **a few pages torn from a beautifully designed magazine** —
not the same brand slide nine times with the words swapped. This skill is the *editorial
standard + critic*. It **does not render**: the `my-social-builder` app owns the locked
lanes, fonts, and Puppeteer render, and `social-post-builder` writes the `post.json` the app
renders. This skill chooses the right lane, holds the editorial bar, scores the result, and
feeds critique back into the review loop.

> **Routing — this skill vs the rest.** Editorial / Journal carousel standard + critique →
> **here**. Writing the `post.json` for a lane → **`social-post-builder`**. Rendering it →
> **the `my-social-builder` app**. Paid ad creatives → **`ad-creative-builder`**. Brand-rule
> lookup → **`brand-guidelines-manager`**. Caption/copy QA → **`copy-qa`**.

## The standard, in one line

> One idea, photography that carries, type that's restrained and consistent, hierarchy from
> **space** not size. Drama comes from air and from one or two earned moments — never from
> emphasising a word on every slide.

If a slide only repeats the layout of the one before it, the deck is a template. Fix that
before anything else.

## When to use

Any multi-slide editorial carousel (or editorial story) for Fig & Bloom — from scratch,
adapting a Journal post, or critiquing/elevating an existing set. Always run the loop; never
sign off a first render.

## The loop (run every time)

1. **Map the arc, then pick the lane.** Write the slide list as a narrative: open (hook) →
   develop → **turn** (the line that reframes) → resolve / sign-off. 7-10 slides; curated,
   not inflated. Decide each slide's texture (photo / statement / quote / breath / closer)
   and confirm **no two adjacent slides share texture *and* layout**. Choose the builder lane
   (`carousel-journal` for a feed carousel, `story-editorial` for a story) — see
   `references/benchmark.md` and `references/builder-integration.md`.
2. **Get the `post.json` written — don't hand-build HTML.** Hand the arc to
   `social-post-builder` (or fill the app form), targeting the lane's real tokens from
   `GET /api/schema`. Photo tokens use `query: …` against the asset library; **no AI
   photography.**
3. **Render via the builder.** `POST /api/render {post, scale:2}` (or the UI) rasterises the
   locked lane to a 2160x2700 PNG set. You critique *that* — not a mock.
4. **Self-critique against the rubric.** Score every slide on hook, hierarchy, restraint,
   rhythm, image craft, finish, and **honesty (does the photo's content match the headline's
   claim?)**. Name the gap on each; read every product shot *against the words above it*.
   See `references/critique-rubric.md`, and `references/worked-example.md` for a real run.
5. **Iterate as token edits.** Feed fixes back as edits to the post (widows, breaks, emphasis,
   anchoring, wrong lane), re-render, re-check — at least twice. First render is a draft.
6. **Return critique through the loop; escalate.** Deliver the critique as campaign feedback
   (`POST /api/campaigns/:id/posts/:postId/feedback`), not a side document. **Never publish to
   social or a live page — escalate to Dan first.**

## Non-negotiable guardrails

**`brand-guidelines-manager` is the source of truth for voice, palette, fonts, and the brand
POV — look there, don't restate it.** The below is only the *carousel-specific application*;
if it ever conflicts with the brand guide, the brand guide wins.

- **Voice & POV (per brand guide):** premium-not-pretentious, calm, Australian English, no
  discount/urgency, no emojis, no clichés. *The moment after matters most.* Close on the point
  of view, never a promotion.
- **Imagery: owned first, AI never.** Owned library (via the photo-token `query:`) first;
  licensed editorial context only for clearly-not-our-product scene-setting; **never
  AI-generated photography, never stock passed off as ours.** Verify provenance if unsure.
- **Hero/photo slides read horizontal.** Crop to a horizontal feel; **never stack two
  full-width portraits** — pair images side-by-side as a band.
- **Emphasis is Cervanttis italic, used rarely.** The brand set has a real italic display face
  (**Cervanttis**) — emphasise the *turn* word with it, a palette colour shift, or the line
  break, and do it sparingly (<= 3 moments across 9 slides). Never synthesise a slant and never
  substitute Neuzeit Bold for italic. If a lane has no italic/emphasis token, raise it as a
  builder gap — don't invent a workaround.
- **Proof must match the claim.** A product shot must demonstrate what its headline asserts
  (see the Honesty axis in `references/critique-rubric.md`).

## Type & emphasis (the craft that makes or breaks it)

The builder owns the actual font files and the lane CSS; this is the *editorial discipline*
applied on top.

- **Two display roles, held all the way:** Lust (roman display) + Cervanttis (italic, for the
  rare emphasis moment). Body/kicker is Neuzeit Grotesk (Light / Bold). No third voice.
- **A tight display ladder** — roughly three steps; assign each slide one. The thesis/peak
  slide gets the top step; photo headlines sit *in* the ladder (never a timid size that makes
  images whisper). Don't freestyle nine sizes.
- **Hierarchy from scale + space + colour**, not many sizes (the Cereal lesson).
- **Emphasis = the turn word only**, in Cervanttis italic or a clay colour shift — one method
  per moment, kept scarce. Restraint in the type is usually the brand's argument.
- **Typography finish:** curly apostrophes/quotes, em dashes, no widows, no orphan
  single-word lines. Break headlines by **sense** — verify in the render.

## Pacing & composition

- **Alternate texture** every slide; vary vertical placement (top-weighted / centred /
  base-anchored) so the system reads as rhythm, not repetition.
- **One accent changes per slide** (folio, a colour field, a rule) — repetition-with-variation
  is what reads as "a designed report".
- **Anchor every base.** A bounded composition reads as composed negative space; an unbounded
  void reads unfinished.
- **Include a "breath" slide** — one quieter, more spacious beat — to break a run of statements.
- **Image moments ~ 40%**, woven through, not clustered. Text-forward is fine *if* the text
  slides vary.

## Caption <-> carousel

Slides are the **headlines**; the caption is the **article**. Don't print the caption's prose
on the slides — trim on-slide body to a short supporting line. The first caption line should
*complement* slide 1 (deepen the hook), not echo it. The closer slide and the caption CTA are
one move.

## Pre-ship QA checklist

- [ ] Arc mapped; correct lane chosen; no two adjacent slides share texture **and** layout.
- [ ] One focal point per slide; ~3 display sizes, all from the ladder.
- [ ] Emphasis is rare (<= 3 moments) and real — **Cervanttis italic / colour / line-break**,
      never a synthesised slant or Neuzeit-Bold-as-italic.
- [ ] No widows, no orphan single-word lines; breaks by sense; curly punctuation.
- [ ] Every base anchored; folios legible on photo slides (scrim/contrast).
- [ ] Photo slides horizontal-feeling; no stacked portraits; type has real contrast.
- [ ] Every product shot **demonstrates the claim above it** — no proof-vs-claim mismatch.
- [ ] On-slide body trimmed; prose lives in the caption.
- [ ] AU English; no emojis; no discount/urgency; closes on POV.
- [ ] Imagery owned/licensed-context only via the asset library; **no AI photography.**
- [ ] Rendered by the builder at full 2160x2700; eyeballed desktop **and** mobile; iterated >= twice.
- [ ] Critique returned as campaign feedback; **nothing published — escalated to Dan.**

## References

- `references/benchmark.md` — the publisher benchmark (cover, hierarchy, pacing, ratio,
  caption, close) with the patterns to copy.
- `references/critique-rubric.md` — the seven-axis scoring rubric (incl. Honesty) + the
  recurring "template tells" to hunt for.
- `references/worked-example.md` — a real critique run (the One Foliage deck).
- `references/builder-integration.md` — how this skill targets the my-social-builder lanes,
  the `post.json` contract, the API surface, and where critique feedback goes.
