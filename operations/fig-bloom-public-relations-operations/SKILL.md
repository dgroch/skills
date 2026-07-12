---
name: fig-bloom-public-relations-operations
description: Operate Fig & Bloom Public Relations workflows with Trello as the control plane, especially Medianet press-release campaigns, inbound journalist enquiries, reply drafting, approval gates, and coverage/link outcomes.
version: 1.0.0
created_by: agent
---

# Fig & Bloom Public Relations Operations

Use this skill when Daniel asks about Fig & Bloom PR, Medianet media release distribution, journalist inbound enquiries, PR Trello cards, media@ replies, quotes/interviews/assets, or PR coverage/link tracking.

## Core architecture

- **Medianet is the distribution channel, not the workflow source of truth.** Use Medianet confirmations as evidence to create/update campaign cards.
- **Trello is Daniel's live PR control plane and inbox.** If Daniel needs to read, approve, reply, supply assets, or make a decision, the card must be in the relevant PR inbox list.
- **Media Communications is relationship memory.** Record inbound/outbound messages and look up prior context before drafting replies.
- **Notion's `Contacts & Coverage` database is the journalist relationship system of record.** Every verified human-authored pickup must create or update one journalist record, increment `Coverage Count`, append the live article to `Coverage Links`, refresh the latest `Coverage URL` and `Coverage Date`, and preserve contact-source provenance (individual address vs shared editorial inbox). Trello remains the operational control plane for campaigns, approvals and next actions.
- **Thank-you automation is calibrated on the first email.** The first exact addressed thank-you/address-request email requires Daniel's approval. After Daniel approves that template/tone, later low-risk thank-yous for verified individual journalist pickups may be sent automatically; requests involving ambiguity, incentives beyond the approved bouquet, sensitive coverage or uncertain recipients still require approval.

## Daniel's PR Trello inbox lists

| List | Meaning |
|---|---|
| `Pitch Draft Ready` | Exact release/pitch copy is drafted and awaiting routine approval. |
| `Daniel Approval Needed` | Claim, quote, image, asset, commercial term, or risk decision needs Daniel/Kellie approval. |
| `Reply / Journalist Interest` | Journalist has replied; needs review/reply handling. |
| `Interview / Asset Request` | Journalist asks for quote/interview/images/data/deadline-sensitive asset; high-priority inbox. |

Preserve this mental model: do not bury cards needing Daniel's attention in `Idea Bank`, `Green-Light Scoring`, `Wide Pitching`, or status/outcome lists.

## Medianet card model

Use explicit card types:

1. `CAMPAIGN — <release title>`
   - One parent card per Medianet press release.
   - Created from a Medianet submission/distribution confirmation email, or manually before distribution.
   - Stores release copy, distribution metadata, approved talking points, asset links, and global status.
2. `ENQUIRY — <outlet/contact> — <campaign slug>`
   - One child card per journalist/contact inbound thread.
   - Created by the inbox router for a human journalist reply.
   - Links back to the parent campaign card and owns reply drafting, asset approvals, deadline handling, and outcome.
3. `COVERAGE — <outlet> — <campaign slug>`
   - Optional child card, or final state of an enquiry once coverage is live.
   - Stores verified URL, screenshot/archive evidence, backlink status, and follow-up notes.

## List interpretation for Medianet PR

| List | Medianet PR meaning |
|---|---|
| `Asset / Data Needed` | Campaign not distribution-ready; missing data/assets/quotes/photos. |
| `Pitch Draft Ready` | Release/campaign copy drafted but not approved. |
| `Daniel Approval Needed` | Claims, quotes, images, assets, or response require approval. |
| `Wide Pitching` | Medianet campaign submitted/distributed; awaiting inbound. |
| `Reply / Journalist Interest` | Human journalist enquiry received; response needed. |
| `Interview / Asset Request` | Quote/interview/image/data/deadline request. |
| `Coverage Landed` | Coverage live but backlink may be absent or unverified. |
| `Link Secured` | Live URL verified and contains the desired link. |

## Inbound router requirements

When sweeping `media@figandbloom.com`:

1. **Detect Medianet campaign confirmations.**
   - Sender domain: `medianet.com.au`.
   - Subject/body signals: `submitted`, `distributed`, `distribution`, `media release`, `press release`, `confirmation`, `campaign`, `order`.
   - Create/update `CAMPAIGN — <release title>` in `Wide Pitching` when submitted/distributed.
   - Store Medianet message-id, release title, distribution/reference ID if present, submitted/distributed timestamp, and clean confirmation evidence.
2. **Keep admin noise out of journalist workflow.**
   - Medianet onboarding, billing, newsletters, DocuSign/order admin should be recorded/admin-routed, not treated as journalist interest.
3. **Match journalist replies to campaigns before creating triage.**
   - Match by References/Message-ID, normalised subject/release title/campaign slug, body key phrase, existing child enquiry sender/outlet, then fallback to unmatched PR enquiry.
4. **Create child enquiry cards for human replies.**
   - One `ENQUIRY` card per journalist/outlet/thread.
   - Link parent and child cards both ways.
   - Move to `Interview / Asset Request` if the request asks for quote, interview, image, data, deadline, sample/product, or asset.

## Reply drafting rules

- Draft only; never send by default.
- Post exactly one Trello comment per inbound message:
  - `PROPOSED REPLY — PR enquiry`, or
  - `HOLD — Kellie/Daniel approval needed`.
- Use exact available campaign facts only. Do not invent quotes, data, embargo details, image rights, customer stories, or claims.
- Requests for founder/Kellie quote, interview, images, data, samples, commercial terms, exclusives, or deadline commitments need approval unless the campaign card already has exact approved material.
- If supplying assets, use only approved asset links/attachments recorded on the campaign card.
- Keep replies concise, human, and Australian English; use first-name greetings where the journalist name is known.

## Send policy

Current default: **no automatic journalist replies**.

If a future PR approved-reply sender is built, it must be separate from the router/drafter and require:

- enquiry card checklist `Approved to send exact PR reply` complete;
- latest `PROPOSED REPLY` passes recipient/subject/body validation;
- no internal Trello text, placeholders, code/data dumps, private data, unapproved quotes, or unsupported claims;
- Sent Mail Message-ID readback before commenting `SENT` evidence or moving cards.

## Campaign card convention

See `references/medianet-inbound-pr-data-flow.md` for the detailed campaign/enquiry card templates and data-flow design.

## Authenticated Medianet browser access

When Medianet requires interactive login, use a persistent browser identity rather than a temporary browser session. The human must enter credentials and MFA directly in the live browser; never ask them to paste secrets into chat. After login, close the initial session so state is committed, wait briefly, then open a wholly new session with the same identity and verify an authenticated Medianet page before reporting success.

See `references/persistent-medianet-browser-session.md` for the reusable Browserbase Context/live-view workflow and verification gates.

## Creating Medianet release drafts

When asked to prepare a release for review, create and verify a saved draft without submitting it. Preserve unresolved dates, names, contact details and unapproved quotes as explicit placeholders rather than inventing them. Assign saved campaign audiences through `MY LISTS`, attach only source-authentic or approved imagery, and verify text, audience and media persistence from a wholly fresh Browserbase session before reporting success.

See `references/medianet-draft-builder.md` for field mapping, Blazor/TinyMCE event requirements, image persistence checks, saved-list assignment and the final readback contract.

## Processing Medianet pickups and journalist relationships

For recurring post-distribution work, inspect every pickup through the live article, exclude automated syndication, require a verified human byline or responsible editor, and resolve contact provenance without guessing. Upsert Notion `Contacts & Coverage` by journalist + outlet, dedupe on coverage URL, increment cumulative coverage exactly once, append every article link, and verify any calibrated thank-you by Sent Mail Message-ID. Reruns must not duplicate links, counts, records, or outreach.

This proactive thank-you path is distinct from replying to inbound journalist enquiries: the first exact thank-you template requires Daniel's approval, after which only low-risk messages matching the calibrated template may be automated. Ambiguous routing, sensitive coverage, uncertain identity, or any additional incentive remains approval-gated.

See `references/medianet-pickup-journalist-relationship.md` for qualification rules, Medianet contact resolution, Notion schema/upsert requirements, approved outreach gates, idempotency checks and routine evidence handles.

## Pitfalls

- Do not interpret `Wide Pitching` as direct email sent; for Medianet it means distributed/submitted via Medianet.
- Do not use direct-email `Sent Status` for Medianet distribution. Track Medianet via Distribution Channel/Status.
- Do not let unmatched journalist replies sit only in email; create Trello enquiry cards.
- Do not auto-answer journalist enquiries just because a response draft exists.
- Do not move to `Coverage Landed` or `Link Secured` without live URL verification.
