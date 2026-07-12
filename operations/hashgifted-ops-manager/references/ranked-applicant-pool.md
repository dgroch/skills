# Ranked Applicant Pool Policy

Use this policy for Fig & Bloom Hashgifted campaigns with throttled intake and ongoing weekly gifting.

## Campaign states

`Intake Closed` is not `Completed`. An intake-closed campaign retains and progresses its existing applicant pool while accepting no new applicants.

- Weekly release: two gifts per campaign, released together on Monday in Australia/Melbourne.
- Close intake when the eligible or near-eligible pool exceeds six weeks of capacity.
- Reopen intake when it falls below four weeks.

## Ranking

Retain every applicant and rank separately per campaign.

| Factor | Points |
|---|---:|
| Brand fit | 40 |
| Content quality and reusability | 30 |
| Reliability | 20 |
| Application age | 10 |

New creators receive a neutral 10/20 reliability score when no evidence exists. Location and active-gift state are eligibility gates, not ranking bonuses.

Outreach threshold: 70/100 overall and at least 28/40 brand fit. Once reached, immediately request broad delivery-region/eligibility confirmation and transparently state that the creator is in a ranked waiting pool with no guaranteed gifting date.

When a creator first becomes `Approved Reserve`, send exactly one transparent queue-status message unless the complete Hashgifted transcript already contains one. It must say that qualification/approval does not confirm a gifting date, that weekly slots are limited, and that Fig & Bloom will message before anything is locked in. Verify exact thread readback and do not repeat the notification on later sweeps.

## Queue mechanics

- Re-rank continuously when new evidence arrives.
- Six-week Trello horizon per campaign: positions 1–12 planned, positions 13–15 alternates.
- Lock only positions 1–2 for the next weekly release; positions 3 onward may move.
- Rank a creator separately in each campaign, but allow only one active Fig & Bloom gift at a time.
- After the initial eligibility message and +3/+7-day nudges, move a non-responder to the bottom of that campaign pool. A later complete reply restores normal fit-based ranking.

## Trello

- `Parked Applicant Pool`: retained applicants outside the 15-position operational horizon.
- `Triage / Brand Fit`: near-term Applied applicants still undergoing fit/eligibility work.
- `Shortlisted`: near-term creators shortlisted in Hashgifted but not fully qualified.
- `Approved Reserve`: qualified creators inside the operational horizon while cadence is full.
- `Needs Daniel`: only commercial/policy exceptions, material delivery problems, and genuine brand-safety ambiguity.

Unknown location, ordinary rank uncertainty, intake-closed status, outside-metro status, or incomplete routine evidence are not by themselves Daniel decisions. Keep such applicants ranked but ineligible until eligibility is confirmed.

Persist the complete pool in Hashgifted/Notion and the ranked audit artifact. Every Trello card managed by this policy must show campaign position, score breakdown, eligibility state, queue state, and last-ranked timestamp. Verify every list/description write by readback.

## Implementation

- Canonical ranking/actioner: `scripts/hashgifted_ranked_pool.py`
- Canonical hybrid conversation actioner: `scripts/hashgifted_hybrid_pipeline.py`
- Canonical tests: `scripts/test_hashgifted_ranked_pool.py` and `scripts/test_hashgifted_hybrid_pipeline.py`
- Deployed runtime copies: `/opt/data/profiles/creative/scripts/`
- Latest plan: `/opt/data/profiles/creative/tmp/hashgifted-ranked-pool-plan.json`
- Latest application result: `/opt/data/profiles/creative/tmp/hashgifted-ranked-pool-apply.json`
