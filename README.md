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

- `creative/ai-video-clone-workflow` (`ai-video-clone-workflow`): Clone a short-form video (competitor ad or your own winner) using AI actors — multi-scene, native audio, captions, brand product integration. Reference-seed prompting, camera/hands + capture-realism hard-fail gates, a per-clip motion critic, and a Brand Profile + MCP/CLI adapter for multi-brand, multi-runtime use.
- `creative/add-creative-builder` (`ad-creative-builder`): Build production-ready static and carousel ad creatives from existing photography, copy, and brand assets.
- `creative/asset-adapter` (`asset-adapter`): Reformat a hero creative into platform-specific variants using deterministic crop/safe-zone rules.
- `creative/brand-guidelines-manager` (`brand-guidelines-manager`): Enforce and maintain Fig & Bloom brand rules for visual and tonal consistency.
- `creative/creative-communications-calendar-planner` (`creative-communications-calendar-planner`): Plan integrated Fig & Bloom email, social, and blog calendars with blog-to-email link maps and Paperclip issue breakdowns.
- `creative/creative-social-grid-planner` (`creative-social-grid-planner`): Plan Fig & Bloom 9- or 12-tile social grid chapters using campaign-world art direction and product/human/proof balance.
- `creative/copywriting-qa` (`copy-qa`): QA customer-facing copy against brand voice and messaging standards.
- `creative/email-template-builder` (`email-template-builder`): Create, build, and deploy Klaviyo email campaigns and automated flows from a modular component library.
- `creative/blog-post-builder` (`blog-post-builder`): Build and publish a Fig & Bloom Shopify blog post end-to-end from a Notion editorial brief — brand voice + Thought-Leader Lens drafting, integrated internal linking + product merchandising (single callout or shoppable banner), and Shopify publish.
- `creative/editorial-carousel-craft` (`editorial-carousel-craft`): Editorial standard + critic for Fig & Bloom social carousels and statics — sets and scores the bar a multi-slide editorial carousel must clear (publisher benchmark, seven-axis critique rubric incl. honesty, editorial arc + pacing). Does not render; targets the my-social-builder lanes and returns critique through the campaign loop.
- `creative/email-production-loop` (`email-production-loop`): Drive a single Fig & Bloom campaign brief to a critic-approved, validated, rendered email parked as an unsent Klaviyo draft — zero human in the loop until PASS or escalation.

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

