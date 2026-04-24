# Florist Pilot Package Contract

This file is the current contract for the Fig & Bloom florist creative-operations pilot.

## Upstream brief payload

The brief-building routine currently returns a payload shaped like this:

```json
{
  "benchmarkIssueId": "FIGA-708 or other approved benchmark issue",
  "benchmarkPackUrl": "https://drive.google.com/...",
  "campaignObjective": "Prospecting conversions",
  "channel": "meta",
  "placements": ["reels", "stories", "feed"],
  "offerGuardrails": {
    "allowedClaims": ["same-day delivery", "from $85"],
    "disallowedClaims": ["invented discounts", "unverified cutoff promises"]
  },
  "landingPageUrls": [
    "https://figandbloom.com/pages/same-day-delivery"
  ],
  "productFeedUrl": "https://feeds.datafeedwatch.com/112192/b71f90bd6d650fe7bdbca2d900a80635d1b87249.xml",
  "driveFolderUrl": "https://drive.google.com/...",
  "notes": "Optional campaign context or testing constraints"
}
```

## Downstream transformer payload

The `transformer-package-assembly` routine currently expects:

```json
{
  "jobId": "florist-prospect-2026-04-25-001",
  "concept": {
    "hook": "same-day flower delivery rescue",
    "offerAngle": "recipient-led gifting",
    "targetPlatform": ["meta", "tiktok"]
  },
  "sourceVideo": {
    "driveFileId": "<source-video-file-id>",
    "durationSec": 18,
    "aspectRatio": "9:16",
    "language": "en-AU"
  },
  "brandSeed": {
    "brand": "Fig & Bloom",
    "landingPageUrl": "https://figandbloom.com/pages/same-day-delivery",
    "requiredClaims": ["same-day delivery"],
    "bannedClaims": []
  },
  "references": {
    "benchmarkIssueId": "FIGA-676",
    "approvedConceptIssueId": "<issue-id>"
  },
  "output": {
    "driveFolderId": "<target-folder-id>"
  }
}
```

## Mapping rules

Map upstream to downstream like this:

| Upstream field | Downstream field | Rule |
|---|---|---|
| `benchmarkIssueId` | `references.benchmarkIssueId` | Preserve exactly |
| approved brief issue id | `references.approvedConceptIssueId` | Preserve exactly |
| `landingPageUrls[0]` | `brandSeed.landingPageUrl` | Use the primary landing page for the package |
| `offerGuardrails.allowedClaims` | `brandSeed.requiredClaims` | Include only claims that must survive into the transformation brief |
| `offerGuardrails.disallowedClaims` | `brandSeed.bannedClaims` | Carry forward and add obvious competitor residue exclusions |
| `channel` + `placements` | `concept.targetPlatform` | Normalize to one or more target platforms |

## Required Drive structure

Use Google Drive as the human-facing system of record.

Recommended folder path:

`09 - Shared Resources / Cross-Team Projects / Florist Creative Operations Pilot / Transformer Packages / <jobId>/`

Recommended contents:

- `transformer-run-payload.json`
- `package-manifest.md`
- `qa-checklist.md`
- `source-asset-index.md` if more than one source file exists

## Package manifest minimum

The manifest should answer:
- what concept this package runs
- which brief approved it
- which benchmark inspired it
- which source asset is in scope
- which landing page and claims are allowed
- where outputs should land

## Quality gates

Reject the package if any of the following are missing:
- source video file id
- source video duration
- source video aspect ratio
- approved concept reference
- landing page URL
- output Drive folder id

Reject the package if:
- the package contains more than one incompatible concept
- the package still contains competitor names, logos, prices, or copy fragments
- claims are not grounded in the approved brief and landing page

## Constraints

Keep these guardrails in force for the current pilot:
- florist prospecting lane first
- Google Drive is canonical
- prefer rejecting incomplete jobs over creating weak transformer inputs
- do not auto-expand one brief into many packages without explicit instruction
