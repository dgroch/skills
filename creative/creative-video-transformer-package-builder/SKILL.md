---
name: creative-video-transformer-package-builder
description: Build a machine-ready Fig & Bloom video transformation package from an approved prospecting brief, Google Drive source assets, and brand seeds. Use this skill when a florist creative brief is approved and needs to be converted into a validated payload, manifest, and Drive handoff for the transformer-package-assembly routine.
author: Dan Groch
license: MIT
---

# Video Transformer Package Builder

Use this skill after the brief is approved. Its job is to turn upstream briefing output into a deterministic package that the transformation workflow can run without guesswork.

This skill is for the current florist pilot:
- lane: florist prospecting ads first
- artifact system: Google Drive
- brand policy: format borrowing is allowed, but the output must be re-authored through Fig & Bloom brand seeds and visual character

Read `references/package-contract.md` at the start of every run. It contains the current florist pilot contract for:
- upstream brief fields
- downstream transformer payload
- Drive folder structure
- package deliverables

## When to use

Use this skill when all of the following are true:
- a florist prospecting concept or brief has been approved
- the source video asset already exists in Google Drive
- the caller needs a package that can be passed to the `transformer-package-assembly` routine

Do not use this skill when:
- the upstream brief is still being decided
- there is no source video or no target Drive folder
- the task is to generate the video itself
- the task is to write the creative brief

## Required inputs

You need:
- the approved brief payload from the brief-building step
- the approved concept reference issue or equivalent approval record
- at least one concrete source video asset in Google Drive
- a target Google Drive folder for package outputs

Hard stop if any of these are missing:
- `benchmarkIssueId`
- `campaignObjective`
- `landingPageUrls`
- `offerGuardrails`
- source video `driveFileId`
- source video `durationSec`
- source video `aspectRatio`
- package output `driveFolderId`

## Workflow

### 1. Validate the handoff

Confirm the job is actually ready for packaging.

Check:
- the brief is approved, not draft
- the lane is still florist prospecting
- the source video is real and identifiable
- the landing page is explicit
- claims and guardrails are explicit enough to survive prompt generation

If anything is ambiguous, stop and return the missing field list. Do not infer commercial claims.

### 2. Normalize the concept

Reduce the brief to one transformation concept that the downstream routine can execute.

Produce:
- `hook`
- `offerAngle`
- `targetPlatform`

Rules:
- keep the concept narrow enough for one package
- if the brief contains multiple concepts, split them into separate packages
- prefer one source video per package

### 3. Build the package payload

Map the approved brief into the downstream payload in `references/package-contract.md`.

Use these rules:
- `jobId`: stable, human-readable, date-stamped
- `brandSeed.brand`: always `Fig & Bloom`
- `brandSeed.landingPageUrl`: choose the primary landing page for this package
- `brandSeed.requiredClaims`: only include claims explicitly allowed by the brief and supported by the landing page
- `brandSeed.bannedClaims`: include disallowed claims plus any competitor-specific residue that must not survive
- `references.benchmarkIssueId`: preserve the benchmark source
- `references.approvedConceptIssueId`: preserve the approving issue or equivalent approval handle

### 4. Assemble the Drive package

Use Google Drive as the canonical artifact layer for humans.

Create or populate the package folder described in `references/package-contract.md`.

Minimum package files:
- `transformer-run-payload.json`
- `package-manifest.md`
- `qa-checklist.md`

If useful, also include:
- `brief-summary.md`
- `source-asset-index.md`

### 5. Run the quality gate

Before declaring the package ready, verify:
- the payload is complete and internally consistent
- every Drive reference points to a concrete asset or destination
- the concept is still prospecting-first
- the package contains explicit brand-seed requirements
- the package blocks unedited competitor residue
- the landing page and claims align

Reject the package if:
- the source video is missing
- the output folder is missing
- claims are implied rather than explicit
- multiple incompatible concepts were jammed into one payload

### 6. Hand off

Return:
- the package folder link
- the final payload
- the key constraints that protect quality
- whether the package is ready to fire against the transformer routine now

If the caller has routine access and explicitly wants execution, this skill may be used to prepare the exact payload for the routine run. Do not auto-fire if approval is unclear.

## Output standard

The final package should make the downstream step boring. A strong output means the next agent does not need to guess:
- what video to use
- what concept to apply
- what claims are allowed
- what brand cues must appear
- where the outputs belong

## What to avoid

- Do not create packages from unapproved creative direction.
- Do not write generic prompts without landing-page and claim alignment.
- Do not use Drive as a dumping ground; keep one package per concept.
- Do not let competitor names, logos, pricing, or claims leak into the final payload.
- Do not infer banned claims from instinct alone; use explicit guardrails first, then add obvious competitor residue exclusions.
