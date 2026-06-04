# Builder Backend — Task Spec (for `dgroch/my-email-buider`)

These tasks belong in the **builder's own repo** (https://github.com/dgroch/my-email-buider),
which is what deploys to https://my-email-builder.onrender.com. They are **out of scope
for `dgroch/skills`** — recorded here so the agent-facing and builder-facing sides stay
coherent. Run them against the builder repo, not this one.

Grounded in the current source (server.js route table; `lib/designs.js` and
`lib/notionStore.js` share the interface `{ list, get, create, update, clone, remove }`;
`lib/klaviyo.js`). Endpoints already live: `schema, assemble, render, render-slices,
export, designs (CRUD + clone), klaviyo-audiences, klaviyo-draft`.

---

## Recommendation summary

| Item | Verdict | Why |
|---|---|---|
| `GET /api/agent-contract` | **Skip** | Redundant with `/api/schema` + the skill's CANONICAL WORKFLOW block. A second contract source is a new drift risk for no new information. |
| `GET /api/examples` | **Build, as data not a new path** | Approved JSON exemplars are genuinely useful for agents — but expose them through the existing designs store via a flag, not a parallel system. |
| Intent metadata in `/api/schema` | **Build (additive)** | Lets agents reason about component choice from the contract itself; complements `component-strategy.md`. |
| Teaching validation errors | **Build** | Highest-value backend change — turns silent bad output into actionable feedback. |
| Rich Notion metadata per design | **Build** | Enables search/reuse of approved patterns. |

---

## Task 1 — Skip `/api/agent-contract` (decision, not work)

Do **not** add it. The execution contract is `/api/schema` (components, tokens, presets,
ordering + case rules); the workflow/MUST-rules live in the skill, which agents load
before touching the API. If a machine-readable entry point is still wanted later, make it
a tiny static derivative of `/api/schema` (canonicalWorkflow flag + endpoint map) with a
test asserting it never disagrees with schema — but prefer not to.

## Task 2 — `GET /api/examples` as tagged designs (small)

Reuse the designs store instead of a new subsystem.

- Add an `isExample` boolean + `objective` string (see Task 4 taxonomy) to the design
  record (`create`/`update` in both `designs.js` and `notionStore.js`).
- `GET /api/examples` → `designs.list()` filtered to `isExample === true`; support
  `?objective=farewell_sellthrough`.
- Seed with the repaired **"RH | 2026-06 Farewell Weekend + Glow Up Tease"** design
  (`375fdc24-425f-8185-87fd-e75630c999eb`) as the `farewell_sellthrough` exemplar; add
  others as approved.
- **Invariant:** every example must `assemble` with zero `(missing template)` and zero
  unfilled tokens. Add a test that asserts this for all `isExample` designs.

## Task 3 — Intent metadata in `/api/schema` (additive)

In `lib/parseTemplates.js`, add per-component optional fields (purely additive — existing
consumers ignore unknown keys):

```json
{ "name": "blocks/editorial-hero", "group": "blocks", "designed": true,
  "bestFor": ["range_launch","occasion_gifting","product_spotlight"],
  "avoidFor": ["discount_offer","value_prop"],
  "visualRole": "high-impact opening: photo + serif headline + script accent on an overlapping plate",
  "requiresImage": true, "imageRatio": "600x440", "tone": "editorial, premium, calm" }
```

Source the values from `references/component-strategy.md` so the two never disagree —
ideally generate from a shared table. Keep names **group-prefixed**, matching `name`.

## Task 4 — Campaign objective taxonomy (shared)

Expose the canonical objective list (mirror of `component-strategy.md`):
`farewell_sellthrough, range_launch, product_spotlight, occasion_gifting, discount_offer,
value_prop, education_howto, social_proof, lifecycle`. Per objective, recommend: block
sequence, hero options, proof modules, CTA style, urgency level, modules-to-avoid.
Surface under `/api/schema` (e.g. `objectives`) or `/api/examples?objective=…`.

## Task 5 — Teaching validation errors (highest value)

`/api/assemble` already returns `unfilled`. Extend validation so failures are actionable:

- **Bare component name** → today yields `{token:"(missing template)"}`. Detect when a
  bare name (e.g. `hero-d-clay`) matches a known component under a group, and return a
  fix:
  ```json
  { "error": "Unknown component 'hero-d-clay'", "component": "hero-d-clay",
    "rule": "component names are group-prefixed",
    "suggestion": "heroes/hero-d-clay" }
  ```
  *(This is the exact class of error that caused the original hand-coded-HTML
  regression — make it impossible to miss.)*
- **Casing violations** → Cervanttis tokens must be lowercase; Lust tokens Sentence case
  (`tokenRules` in schema). Return component, token, rule, and a corrected `suggestion`.
- Consider a `POST /api/validate` (or `?validate=1` on assemble) returning a structured
  report without rendering, so agents can self-correct before saving.

## Task 6 — Rich Notion metadata per design (medium)

`notionStore.js` currently persists campaign JSON as a code block with minimal metadata.
Add structured properties so approved patterns are searchable/reusable:

`campaignType/objective, audienceAwareness, primaryCTA, emotionalTone, componentsUsed
(derived from blocks), approvalStatus (draft|approved|sent), sourceBriefLink,
klaviyoLink, resultNotes`.

Add the matching Notion DB properties (`NOTION_DESIGNS_DB`), extend `create`/`update` to
write them, and surface them in `list()`/`get()`. Keep `disk` backend (`designs.js`) at
parity for local dev (store the same fields in the JSON record).

---

## Guardrails for all backend work
- **Design system is one-directional:** templates/shells/assets/manifest are sourced from
  `creative/creative-email-campaign-builder/references/` in `dgroch/skills`; the builder's
  `design-system/` mirrors it. Never edit templates only in the builder repo.
- **Keep `disk` and `notion` design stores at interface parity** (`list/get/create/update/
  clone/remove`).
- **Add a test** that every component `name` from `/api/schema` resolves to an existing
  template file — this alone prevents whole classes of the prefix bug.
