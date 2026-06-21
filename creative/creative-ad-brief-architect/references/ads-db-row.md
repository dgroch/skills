# Ads Database — row schema for logging

Every produced ad gets a row in the Ads Database. The brief emits a `Draft` row;
performance fields are filled post-flight. Field names and select values below
mirror the live Notion database — use the exact select values or the sync breaks.

## Fields to fill at brief time

| Field | Type | Fill with |
|---|---|---|
| `Ad` (title) | title | Short ad name, e.g. "Long-Distance Bestie — Osaka" |
| `Headline` | text | The working hook line (final line comes from the scriptwriter) |
| `Primary Text` | text | One-line caption direction (scriptwriter finalises) |
| `Angle` | text | The avatar + recognition angle, and the lens routing string |
| `Hypothesis` | text | House form: "[Hook] stops the [avatar]; [mechanism] + message-back resolve the doubt that [fear]." |
| `Occasion` | select | One of the valid values below |
| `CTA` | select | `Shop Now` (default) / `Sign Up` / `Learn More` / `Get Offer` |
| `Funnel` | select | `TOFU` (prospecting default) / `MOFU` / `BOFU` |
| `Campaign Type` | select | `Prospecting` (default) / `Retargeting` / `Re-engagement` / `Brand Awareness` |
| `Platform` | multi-select | `Meta` (default) / `TikTok` / `Google` |
| `Status` | select | `Draft` at brief time → `Approved` → `Active` → `Paused` / `Killed` |
| `Target Audience` | text | The named avatar/persona + the specific moment |
| `Campaign` | select | Existing campaign if one fits, else leave blank for ops |
| `Campaign Page` | url | If a landing page is specified |

## Valid select values

- **Occasion:** Anniversary · Apology · Dinner Party · Mothers Day · New Baby ·
  Evergreen · Get Well · Birthday · Congratulations · I Love You · Thinking of You
- **CTA:** Shop Now · Sign Up · Learn More · Get Offer
- **Funnel:** TOFU · MOFU · BOFU
- **Campaign Type:** Prospecting · Retargeting · Re-engagement · Brand Awareness
- **Status:** Draft · Approved · Active · Paused · Killed
- **Platform:** Meta · TikTok · Google

## Leave empty at brief time (filled post-flight)

`Budget ($/day)`, `Spend`, `Revenue`, `ROAS`, `CPA`, `Clicks`, `Impressions`,
`Conversions`, `CTR (%)`, `Start Date`, `End Date`, `Last Synced`, `Ad ID`,
`Adset ID`, `Campaign ID`, `Creatives (CDN)`.

## Output format

Emit as a fenced block of `Field: value` lines so it can be pasted or synced.
Note where Occasion names diverge from the Sales Legends matrix (which uses 9):
log against the **Ads DB** occasion above, and route lenses using the closest
matrix occasion.
