---
name: digital-pr-control-plane
description: Operate Fig & Bloom's Notion control plane for quality digital PR backlink acquisition — opportunity approval, proposed link assets, Ahrefs-backed scoring, outreach status, secured backlink logging, and Clawd publishing handoff.
version: 1.0.0
author: agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [seo, digital-pr, backlinks, notion, ahrefs, fig-and-bloom, outreach]
---

# Digital PR Control Plane

Use this skill when operating the **consumer/operator side** of Fig & Bloom's backlink acquisition workflow in Notion: reviewing link opportunities, approving proposed content, running outreach, tracking follow-ups, verifying secured backlinks, and handing approved content briefs to Clawd.

This skill documents the application usage layer. The execution mechanics for media inboxes, PR safety rules, and pitch-writing live in `digital-pr-outreach`; this skill explains how the Notion control plane should be consumed by Daniel and agents. It must not define or mutate the SEO Backlink Trello lifecycle directly: all card/list creation, moves, comments, retirement and structural changes defer to `backlink-outreach-automation`, `references/trello-unitary-board-operator.md`, `/opt/data/workspace/backlink_outreach/backlink_board_contract.json`, and the shared `BoardOperator`.

## Goal

Raise Fig & Bloom's authority above Daily Blooms while preserving brand quality.

- **Source of truth for authority/rank data:** Ahrefs.
- **Initial market boundary:** Australia only.
- **Operating principle:** quality **and** cadence — high velocity without spam, link farms, competitor-florist pitches, or low-relevance outreach.
- **Publishing boundary:** Hermes produces approval-ready briefs/Markdown; **Clawd remains the blog publisher** unless Daniel explicitly asks otherwise.

## Control Plane Location

Parent page:

| Surface | ID / URL |
|---|---|
| SEO page | `38bfdc24-425f-817e-9c85-c953c7fa0357` |
| SEO URL | `https://app.notion.com/p/SEO-38bfdc24425f817e9c85c953c7fa0357` |

Backlink-specific databases:

| Database | Database ID | Data source ID | Purpose |
|---|---|---|---|
| SEO – Websites & Publications | `2624b145-7212-4fd4-a484-b1fda81d9f84` | `f9247124-ad6b-4ae5-970c-0a38180fd722` | Site-level dedupe, authority metrics, editorial policy, contact state. |
| SEO – Link Opportunities | `9feeda10-13aa-4e86-a31c-f0ed2d4d54f5` | `602bdc58-ddbb-4a8d-9a05-6f9f916c0dea` | One row per target article/page where a link may be earned. |
| SEO – Proposed Link Assets | `48fab7c6-ab51-43a8-a7cc-1b18a8919984` | `8acdbee3-a6c7-4b2d-9dcb-cab8bfe8c70a` | Blog/resource ideas needing Daniel approval before production. |
| SEO – Backlinks Secured | `c261ea7a-c433-40d0-ad0e-5488de24ccc4` | `6071d5dc-c1ae-4165-b740-883c41cb4f14` | Verified backlink ledger and link health monitor. |

Existing PR databases to preserve:

| Database | Data source ID | Use |
|---|---|---|
| Journalist Contacts & Coverage | `3cacb1d2-fc05-4bba-b524-0a9938145f3c` | Human/outlet contact history and coverage records. |
| Press Releases | `3df591e8-385c-4e6d-a7ac-6f9939797dea` | Formal PR/press release approval workflow. |

Do **not** overload the PR databases with operational SEO details; link them by relation where relevant.

## Database Usage

### 1. Websites & Publications

Create one row per publication/site/domain.

Use it to prevent duplicate outreach and to track site-level quality.

Required operator checks:

- Is it genuinely editorial or a useful site-owner publication?
- Is it Australian or strongly Australia-relevant?
- Does it sell flowers or flower delivery? If yes, mark `Sells Flowers? = true` and usually skip.
- Is there an editorial/contact/submissions policy?
- Has this site or shared inbox been contacted recently?
- Are Ahrefs DR, organic traffic, and referring domains recorded or flagged for fill?

Recommended statuses:

- `Not Contacted`
- `Qualified`
- `Ready`
- `Pitched`
- `Follow-up Due`
- `Responded`
- `Secured`
- `Rejected`
- `No Reply`
- `Skipped`
- `Do Not Contact`

### 2. Link Opportunities

Create one row per **specific source URL**.

A good opportunity row should answer:

- What article/page are we targeting?
- Why would a Fig & Bloom link make this page more useful?
- What exact Fig & Bloom URL should be linked?
- What natural anchor text should be suggested?
- Does this require a new Fig & Bloom resource/post first?
- Is Daniel approval required before outreach?

Important properties:

- `Source URL`
- `Source Domain`
- `Article Title`
- `Niche`
- `City / Market`
- `Opportunity Type`
- `Missing Link Angle`
- `Suggested Anchor Text`
- `Suggested Target URL`
- `Requires New Post?`
- `Proposed Link Asset`
- `Approval Required?`
- `Approval Status`
- `Status`
- `Priority`
- Ahrefs metrics
- `Outreach Draft`
- `Follow-up Due`

### 3. Proposed Link Assets

Create a row when the opportunity needs a new link-worthy Fig & Bloom post/resource.

This is Daniel's content approval queue.

Valid statuses:

- `Proposed`
- `Brief Pending Approval`
- `Approved`
- `Rejected`
- `In Production`
- `Markdown Ready`
- `Published`

A proposed asset must include:

- strategic purpose
- target keyword/topic
- backlink use case
- target audience
- brief markdown
- Ahrefs keyword data if available
- related opportunities

Do not publish. Once approved, prepare Markdown for Clawd.

### 4. Backlinks Secured

Create one row per verified live backlink.

Required fields:

- `Source URL`
- `Source Domain`
- `Target Fig & Bloom URL`
- `Anchor Text`
- `Follow/Nofollow`
- `Link Type`
- `Ahrefs DR at Secured Date`
- `Ahrefs UR at Secured Date`
- `Date Secured`
- `First Verified`
- `Last Verified`
- `Status`
- relations back to opportunity, site, asset, and contact where possible

Valid statuses:

- `Live`
- `Lost`
- `Changed`
- `Redirecting`
- `Needs Recovery`

## Approval Gates

Daniel approved these rules:

### Autonomous

Agents may autonomously:

- discover prospects
- score and qualify prospects
- create/update Notion rows
- draft outreach
- skip bad opportunities
- verify backlinks
- record secured/lost links
- run low-risk AU editorial/site-owner outreach after the opportunity is approved/ready

### Daniel approval required

Daniel must approve:

- link opportunities marked approval-required
- proposed blog/resource/link assets before production
- any proposed content brief before handoff to Clawd
- images or media sent to journalists/site owners
- interviews or spokesperson requests
- paid placements or sponsored opportunities
- discounts/commercial terms
- link exchanges
- private/proprietary/sensitive data
- unverified claims or uncertain editorial risks

### Outreach approval nuance

Outreach emails themselves do **not** require approval once:

1. the Link Opportunity is approved/ready,
2. the outreach is low-risk and Australia-focused,
3. the pitch is a genuine editorial/resource update,
4. no escalation trigger is present.

If any escalation trigger appears, stop and ask Daniel.

## Prospect Quality Rules

Prioritise:

- Australian lifestyle/editorial publications
- city guides
- wedding publications
- gifting guides
- corporate/EA/admin/business resources
- wellbeing/sympathy resources
- seasonal gift guides
- existing listicles where Fig & Bloom is absent or outdated
- unlinked brand mentions
- broken/redirecting old Fig & Bloom links

Skip:

- competitor florist or flower-delivery sellers
- low-quality directories
- link farms
- paid-only placements
- sites requiring reciprocal links
- irrelevant overseas sites
- generic guest-post farms
- pages where Fig & Bloom would not genuinely help the reader

Do not pad reports with low-quality items to hit a quota. Report the skip list if the quality pool is thin.

## Ahrefs Usage

Ahrefs is the source of truth for:

- DR / domain rating
- UR / URL rating
- referring domains
- organic traffic
- keyword/rank tracker data
- keyword difficulty and volume for proposed assets

Rules:

- Never invent Ahrefs metrics.
- If direct Ahrefs access is unavailable, leave fields blank and note `Ahrefs fill required`.
- Use Ahrefs rank tracker for keyword movement rather than ad hoc SERP checks when the keyword is already tracked.
- Use ad hoc Google checks only as supplementary evidence.

## Clawd Publishing Handoff

When a proposed link asset is approved, produce Markdown for Clawd in this format:

```markdown
# Proposed Link Asset: [Title]

## Strategic Purpose

## Target Search / Ahrefs Opportunity

## Backlink Use Case

## Reader Promise

## Outline

## Required Internal Links

## Suggested External References

## Notes for Clawd
```

Update the Proposed Link Asset row:

- `Status = Markdown Ready`
- add the Markdown document/file URL if hosted
- keep `Published URL` blank until Clawd publishes

After Clawd publishes, update:

- `Status = Published`
- `Published URL = final Fig & Bloom URL`
- related Link Opportunities from `Needs Post` / `Brief Pending Approval` to `Ready to Pitch` where appropriate

## Email Sender

Daniel requested `media@figandbloom.com.au` for this workflow.

As of 2026-07-02, the tested configured inbox in Hermes was `media@figandbloom.com` with IMAP/SMTP OK. Do not send from `.com.au` until its credentials are configured and tested.

Sending rules:

- Use IMAP/SMTP PR inbox only.
- Never use `gws` or Gmail API for PR/backlink outreach.
- Never send from Daniel's personal/admin address.
- BCC admin where the configured sender policy requires it.

## High-Cadence Operating Loop

Recommended fast cadence:

1. **Daily prospecting** — find and qualify AU opportunities; write Notion rows.
2. **Daily approval queue** — Daniel reviews Link Opportunities and Proposed Link Assets.
3. **Daily outreach wave** — send low-risk approved outreach; log status and follow-up date.
4. **Follow-up wave** — one follow-up after five business days; no second follow-up unless relationship-specific reason.
5. **Backlink verification** — check replies, live source HTML, target URL, anchor, follow/nofollow.
6. **Ahrefs reporting** — update DR/UR/rank-tracker progress from Ahrefs, not guesses.

## Reporting to Daniel

A useful report should include:

- opportunities added
- opportunities needing approval
- proposed assets needing approval
- outreach sent
- follow-ups due
- secured backlinks
- high-quality skipped items and why
- Ahrefs blockers/fields needing manual fill

Keep the approval table short and action-oriented.

## Related Skills

- `digital-pr-outreach` — pitch writing, PR safety rules, inbox mechanics.
- `notion` — Notion API/database operations.
- `seo-backlink-management` — backlink monitoring concepts.
- `fig-bloom-blog-thought-leader-workflow` — editorial quality lens.
