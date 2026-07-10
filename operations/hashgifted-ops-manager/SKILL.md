---
name: hashgifted-ops-manager
description: Manage Hashgifted influencer marketing operations through portable browser_operator workflows, including campaign setup, creator shortlisting, creator selection, monitoring, content capture, story capture escalation, closeout, run modes, approval gates, and audit logging. Use when a marketer asks to plan, run, automate, refactor, or supervise Hashgifted creator operations or build Hashgifted lifecycle skills.
---

# Hashgifted Ops Manager

## Overview

Use this as the operating brain for Hashgifted influencer campaigns. It coordinates lifecycle skills, risk controls, and audit logging while keeping browser work portable through `reference-browser-operator` and `hashgifted-browser-adapter-map`.

## Required References

- Read `reference-browser-operator` before authoring or executing browser-driven flows.
- Read `hashgifted-browser-adapter-map` before mapping Hashgifted UI intents.
- Read `references/lifecycle.md` when deciding which workflow should run.
- Read `references/audit-log.md` before any live browser action or external write.
- Read `references/story-capture.md` for Instagram story handling.
- Read `references/skill-suite.md` when authoring or refactoring the individual lifecycle skills.
- Read `references/build-state.md` before resuming the Fig & Bloom Hashgifted workflow build.
- Read `references/cron-automation.md` before registering or modifying recurring Hashgifted cron jobs.
- Read `references/notion-creator-crm.md` before designing or running creator lifecycle persistence, applicant review sync, or cross-campaign creator queries.
- Read `references/ranked-applicant-pool.md` before ranking, parking, contacting, or releasing applicants in throttled/intake-closed campaigns.
- Read `references/trello-ugc-board.md` before any Hashgifted workflow that touches creator lifecycle state; Trello is the human-facing UGC kanban and must be reconciled after Hashgifted/Notion changes.

## Architecture

Use this split:

- Skill layer: portable Hashgifted workflow instructions.
- Business brain: agent reasoning, campaign rules, creator decisions, message drafting.
- Adapter layer: Hashgifted browser intent map.
- Runtime layer: Playwright + Browserbase for production; Hermes, Claude-in-Chrome, or Camofox for exploration and fallback.

Keep the abstraction practical. Skills stay abstract; the Hashgifted adapter must be concrete, tested, and evidence-logged.

## Run Modes

Support four run modes in every Hashgifted operation:

- `plan`: inspect and say what would happen.
- `dry_run`: compose decisions, messages, filenames, and updates without clicking, sending, uploading, or writing.
- `assist`: act up to approval gates. Use this as default for live runs.
- `auto`: low-risk actions only after confidence is proven for that exact workflow.

Ask for confirmation before high-risk actions unless the user explicitly chose `auto` and the workflow has been proven.

High-risk actions include creator select, decline, exclusion, message send, mark complete, campaign status changes, and public-facing updates. Creator messages are draft-only unless the run mode is explicitly `auto` or Daniel approves the individual draft in `assist`.

## Lifecycle Dispatch

Use the first matching state from `references/lifecycle.md`. Do not dispatch the same creator twice in one cycle.

Priority order:

1. Story capture.
2. Content capture.
3. Creator closeout.
4. Creator selection.
5. Creator shortlisting.
6. Nudges and reminders.
7. Campaign setup or cleanup.

Stories decay fastest, so capture or escalate them immediately.

## Core Safety Rules

- Assume the agent is logged in, but never try to repair Hashgifted, Instagram, or Browserbase authentication inside a business skill.
- If Instagram story capture returns 401 or checkpointing, report: `IG story capture session expired; manual re-auth required.`
- Use Notion, Drive, and CDN skills or tools through their own interfaces; do not route non-browser work through `browser_operator`.
- Never invent creator facts, content details, delivery addresses, post status, or message history.
- Screenshot before and after high-risk browser actions.
- Write or return an audit record for every run.

## Message Tone

Use warm, professional, plain-spoken Australian English. Keep creator messages short and specific. Avoid corporate phrasing, salesy language, overpromising future work, internal jargon, or framing deliverables as homework.

## Fig & Bloom Delivery Eligibility

Hashgifted campaigns are deliverable only to Melbourne, Sydney, and Brisbane metro areas. Before a creator can be selected, confirm they live in one of those metro areas. If location is unknown or only loosely inferred, ask the creator during the selection/qualification message rather than declining on weak evidence. A creator “30km out of Brisbane” qualifies as Brisbane metro for profile-inference purposes; use the same <=30km rule for Melbourne/Sydney/Brisbane unless overridden.

## Notion Creator CRM

Use the Notion Creators DB as the persistent lifecycle memory for creators. Store status, campaign relation, location inference/confirmation, metrics, and visual-feed properties there so future campaign applications can reuse prior work and the business can query creator history. See `references/notion-creator-crm.md`.

## Trello UGC Kanban

Use the `🤖 User Generated Content` Trello board as the operational kanban for Hashgifted creators. For every touched creator/campaign row, upsert or move the matching Trello card according to `references/trello-ugc-board.md`, then verify readback. Hashgifted remains source of truth for platform status and Notion remains source of truth for CRM/brief/assets; Trello mirrors the workflow state for Daniel and operators.

If Trello credentials/board access are unavailable, continue safe Hashgifted/Notion actions and report `trello_unavailable`; do not pretend the kanban was moved.

## Build Order

Prefer this order for the Hashgifted skill suite:

1. `reference-browser-operator`
2. `hashgifted-browser-adapter-map`
3. `hashgifted-campaign-init`
4. `hashgifted-creator-shortlist`
5. `hashgifted-creator-select`
6. `hashgifted-creator-monitor`
7. `hashgifted-content-capture`
8. `hashgifted-creator-close`
9. `hashgifted-story-capture`
