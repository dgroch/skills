---
name: creative-florist-ad-brief-builder
description: Build a production-ready florist prospecting ad brief from approved benchmark ads, platform goals, offer guardrails, and Google Drive asset references. Use when an agent needs to turn winning florist or adjacent gifting patterns into a launchable creative brief with hooks, recipient framing, proof points, storyboard, CTAs, and a test matrix.
---

# Florist Ad Brief Builder

This skill converts approved benchmark ads into a production-ready brief for Fig & Bloom creative work.

Default mode: florist prospecting ads for cold audiences.

Read these references when needed:
- `references/prospecting-defaults.md` at the start of every brief
- `references/brief-schema.md` before drafting the final output
- `reference/reference-google-drive` skill when reading or validating Drive assets

## When to use

Use this skill when the task is to:
- turn benchmark ads into a creative brief
- prepare a florist ad concept pack for designers, editors, or a creative team
- brief prospecting ads for Meta or TikTok
- extract reusable hooks, storyboard beats, or test angles from approved ad references

Do not use this skill for:
- transformer package assembly
- raw asset generation
- final brand QA after assets are already produced

## Required inputs

Do not draft the final brief until these are present:
- approved benchmark ads or benchmark summary
- target platform: `Meta`, `TikTok`, or both
- campaign objective, default `prospecting`
- offer guardrails: what can and cannot be claimed or discounted
- Google Drive asset references for source footage, product imagery, brand seeds, or folder locations

If benchmark approval status is unclear, stop and ask for confirmation before proceeding.
If Drive references are missing, ask for the folder links or IDs before finalizing.

## Workflow

### 1. Normalize the inputs

Read `references/prospecting-defaults.md` first and apply those defaults unless the task overrides them.

Then extract:
- platform and placement assumptions
- benchmark hook patterns
- recipient angles
- price or delivery proof points
- visual format cues
- asset availability from Google Drive

Reduce the benchmark set to `3-5` transferable mechanics. Name the mechanic, not just the source ad.

Examples:
- `price discovery in first frame`
- `same-day delivery rescue`
- `recipient-specific gifting`
- `bouquet range browse`
- `creator-style unwrapping or handoff`

### 2. Build the creative thesis

For each brief, define:
- one primary audience frame
- one primary recipient scenario
- one dominant promise
- one friction reducer

Use florist prospecting defaults:
- audience = cold or lightly aware
- promise = ease, relevance, and perceived thoughtfulness
- friction reducer = clear price, clear delivery, or clear occasion fit

Do not write broad brand campaigns. Prospecting briefs must make the first action obvious.

### 3. Convert patterns into modules

Produce the following modules from the benchmarks:
- `Hook bank`
- `Audience / recipient framing`
- `Proof points`
- `Storyboard or shot list`
- `CTA variants`
- `Test matrix`

Rules:
- Hooks should be short enough to fit opening frames or voiceover lines.
- Proof points must be concrete. Prefer `from $X`, `same-day delivery`, `order by 2pm`, `best sellers`, `occasion-ready` over vague quality claims.
- Storyboards should assume native vertical capture first unless the brief explicitly says otherwise.
- CTAs must match the platform and landing flow.
- The test matrix should vary one lever at a time.

### 4. Use Google Drive as the asset system of record

Assume the human-facing source of truth is Google Drive.

The brief must identify:
- the intake folder or asset folder link
- which assets already exist
- which missing assets need to be created or sourced
- which files are the brand-seed references

If the Drive links are vague, list the exact missing references under `Asset gaps` instead of guessing.

### 5. Draft the final brief

Before writing, read `references/brief-schema.md` and follow it exactly.

The final brief must be directly usable by:
- MarketingManager
- ContentWriter
- BrandManager
- paid media buyers
- a human creative team

No placeholders, no `TBD`, no generic brainstorm lists.

If a required input is missing, stop at a short intake summary and ask only for the missing fields.

## Output rules

- Prefer florist prospecting over retention or seasonal framing unless told otherwise.
- Borrow mechanics aggressively from approved benchmarks, but rewrite them into Fig & Bloom language and world cues.
- Keep the brief concrete enough that a human editor or designer can start without another strategy round.
- Always include both `What to make` and `Why this should convert`.
- When both Meta and TikTok are in scope, separate platform notes rather than blending them.

## Quality gates

Before delivering the brief, check:
- [ ] The benchmark mechanics are explicit and transferable
- [ ] The audience is cold-prospecting unless intentionally overridden
- [ ] Price or delivery proof appears in the brief when available from inputs
- [ ] Google Drive asset references are captured
- [ ] Missing assets are called out explicitly
- [ ] Hook bank contains at least `6` options
- [ ] Storyboard includes at least `5` beats for video concepts
- [ ] Test matrix varies hook, proof point, or CTA cleanly
- [ ] The writing sounds like Fig & Bloom, not the source competitor

## After delivery

Offer the next action that matches the workflow:
- pass the brief to the creative team
- adapt it into platform-specific variants
- hand it to the transformer-package builder once the asset folder is complete
