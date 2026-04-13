---
name: seo-backlink-management
description: Paperclip SEO workflow for Backlink Management. Use this skill when you need to monitor backlink health, identify risks, and plan outreach or disavow actions.
---


# Backlink Management (Paperclip)

This skill was adapted from the CSTMR SEO specialist system for Paperclip AI.

Paperclip path mapping:
- Treat any `tracker/` paths below as relative to your Paperclip project workspace data directory.
- Keep file structures and schemas consistent across runs so other SEO skills can consume outputs.
- Replace any references to `agent.yaml` routing with your Paperclip notification or orchestration settings.


## Purpose

Monitor, analyse, and grow the client's backlink profile. Protect against toxic links. Identify link building opportunities. All domain/market context from `config/client.yaml`.

## Tools Required

- Ahrefs (backlink index, referring domains, anchor text, toxic score)
- Google Search Console (links report)
- Firecrawl (unlinked mention discovery, competitor link pages)

## Data Storage

- `tracker/data/backlinks/inventory_{date}.json` — full backlink snapshot
- `tracker/data/backlinks/changes.json` — rolling log of new/lost links
- `tracker/data/backlinks/disavow_draft.txt` — prepared disavow file (if needed)

## Modes

### `baseline`

**When:** Bootstrap step 4.
**Pre-conditions:** Pre-flight passed.

**Steps:**
1. Ahrefs site explorer: domain rating (DR), referring domains, total backlinks, dofollow ratio
2. Full backlink inventory: source URL, target URL, anchor text, DR of source, dofollow/nofollow, first seen, last seen
3. Anchor text distribution analysis:
   - Target: 40–50% branded, 20–30% natural/generic, 10–15% partial match, 5–10% exact match, 5–10% URL
   - Flag if distribution is skewed (>20% exact match = risk)
4. Toxic link assessment: links from low-DR spam domains, irrelevant niches, PBN patterns
5. Link quality distribution: score each link (Source DR × 0.3) + (Relevance × 0.3) + (Traffic × 0.2) + (Achievability × 0.2)
6. Write inventory to `tracker/data/backlinks/inventory_{date}.json`
7. Create tasks for toxic link cleanup if significant issues found
8. Create summary in state.json metadata

### `monitoring`

**When:** Wednesday 06:00 (weekly-backlinks cron).
**Pre-conditions:** Baseline exists.

**Steps:**
1. Ahrefs: new backlinks since last check, lost backlinks since last check
2. For each new link: score quality, check relevance, flag if toxic
3. For each lost link: assess impact (was it high-value?), check if recoverable (page still exists?)
4. Unlinked brand mentions: Ahrefs content explorer or Firecrawl search for brand name on external sites without a link back
5. Append to `tracker/data/backlinks/changes.json`
6. Create tasks:
   - Toxic new links → investigate / disavow candidate
   - Lost high-value links → outreach/recovery candidate
   - Unlinked mentions → outreach candidate
7. If >5 toxic links detected in one period, trigger backlink-spam event

**Budget degradation:** At circuit-breaker, check new/lost only (skip unlinked mentions). At hard-stop, skip entirely — rely on monthly deep check.

### `disavow`

**When:** Triggered by backlink-spam event or operator request.
**Decision level:** Escalate — requires operator approval before submission.

**Steps:**
1. Compile toxic link list from monitoring history
2. Verify each: is it genuinely toxic (spam domain, irrelevant, PBN)?
3. Format as Google disavow file (domain-level where appropriate, URL-level otherwise)
4. Write draft to `tracker/data/backlinks/disavow_draft.txt`
5. Create escalation task with: count, risk assessment, recommendation
6. Wait for operator approval before any action

### `strategy`

**When:** Monthly or quarterly, as part of broader strategy review.
**Decision level:** Recommend — operator reviews and approves tactics.

**Steps:**
1. Competitor backlink gap: domains linking to competitors but not to client (from competitor-analysis data)
2. Evaluate tactics:
   - Digital PR (newsjacking, data stories, expert commentary)
   - Guest posting (relevant industry blogs, local publications)
   - Resource link building (create link-worthy content assets)
   - Broken link building (find broken outbound links on relevant sites, offer replacement)
   - Local citations (directory listings — see local-seo skill)
   - Partnerships (complementary businesses, suppliers, event sponsors)
3. Anchor text plan: what anchor distribution to target given current state
4. Produce link building roadmap with priorities, estimated effort, expected impact
5. Create tasks for approved tactics
