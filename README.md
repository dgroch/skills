# OpenClaw Skills

A shared collection of agent skills for OpenClaw and Paperclip-style deployments.

## Repository Layout

Skills are grouped by domain:

- `creative/`
- `human-resources/`
- `seo/`

Each skill is self-contained and includes a `SKILL.md` file (plus optional `scripts/`, `references/`, and templates).

## Skills

### Creative

- `creative/add-creative-builder` (`ad-creative-builder`): Build production-ready static and carousel ad creatives from existing photography, copy, and brand assets.
- `creative/asset-adapter` (`asset-adapter`): Reformat a hero creative into platform-specific variants using deterministic crop/safe-zone rules.
- `creative/brand-guidelines-manager` (`brand-guidelines-manager`): Enforce and maintain Fig & Bloom brand rules for visual and tonal consistency.
- `creative/copywriting-qa` (`copy-qa`): QA customer-facing copy against brand voice and messaging standards.

### Human Resources

- `human-resources/deputy-connector` (`deputy-connector`): General-purpose Deputy API connector for employees, rosters, timesheets, leave, and related resources.
- `human-resources/fig-bloom-rostering` (`fig-bloom-rostering`): Build and optimize weekly rosters using Deputy + Shopify inputs and labour budget constraints.

### SEO

Paperclip-adapted SEO specialist workflows:

- `seo/analytics-reporting`
- `seo/backlink-management`
- `seo/competitor-analysis`
- `seo/content-strategy`
- `seo/copywriter-handoff`
- `seo/keyword-research`
- `seo/local-seo`
- `seo/on-page-specs`
- `seo/rank-tracking`
- `seo/site-architecture`
- `seo/task-tracker`
- `seo/technical-audit`

## Installation

```bash
clawhub install <skill-name>
```

Or copy the required skill directory directly into an agent's `skills/` folder.
