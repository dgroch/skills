# Fig & Bloom — Editorial Scale & 5-Beat Rhythm (worked example)

This is a worked example of the design-discipline skill in production. The Fig & Bloom
2024 newsletter is the canonical reference for the editorial scale and the
5-beat typographic rhythm. Pair this with the skill's defaults — when the brand
overrides the defaults, the override reason + reference is captured here so the
next session can apply the same reasoning.

---

## 1. When the defaults don't fit

The skill's default type scale (Section 3) suggests **display 96–160** for a
1080-wide frame. That fits loud, statement-style brand work. Editorial florists
like Fig & Bloom read at magazine scale, not banner scale. The defaults
*must* be overridden by the brand — and the override itself must be
disciplined (not freeform).

## 2. The Fig & Bloom editorial scale (1080 base)

Derived from the 2024 newsletter reference:

| Role | Skill default | Fig & Bloom | Why |
|---|---|---|---|
| Display headline | 96–160 | **48–56** | Editorial, not banner. The hero declares, it doesn't shout. |
| Title / sub-headline | ~52 | **32–36** | Half-step below display, ample breathing room. |
| Body copy | implied ~26 | **16–18** | Magazine column. Long reads, calm register. |
| Caption | n/a | **14** | Secondary description, slightly smaller than body. |
| Kicker / CTA / pill | ~26 | **12** | Tracked all-caps, small. Whispers, doesn't shout. |
| Voice (script italic line) | n/a | **20–24** | New role — see Section 3 below. |

The ratio of display to body is roughly **3–3.5×** (48 vs 16). The skill's
default ratio is closer to **6×** (120 vs 26). Editorial brands compress the
ratio; commercial brands expand it.

## 3. The italic-accent rule (Cervanttis / similar script)

A separate role emerges: a small **script** or **italic display** line that
sits *beside* the main type, not *inside* it. Fig & Bloom uses a Cervanttis
cut (House Industries) for this role.

**The rule, stated flat:**

> A script/italic-accent line is **never** used as inline italic *within*
> a sentence. It is its own block, with breathing room above and below. It
> speaks. The main type declares. They don't share a sentence.

### Roles where the script / italic-accent is correct

- **Kicker-voice** — a small line *above* a headline, setting the tone
  (e.g. *"for a most magical what-you-want"* above a CTA).
- **Product tagline** — a descriptor *under* the product name
  (e.g. *"Sophisticated and romantic, a true classic"* under *Paris*).
- **Sign-off** — at the end of a section, before the CTA
  (e.g. *"For the moment they feel what you meant."*).
- **Attribution** — under a pull-quote
  (e.g. *"— Grace, Ireland"*).
- **Soft pull-quote** — the entire quote is in script, sitting as its
  own moment on a dark plate.

### Roles where it is **wrong** (the common mistakes)

- ❌ Inline italic on a single word inside a Lust sentence.
- ❌ A long body paragraph in script.
- ❌ A CTA button label in script.
- ❌ Two or more script lines stacked (no clear hierarchy).

### When the brand doesn't have a script cut

Drop the role entirely. Don't try to fake italic with `font-style: italic`
on the main serif — the result looks amateur. Use Neuzeit Bold all-caps
with a wider tracking for the "softener" role instead.

## 4. The 5-beat typographic rhythm

A repeating pattern across every section of the editorial:

```
1. KICKER   — small, tracked, all-caps. Category or mood.
2. VOICE    — script/italic, optional. The aside, the human note.
3. DISPLAY  — the headline. The single line that says "this is the moment."
4. BODY     — one or two short lines. Quietly explained.
5. CTA      — full-width black bar, all-caps, tracked. The action.
```

| Beat | Required? | When to skip |
|---|---|---|
| Kicker | Usually | Only on a true single-sentence piece (a manifesto, a sign-off). |
| Voice | Optional | Skip on utility/instructional sections; keep on brand moments. |
| Display | **Always** | This is the only mandatory beat. |
| Body | Often | Skip on sign-offs and one-word moments. |
| CTA | Often | Skip on manifesto plates that exist to be felt, not clicked. |

The same five-beat pattern applies whether the canvas is a 9:16 Story, a
4:5 Feed, an email hero, or a 1:1 square. The shape of the rhythm is fixed;
the *weight* of each beat changes with format.

## 5. Spacing tokens (editorial variant)

Same 8px scale as the skill default (8 / 16 / 24 / 40 / 64 / 96). What
changes for the editorial variant:

- **Above the kicker:** minimum **64px** (no orphan top-edge).
- **Between kicker and voice:** **16px** (related — same emotional unit).
- **Between voice and display:** **24–40px** (the visual unit shifts from
  script to serif; the gap is the breath).
- **Between display and body:** **24px**.
- **Between body and CTA:** **40–64px** (the gap that signals "decision").
- **Below the CTA / above the logo:** **64–96px** (the brand-mark zone).

## 6. When this scale is the wrong choice

The editorial scale assumes the brand is **calm, considered, premium**.
If the brand brief says any of:

- "High-energy", "vibrant", "youth-skewed", "fast-fashion"
- "Stop the scroll", "punchy", "loud"
- "Sale", "limited time", "act now"

…then the skill's *default* scale (96–160 display, larger body, louder
kicker) is the right starting point. The editorial scale is the quieter
sibling. Pick consciously, not by inertia.
