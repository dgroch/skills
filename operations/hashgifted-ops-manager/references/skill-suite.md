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
| `hashgifted-creator-shortlist` | Step 1 | Qualify applied creators against the Campaign record, hard gates, and shared brand rubric before communication. |
| `hashgifted-creator-select` | Step 2 | Contact shortlisted creators about campaign messaging, metro delivery eligibility, deliverables, deadlines, and select only after agreement. This is where most creator communications live; do not create a separate generic communications skill unless the message surface grows beyond selection/nudges/Q&A/closeout. |
| `hashgifted-creator-monitor` | Orchestrator | Sweep active campaigns, identify per-creator state, dispatch one highest-priority action per creator. |
| `hashgifted-content-capture` | Capture | Pull completed post/reel assets, organise Drive, sync CDN, embed/log in Notion. |
| `hashgifted-creator-close` | Final | Delivered path: appreciation, mark complete, score. Ghost path: silent close, exclude, log. |
| `hashgifted-story-capture` | Urgent capture | Use separate story capture service, then route through Drive, CDN, and Notion. |

## Authoring Rules

- Keep business skills free of runtime-specific calls, selectors, coordinates, and sleeps.
- Include run mode behaviour in every lifecycle skill.
- Include pre-flight checks, decision tree, action sequence, quality gates, failure modes, and tacit knowledge.
- Use Australian English.
- Keep creator-facing messages warm, professional, plain-spoken, and short; not corporate.
- Use `assist` as default for live actions.
- In `assist`, draft messages and pause for approval before sending. Send autonomously only in explicit `auto` mode.
- Include audit log output expectations.
- Persist creator lifecycle/status/location/visual-review findings to the Notion Creators CRM; do not let browser audit logs become the only store of creator knowledge.

## Story Capture Constraint

Story capture is a separate service boundary, not a normal Hashgifted browser flow. The main operator only detects, dispatches, and logs. It does not fix Instagram auth.
