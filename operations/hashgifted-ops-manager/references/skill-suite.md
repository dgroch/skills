# Hashgifted Skill Suite

Use this when authoring or refactoring the individual lifecycle skills.

## Foundation

| Skill | Purpose |
| --- | --- |
| `reference-browser-operator` | Abstract browser action vocabulary used by all browser-driven skills. |
| `hashgifted-browser-adapter-map` | Concrete Hashgifted intent map for browser runtime adapters. |
| `hashgifted-ops-manager` | Operating brain for lifecycle dispatch, risk gates, run modes, and audit logging. |

## Lifecycle Skills

| Skill | Position | Scope |
| --- | --- | --- |
| `hashgifted-campaign-init` | Step 0 | Interview marketer, create Notion campaign and brief records, flag manual share-to-web step. |
| `hashgifted-creator-shortlist` | Step 1 | Qualify applied creators against campaign objectives, hard gates, and aesthetics before communication. |
| `hashgifted-creator-select` | Step 2 | Contact shortlisted creators about campaign messaging, deliverables, deadlines, and select only after agreement. |
| `hashgifted-creator-monitor` | Orchestrator | Sweep active campaigns, identify per-creator state, dispatch one highest-priority action per creator. |
| `hashgifted-content-capture` | Capture | Pull completed post/reel assets, organise Drive, sync CDN, embed/log in Notion. |
| `hashgifted-creator-close` | Final | Delivered path: appreciation, mark complete, score. Ghost path: silent close, exclude, log. |
| `hashgifted-story-capture` | Urgent capture | Use separate story capture service, then route through Drive, CDN, and Notion. |

## Authoring Rules

- Keep business skills free of runtime-specific calls, selectors, coordinates, and sleeps.
- Include run mode behaviour in every lifecycle skill.
- Include pre-flight checks, decision tree, action sequence, quality gates, failure modes, and tacit knowledge.
- Use Australian English.
- Keep creator-facing messages warm, plain-spoken, and short.
- Use `assist` as default for live actions.
- Include audit log output expectations.

## Story Capture Constraint

Story capture is a separate service boundary, not a normal Hashgifted browser flow. The main operator only detects, dispatches, and logs. It does not fix Instagram auth.
