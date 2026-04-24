# Paperclip AI Skills

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
- `creative/email-template-builder` (`email-template-builder`): Create, build, and deploy Klaviyo email campaigns and automated flows from a modular component library.

### Human Resources

- `human-resources/deputy-connector` (`deputy-connector`): General-purpose Deputy API connector for employees, rosters, timesheets, leave, and related resources.
- `human-resources/employee-offboarding` (`workforce-employee-offboarding`): Offboard a departing employee at Fig & Bloom — save resignation notice, send formal acknowledgement, revoke platform access, and schedule Deputy archival.
- `human-resources/fig-bloom-rostering` (`fig-bloom-rostering`): Build and optimize weekly rosters using Deputy + Shopify inputs and labour budget constraints.

### SEO

Paperclip-adapted SEO specialist workflows:

- `seo/analytics-reporting`: Track organic performance, detect anomalies, and produce weekly/monthly SEO reporting.
- `seo/backlink-management`: Monitor backlink profile health, detect toxic links, and plan outreach/disavow actions.
- `seo/competitor-analysis`: Analyze SEO competitors, track movement, and surface strategic opportunities.
- `seo/content-strategy`: Plan and prioritize the SEO content roadmap and editorial pipeline.
- `seo/copywriter-handoff`: Build structured SEO briefs and handoff packages for copy production.
- `seo/keyword-research`: Discover, cluster, and prioritize keyword opportunities by intent and impact.
- `seo/local-seo`: Manage location-based SEO strategy, local pack visibility, and citation hygiene.
- `seo/on-page-specs`: Define and audit on-page SEO requirements (title/meta/headings/schema/internal links).
- `seo/rank-tracking`: Monitor keyword rankings, SERP features, and movement trends over time.
- `seo/site-architecture`: Design and maintain URL hierarchy, internal linking, and redirect strategy.
- `seo/task-tracker`: Maintain persistent SEO operating state, tasks, alerts, and run metadata.
- `seo/technical-audit`: Run technical SEO audits for crawl/index/performance issues and remediation priorities.

## A Joke to Brighten Your Day

> Why do programmers prefer dark mode?
>
> Because light attracts bugs.

