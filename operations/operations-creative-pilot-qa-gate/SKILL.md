---
name: operations-creative-pilot-qa-gate
description: Paperclip operations workflow for pilot creative QA. Use this skill when reviewing florist pilot outputs across the human brief path or transformer-package path and you need a launch-readiness verdict covering artifact completeness, ownership clarity, brand-seed presence, world-consistent visual character, and competitor-residue removal.
---

# Creative Pilot QA Gate

This skill is the release gate for the florist creative-operations pilot.
It does not generate briefs, packages, or assets. It decides whether the
submitted work is complete, brand-safe, operationally clear, and ready to
move to launch.

Use it for both pilot paths:

- **Human brief path**: benchmark pack -> approved production brief ->
  creative variants -> QA before paid-media handoff
- **Transformer path**: approved brief -> validated
  `transformer_input_package` -> transformed output -> QA before launch

The standard is not originality versus the borrowed ad format. The
standard is whether the output has been convincingly converted into a
Fig & Bloom-ready asset with clear ownership and no unresolved launch risk.

## Primary users

- **ChiefOfStaff**: operational completeness, handoff clarity, launch risk,
  "would shipping this embarrass the company?"
- **BrandManager**: brand cues, copy/tone drift, product/pricing truth,
  visual-world consistency, competitor-residue detection

## Required inputs

You must have enough evidence to review. Do not guess.

### For the human brief path

Minimum review set:

- Approved benchmark pack or benchmark references
- Approved production brief
- Creative asset(s) or variants being reviewed
- Destination URL or landing-page type
- Named owner for the next step after QA

### For the transformer path

Minimum review set:

- Approved production brief
- Validated `transformer_input_package`
- Source asset inventory
- Final transformed output(s) under review
- Named owner for technical fixes and named owner for brand fixes

If the submission mixes both paths, review each path separately and then
issue one final launch verdict.

## Hard-stop rules

Any item below is an automatic **BLOCK**. Do not continue to softer scoring
until these are checked.

- Missing required artifact for the claimed path
- No named owner for the next action or unresolved ownership ambiguity
- Invented product, price, delivery, or market-coverage claim
- Placeholder pricing or generic benchmark pricing not anchored to real
  Fig & Bloom products
- Visible competitor logo, product, watermark, brand name, or unedited copy
- Output still visually reads as the source competitor world rather than a
  Fig & Bloom world
- Required brand-seed cues are absent from a transformed output
- Brief/package lacks explicit forbidden elements or must-change direction
- Landing-page promise clearly mismatches the creative promise
- Delivery urgency or same-day promise appears in the asset without a
  confirmed operational basis
- Technical package is marked anything other than `validated`
- Rights-cleared source confirmation is missing for the transformer path

If any hard-stop rule is hit, stop and report the blocker directly.

## Review dimensions

After hard-stop checks pass, review against these eight dimensions.

### 1. Artifact completeness

Check that the submission contains the artifacts required for its path and
that each artifact is materially usable, not nominally present.

Pass looks like:

- brief/package is complete enough to execute without follow-up guessing
- creative assets are attached or linked clearly
- landing destination is specified
- test angle and CTA path are visible

Fail examples:

- brief exists but omits delivery promise, price anchor, or CTA
- package exists but omits prohibited elements or target output spec
- assets are referenced vaguely ("latest folder") instead of explicitly

### 2. Ownership clarity

Check whether the workflow can advance without role confusion.

Pass looks like:

- approver is named
- next operator is named
- brand fixes and technical fixes have clear owners when applicable
- status of the work is obvious: draft, approved, validated, or ready

Fail examples:

- "marketing will sort it out"
- no owner for landing-page fix
- brand and technical issues are mixed into one unassigned bucket

### 3. Commercial truth

Every commercial cue must be real and grounded in Fig & Bloom reality.

Check:

- product names or product range are real
- price point or price band is real
- delivery window/cutoff/geography are real
- offer framing matches the actual landing destination

Fail examples:

- placeholder "from $79" style copy with no product anchor
- premium cue in ad but low-end landing page on click
- urgency promise with no visible operational basis

### 4. Brief or package discipline

The pilot depends on one dominant commercial angle and explicit control
over what changes versus what stays.

Check:

- one dominant angle only: recipient, urgency, price, occasion, or offer
- `must_keep`, `must_change`, and `forbidden_elements` are specific
- CTA path is singular and clear
- the brief/package does not ask the downstream operator to invent strategy

Fail examples:

- urgency + luxury + assortment + offer all competing in one concept
- "keep the vibe but make it ours" with no concrete change list
- missing banned claims/elements

### 5. Brand-seed presence

The output must have visible Fig & Bloom identity, not generic florist
content with a swapped logo.

Check for:

- Fig & Bloom naming and tone where text is present
- recognizable Fig & Bloom product or merchandising cues
- brand-appropriate colour, typography, composition, or styling cues
- occasion/recipient framing that fits Fig & Bloom's positioning

Fail examples:

- asset is technically polished but brand-anonymous
- tone drifts into generic direct-response spam
- the output relies entirely on the source format and adds no brand layer

### 6. World-consistent visual character

This matters most on transformed assets. Ask whether the output feels like
it belongs to one coherent Fig & Bloom visual world.

Check:

- character, set, props, styling, and mood belong together
- shots do not jump between incompatible visual worlds
- product presentation matches a premium florist context
- AI or edit artefacts do not break believability

Fail examples:

- subject identity drifts across clips
- bouquet/product styling changes in implausible ways
- source-ad residue remains in wardrobe, props, text, or framing logic

### 7. Landing continuity

The click destination must match the promise made in the asset.

Check:

- same product range or category appears immediately after click
- price framing aligns
- delivery promise aligns
- occasion/recipient framing aligns

Fail examples:

- "same-day flowers" creative clicks to generic homepage with no same-day cue
- price-led creative lands on page with hidden or contradictory pricing

### 8. Launch readiness

Final readiness is a release judgment, not a style note.

Ask:

- can media buyers launch this without clarifying intent?
- are fixes minor and mechanical, or is the concept still unstable?
- would a customer see obvious mismatch, residue, or false promise?
- would shipping this embarrass the company?

## Path-specific checks

### Human brief path

Review these in addition to the eight shared dimensions:

- benchmark-to-brief translation is visible and specific
- brief names a real product/range and approved price anchor
- recipient/occasion angle is explicit
- creative scoring logic is present or implied
- final assets still match the approved brief rather than drifting during production

### Transformer path

Review these in addition to the eight shared dimensions:

- package status is `validated`
- source asset inventory is explicit
- source format, aspect ratio, and rights status are clear
- prompt package is specific enough to reproduce intent
- forbidden elements include competitor residue and banned claims
- final output reflects the approved brief and package, not ad hoc edits

## Verdicts

Use exactly one verdict per reviewed item:

- **APPROVE**: ready to launch or hand to media/ops with no material risk
- **REVISE**: concept is valid, but one or more fixable issues remain
- **BLOCK**: cannot proceed because a hard-stop rule or major launch risk exists

Decision rule:

- **APPROVE** only if all hard-stop checks pass and no review dimension has a
  material failure
- **REVISE** if issues are specific, bounded, and can be fixed without
  changing the concept or ownership model
- **BLOCK** if the work is incomplete, misleading, operationally unsafe, or
  still reads as an unconverted competitor artifact

## Output format

Return every review in this format:

```md
## Pilot QA Gate

**Path:** Human brief / Transformer / Mixed
**Item:** [brief name, package id, asset name, or batch label]
**Verdict:** APPROVE / REVISE / BLOCK
**Ready for launch:** Yes / No

### Hard-stop check
- Result: pass / fail
- Notes: [only list blocking items if any]

### Review summary
- Artifact completeness: pass / revise / block — [specific note]
- Ownership clarity: pass / revise / block — [specific note]
- Commercial truth: pass / revise / block — [specific note]
- Brief/package discipline: pass / revise / block — [specific note]
- Brand-seed presence: pass / revise / block — [specific note]
- World-consistent visual character: pass / revise / block — [specific note]
- Landing continuity: pass / revise / block — [specific note]
- Launch readiness: pass / revise / block — [specific note]

### Required fixes
- [exact fix]
- [exact fix]

### Owners
- Brand fix owner: [agent or role]
- Technical/package fix owner: [agent or role]
- Final approver after fixes: [agent or role]

### Next action
- [what should happen next]
```

Rules for the output:

- Be specific. Name the missing field, broken promise, or residue.
- Do not write vague notes like "tighten the brand."
- If the issue is a blocker, say exactly who must act.
- If there are no required fixes, write `- None`.

## Batch mode

When reviewing multiple assets, produce a compact table first:

```md
| Item | Path | Verdict | Main reason |
|---|---|---|---|
| Asset A | Transformer | REVISE | Brand-seed cues too weak |
| Asset B | Human brief | APPROVE | Complete and launch-ready |
| Asset C | Transformer | BLOCK | Competitor residue remains |
```

Then include detailed review blocks only for `REVISE` or `BLOCK` items, plus
any `APPROVE` item that was borderline.

## Anti-patterns

Do not do these:

- Do not optimize for originality scoring against the source ad
- Do not approve work because "the concept is good" if the artifact is incomplete
- Do not ignore missing owners just because the asset looks strong
- Do not pass pricing or delivery claims that are not explicitly grounded
- Do not let transformed outputs through when competitor residue is still visible
- Do not request broad rework when the issue is a single concrete fix
- Do not collapse brand review and operating review into one vague paragraph

## Escalation guidance

- Escalate to **MarketingManager** if the brief conflicts with established
  brand or campaign intent
- Escalate to **BrandManager** if competitor references, comparative claims,
  or identity drift remain unresolved
- Escalate to **CTO** if the package contract, validation state, or source
  rights/technical preflight are invalid
- Escalate to **ChiefOfStaff** if repeated rework shows the pilot handoffs are
  failing systemically rather than item-by-item

## What good looks like

A strong pilot QA decision:

- rejects missing or invented commercial facts immediately
- distinguishes operational incompleteness from brand drift
- makes the next owner obvious
- protects launch quality without demanding unnecessary originality
- keeps the pilot moving by giving bounded revisions when possible
