# Medianet pickup → journalist relationship workflow

Use this procedure for recurring post-distribution pickup processing.

## Qualification

1. Open each sent release through **My Press Releases → Sent → View pickups**. Direct pickup URLs can render only the application shell unless the authenticated dashboard has been entered first.
2. Enumerate every pickup and click through to the live article.
3. Exclude exact-title release hubs, automated syndication networks, anonymous reposts, and generic `staff` reproductions.
4. Qualify only coverage with a verified individual byline or clearly responsible human editor, live URL, outlet, and publication date. A rewritten headline/body supports human handling but does not replace byline verification.

## Contact resolution

1. Search Medianet Contacts for the exact journalist.
2. If absent, search the exact outlet and inspect its indexed contacts and editorial inbox.
3. Never assign an outlet founder/editor's address to a different bylined journalist.
4. A verified shared editorial inbox may be used only when it can reasonably route to the named journalist. Record provenance as `shared editorial inbox`, not as the journalist's private email.
5. Hold ambiguous identity/routing for review; do not guess address patterns.

## Notion relationship record

Notion `Contacts & Coverage` is the relationship system of record; Trello is the campaign/action control plane.

Upsert one record per exact journalist + outlet. Dedupe by coverage URL before changing counters.

For each genuinely new article:

- increment `Coverage Count` exactly once;
- append a numbered linked entry to `Coverage Links`;
- update latest `Coverage URL` and `Coverage Date`;
- preserve all historical links;
- set `Status` to `Coverage Secured`;
- use the existing `Coverage Type` taxonomy;
- record individual/private/shared-inbox provenance in `Notes`.

If the database lacks cumulative fields, add:

- `Coverage Count` — Number
- `Coverage Links` — Rich text

After writes, read the page back and verify count, links, date, status, and URL. A rerun against the same URL must leave count and outreach state unchanged.

## Calibrated thank-you outreach

The first exact email requires Daniel's approval. Once approved, later low-risk messages may be automated for newly qualifying coverage.

Default copy:

```text
Subject: Thank you for covering our <topic> story

Hi <First name>,

Thank you for covering our <specific story/topic> in <Outlet>. We really appreciated the thoughtful way you turned the findings into a clear, useful story for your readers.

We’d love to send you a Fig & Bloom bouquet as a small thank you. If you’re comfortable sharing the best delivery address and a suitable delivery day, we’ll arrange it for you.

Thanks again for the coverage.

Dan
Fig & Bloom
```

Automation gates:

- send only for a new, uniquely identified article and recipient;
- do not send for critical/sensitive coverage, uncertain bylines, unreliable shared-inbox routing, or repeat URLs;
- do not add incentives beyond the approved bouquet;
- verify the exact Message-ID in Sent Mail before recording success;
- then update Notion `Last Contact Date` and outreach evidence in `Notes`;
- verify reruns produce no duplicate email, count, or link.

## Routine contract

A recurring processor should:

1. inspect all sent releases, not only the newest;
2. use Notion URLs as idempotency keys;
3. update Notion before sending;
4. send only after qualification and contact provenance pass;
5. verify Sent Mail;
6. optionally create/update the corresponding Trello `COVERAGE` card;
7. report new qualifying pickups, excluded syndications, Notion changes, verified sends, and held ambiguities.

## Evidence standard

Retain stable handles for every action:

- Medianet release/job ID
- pickup dashboard URL
- live article URL
- Medianet contact/outlet profile ID when available
- Notion page ID/URL
- email Message-ID
- Trello card URL when used
