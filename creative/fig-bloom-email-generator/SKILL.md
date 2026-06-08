---
name: fig-bloom-email-generator
description: Generate validated Fig & Bloom campaign JSON (campaignName, subjectLine, previewText, blocks[]) from a free-form brief, with all brand voice, persona, and lens-routing context pre-loaded. Use this skill whenever someone (or the email-builder "Create Campaign" button) asks to draft a Fig & Bloom email campaign from a brief. Companion to creative-email-campaign-builder — the generator is what the LLM is *given*; the email-campaign-builder is the workflow the agent follows after the JSON arrives.
version: 1.0.0
metadata:
  hermes:
    tags: [Email, Klaviyo, Fig & Bloom, Brand, Marketing, Generative, Campaign]
    category: creative
    related_skills:
      - creative-email-campaign-builder
      - creative-campaign-brief-generator
---

# Fig & Bloom — Email Campaign Generator

> **The point of this skill:** a free-form brief ("farewell weekend for 7 designs, Friday + Saturday only, glow up tease for next week") → a **validated, builder-ready campaign JSON** (`campaignName`, `subjectLine`, `previewText`, `blocks[]`) → saved to the Fig & Bloom email builder, no further LLM round-trip needed.
>
> The LLM is loaded once with **everything Fig & Bloom** — brand POV, voice, the 8 personas, the Sales Legends lens system, component strategy, token rules, the output schema, the QA bar — and asked to produce a single, complete campaign. After that, the existing `creative-email-campaign-builder` workflow (validate → assemble → save → optional Klaviyo draft) takes over without re-specifying context.

## When to use

- The user clicks the **"Create Campaign"** button in the email builder UI and types a brief.
- An agent (in chat) is asked to **"draft a Fig & Bloom email for X"** with a brief.
- An agent needs to produce a `*Email-Build-*.md` (the internal format) from a brief.
- You want to bootstrap a campaign JSON to start editing in the email builder.

## When NOT to use

- The user wants to **edit an existing saved campaign** — that's the existing builder UI + `/api/designs/:id` PUT.
- The user has a hand-written campaign and just wants to **push to Klaviyo** — that's `POST /api/klaviyo-draft` on an existing design.
- The brief is for a non-email artefact (paid ad, landing page, blog post, SMS). Each of those has its own skill.

## How it works (the one-page version)

```
BRIEF  →  [system prompt + user template]  →  LLM  →  CAMPAIGN JSON  →  /api/validate  →  /api/designs  →  design id
```

1. **Brief** is supplied (button click → textarea; agent → user message).
2. **System prompt** (`references/system-prompt.md`) is pre-loaded into the LLM. It contains: brand POV, voice, 8 personas, lens routing, component strategy, output schema, QA bar.
3. **User template** (`references/user-prompt-template.md`) is filled with the brief and shipped to the LLM.
4. The LLM returns **campaign JSON** matching the schema exactly.
5. The host calls `POST /api/validate` — fail-fast on unknown components, casing errors, or unfilled tokens. The LLM is told to self-validate before returning.
6. The host calls `POST /api/designs` to save. The design is now editable in the builder UI.
7. Klaviyo draft is *not* pushed automatically — that requires human approval (per the existing skill).

## The prompts

| File | What it is |
|---|---|
| `references/system-prompt.md` | Pre-loaded once per LLM call. Brand foundations + 8 personas + lens system + component strategy + output schema + QA bar. ~6–8 KB. |
| `references/user-prompt-template.md` | The user-side message: takes a brief, asks the model to identify objective/persona/lens and emit campaign JSON. Has a worked example. |
| `references/personas.md` | The 8 occasion-based personas, with Core Job, Primary Problem, Objections, Tagline, What Convinces, Offers, Angles. Reference for the system prompt. |
| `references/lens-system.md` | The Sales Legends lens system (Robbins, Ziglar, Cialdini + 7 more) — when to route to which lens per occasion. Reference for the system prompt. |

## Companion skills

- **`creative-email-campaign-builder`** — the canonical workflow. Run *after* the JSON arrives: validate, assemble, render, save, optional Klaviyo draft. The generator's JSON should always be validated through `/api/validate` before saving.
- **`creative-campaign-brief-generator`** — if the brief is too thin to act on, run this first to flesh it out, then feed the result into the generator.

## Hosting in the email builder

The email-builder button endpoint (`POST /api/campaigns/generate` in `dgroch/my-email-builder`) does the following:

1. Receives `{ brief, audience }`.
2. Loads `system-prompt.md` and `user-prompt-template.md` from the skill bundle (the email-builder ships a copy under `lib/prompts/`).
3. Substitutes the brief + audience into the user template.
4. Calls the LLM (Anthropic Claude Sonnet by default — editorial register, strong at voice).
5. Strips any markdown code-fences from the response, parses JSON.
6. Calls `POST /api/validate` on the host (self-call) to confirm `ok: true`.
7. If validation fails, retries once with the LLM (telling it the validation errors).
8. Returns `{ campaign, validation, subjectLine, previewText }` to the UI.
9. The UI shows the JSON in the existing builder, where the user can edit tokens, then save normally.

The system prompt and user template are kept in sync with the skill via a sync script (`scripts/sync-prompts-from-skill.sh`) — the email-builder repo is the *runtime* home; the skill is the *source of truth*.

## The QA bar (self-check before returning JSON)

The LLM is told to self-check the campaign against this bar before returning. If any check fails, it should fix and return, not surface a half-baked campaign.

1. **Useful before it sells** — the lead block reduces one real anxiety or teaches one decision. Not "buy now".
2. **Headline matches awareness** — what the reader already knows vs. what's new.
3. **Identity-affirming** — the subscriber is framed as someone who notices and marks moments with intention.
4. **Real, specific, active products** — every named bouquet is on the live store at build time, with current from-prices.
5. **Warm, quietly confident** — no hype, no countdown pressure, no "last chance!".
6. **Australian English** — colour, realise, -ise endings, centre, favour, "have a look", "we'll be in touch".
7. **One clear next action** — a single primary CTA, matched to intent.
8. **Brand protected** — no discount framing, no manufactured urgency, no overclaim. Sub-claims stay general.

(See the system prompt for the full bar with the *why* behind each item.)

## Failure modes (and what to do)

| Failure | What to do |
|---|---|
| LLM returns invalid JSON | Retry once with the LLM, telling it to return *only* the JSON object, no fences. If still failing, surface the error to the user with the raw output. |
| `/api/validate` returns issues | Retry once, telling the LLM the structured issues. If still failing, surface issues to the user; do not save. |
| LLM hallucinates a component name | The system prompt lists the *live* components via the schema; bare names (`hero-d-clay` instead of `heroes/hero-d-clay`) are caught by `/api/validate` as `suggestion` issues. |
| LLM uses the wrong case for `HEADLINE` | Casing rule is in the system prompt; `/api/validate` flags casing. |
| Brief is too thin to act on | Either ask the user one clarifying question, OR run `creative-campaign-brief-generator` first to flesh it out. |
| LLM goes over length or off-brand | The QA bar + sibling-brand guardrail in the system prompt catches it; surface the JSON and let the user edit. |

## Pitfalls

- **Don't bypass `/api/validate`.** The schema is the contract; the validator is the cheapest way to enforce it.
- **Don't push to Klaviyo automatically.** Drafts only. Human approval is mandatory.
- **Don't substitute the campaign JSON for the marketing source of truth.** Paperclip / Notion campaign plans remain the editorial source; the JSON is the *email-side* render of the plan.
- **Don't reuse a "Moment Maker" tag-line you can't defend.** The Lens System is brand-confirmed (Robbins / Ziglar / Cialdini as the three primaries). Off-lens hooks drift the voice.
- **Don't add a "subscribe" / "discount" / "first-order" message.** That's Whoosh / Bower territory, not Fig & Bloom.
- **Don't fabricate prices or product names.** Every product reference must trace to a live Shopify SKU (verify at build).

## Tests

End-to-end:
1. Click "Create Campaign" in the email builder, type a short brief.
2. Confirm modal submits, endpoint returns, validation passes, JSON renders in builder.
3. Edit a token, render PNG, push a Klaviyo draft.
4. Open the saved design — confirm the campaign JSON round-trips.

Unit:
- `system-prompt.md` and `user-prompt-template.md` are valid markdown, < 12 KB combined.
- Persona list contains exactly the 8 personas, all 5 fields present.
- Component list matches `GET /api/schema` (pulled live at build, not duplicated).
- A sample brief produces a JSON that passes `POST /api/validate` with `ok: true`.

## Sync discipline

The skill is the source of truth. The email-builder mirrors the prompts under `lib/prompts/`. To re-sync:

```bash
# In my-email-builder:
./scripts/sync-prompts-from-skill.sh
```

Or just copy:
```bash
cp /opt/data/workspace/skills/creative/fig-bloom-email-generator/references/*.md \
   /opt/data/workspace/my-email-builder/lib/prompts/
```

The skill's version is bumped in `SKILL.md` `version:` whenever a prompt changes.
