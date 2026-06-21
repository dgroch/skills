---
name: creative-ad-scriptwriter
description: Write a Fig & Bloom prospecting-video ad script using the Winning Ads Framework (Pattern Interrupt → Proof). Use when you need the actual spoken lines, on-screen text, and screen cues for a paid social/prospecting VIDEO ad — recognition-shape hook gated by the resonance test, the five beats, the message-back proof + risk reversal, a single Shop Now CTA, AU English, calm punctuation, value-not-discount. Triggers on "write the ad script", "script this video ad", "hook for [occasion] ad", "turn this brief into a script". Takes a brief from creative-ad-brief-architect; defers the voice gate to creative-copy-qa.
---

# Ad Scriptwriter — Fig & Bloom

Writes the words and screen direction for a prospecting **video** ad on the
Winning Ads Framework. It renders a brief into the five beats: a recognition hook
that voices what the avatar already feels, the avatar drilled, the real doubt,
the named design as the mechanism, and proof via the message back + the offer
stack — closing on one clear CTA.

It writes the script. It does **not** decide strategy (`creative-ad-brief-architect`),
gate the voice (`creative-copy-qa`), or produce footage/stills (`creative-ugc-photo-generation`,
`creative-video-transformation`, `creative-ad-creative-builder`).

## Input

Ideally a brief from `creative-ad-brief-architect` (occasion · one avatar · named
design · lens routing · offer · CTA · asset tags · hypothesis). If asked to write
cold, gather those first — at minimum the **occasion**, the **one avatar**, and
the **real named design**; infer the rest from the references and confirm.

## Read first

- `references/hook-shapes.md` — the recognition-shape bank and the resonance test.
- `../creative-ad-brief-architect/references/winning-ads-framework.md` — the five
  steps, the keep/drop list, the pre-ship checklist.
- `../creative-ad-brief-architect/references/offers.md` — exact offer wording for
  the proof step.

Canonical voice = `creative-brand-guidelines-manager`. Tone gate before
hand-off = `creative-copy-qa`. Don't restate their rules; write to them.

## The hook (get this right or nothing else matters)

The pattern interrupt speaks **directly to one avatar**, present tense, second
person, voicing something they **already feel or think** — so a true match
recognises themselves and stops. Never the talent narrating themselves.

Write **5–7 hook options** across different recognition *shapes* (see
hook-shapes.md): name a feeling, voice a private thought, state a tension, reflect
a belief/identity. *"You want X / you've got Y"* is one shape, not the rule.

Gate every option on the **resonance test**: *would the right person feel that's
me?* Cut anything that's a claim, a flash, or could run on a Whoosh ad. The named
bouquet is visible by ~second 2, so feeling and product land together.

✅ "You're still waiting for someone to send them."
❌ "I've never been the flowers guy." (talent narrating self)
❌ "Australia's #1 florist — 50% off today." (claim + discount = not ours)

## The five beats (script structure)

Write each beat as: **spoken line(s)** + `[on-screen text]` + `[screen cue]`.
Keep lines short enough to actually say in time. Feeling leads; logistics support.

1. **Pattern interrupt + self-recognition (0–~2s)** — the chosen hook, the avatar
   implied so precisely it's unmistakable, named bouquet visible by ~2s. Steps 1
   and 2 fire together. `[screen cue: AI-draft OK]`
2. **Problem articulation** — the avatar's real doubt in one or two plain lines.
   The enemy is *careless gifting* (arrives small, tired, nothing like the
   photo). No rival named, no clinical list. Any falling-short gift shown is
   deliberately **not** a Fig & Bloom design. State the fear, then move.
3. **Unique mechanism** — the named design: designed-not-assembled, hand-tied,
   arrives looking exactly like the photo, still beautiful in seven days. The
   design **is** the proof of difference. `[screen cue: REAL HERO SHOT REQUIRED —
   real product photography before ship]`
4. **Proof** — the **message back** (the call, the photo on the table) as the
   social proof of the moment after, then risk reversal: the offer stack in the
   exact wording from offers.md (default: Free Size Upgrade behind the 7-Day
   Freshness Promise). **No fabricated testimonials or review counts.** For tender
   occasions, let presence be the proof and keep the guarantee a quiet closing
   line, not a super.
5. **CTA** — one ask. Default *Shop Now*. Tie it to the feeling, not urgency.

## On-screen text & captions

- Opening on-screen text is a second hook for the muted viewer — short, the
  recognition in 3–6 words. It can differ from the spoken hook.
- Provide a **Primary Text** caption (1–2 lines, lead with the offer or the
  recognition) and 3–5 restrained hashtags if the platform wants them. AU
  English, calm punctuation, no hype.

## Deliver

1. **Hooks** — 5–7 numbered options, each tagged with its recognition shape.
2. **Script** — the five beats with spoken lines, `[on-screen text]`, `[screen
   cues]` including asset tags.
3. **On-screen opener** + **Primary Text** caption, each in its own code block.
4. **Hand-off note** — "Send to `creative-copy-qa` for the voice gate, then to
   `creative-ugc-photo-generation` / `creative-video-transformation` for
   production (real hero shot on the mechanism beat)."

Then self-check against the pre-ship checklist in `winning-ads-framework.md` and
flag any miss — especially the Whoosh test, value-not-discount, one avatar, real
hero shot tagged, and no fabricated proof.

## The test that governs everything

> If a hook or line would also work on a Whoosh ad, it isn't ours yet.

## When NOT to use this skill

- Strategy / brief / lens routing → `creative-ad-brief-architect`.
- Email copy → `creative-email-campaign-builder` / `fig-bloom-email-generator`.
- Voice/tone review → `creative-copy-qa`.
- Producing the imagery or video → the Higgsfield production skills.
