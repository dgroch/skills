# Medianet Inbound PR Data Flow

Use this reference when wiring or auditing Fig & Bloom PR workflows after Medianet distribution.

## Current verified operating posture

- `media-inbox-router` reads `media@figandbloom.com`, records Media Communications memory, routes backlink replies to backlink Trello, routes PR/journalist replies to Public Relations Trello, and never sends replies.
- `media-reply-response-drafter` drafts `PROPOSED REPLY` or `HOLD` comments on Trello and never sends replies.
- **Trello is the operational control plane** for campaigns, approvals and next actions.
- **Notion `Contacts & Coverage` is the journalist relationship system of record** for contact provenance, cumulative coverage count and article-link history.
- `public-relations-trello-notion-sync` is a supporting dashboard sync; a sync error must not erase or override either source of truth.

## Daniel's inbox convention

Daniel's practical inbox is the Trello list containing cards that need his decision.

PR/Medianet inbox lists:

- `Pitch Draft Ready` — exact release/pitch copy awaits routine approval.
- `Daniel Approval Needed` — claims, quotes, assets, commercial terms, or risky decisions need approval.
- `Reply / Journalist Interest` — human journalist reply needs review/reply handling.
- `Interview / Asset Request` — quote/interview/image/data/deadline request; high-priority.

Backlink inbox lists for related workflows:

- `Angle / Draft Ready` — exact outbound backlink draft awaits send approval.
- `Approval Needed` — sensitive/risky backlink draft or opportunity needs Daniel review.
- `Reply Received` — inbound reply needs handling/verification.

## Data flow

```text
Medianet confirmation email
        ↓
Create/update CAMPAIGN card in PR Trello
        ↓
Journalist reply arrives at media@
        ↓
media-inbox-router matches to campaign
        ↓
Create ENQUIRY child card
        ↓
media-reply-response-drafter posts PROPOSED REPLY or HOLD
        ↓
Daniel/Kellie approves / supplies quote/assets
        ↓
Manual send or future approved PR reply sender
        ↓
Coverage verified → Coverage Landed / Link Secured
```

## Card types

### `CAMPAIGN — <release title>`

One parent card per Medianet press release. Include:

```markdown
## Campaign
Type: Medianet press release
Campaign slug: <stable-slug>
Release title: <title>
Distribution channel: Medianet
Distribution status: Submitted to Medianet | Distributed | Cancelled
Medianet confirmation email/message-id: <message-id>
Medianet distribution/reference id: <id if present>
Submitted at: <timestamp>
Distributed at: <timestamp if confirmed>

## Release
Headline: <headline>
Approved release copy/source: <file/link or pasted short summary>
Embargo: None | <date/time/timezone>
Regions/categories: <Medianet targeting>

## Approved spokespeople / facts
- Approved spokesperson: <name/title>
- Approved quote(s): <exact approved quotes or link>
- Approved claims/data: <facts only>
- Forbidden claims: <anything not to say>

## Assets
Approved image folder/link: <Drive/CDN/Trello attachment>
Usage notes/credits: <notes>
Assets needing approval: <yes/no + details>

## Inbound tracking
Child enquiries:
- <Trello card URL> — <outlet/contact/status>

## Outcome
Coverage URLs:
- <url> — coverage/link status
```

### `ENQUIRY — <outlet/contact> — <campaign slug>`

One child card per journalist/contact thread. Include:

```markdown
## Inbound journalist enquiry
Parent campaign: <campaign card URL>
Campaign slug: <stable-slug>
From: <name> <email>
Outlet: <outlet if known>
Subject: <email subject>
Received at: <timestamp>
Message-ID: <message-id>
Deadline: <deadline if any>
Request type: interest | quote | interview | image/assets | data | product/sample | correction | other
Risk level: routine | approval-needed | high-risk

## Original message snippet
<clean snippet; no quoted thread dump>

## Routing decision
Route reason: <message-id/subject/domain/medianet campaign match>
Confidence: <score>

## Required action
- Draft reply
- Ask Daniel/Kellie for approval
- Supply approved assets
- Verify coverage

## Reply status
Draft status: none | proposed | approved | sent manually | sent by approved sender
Latest proposed reply comment: <date/comment marker>
```

## Medianet confirmation detection

Create/update campaign cards when:

- sender domain is `medianet.com.au`; and
- subject/body indicates `submitted`, `distributed`, `distribution`, `media release`, `press release`, `confirmation`, `order`, or `campaign`.

Do **not** create journalist workflow cards for Medianet onboarding, billing, newsletters, DocuSign/order admin, or platform updates. Record/admin-route those only.

## Matching journalist replies

Order of confidence:

1. Message-ID / References matching a campaign confirmation or prior enquiry thread.
2. Normalised subject contains release title or campaign slug.
3. Body mentions release title/key phrase.
4. Sender/outlet already has a child enquiry under the campaign.
5. Fallback: create unmatched `ENQUIRY` in `Reply / Journalist Interest`.

Move to `Interview / Asset Request` if the message asks for quotes, interviews, images, data, samples/products, deadlines, or assets.

## Send policy

Default: no automatic journalist replies. Draft on Trello only.

Future approved PR reply sender must require an explicit approval checklist, final body validation, and Sent Mail Message-ID verification before moving/commenting sent evidence.
