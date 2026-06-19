---
name: lifecycle-birthday-club-flow
description: Design Birthday Club, recipient-card, reminder, and lifecycle cohort flows for Echo. Use for Klaviyo flow architecture, birthday reminder journeys, recipient acquisition loops, backend integration requirements, cohort targeting, and handoff specs for Stack and Atlas.
---

# Birthday Club Lifecycle Flow

This skill turns the Birthday Club and recipient-card strategy into lifecycle journeys that Echo, Stack, Atlas, and Conductor can implement and measure.

## Trigger

Use when work involves:

- Birthday Club flow design;
- Klaviyo automated flows for reminders, nudges, onboarding, recipient conversion, or winback;
- recipient-card acquisition loops;
- reminder backend integration requirements;
- lifecycle cohort targeting;
- handoff specs for portal, Shopify, Klaviyo, or gift-card automation.

Run `reference-brand-voice-guardrail` before writing customer copy and `reference-spend-discipline-guardrail` before adding incentives or credits.

## Required Inputs

- Program offer and tiers.
- Birthday record model: sender, recipient, date, relationship, budget, tier, consent, reminder preference.
- Trigger dates: signup, birthday minus 30/14/5/1 days, birthday day, post-delivery, recipient card redemption.
- Channels allowed: email, SMS, portal, card insert, paid retargeting.
- Data sources: Shopify, Klaviyo, portal backend, gift card app, AI helper.
- Suppression rules and sensitivity flags.

## Core Flows

### Sender Onboarding

Goal: collect birthdays once, set budget/tier preferences, and earn trust.

Events:

- `birthday_club_signed_up`
- `birthday_added`
- `tier_selected`
- `sender_preferences_saved`

Minimum messages:

1. Welcome and how the club works.
2. First birthday added confirmation.
3. Add five birthdays prompt for squad perk.

### Birthday Reminder

Goal: make sending easy without feeling automated or careless.

Default cadence:

- 30 days before: planning prompt;
- 14 days before: tier/product selection;
- 5 days before: confirm-or-skip nudge;
- 1 day before: last operational reminder only if same-day fulfilment is realistic.

### Recipient Card Loop

Goal: turn happy recipients into new senders at controlled CAC.

Rules:

- The card offer is conditional, not unconditional.
- Record card code, original order, expiry, redemption status, and source campaign.
- Suppress if the recipient opts out or has already joined.

### Post-Delivery Proof and Feedback

Goal: gather proof, learn, and feed real testimonial workflows.

Messages:

- sender delivery confirmation;
- recipient care note if consent exists;
- feedback request;
- testimonial permission ask only after a positive signal.

## Cohort Targeting

Segment by:

- new sender vs repeat sender;
- number of birthdays saved;
- upcoming birthday window;
- tier preference;
- first recipient-card redemption;
- lapsed sender;
- corporate buyer;
- sympathy-sensitive exclusions.

Do not blend acquisition, retention, and recipient conversion metrics. Report them separately.

## Backend Handoff

Create a punch-list for Stack:

- event names and payload fields;
- Klaviyo profile properties;
- Shopify tags/metafields;
- gift card or discount-code rules;
- consent handling;
- suppression logic;
- audit logs for automated sends;
- failure states and manual override paths.

## Output Format

```markdown
# Lifecycle Flow Spec - [Program]

## Journey Map
[flow table by stage, trigger, channel, message job, owner]

## Events and Data Model
[event/property table]

## Klaviyo Flow Requirements
[trigger, filters, splits, suppressions]

## Backend Punch-List
[Stack tasks]

## Copy Direction
[message intent, not final copy unless requested]

## Measurement
[activation, conversion, CAC, LTV, payback, retention]

## Open Decisions
[CEO/Conductor/Stack/Echo questions]
```

## Quality Gates

- Every automated send has a clear trigger and suppression rule.
- Customer consent and sensitivity exclusions are defined.
- Incentives have a margin/payback check.
- Copy avoids banned words and exclamation marks.
- Measurement separates sender, recipient, and returning-customer behaviour.
