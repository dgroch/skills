# OpenClaw Skills

A shared collection of agent skills for OpenClaw deployments. Each skill is self-contained and designed to be installed into an agent's `skills/` directory.

## Skills

### deputy-connector

A general-purpose connector for the Deputy staff rostering platform. Provides helper scripts and API reference for working with Deputy's full resource model — employees, rosters, timesheets, leave, locations, and more.

Requires: Deputy subdomain + API token (from the Deputy web interface).

---

### fig-bloom-rostering

A workflow skill for building optimised weekly staff rosters. Combines revenue data from Shopify with employee availability and leave data from Deputy to construct rosters that stay within a target labour budget (default: 8.5% of gross revenue).

The workflow follows a clear priority order: full-time staff first (fixed hours), then part-time minimums, then casuals to fill remaining gaps. The skill includes scripts for fetching the necessary data and a reference guide for the business rules.

Requires: Deputy (subdomain + token) + Shopify (store domain + Admin API token).

---

### Paperclip SEO skill set

Imported/adapted from the CSTMR SEO specialist workflows for use in Paperclip:

- analytics-reporting
- backlink-management
- competitor-analysis
- content-strategy
- copywriter-handoff
- keyword-research
- local-seo
- on-page-specs
- rank-tracking
- site-architecture
- task-tracker
- technical-audit

---

## Installation

```
clawhub install <skill-name>
```

Or copy the skill directory directly into your agent's `skills/` folder.
