# Paperclip AI Skills

A shared collection of agent skills for OpenClaw and Paperclip-style deployments.

## Repository Layout

Skills are grouped by domain:

- `creative/`
- `human-resources/`
- `seo/`

Each skill is self-contained and includes a `SKILL.md` file (plus optional `scripts/`, `references/`, and templates).

## Skills

### Operations

- `operations/hashgifted-browser-adapter-map` (`hashgifted-browser-adapter-map`): Concrete Hashgifted browser intent mapping for portable browser operator runtimes.
- `operations/hashgifted-campaign-init` (`hashgifted-campaign-init`): Create Notion campaign and brief records before opening applicants.
- `operations/hashgifted-creator-shortlist` (`hashgifted-creator-shortlist`): Qualify Hashgifted applicants for a campaign shortlist before creator communication.
- `operations/hashgifted-ops-manager` (`hashgifted-ops-manager`): Manage portable Hashgifted creator operations with run modes, lifecycle dispatch, and audit logging.
- `operations/operations-output-to-drive` (`operations-output-to-drive`): Persist generated outputs to Drive and maintain related manifests.

### Reference

- `reference/reference-browser-operator` (`reference-browser-operator`): Portable browser automation vocabulary for skills that run across Playwright, Browserbase, Hermes, Camofox, and visual browser runtimes.
- `reference/reference-google-drive` (`reference-google-drive`): Google Drive operating conventions for shared output and asset workflows.
- `reference/reference-puppeteer` (`reference-puppeteer`): Puppeteer reference workflows and examples.

### Creative

- `creative/add-creative-builder` (`ad-creative-builder`): Build production-ready static and carousel ad creatives from existing photography, copy, and brand assets.
- `creative/creative-ad-brief-architect` (`creative-ad-brief-architect`): Build a prospecting-video ad brief on the Winning Ads Framework (Pattern Interrupt → Proof) — avatar, lens routing, offer, named design, five-step beat sheet, and an Ads Database row.
- `creative/creative-ad-scriptwriter` (`creative-ad-scriptwriter`): Write the prospecting-video ad script from the brief — recognition-shape hook, the five beats, message-back proof + risk reversal, single Shop Now CTA.
- `creative/asset-adapter` (`asset-adapter`): Reformat a hero creative into platform-specific variants using deterministic crop/safe-zone rules.
- `creative/brand-guidelines-manager` (`brand-guidelines-manager`): Enforce and maintain Fig & Bloom brand rules for visual and tonal consistency.
- `creative/creative-communications-calendar-planner` (`creative-communications-calendar-planner`): Plan integrated Fig & Bloom email, social, and blog calendars with blog-to-email link maps and Paperclip issue breakdowns.
- `creative/creative-social-grid-planner` (`creative-social-grid-planner`): Plan Fig & Bloom 9- or 12-tile social grid chapters using campaign-world art direction and product/human/proof balance.
- `creative/copywriting-qa` (`copy-qa`): QA customer-facing copy against brand voice and messaging standards.
- `creative/email-template-builder` (`email-template-builder`): Create, build, and deploy Klaviyo email campaigns and automated flows from a modular component library.
- `creative/blog-post-builder` (`blog-post-builder`): Build and publish a Fig & Bloom Shopify blog post end-to-end from a Notion editorial brief — brand voice + Thought-Leader Lens drafting, integrated internal linking + product merchandising (single callout or shoppable banner), and Shopify publish.

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

