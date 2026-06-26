---
name: email-production-loop
description: >
  Drive a single Fig & Bloom campaign brief to a critic-approved, validated,
  rendered email parked as an unsent Klaviyo draft — zero human in the loop
  until PASS or escalation. For the campaign: choose strategy and components,
  write copy, source brand imagery owned-first, validate/assemble/render via
  the builder, have an independent critic score the rendered email against the
  bundled rubric, and refine until it passes or escalates. Use whenever the
  brief is "build and QA this campaign", "run the email loop", "produce this
  send to a ready draft", or any single-campaign task that ends in an approval
  -ready Klaviyo draft.
license: MIT
metadata:
  author: Daniel Groch
  related_skills:
    - creative-email-campaign-builder
    - fig-bloom-email-generator
    - photography-ugc-review
    - blog-internal-linking
    - brand-cdn
---

# Email Production Loop

One inner loop. It drives a single campaign brief through maker → critic →
refine until the critic's verdict is PASS or the attempt cap forces an
escalation. This is the email analogue of `blog-production-loop`; the producer
(`creative-email-campaign-builder` + `fig-bloom-email-generator`) is solved —
this skill is the **critic and the gate** around it.

Scope is deliberately **single-campaign**. There is no editorial-calendar outer
loop. Pass it one brief; it returns either an approval-ready Klaviyo draft or an
escalated saved design with a logged reason.

## Operating principles — non-negotiable

1. **The maker never grades its own work.** The critic runs in a fresh,
   isolated context with no access to the maker's reasoning — only the rendered
   email, the rubric, and the objective-matched exemplar.
2. **The critic reviews the rendered email**, not the campaign JSON. Judgement
   happens where the reader is: the full-email PNG (`/api/render`) for layout
   and imagery, the assembled HTML (`/api/assemble`) for copy, links and tokens.
3. **PASS is the only path to a Klaviyo draft — and the draft is unsent.**
   Everything short of PASS stays a saved builder design. Scheduling and sending
   always stay with Dan. No exceptions, no "close enough".
4. **Owned imagery first, generated second, stock never.**
5. **Escalation is a success state.** A campaign parked with a clear reason after
   four attempts is the loop working, not failing.

## Roles (context-isolated agents)

| Role | Does | Must not |
|---|---|---|
| **Orchestrator** | Holds the brief, runs the loop, tracks state, writes the run report | Write copy or score quality |
| **Maker** | Strategy + component choice + copy + builder JSON; applies revision directives | See the rubric scores it "would get"; create the Klaviyo draft itself |
| **Image Sourcer** | Runs the imagery waterfall (below) | Embed anything unowned, unrights-cleared, or placeholder |
| **Critic** | Scores the rendered email against `resources/email-critic-rubric.md` | Rewrite copy; see maker context |
| **Publisher** | Saves the design; on PASS creates the **unsent** Klaviyo draft and sets subject/preview in the Klaviyo editor | Send, schedule, or act on anything but a PASS verdict |

## Inputs

- **One campaign brief** — objective, occasion/persona, hero product(s), imagery
  angle, audience, any blog post being linked. Thin briefs are clarified with Dan
  **upfront**, before building (objective and hero product especially).
- **Rubric** — `resources/email-critic-rubric.md` (bundled). The critic loads it
  fresh every review.
- **Producer skills** — `creative-email-campaign-builder` (workflow, schema,
  components) and `fig-bloom-email-generator` (brief → validated JSON in one shot).
- **Builder base** — `https://my-email-builder.onrender.com`. Free Render plan →
  cold-start latency; use long timeouts and retry.

## The inner loop — one campaign, end to end

### P1 — Brief → strategy *(Orchestrator → Maker)*

Resolve objective (taxonomy in the rubric §0 / generator §8), persona + lens,
hero product, and imagery angle. Confirm gaps with Dan now, not mid-build.

### P2 — Copy + JSON *(Maker)*

Produce campaign JSON via `fig-bloom-email-generator` (or hand-assemble against
the live schema). Group-prefixed components only; `HEADLINE` casing matched to
component font; `brand-voice.md` respected at draft time, not patched later.
On attempts ≥2, the maker receives **only** the critic's revision directives and
the prior JSON — directives are instructions, not suggestions.

### P3 — Imagery *(Image Sourcer)* — the waterfall

For every image slot:

1. **Asset library first (owned).**
   `GET https://asset-library-u70t.onrender.com/api/search?q={scene description}`
   (`--max-time 120`; cold start). `url` values are already on
   `brand-cdn.figandbloom.workers.dev` — embed directly. Query the *scene*, not
   keywords. **Check `rights` via `/api/assets/{id}` before any UGC or person-bearing
   asset**; gate uncertain candidates through `photography-ugc-review`.
2. **Licensed lifestyle** (Pexels / Unsplash, official APIs) — editorial context
   only; never pass stock florals off as Fig & Bloom product.
3. **AI brand photography** (`brand-photographer`) — last resort; match Noir/Clay/
   White; host via `brand-cdn` before embedding.

### P4 — Product truth & links *(Maker)*

Every named product confirmed live on the collection page (not Shopify admin
search) with a real from-price via `figandbloom.com/products/{slug}.js`. Every
link on **`figandbloom.com`**, resolving to a live page (no `-archived` slugs).
Any linked blog post must be **live on Shopify before send** — record its status.
No discount / delivery-cutoff / city-specific claim without sign-off.

### P5 — Validate, assemble, render, persist *(Maker → Publisher)*

1. `POST /api/validate` → fix every issue (bare/unknown components, casing).
2. `POST /api/assemble` (`markBlocks: true`) → `unfilled` must be empty; check
   hrefs and tokens in the HTML.
3. `POST /api/render` → full-email PNG; view it for broken images.
4. Persist: new → `POST /api/designs`; existing → **`GET /api/designs/{id}` first**,
   modify, then `PUT /api/designs/{id}` (never re-POST the original build JSON —
   it wipes in-builder edits). Capture the design `id`.

### P6 — Critic review *(Critic, fresh context)*

1. Load `resources/email-critic-rubric.md` fresh. Pull the objective-matched
   exemplar: `GET /api/examples?objective=<objective>`.
2. Take the rendered PNG (`/api/render`) and assembled HTML (`/api/assemble`) as
   the only inputs — no maker context.
3. Score: hard gates first (EG1–EG12), then the seven weighted dimensions, then
   the verdict block in the rubric's exact output format. No false passes —
   uncertainty is REVISE or ESCALATE.

### P7 — Gate *(Orchestrator + Publisher)*

- **PASS** → Publisher confirms the design is saved, then creates the **unsent**
  Klaviyo draft (`POST /api/klaviyo-draft`), **sets subject + preview directly in
  the Klaviyo campaign editor** (the builder value does not sync), confirms any
  linked blog is live, and parks it for Dan to schedule/send. Log scores.
- **REVISE** → attempt counter +1; directives go to the Maker (and Image Sourcer
  if ED4 failed); loop to P2/P3.
- **ESCALATE** (4th REVISE, EG6 dishonest imagery, ambiguous objective,
  unreadable render) → leave the saved design, do **not** create a Klaviyo draft,
  park with full score history and the critic's final directives.

## Stop conditions & budgets

- **Per campaign:** 4 attempts, then ESCALATE. Hard.
- **Never auto-send.** PASS produces an unsent draft only.
- Run-level sanity from the rubric: if first-attempt PASS is the norm across many
  sends, the bar may be mis-set — flag it.

## Run report *(Orchestrator, end of run)*

```markdown
# Email production run — {campaign} — {date}
- Verdict: PASS (unsent Klaviyo draft) | ESCALATED (saved design only)
- Attempts: N | Final weighted total: N/50
- Design id: … | Klaviyo draft: {id or "—"} | Subject/preview set in Klaviyo: yes/no
- Linked blog live: yes/no/NA

## Scores (final attempt)
| ED1 | ED2 | ED3 | ED4 | ED5 | ED6 | ED7 | Total |

## If escalated — needs Dan's eye
{Blocking issue in the critic's words, plus the design id to open.}

## Patterns
{Recurring failure modes across attempts — skill/rubric improvement candidates,
e.g. "subject failed ED1 on every attempt — preview kept repeating the subject".}
```

## Running it

**Turn-by-turn (default):** follow P1–P7; role isolation maps to fresh sub-agent
spawns. The **Critic must be a separate spawn** — never the same context as the
Maker.

**As a Claude Code workflow:** pair with `/goal` set to *"the campaign is either an
unsent Klaviyo draft with a PASS verdict, or an escalated saved design with a logged
reason."* Set a token budget; long timeouts for builder cold starts.

## What this skill does NOT cover

- Writing or amending the rubric (versioned in `resources/`)
- Authoring briefs or a campaign calendar (single-campaign in; no batch)
- Sending or scheduling — the draft is unsent; send stays with Dan
- Template development — if a need can't be met within locked components, escalate

## When in doubt

- Brief has no clear objective or hero product? → Ask Dan. The objective sets the
  whole beat.
- Asset library returns near-misses only? → Generate; never settle for off-brand
  owned imagery just because it's owned.
- Builder schema surprises you? → Validate, don't guess. A failed validate is free;
  a malformed render wastes a cycle.
- Critic and a producer reference disagree? → `brand-voice.md` wins on voice,
  `/api/schema` wins on structure; flag the ambiguity in the run report.