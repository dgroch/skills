---
name: reference-spend-discipline-guardrail
description: Reusable spend discipline guardrail for Phase 0 CAC ceiling enforcement, payback checks, and budget reallocation. Use before approving paid media scale, creator spend, partner costs, tooling spend, or any growth experiment with financial exposure.
---

# Spend Discipline Guardrail

This skill enforces the reorg rule: no paid channel scales past the CAC ceiling until Phase 0 analytics, gross margin, and payback assumptions are signed off.

## Trigger

Use before:

- increasing paid media budgets;
- launching creator, Hashgifted, PR, partnership, or affiliate programs with spend;
- approving Bower value bundles, partner gifts, discounts, or gift cards;
- reallocating budget between channels;
- committing new tools, agencies, contractors, or subscriptions.

## Required Inputs

- Spend amount, cadence, owner, and cancellation/renewal point.
- Expected acquisition or revenue outcome.
- Gross margin assumption and source.
- CAC ceiling or, if Phase 0 is incomplete, a statement that paid scale is capped.
- Payback target and expected payback period.
- Measurement plan: Shopify, GA4, Klaviyo, ad platform, creator code, affiliate link, or manual ledger.

## Rules

- If Phase 0 CAC ceiling is not signed off, do not approve scale. Only allow tightly bounded tests with a clear stop-loss.
- Do not treat revenue as profit. Use contribution margin after product, fulfilment, discount, partner, and platform costs.
- Separate new-customer CAC from returning-customer spend.
- Separate Fig & Bloom and Bower CAC, LTV, margin, and payback.
- Stop or reduce spend when payback breaks the approved threshold, attribution is unmeasurable, or creative fatigue is visible.
- Record assumptions. A budget without assumptions is not approved.

## Decision Template

```markdown
## Spend Discipline Check

**Proposal:** [proposal]
**Amount:** [$ / cadence]
**Owner:** [owner]
**Verdict:** Approved / Approved for bounded test / Blocked

| Input | Value | Source |
|---|---|---|
| CAC ceiling | | |
| Gross margin | | |
| Payback target | | |
| Expected CAC | | |
| Expected payback | | |
| Measurement plan | | |

### Conditions
[stop-loss, reporting cadence, max spend, renewal date]
```

## Escalation

Escalate to the CEO for budget requests outside existing authority, spend that exceeds the Phase 0 ceiling, unclear payback on material spend, or any request to bypass this guardrail.
