---
name: conversion-intelligence
description: >-
  Closed CRO learning loop for Fig & Bloom. On a heartbeat, reads the GA4 funnel
  and Shopify outcomes, ranks drop-off by lost-revenue impact, refreshes an
  ICE-scored hypothesis backlog, reads live Mida experiment results, and logs
  every step to the Notion CRO ledger. Observe → Hypothesise → Test → Read →
  Decide + Log → repeat.
when_to_use: >-
  Runs autonomously on a heartbeat (daily observe + weekly readout), not as a
  manual session. Invoke manually only to backfill a window, re-read a closed
  test, or debug the loop.
owner: CRO
surface: Notion (CRO — Conversion Intelligence Programme)
inputs: [GA4 Data API, Shopify Admin API, Mida V2 API]
outputs: [CRO — Hypotheses, CRO — Tests, CRO — Run Log]
---

# Conversion Intelligence Programme

A Paperclip skill that runs a closed CRO learning loop for **Fig & Bloom**
(`figandbloom.com.au`). It ingests **events and metrics, never raw recordings**,
finds where revenue leaks out of the funnel, proposes prioritised experiments,
reads their results, and writes everything to Notion so the loop is observable
and compounds.

## Entry conditions

Run when **any** of these is true:

- The heartbeat fires (daily observe, or the weekly readout — see `cron/heartbeat.md`).
- An operator needs a specific window backfilled (`--mode manual --window-days N`).
- A Mida test has closed and its result needs reading into the ledger.

**Do not run** if:

- GA4 credentials are missing/invalid — without the funnel there is no Observe
  step; the loop will write a `Failed` Run Log row and exit non-zero. Fix creds first.
- You are tempted to ingest session recordings or mutate GA4/analytics config — out of scope, hard no.

Pre-flight before first scheduled run: `python loop.py --check`, then
`--dry-run`, then a real run (see README).

## Decision tree (the loop)

```
OBSERVE
  ├─ GA4: funnel_report(window [, compare]) → sessions per locked step, drop-off %,
  │        segmented by device / channel / landing page
  └─ Shopify: orders_summary(window) → orders, AOV, currency
              abandoned_checkouts(window) → count + lost $ (the checkout→purchase bleed)
        │
        ▼
DETECT  rank each funnel transition by REVENUE AT RISK, not raw CVR:
        revenue_at_risk = lost_sessions × P(purchase | reached 'to' step) × AOV
        (final transition collapses to lost × AOV ≈ abandoned-checkout value)
        → worst transition = top drop-off
        │
        ▼
HYPOTHESISE  for the top N bleeding transitions:
        pick the playbook candidate for that transition (tacit knowledge),
        score ICE = Impact(from revenue rank) × Confidence × Ease,
        upsert to CRO — Hypotheses (idempotent on dedup key = "<transition>|<slug>").
        Never overwrite a hypothesis that an operator has moved past Backlog.
        │
        ▼
READ TESTS  if Mida reporting API configured → list experiments,
        for each live/closed one → get_results → normalise per variant (RPV/AOV/lift),
        decide(significance, winner) → Ship / Kill / Continue / Pending,
        upsert to CRO — Tests (idempotent on Mida experiment key).
        else if GA4 bridge → read mida_conversion/mida_execute by variant for named tests.
        │
        ▼
DECIDE + LOG  append one CRO — Run Log row: window, top drop-off, actions taken,
        records touched, status (OK / Partial / Failed).
```

## Quality gates

A run is healthy only if **all** hold:

1. **Funnel measured consistently** — every read uses `funnel.py`'s locked steps
   and GA4 events. If a GA4 event is missing, fix the tagging; never silently
   swap the event.
2. **Windows end on yesterday** — no partial-day data in a read.
3. **Ranking is revenue-first** — the top drop-off is chosen by `revenue_at_risk`,
   not by the largest percentage on a low-traffic step.
4. **Writes are idempotent** — re-running the same window updates records, never
   duplicates them (hypotheses keyed on dedup key, tests on Mida key).
5. **Exactly one Run Log row per run** — even on failure. If there's no Run Log
   row, the run didn't really happen.
6. **No mutation of analytics** and **no recording ingestion** — read-only on GA4,
   events/metrics only.
7. **A real drop-off yields a ranked hypothesis** — if the funnel shows a bleed and
   the backlog didn't change, investigate the playbook mapping.

## Failure modes

| Symptom | Likely cause | Response |
|---|---|---|
| `Failed` Run Log, GA4 init error | bad/missing service account or property id | Loop exits non-zero by design. Fix creds; do not proceed without the funnel. |
| `Partial` Run Log, Shopify error | token scope/expiry, API version drift | Funnel still ranks (uses AOV=0 → revenue_at_risk degrades to 0, ranking falls back to drop-off size). Restore `read_orders`/`read_checkouts`. |
| Mida results look empty / wrong fields | live result JSON differs from the defensive parser | Inspect `_raw` in `mida.py._normalise_result`; adjust field mapping. **Do not invent fields.** |
| Mida reporting API unavailable | no API key, or plan without reporting | Set `MIDA_BRIDGE_TESTS` and read via the GA4 bridge instead. |
| Duplicate hypotheses/tests in Notion | dedup key changed, or integration lacks query access | Keep slugs/keys stable; confirm the integration is shared on the parent page. |
| Notion 401/404 | integration not shared on the parent page | Add the integration under the page's *Connections*. |
| Rankings dominated by tiny-traffic steps | low-volume noise | revenue weighting already mitigates; if needed add a min-session floor in `rank_dropoffs`. |

The loop **fails soft**: each stage is isolated, errors are captured into the Run
Log's *Actions taken*, and a hard failure (no funnel) is the only thing that
exits non-zero.

## Tacit knowledge

- **Gifting funnel ≠ generic ecommerce.** For Fig & Bloom the recurring bleed is
  *delivery certainty and total price*. PDP→cart and checkout→purchase plays in
  `playbook.py` lead with delivery-date clarity, all-in pricing, and express
  wallets for exactly this reason.
- **Abandoned-checkout dollars are the truth signal for the last step.** When GA4
  shows a checkout→purchase bleed, Shopify's abandoned-checkout value sizes it in
  real dollars — that's the join key between behaviour and outcome.
- **Rank by money, not percentage.** A 70% drop on a step 30 people reach matters
  less than a 25% drop on a step 8,000 reach. `revenue_at_risk` encodes this.
- **Impact is earned, Confidence/Ease are priors.** Impact comes from the revenue
  rank each run; the playbook only supplies Confidence/Ease priors. So the backlog
  re-sorts itself as the funnel shifts.
- **Don't trample operator decisions.** Once a hypothesis leaves `Backlog`
  (someone promoted it to Testing/Shipped/Killed), the loop refreshes evidence and
  priority but leaves Status alone.
- **Mida is delivery-side first.** Its SDKs assign variants and track events; the
  *results* read is the V2 reporting API (`/experiment/{id}/result`) with the GA4
  bridge as the real fallback. Never fabricate a results endpoint.
- **Weekly readout is where decisions live.** Daily keeps the backlog warm; the
  weekly pre/post compare is when trends are trustworthy enough to ship/kill.

## Handoff protocol

- **Owner:** `CRO` (configurable via `CRO_OWNER`). The heartbeat is wired as a
  Claude Code / Cowork routine rather than a dedicated VPS agent.
- **Build vs run:** Stack builds and maintains the skill; the routine operates it.
- **Surface:** the **CRO — Conversion Intelligence Programme** Notion page and its
  three databases are the only handoff surface — no separate dashboard or report.
- **What downstream consumers read:**
  - *Hypotheses* (Backlog/Testing) → whoever builds the Mida experiment.
  - *Tests* with a `Ship`/`Kill` decision → whoever ships or reverts the change.
  - *Run Log* → operators monitoring loop health; `Partial`/`Failed` rows carry the error.
- **To pause:** disable the heartbeat routine. The ledger persists; the next run
  resumes idempotently with no duplicate records.
- **Escalate to a human** when a test result implies a large/architectural change,
  when the Mida result parser stops matching the live payload, or when GA4 tagging
  drift breaks the locked funnel.
