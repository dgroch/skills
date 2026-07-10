---
name: operations-growth-control-loop
description: Run Conductor's growth operating loop across KPI dashboards, OODA reviews, budget reallocation, and phase gates. Use for KPI dashboard specs, weekly growth reviews, CAC ceiling enforcement, budget decisions, and cross-pod orchestration.
---

# Growth Control Loop

This skill gives Conductor a repeatable operating cadence for turning dashboard signals into decisions across PR, partnerships, lifecycle, creative, Bower, and engineering.

## Trigger

Use when asked to:

- design or review a KPI dashboard;
- run weekly or monthly growth reviews;
- apply an OODA loop;
- reallocate budget;
- enforce CAC ceiling and payback rules;
- coordinate cross-pod decisions;
- prepare CEO or board updates on the reorg growth plan.

Run `reference-spend-discipline-guardrail` for budget decisions and `reference-brand-separation-guardrail` when Bower is included.

## KPI Dashboard Minimum Set

| Area | Metrics |
|---|---|
| Acquisition | new customers/month, blended CAC, channel CAC, source mix |
| Retention/LTV | repeat rate, cohort LTV, payback, margin by cohort |
| Lifecycle | Birthday Club signups, birthdays added, reminder conversion, recipient-card redemption |
| Occasion | sympathy revenue, corporate revenue, conversion by collection |
| Creative | follower growth, creator assets approved, paid creative win rate |
| PR/Partners | media wins, backlinks, partner pipeline stage, bundle attach rate |
| Bower | separated CAC, AOV, contribution margin, payback |

## OODA Cadence

### Observe

Pull fresh data from Shopify, GA4, Klaviyo, ad platforms, creator tracker, partner tracker, and finance inputs.

### Orient

Explain what changed:

- signal versus noise;
- leading versus lagging indicators;
- channel quality;
- margin impact;
- operational constraints;
- brand or ethics risk.

### Decide

Choose one action per pod:

- scale;
- hold;
- cut;
- retest;
- fix instrumentation;
- ask for CEO decision.

### Act

Create or update issues with owner, deadline, metric, and decision rationale.

## Budget Reallocation Rules

- Do not scale without CAC ceiling and payback context.
- Reallocate from channels with weak payback to channels with stronger contribution margin and measurement.
- Keep test budgets bounded until signal quality is high.
- Do not let PR or creator enthusiasm override evidence and usage rights.
- Separate Bower and Fig & Bloom budgets.

## Output Format

```markdown
# Growth Control Loop - [Period]

## Dashboard Snapshot
[metric table]

## OODA Review
### Observe
### Orient
### Decide
### Act

## Budget Decisions
[channel, decision, rationale, owner]

## Blockers
[instrumentation, owner, unblock action]

## CEO Decisions Needed
[only material decisions]
```

## Quality Gates

- Every decision links to a metric or documented strategic constraint.
- Budget decisions include payback and margin context.
- Bower and Fig & Bloom are separated.
- Blockers identify owner and unblock action.
- Cross-pod actions become issues, not informal notes.
