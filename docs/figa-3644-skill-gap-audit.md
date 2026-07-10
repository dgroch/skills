# FIGA-3644 Skill Gap Audit

Source scope: FIGA-3644, FIGA-3643, FIGA-3642, FIGA-3645, and FIGA-3646. Current repo coverage was checked against the skills present on `origin/main` before these additions.

| Capability | Agent(s) needing it | Existing skill? | Action |
|---|---|---|---|
| Founder thought leadership | Herald | No dedicated PR skill | Added `publicity-earned-media-engine` |
| Data-PR storytelling | Herald, Bloom, Conductor | Partial SEO/reporting only | Added `publicity-earned-media-engine` with data story and evidence ledger workflow |
| Media-list building | Herald | No | Added `publicity-earned-media-engine` |
| Journalist pitch writing | Herald | No | Added `publicity-earned-media-engine` |
| PR ethics, testimonial verification, no fake quotes | Herald, Muse, Solace, Broker | Partial copy QA only | Added `reference-pr-ethics-guardrail` |
| Partner scouting | Broker, Ledger, Bower Ops | No dedicated partner pipeline | Added `partnerships-gifting-pipeline` |
| Partner deal tracking | Broker, Ledger, Conductor | No | Added `partnerships-gifting-pipeline` |
| Partner unit economics | Broker, Ledger, Bower Ops | Partial finance discipline missing | Added `partnerships-gifting-pipeline`; reinforced by `reference-spend-discipline-guardrail` |
| Occasion collection curation | Solace | Partial campaign/product selection only | Added `occasion-sympathy-curation` for sensitive occasion curation |
| Bereavement tone review | Solace, Herald, Ledger | Partial copy QA only | Added `occasion-sympathy-curation` plus `reference-brand-voice-guardrail` |
| B2B funeral outreach | Solace, Herald, Broker | No | Added `occasion-sympathy-curation` with funeral/care outreach inputs |
| Corporate recurring gifting | Ledger | No | Added `corporate-recurring-gifting-program` |
| EOFY program builder | Ledger, Echo | No | Added `corporate-recurring-gifting-program` |
| Quote/invoice flow | Ledger, FinanceManager | No dedicated skill | Added `corporate-recurring-gifting-program` with finance approval gate |
| Klaviyo flow design | Echo | Partial email campaign builder | Added `lifecycle-birthday-club-flow` for lifecycle automation architecture |
| Birthday Club flow | Echo, Stack, Atlas, Conductor | No | Added `lifecycle-birthday-club-flow` |
| Reminder backend integration | Echo, Stack | No | Added `lifecycle-birthday-club-flow` backend handoff |
| Lifecycle cohort targeting | Echo, Conductor | Partial analytics/reporting only | Added `lifecycle-birthday-club-flow` |
| Hashgifted campaign runner | Muse, Buzz | Partial operations/hashgifted skills present | Added `creative-creator-ugc-engine` to connect Hashgifted ops to creator strategy, rights, and testimonial evidence |
| Testimonial reel production | Muse, Herald | No | Added `creative-creator-ugc-engine` |
| Creator outreach sequencing | Muse | Partial Hashgifted ops | Added `creative-creator-ugc-engine` |
| Brand separation checks | Bower Ops, Conductor, all new SOULs | No reusable guardrail | Added `reference-brand-separation-guardrail` |
| Value bundle builder | Bower Ops, Broker | No | Added `operations-bower-launch-control` |
| CAC payback tracker | Bower Ops, Conductor | Partial SEO/analytics only | Added `operations-bower-launch-control`; reinforced by `reference-spend-discipline-guardrail` |
| KPI dashboard | Conductor, CTO, DataAnalyst | Partial analytics/reporting only | Added `operations-growth-control-loop` |
| OODA loop runner | Conductor | No | Added `operations-growth-control-loop` |
| Budget reallocation rules | Conductor, Bower Ops, paid teams | No reusable spend gate | Added `operations-growth-control-loop` and `reference-spend-discipline-guardrail` |
| AU English, banned-word list, no exclamation marks | All new SOULs, creative, PR, lifecycle | Partial copy QA and email references | Added `reference-brand-voice-guardrail` |
| Spend discipline and Phase 0 ceiling enforcement | Conductor, Bower Ops, Broker, Muse, paid media | No reusable guardrail | Added `reference-spend-discipline-guardrail` |

## Recommended Targeted Assignments

Assign after merge and import; do not assign broadly.

| Skill | Recommended agents |
|---|---|
| `reference-brand-voice-guardrail` | Conductor, Herald, Broker, Solace, Ledger, Echo, Muse, Bower Ops, Buzz, Bloom, Atlas |
| `reference-pr-ethics-guardrail` | Herald, Muse, Solace, Broker, Conductor |
| `reference-brand-separation-guardrail` | Bower Ops, Conductor, Broker, Ledger, Muse, Buzz |
| `reference-spend-discipline-guardrail` | Conductor, Bower Ops, Broker, Muse, Ledger, paid media agents when reactivated |
| `publicity-earned-media-engine` | Herald; optionally Bloom for data-PR SEO handoffs |
| `partnerships-gifting-pipeline` | Broker, Ledger, Bower Ops |
| `lifecycle-birthday-club-flow` | Echo, Stack, Atlas, Conductor |
| `occasion-sympathy-curation` | Solace, Herald, Ledger |
| `corporate-recurring-gifting-program` | Ledger, Broker, FinanceManager |
| `creative-creator-ugc-engine` | Muse, Buzz, Herald |
| `operations-bower-launch-control` | Bower Ops, Conductor |
| `operations-growth-control-loop` | Conductor, CTO, DataAnalyst |

## Coordination Notes

- WorkforceManager owns FIGA-3643 SOUL drafts. These skills should be referenced in the new SOULs rather than copied wholesale.
- CEO should review the four guardrail modules before Phase 1 build starts, because they set cross-agent operating constraints.
- After merge and Paperclip import, use targeted `desiredSkills` syncs per role rather than adding every skill to every agent.
