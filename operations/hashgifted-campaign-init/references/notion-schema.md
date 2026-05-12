# Notion Schema

Use these data source IDs and property names for Hashgifted campaign setup.

## UGC Hub

- UGC hub page: `https://www.notion.so/35bfdc24425f80b199dfea0d2b615ab9`
- Briefs data source: `collection://cc0a447f-7d17-4f26-9d2f-dcf007549a7a`
- Campaigns data source: `collection://a8602813-2cca-4f84-8c99-fad58b5c014b`
- Creators data source: `collection://221846a5-866d-43ef-bb19-6883fe1c2bdb`

## Campaigns

Writable properties:

- `Campaign Name` title
- `Status` select: `Planning`, `Open for Applicants`, `Active`, `Wrapping`, `Complete`, `Paused`
- `Hard Gates` text
- `Deliverables` text
- `Target Selected` number
- `Deadline Window` text
- `Notes` text
- `Briefs` relation to Briefs
- `Creators` relation to Creators

For campaign-init, set `Status` to `Planning`.

## Briefs

Writable properties:

- `Brief Name` title
- `Status` select: `Draft`, `Published`, `Archived`
- `Concept Hook` text
- `Public Link` URL
- `Campaigns Using This Brief` relation to Campaigns

For campaign-init, set `Status` to `Published`, but leave `Public Link` empty until the marketer manually enables Share-to-web and pastes the public URL.

## Creators

Campaign-init does not normally create creators, but downstream lifecycle skills must use the Creators DB as the persistent CRM. See `hashgifted-ops-manager/references/notion-creator-crm.md` for the canonical schema, creator upsert script, and the rule that “30km out of Brisbane” qualifies as Brisbane for metro inference.

Core writable properties:

- `Creator Name` title
- `Handle` text
- `Instagram` URL
- `TikTok` URL
- `Location` text
- `Tier` select
- `Status` select: `Active`, `Preferred`, `Excluded`, `Archived`
- `Hashgifted Stage` select
- `Application Status` select
- `Decision` select
- `Decision Confidence` select
- `Metro Area` select
- `Metro Eligible` select
- `Location Confidence` select
- `Distance From Metro Km` number
- `Followers` number
- `Engagement Rate` percent number
- `Visual Review Status` select
- `Brand Fit` select
- `Content Quality` select
- `Reel Ability` select
- `Audience Fit` select
- `Engagement Quality` select
- `Brand Safety` select
- `Content Themes` multi-select
- `Visual Style` multi-select
- `Visual Evidence` text
- `Fit Signals` text
- `Risk Notes` text
- `Last Contacted` date
- `Last Reviewed` date
- `Last Visual Review` date
- `Notes` text
- `Campaigns` relation to Campaigns
