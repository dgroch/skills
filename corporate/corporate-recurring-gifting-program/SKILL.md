---
name: corporate-recurring-gifting-program
description: Build corporate recurring gifting, EOFY programs, quote workflows, and invoice handoffs for Ledger. Use for B2B gifting program design, corporate buyer journeys, recurring occasion calendars, EOFY thank-you campaigns, quote/invoice specs, and finance handoffs.
---

# Corporate Recurring Gifting Program

This skill helps Ledger turn corporate gifting into a repeatable, margin-aware B2B program instead of one-off manual orders.

## Trigger

Use when asked to design or operate:

- corporate recurring gifting;
- EOFY or end-of-year thank-you programs;
- client, staff, referral, settlement, or event gifting calendars;
- quote and invoice flows;
- B2B landing pages or sales handoffs;
- partner gift bundles for corporate buyers.

Run `reference-brand-voice-guardrail`, `reference-spend-discipline-guardrail`, and `partnerships-gifting-pipeline` when partner items or discounts are involved.

## Program Types

| Program | Typical Buyer | Cadence | Key Need |
|---|---|---|---|
| Client birthdays | professional services, agencies | monthly | never miss dates |
| EOFY thanks | finance, property, consulting | annual | polished bulk send |
| Staff milestones | HR, people teams | monthly/quarterly | consistency and budget control |
| Referral thanks | real estate, brokers | event-triggered | fast fulfilment |
| Sympathy/care | employers, professional services | event-triggered | tone and privacy |

## Workflow

1. Define buyer, budget, cadence, recipient count, and decision deadline.
2. Build gifting calendar:
   - recipient name;
   - occasion;
   - date;
   - budget/tier;
   - message owner;
   - delivery constraints;
   - privacy notes.
3. Choose fulfilment model:
   - recurring standing order;
   - pre-funded credit;
   - quote per batch;
   - invoice after dispatch;
   - Shopify draft order.
4. Model unit economics:
   - product COGS;
   - delivery;
   - labour;
   - partner items;
   - payment terms;
   - bad-debt risk;
   - support load.
5. Specify quote and invoice handoff.
6. Create renewal and review cadence.

## Quote and Invoice Flow

Minimum fields:

- company legal name and billing contact;
- ABN if available;
- delivery contact;
- recipient count and date range;
- product/tier;
- delivery zones;
- message/card requirements;
- payment terms;
- purchase order requirement;
- finance owner;
- approval status.

Do not promise invoice terms before FinanceManager approval.

## EOFY Builder

EOFY programs need:

- lead-time calendar;
- client segmentation;
- restrained corporate copy;
- tiered budget options;
- cut-off dates;
- bulk upload template;
- substitutions policy;
- approval and invoice timeline.

## Output Format

```markdown
# Corporate Gifting Program - [Buyer/Program]

## Buyer and Objective
[summary]

## Gifting Calendar
[recipient/occasion/date/tier/status table]

## Offer and Tiers
[what is included, price, margin notes]

## Quote and Invoice Flow
[steps and owners]

## Operations Handoff
[fulfilment, delivery, support, substitutions]

## Measurement
[revenue, margin, repeat rate, referral, payback]

## Open Decisions
[Finance/CEO/customer questions]
```

## Quality Gates

- Margin and payment terms are explicit.
- Finance approves invoice terms before promise.
- Sensitive gifting uses Solace tone rules.
- Partner bundles pass unit economics and brand separation checks.
