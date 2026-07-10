# Hashgifted Trello UGC Board Integration

Use this reference whenever a Hashgifted workflow reads, writes, or reconciles creator lifecycle state. Trello is the human-facing kanban surface for Daniel and the UGC operator; Hashgifted remains the source of truth for platform status, and Notion remains the durable CRM/brief/content database.

## Board of record

- Board name: `🤖 User Generated Content`
- Board URL: `https://trello.com/b/zDpcpS3V/%F0%9F%A4%96-user-generated-content`
- Board short ID: `zDpcpS3V`

Verified open lists:

1. `START HERE / Operating Manual`
2. `Inbox / Applied`
3. `Triage / Brand Fit`
4. `Parked Applicant Pool`
5. `Needs Daniel`
6. `Shortlisted`
7. `Approved Reserve`
8. `Selected / Brief Sent`
9. `Active Q&A / Awaiting Content`
10. `Content Received`
11. `Ingested / Indexed`
12. `Ready to Schedule`
13. `Scheduled in Later`
14. `Posted / Live`
15. `Completed / Scored`
16. `Lapsed / Declined / Do Not Use`

## Role of Trello in the system

- **Hashgifted/Gifted**: source of truth for creator application/selection/completion status and message thread.
- **Notion**: source of truth for Campaigns, Briefs, creator CRM, asset manifest, and durable lifecycle memory.
- **Trello UGC board**: operational kanban and human review surface. Every live creator row should have one card per creator/campaign application whenever a workflow touches them.

Do not let Trello override live Hashgifted state. If Trello and Hashgifted conflict, trust Hashgifted, move/update the Trello card, and mention the reconciliation in the audit.

## Card identity and idempotency

Use one card per creator per campaign. Do not create one card per message or one card per content item.

Preferred card title:

```text
[HG] @handle — Campaign Name
```

If no handle is visible:

```text
[HG] Creator Name — Campaign Name
```

Before creating a card, search existing open and closed cards by:

1. exact title,
2. Hashgifted row/application UID in card description,
3. creator handle + campaign name,
4. Notion creator/page ID if available.

If a card exists, update/move it rather than duplicating it. If a duplicate is discovered, preserve the richest card, link/mention the duplicate in the audit, and do not archive/delete without explicit instruction.

## Required card content

A card in `Needs Daniel` is invalid unless Daniel can act from the card without reconstructing context. Before moving any card there, its description must contain, at the top:

1. `ACTION STATUS`.
2. `WHAT DANIEL NEEDS TO DECIDE` — the smallest specific choice, not `manual_review` or `review the thread`.
3. `RECOMMENDED HANDLING`.
4. `HOW TO ACTION` — exact supported Trello command or explicit decision wording.
5. `DECISION EVIDENCE` — location, deliverable, brief, policy exception, and latest relevant creator message.
6. A clickable Hashgifted campaign/conversation-context URL plus exact Wave/Application UID.
7. The complete latest live Hashgifted conversation transcript, clearly identifying creator vs Fig & Bloom messages.

If any of these are unavailable, do not claim the card is ready for Daniel; mark the sync/audit as `review_card_incomplete` and surface the missing source field. Cards with already-actioned approval and no newer creator inbound must remain in `Approved Reserve` or `Selected / Brief Sent`, never return to `Needs Daniel` because of an old classifier result.

Do not post recurring per-run status comments such as `Reflexed Rose sweep ... Verified in Hashgifted audit.` Routine run state belongs in the idempotent description and audit log. Comments are reserved for creator messages, Daniel commands, action confirmations, and material exceptions.

Card description should be structured and updated idempotently:

```markdown
Source: Hashgifted / Fig & Bloom UGC
Campaign: <campaign name>
Creator: <name> / @<handle>
Hashgifted row UID: <uid if available>
Hashgifted campaign URL: <url>
Notion creator: <url/id if available>
Notion campaign: <url/id if available>
Current lifecycle state: <state>
Last verified: <ISO timestamp>

Delivery eligibility:
- Metro/city: <Melbourne/Sydney/Brisbane/Unknown/No>
- Evidence: <profile/thread snippet>

Fit / decision:
- Decision: <Shortlist/Manual Review/Reserve/Selected/Complete/etc>
- Confidence: <High/Medium/Low>
- Reason: <brief reason>

Latest action:
- <what was sent/moved/captured/selected, with timestamp>

Content / assets:
- <Drive/Notion/CDN/source URLs as available>

Open questions / manual review:
- <smallest decision Daniel needs to make, if any>
```

Add comments for important lifecycle events rather than overwriting all history: message sent, qualified, selected, order booked/acknowledged, content received, asset indexed, marked complete, declined/ghosted. Also mirror Hashgifted thread messages into Trello comments with `RECEIVED MESSAGE` for creator/influencer messages and `SENT MESSAGE` for brand/Hermes messages. Include a stable `Message sync id` and skip messages whose sync id already appears on the card, so conversation logs are not duplicated across sweeps.

## Lifecycle → Trello list mapping

| Hashgifted/Notion lifecycle state | Trello list |
|---|---|
| Applied/SUBMITTED discovered, not reviewed | `Inbox / Applied` |
| Ranked applicant outside the six-week/15-position operational horizon | `Parked Applicant Pool` |
| Currently being visually/profile reviewed inside the operational horizon | `Triage / Brand Fit` |
| Commercial/policy exception, material delivery problem, or genuine brand-safety ambiguity | `Needs Daniel` |
| Shortlisted in Hashgifted, not fully qualified/selected | `Shortlisted` |
| Fully qualified but weekly/campaign cadence is full | `Approved Reserve` |
| Selected/Accepted in Hashgifted or selected + brief/order flow initiated | `Selected / Brief Sent` |
| Selected/accepted, thread needs answer, order placed/acknowledged, or awaiting content | `Active Q&A / Awaiting Content` |
| Content/story/post evidence detected but not saved/indexed | `Content Received` |
| Content saved to Drive/CDN and indexed to Notion/asset manifest | `Ingested / Indexed` |
| Asset ready for media buyer/social scheduling handoff | `Ready to Schedule` |
| Asset scheduled in Later/social tool | `Scheduled in Later` |
| Post is live/verified on social | `Posted / Live` |
| Deliverables captured, creator thanked, completed and scored | `Completed / Scored` |
| Creator declined, lapsed, ghosted, hard blocked, or do-not-use | `Lapsed / Declined / Do Not Use` |

## Workflow-specific Trello duties

### New applicant shortlist sweep

- Upsert/move touched applicants to `Inbox / Applied` before review when practical.
- Move creators under active profile/feed review to `Triage / Brand Fit` only if the run is long enough for Daniel to benefit from seeing in-progress state; otherwise skip transient movement.
- After action:
  - shortlisted → `Shortlisted`
  - outside the 15-position operational horizon → `Parked Applicant Pool`
  - routine location/fit uncertainty inside the horizon → `Triage / Brand Fit`
  - commercial/policy exception, material delivery problem, or genuine brand-safety ambiguity → `Needs Daniel`
  - clear hard blocker/decline → `Lapsed / Declined / Do Not Use`
- Record the visual-review decision, location inference, brand-fit signals, and Hashgifted status readback in the card.

### Shortlisted reply / selection sweep

- Initial qualification message sent but not yet replied → keep/move to `Shortlisted` and comment `selection_initial_sent`.
- Missing gate question or answerable Q&A sent → keep/move to `Shortlisted` unless it is post-selection Q&A.
- Fully qualified but campaign/week cap full → `Approved Reserve`.
- Select/Accept verified → `Selected / Brief Sent`.
- Accepted creator has booked/placed order or has active post-selection question → `Active Q&A / Awaiting Content`.
- Explicit negative/declined/ghost closeout → `Lapsed / Declined / Do Not Use`.

### Content capture / story capture / closeout

- Story/post/reel/content signal detected but not captured → `Content Received`.
- Asset downloaded/saved and Notion/asset manifest indexed → `Ingested / Indexed`.
- Media-buyer handoff prepared and no further capture work remains → `Ready to Schedule`.
- If Later/social scheduling is verified → `Scheduled in Later`.
- If live post is verified → `Posted / Live`.
- If Hashgifted deliverables are complete, thank-you sent, status readback verified, and creator review score recorded → `Completed / Scored`.
- If selected creator ghosts past closeout threshold with no deliverable → `Lapsed / Declined / Do Not Use`.

## Labels

Create labels if missing and apply conservatively:

- `Hashgifted`
- `Reflexed Rose`
- `Melbourne`
- `Sydney`
- `Brisbane`
- `Needs Daniel`
- `Approved Reserve`
- `Content Received`
- `Ready for Meta`
- `Do Not Use`

Do not label location as confirmed unless the creator thread or another explicit source confirms it. Profile inference can be noted as `Likely` in the description.

## API rules

- Verify Trello credentials with `GET /1/members/me` before writes. Do not print keys/tokens.
- Read board lists before moving cards; fail safely if a required list is missing.
- Use request body payloads for long descriptions/comments, not query-string-only writes.
- After any card create/move/comment/label update, read back the card and verify `idList`, title, URL, and relevant description/comment evidence.
- Include Trello card URL(s) in audit output and final cron reports.

## Failure handling

- If Trello credentials are missing or board access fails, continue Hashgifted/Notion work and report `trello_unavailable`; do not block creator safety-critical replies or story capture.
- If the UGC board/list names changed, stop Trello writes, report `trello_schema_changed`, and include the observed board/list names.
- If a Trello move fails after a successful Hashgifted send/select/content capture, do not retry risky Hashgifted actions. Report the Trello reconciliation failure separately.
