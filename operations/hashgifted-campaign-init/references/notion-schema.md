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

Campaign-init does not create creators. Downstream skills may use:

- `Creator Name` title
- `Handle` text
- `Instagram` URL
- `TikTok` URL
- `Location` text
- `Tier` select
- `Status` select: `Active`, `Preferred`, `Excluded`, `Archived`
- `Last Contacted` date
- `Notes` text
- `Campaigns` relation to Campaigns
