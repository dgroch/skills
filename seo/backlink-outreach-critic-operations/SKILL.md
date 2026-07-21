---
name: backlink-outreach-critic-operations
description: Run phased Daniel-proxy critic review for Fig & Bloom backlink outreach Trello cards, including digest UX, pass/fail feedback capture, and safe rollout from review-only to low-risk auto-approval.
version: 1.0.0
created_by: agent
---

# Backlink Outreach Critic Operations

Use this when reducing Daniel’s Trello review burden for Fig & Bloom backlink outreach, or when operating a critic/approver agent over backlink Trello cards.

## Operating principle

The critic acts as a Daniel-proxy reviewer, not an unrestricted sender. Roll out authority in phases and keep all decisions auditable on Trello and in the local feedback dataset.

## Rollout phases

1. **Phase 1 — review-only calibration**
   - Comment `CRITIC REVIEW:` decisions on Trello.
   - Deliver a compact digest to Daniel.
   - Store decisions in SQLite.
   - Do **not** tick send gates.
   - Do **not** send emails.
2. **Phase 2 — low-risk auto-approval**
   - Only after Daniel explicitly approves moving phases.
   - Critic may tick `Approved to send exact draft on this card` only for low-risk, high-confidence cases.
   - Existing send actioner still owns business-hours SMTP send and Sent Mail verification.
3. **Phase 3 — feedback learning and sampled QA**
   - Sample auto-decisions for Daniel review.
   - Extract repeated fail reasons into rubric updates.
4. **Phase 4 — exception-only review**
   - Daniel sees high-risk, low-confidence, unusual, or sampled cases only.

## Digest UX requirements

Daniel may review a digest hours later after newer digests have arrived. Therefore:

- Every digest table must include a dedicated clickable link column, e.g. `[Open card](https://trello.com/c/...)`.
- Do not hide the only link behind a long truncated card title; Telegram table rendering can make that hard to tap.
- Every digest must append a **Reply key** with a stable digest ID.
- Feedback examples must include the digest ID so numbered replies resolve to the intended list.

Example footer:

```text
## Reply key

Digest ID: `abc123-def456`

Please include the digest ID when replying later, so item numbers do not get confused if a newer digest has arrived.

critic examples:
digest abc123-def456: critic 1 pass
digest abc123-def456: critic 2 fail - should not escalate, this is routine
digest abc123-def456: all pass except 4
```

## Feedback capture

Feedback should be stored as structured preference data, not just chat text:

- decision ID;
- digest ID;
- Trello card URL;
- decision/risk/confidence;
- Daniel verdict: pass/fail;
- Daniel correction note;
- timestamp.

Also comment the feedback back onto the Trello card when possible.

When Daniel marks numbered digest items as `pass`, record the feedback and, if he asks to progress them, tick `Approved to send exact draft on this card` for those passed item numbers only. Do not tick failed/rewrite items. After ticking gates, run a sender dry-run and report which cards would send, which are blocked, and why. Keep the language sharp: **passed / approved / draft posted are not the same as sent**. Only call something sent after Trello has a `SENT:` comment with Message-ID/Sent Mail verification and the card has moved to `Outreach Sent`.

## Auto-approval safety gates

Never auto-approve/send if a card involves:

- paid placement, invoices, contract, legal, sponsorship, discounts, contra, or commercial terms;
- journalist quote, spokesperson, interview, media asset/image request, or PR-sensitive request;
- unsupported claims such as `#1`, `best`, `leading`, `guaranteed`;
- placeholders, internal notes, or Trello/control-plane text in the proposed email body;
- `Do Not Send` label/checklist/comment;
- unclear recipient identity or generic mailbox domain;
- disavow, link-secured claims, or public statements.

## Implementation pattern

Recommended files:

```text
/opt/data/profiles/director/scripts/backlink_critic_approver.py
/opt/data/profiles/director/scripts/backlink_critic_feedback.py
/opt/data/workspace/backlink_outreach/backlink_critic_feedback.sqlite
/opt/data/profiles/director/cron/state/backlink_critic_approver.json
```

Schedule Phase 1 as a no-agent cron, delivered to origin, so Daniel receives review digests:

```bash
hermes --profile director cron create 'every 120m' \
  --name 'backlink-critic-approver-phase1' \
  --deliver origin \
  --script backlink_critic_approver.py \
  --no-agent
```

## Pitfalls

- Freeze and persist the LIVE critic `run_id`, independent `critic_context_id`, provider, model and generated timestamp before launching the once-per-batch communications indexer. If refresh begins before run identity exists, fail closed rather than attaching the mailbox evidence to a retroactively created identity.
- The atomic preflight module's `freshness(connection, max_age_minutes=...)` currently returns `(overall_fresh, rows)`, where `rows` is a list of SQLite rows with `mailbox`, `fresh`, `age_minutes`, and `last_error`. Sanitise this into role indexes before persisting/reporting it; do not assume the details value is a dict, and do not print mailbox identifiers or message bodies.
- A publisher-owned page proving an exact address is insufficient when its own route label conflicts with the request. For example, an address labelled `general editorial enquiries (not submissions)` cannot safely receive copy that both offers contributed text and pitches a related piece. Fail closed as Revise, preserve the exact hash, and require the rewrite to choose one route before fresh criticism.
- Do not advance phases automatically just because the script works; Daniel must explicitly approve Phase 2+.
- Do not produce numbered digests without a digest ID; delayed feedback will become ambiguous.
- Do not make the card link hard to tap on Telegram.
- Do not send parser artefacts: strip `CRITIC VERDICT`, `ANGLE BRIEF`, `APPROVAL GATE`, Trello/internal notes, and placeholder signatures before SMTP; unresolved placeholders must block send. The approved-send actioner should run final pre-send validation for recipient, subject, and body, blocking control-plane text, copied email headers, code fences, JSON/YAML-like dumps, stack traces, env/secret-looking lines, TODO/TBD/TK/template placeholders, overlong bodies, and missing simple greeting/signature.
- Do not send domain-slug greetings such as `Hi Mumsoftheshire team,`. For team greetings, normalise compressed domain/title-case strings into human-readable outlet names (for example `Mums of the Shire`, `Better Built Homes`, `What She Just Said`) before send; prefer a real person name when known. Treat this as an approval blocker, not a cosmetic issue.
- Do not approve stale or irrelevant Fig & Bloom source assets. In particular, reject outreach that pushes old 2019/2020 seasonal Fig & Bloom blog posts (e.g. Valentine's Day/Father's Day/Mother's Day posts) as replacement assets for stale external guides. Require a current, relevant asset or a rewrite.
- Do not approve cold, transactional backlink copy. Outreach should sound interested, earnest, warm, and collaborative. Include a soft optional offer to contribute something useful the author may not have time to create — e.g. a guest paragraph, expert florist note, short quote, or practical tip — without making it feel like a quid pro quo. If this offer is missing but the rest is good, record it as a calibration note; for auto-approval, prefer drafts that include it.
- Never approve drafts that leak internal critic output (`CRITIC VERDICT`, JSON, word counts, parser notes), or that read like scraped context pasted into a sentence rather than a human note from Dan.
- Do not sign as `the Fig & Bloom team`; sign as `Dan` / `Dan Groch`.
- Do not mark `Link Secured` from a positive reply alone; verify the live backlink first.
- Do not let the critic become the sender; keep sending isolated in the approved-send actioner with SMTP and Sent Mail verification.
