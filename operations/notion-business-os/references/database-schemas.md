# Database Schema Reference

Detailed property schemas for all operational databases. Use this when you need to know exact property types, select options, or relation targets.

## Manifest (`357fdc24425f81ed805cc4f9aff0665f`)

| Property | Type | Notes |
|----------|------|-------|
| Asset | title | Filename or descriptive name |
| Aspect Ratio | select | 9:16, 540:959, 135:76, 269:480, 89:160, 270:479, 75:56, 24:43 +103 more |
| Asset Type | select | video, image, other |
| Canonical Product Name | relation | → Products DB |
| Contains Product | select | yes, no |
| Content Type | select | 200+ options (product showcase, lifestyle/social media, influencer promotion, user-generated content/testimonial, customer reaction/testimonial, etc.) |
| Dimensions | rich_text | Pixel dimensions |
| Drive File ID | rich_text | Google Drive file ID |
| Drive Link | url | Google Drive URL |
| Duration Seconds | number | For video assets |
| File Handle | rich_text | |
| Folder Path | rich_text | Logical path within Drive |
| Manifest Model | rich_text | Model used for vision analysis |
| Manifested At | date | When vision analysis completed |
| Mime Type | rich_text | image/jpeg, video/mp4, video/quicktime, image/heif |
| Mood Tone | multi_select | clean, organized, neutral, modern, artistic, quirky +95 more |
| Orientation | select | portrait, landscape, square |
| Original Filename | rich_text | Source filename before rename |
| Overall Description | rich_text | AI-generated vision description |
| People Present | rich_text | none, one person, hands only, etc. |
| Preview | files | Thumbnail preview |
| Preview URL | url | |
| Product Match Confidence | number | 0-1 confidence score |
| Product Match Quality | select | unreviewed, correct, incorrect, not a product, unclear/multiple |
| Product Name | rich_text | Named product |
| Products / Flowers | multi_select | 104+ options (red roses, white alstroemeria, green foliage, etc.) |
| Renamed At | date | |
| Reorg Notes | rich_text | Notes from file organization |
| Setting / Location | rich_text | studio, outdoor, home, etc. |
| Size MB | number | File size |
| Source Folder | rich_text | Original source folder |
| Taxonomy Candidates | multi_select | |
| Taxonomy Version | rich_text | |
| Timestamp Beats | rich_text | For video: key timestamps |
| Usable For | multi_select | 100+ options (social media, website product page, marketing collateral, e-commerce, etc.) |
| Visual Tags | multi_select | 161+ options (white background, studio lighting, product shot, lifestyle, minimalist, still life, etc.) |

## Creators (`b5e1059f-543b-488b-ae19-3a3055dbc672`)

| Property | Type | Options |
|----------|------|---------|
| Creator Name | title | |
| Hashgifted Stage | select | Applied, Manual Review, Shortlisted, Outreach Sent, Qualified, Selected, Content Posted, Captured, Incomplete, Paused, Withdrew, Rejected, Archived, Ineligible |
| Decision | select | Shortlist, Manual Review, Decline, Reserve, Selected, Complete, Pass |
| Decision Confidence | select | High, Medium, Low |
| Application Status | select | New, Reviewed, Shortlisted, Messaged, Qualified, Selected, Not Selected, Declined, Withdrawn, Incomplete |
| Status | select | Active, Preferred, Excluded, Archived |
| Creator Rating | number | 0-5 rating |
| Followers | number | |
| Engagement Rate | number | |
| Engagement Quality | select | Strong, Good, Thin, Suspicious, Unknown |
| Audience Fit | select | Strong, Good, Maybe, Weak, Unknown |
| Brand Fit | select | Strong, Good, Maybe, Weak, Unsafe |
| Brand Safety | select | Clear, Minor Concern, Concern, Unsafe, Unknown |
| Content Quality | select | Excellent, Good, Mixed, Weak, Unknown |
| Content Themes | multi_select | Home, Interiors, Motherhood, Family, Food, Hosting +37 more |
| Visual Style | multi_select | Natural Light, Neutral, Warm, Editorial, Premium, Colourful +42 more |
| Metro Area | select | Melbourne, Sydney, Brisbane, Other, Unknown |
| Metro Eligible | select | Confirmed, Likely, Unconfirmed, No |
| Location Confidence | select | Confirmed, Likely, Weak, Unknown, Outside |
| Distance From Metro Km | number | |
| Tier | select | Nano, Micro, Mid, Macro |
| Reel Ability | select | Strong, Good, Maybe, Weak, Unknown, Excellent |
| Handle | rich_text | Instagram/TikTok handle |
| Instagram | url | |
| TikTok | url | |
| Location | rich_text | |
| Notes | rich_text | |
| Risk Notes | rich_text | |
| Fit Signals | rich_text | |
| Visual Evidence | rich_text | |
| Delivery Eligibility Notes | rich_text | |
| Campaigns | relation | → Campaigns DB |
| Campaign Count | number | |
| Completed Count | number | |
| Selected Count | number | |
| Last Applied | date | |
| Last Completed | date | |
| Last Contacted | date | |
| Last Reviewed | date | |
| Last Selected | date | |
| Last Visual Review | date | |
| Visual Review Status | select | Not Reviewed, Partial, Reviewed, Unavailable, Needs Recheck |
| Profile URL Source | url | |
| Created | created_time | |

## Campaigns (`ab1819ee-4236-4105-b091-d2d0640509a3`)

| Property | Type | Notes |
|----------|------|-------|
| Campaign Name | title | |
| Status | select | Planning, Open for Applicants, Active, Wrapping, Complete, Paused, In Progress |
| Posting Deadline | date | |
| Target Selected | number | Target number of creators |
| Deliverables | rich_text | Expected content deliverables |
| Hard Gates | rich_text | Non-negotiable requirements |
| Deadline Window | rich_text | |
| Hashgifted URL | url | Link to Hashgifted campaign |
| Notes | rich_text | |
| Briefs | relation | → Briefs DB |
| Creators | relation | → Creators DB |
| Created | created_time | |

## Social Media Ads (`361fdc24-425f-80ab-b393-e583a5d9b339`)

| Property | Type | Options |
|----------|------|---------|
| Name | title | Format: PRODUCT_Angle_Format_HookType |
| Angle | select | Pain, Transformation, Social Proof, Authority |
| Creative Format | select | Founder, UGC, Demo |
| Hook Type | select | Question, Stat, Contrarian |
| Status | select | Draft, In Review, Approved, Scheduled, Published, Needs changes |
| Brand QA | select | Pending, Approved, Needs changes |
| Compliance QA | select | Pending, Approved, Needs changes |
| Platform | multi_select | Instagram, Facebook, TikTok, Meta |
| Format | select | Feed, Story, Reel/Short, Carousel, Static |
| Objective | select | Purchase, Lead, AOV lift, Retargeting, Awareness |
| Campaign Concept | select | Same-day gesture rescue, Objects worth keeping, Event table made effortless, Osaka 4x3x3 Test |
| Hook | rich_text | The opening line/hook text |
| Body Copy | rich_text | |
| CTA | rich_text | Call to action |
| Audience | rich_text | Target audience description |
| Asset/Product Used | rich_text | |
| Template Source | rich_text | |
| Notes | rich_text | |
| Editable Link | url | Canva/editable link |
| Preview | files | Preview images |
| Files & media | files | Final assets |
| Owner | people | |

## Review Research (`357fdc24-425f-8123-a9e0-d413eab168f1`)

| Property | Type | Notes |
|----------|------|-------|
| Brand | select | Competitor brand (the-hamper-emporium, mr-roses, flowers-for-everyone, etc.) |
| Source | select | ProductReview, etc. |
| Job To Be Done | select | romance, sympathy, birthday, corporate, unknown, etc. |
| Raw Text | rich_text | Original review text |
| Delight Drivers | rich_text | What made the customer happy |
| Complaints | rich_text | What went wrong |
| Purchase Drivers | rich_text | Why they bought |
| Operational Issue | select | Delivery, quality, packaging, etc. |
| Review Date | date | |
| Review URL | url | |

## Creative Research (`351fdc24-425f-81be-976e-c417a1b9c365`)

| Property | Type | Notes |
|----------|------|-------|
| Name | title | |
| Category | select | pet_parent_gifting, friendship, last_minute, etc. |
| Platform | select | TikTok, Instagram |
| Hook Type | select | pov, contrarian, deadline, etc. |
| Score | number | Virality/quality score |
| Views | number | |
| Comments | number | |
| Shares | number | |
| Why It Worked | rich_text | |
| Signal Notes | rich_text | |
| Local ID | rich_text | |

## Products (`358fdc24-425f-8194-9979-dc3ee44c7ed5`)

| Property | Type | Notes |
|----------|------|-------|
| Product Name | title | |
| Product Type | select | Candle, Vase Arrangement, Bundle, Bouquet, Baby Sleepwear, Greeting Card, Vase, Soap +31 more |
| Handle | rich_text | Shopify handle |
| SKU slug | rich_text | |
| Price AUD | number | |
| Tags | multi_select | hero, gift, mothers-day, valentines, birthday, sympathy +46 more |
| Availability | select | in_stock, out_of_stock |
| Status | select | active, inactive |
| Source | select | Shopify, DataFeedWatch |
| Shopify Product ID | rich_text | |
| Shopify Legacy ID | rich_text | |
| Shopify Status | select | active, draft, archived |
| In DataFeedWatch | checkbox | |
| Image URL | url | |
| Product URL | url | |
| Source URL | url | |
| Vendor | rich_text | |
| Feed Product ID | rich_text | |
| Hero copy | rich_text | |
| Best-seller proof | rich_text | |
| Palette | rich_text | |
| Notes | rich_text | |
| Reference photos | files | |

## Brand Photographer Artifacts (`b1ecf2b1-2f4e-413c-bee6-49758a14d3d2`)

54 properties including: Outfit Colours, Prompt Preview, Asset Manifest Page ID, Source File, Subcategory, Status, CDN URL, Source, Drive File ID, Scene, and many more. This DB feeds the AI brand photographer skill.

## Scheduled Rebalances (`36afdc24-425f-810a-800a-deb862c5865e`)

| Property | Type | Notes |
|----------|------|-------|
| Rebalance | title | |
| Type | select | |
| Scheduled Date | date | |
| Executed At | date | |
| Status | select | Scheduled, Awaiting Approval, Approved, Execute Requested, Executing, Executed, Cancelled, Failed |
| Execute Requested | checkbox | Must be checked alongside Approved status |
| Initial Launch | checkbox | True for the one-off launch rebalance |
| Audit File | rich_text | Path to audit file |
| Approval SHA | rich_text | Hash of audit for tamper detection |
| Notes | rich_text | |

## Trade Executions (`36afdc24-425f-8198-bfed-d4f0482f9ee8`)

| Property | Type | Notes |
|----------|------|-------|
| Ticker | rich_text | |
| Side | select | Buy, Sell |
| Quantity | number | |
| Limit Price | number | |
| Fill Price | number | |
| Notional | number | |
| Value | number | |
| Status | select | Proposed, Submitted, Filled, Cancelled, Failed |
| Order Time | date | |
| Tastytrade Order ID | rich_text | |
| Approval SHA | rich_text | |

## Journalist Contacts & Coverage (`685b6a39-534d-4fb4-bb06-cd63747cdc2a`)

Data source ID for queries: `3cacb1d2-fc05-4bba-b524-0a9938145f3c`

| Property | Type | Notes |
|----------|------|-------|
| Name | title | Journalist name |
| Outlet | rich_text | Publication |
| Role/Beat | rich_text | E.g. "Lifestyle editor" |
| Email | email | Direct contact |
| Phone | rich_text | Phone number |
| Twitter/X | url | Profile link |
| LinkedIn | url | Profile link |
| Location | rich_text | City/market |
| Status | select | Not Contacted, Pitched, Responded, Coverage Secured, Declined, No Reply |
| Last Contact Date | date | Last touchpoint |
| Coverage Type | multi_select | Feature Article, News Mention, Round-up, Interview, Social Post, Podcast, TV/Radio |
| Coverage URL | url | Link to published piece |
| Coverage Date | date | When it went live |
| Notes | rich_text | Free-form context |

Managed by the `digital-pr-outreach` skill. Parent page: Journalists (`38efdc24-425f-8086-a224-c90951a4d52c`).

## Gift Cards Register (`36afdc24425f816fa315ced08f6dcd71`)

| Property | Type | Notes |
|----------|------|-------|
| Gift Card Number | title | |
| Masked Code | rich_text | |
| Redemption Code | rich_text | |
| Balance | number | |
| Currency | select | |
| Status | select | |
| Shopify Enabled | checkbox | |
| Created At | date | |
| Expires On | date | |
| Last Synced | date | |
| Notes | rich_text | |
