# Hashgifted Creator CRM in Notion

Use this as the persistent memory layer for Hashgifted/Fig & Bloom creators. The purpose is to avoid re-reviewing the same creator every campaign and to make history queryable: who we worked with, who performed well, location confidence, visual feed fit, and campaign lifecycle state.

## Source of truth

- Notion UGC Hub: `https://www.notion.so/35bfdc24425f80b199dfea0d2b615ab9`
- Creators data source: `221846a5-866d-43ef-bb19-6883fe1c2bdb`
- Creators database parent: `b5e1059f-543b-488b-ae19-3a3055dbc672`
- Campaigns data source: `a8602813-2cca-4f84-8c99-fad58b5c014b`

The Creators data source has been extended for CRM/lifecycle use. Do not create a separate creator table unless this one becomes unusable; reuse the same creator row across campaigns.

## Required creator properties

Identity:

- `Creator Name` — title.
- `Handle` — Instagram/TikTok handle without `@` when possible.
- `Instagram` — canonical profile URL.
- `TikTok` — profile URL when available.
- `Campaigns` — relation to Campaigns.

Lifecycle:

- `Status` — broad account status: `Active`, `Preferred`, `Excluded`, `Archived`.
- `Hashgifted Stage` — campaign lifecycle status: `Applied`, `Manual Review`, `Shortlisted`, `Outreach Sent`, `Qualified`, `Selected`, `Content Posted`, `Captured`, `Complete`, `Declined`, `Ghosted`, `Reserve`, `Do Not Work With`.
- `Application Status` — current application-row state: `New`, `Reviewed`, `Shortlisted`, `Messaged`, `Qualified`, `Selected`, `Not Selected`, `Declined`, `Completed`.
- `Decision` — latest reviewer decision: `Shortlist`, `Manual Review`, `Decline`, `Reserve`, `Selected`, `Complete`.
- `Decision Confidence` — `High`, `Medium`, `Low`.
- `Last Applied`, `Last Reviewed`, `Last Contacted`, `Last Selected`, `Last Completed`.
- `Campaign Count`, `Selected Count`, `Completed Count`, `Creator Rating`.

Location / delivery:

- `Location` — raw location string as seen in profile/Hashgifted/thread.
- `Metro Area` — `Melbourne`, `Sydney`, `Brisbane`, `Other`, `Unknown`.
- `Metro Eligible` — `Confirmed`, `Likely`, `Unconfirmed`, `No`.
- `Location Confidence` — `Confirmed`, `Likely`, `Weak`, `Unknown`, `Outside`.
- `Distance From Metro Km` — numeric distance when stated.
- `Delivery Eligibility Notes` — evidence/source snippet.

Important policy: “30km out of Brisbane” qualifies as Brisbane. Treat up to 30km from Brisbane as Brisbane metro for profile-inference purposes; apply the same 30km inference rule to Melbourne and Sydney unless campaign-specific instructions override it. This is still only `Likely` until the creator explicitly confirms eligibility in the thread. Final selection still requires confirmation.

Visual / feed review:

- `Visual Review Status` — `Not Reviewed`, `Partial`, `Reviewed`, `Unavailable`, `Needs Recheck`.
- `Last Visual Review`.
- `Brand Fit` — `Strong`, `Good`, `Maybe`, `Weak`, `Unsafe`.
- `Content Quality` — `Excellent`, `Good`, `Mixed`, `Weak`, `Unknown`.
- `Reel Ability` — `Strong`, `Good`, `Maybe`, `Weak`, `Unknown`.
- `Audience Fit` — `Strong`, `Good`, `Maybe`, `Weak`, `Unknown`.
- `Engagement Quality` — `Strong`, `Good`, `Thin`, `Suspicious`, `Unknown`.
- `Brand Safety` — `Clear`, `Minor Concern`, `Concern`, `Unsafe`, `Unknown`.
- `Content Themes` — multi-select tags such as `Home`, `Interiors`, `Motherhood`, `Family`, `Food`, `Hosting`, `Lifestyle`, `Beauty`, `Fashion`, `Wellness`, `Events`, `Bridal`, `Flowers`, `Gifting`.
- `Visual Style` — multi-select tags such as `Natural Light`, `Neutral`, `Warm`, `Editorial`, `Premium`, `Colourful`, `Minimal`, `Cosy`, `Clean`, `Polished`, `Casual UGC`, `Text Heavy`, `Chaotic`, `Product Spam`.
- `Visual Evidence` — concise evidence from feed inspection: posts/reels observed, what would make Fig & Bloom plausible, any mismatch.
- `Fit Signals` and `Risk Notes` — short audit notes.

## Operating rules

1. Every applicant review should upsert the creator row before or immediately after the Hashgifted action.
2. Match existing creators by `Instagram`, then `Handle`, then `Creator Name`; avoid duplicate creator rows.
3. Save visual inspection outputs as structured properties, not only prose notes.
4. Keep raw screenshots/contact sheets outside Notion if large, but store enough `Visual Evidence` to avoid repeating the review.
5. Do not promote a creator to `Selected` on inferred location alone. `Metro Eligible = Confirmed` requires a creator-thread statement or another explicit source.
6. When a creator applies to a later campaign, update campaign relation/history/counts instead of overwriting useful prior fit evidence.
7. Use `Creator Rating` and completion counts for “who have we worked with most regularly / best” queries.

## Scripts

- Schema setup / repair: `/opt/data/scripts/ensure_hashgifted_creators_notion_schema.py`
- Generic creator upsert: `operations/hashgifted-ops-manager/scripts/upsert_creator_to_notion.py`
- Shortlist markdown sync: `/opt/data/skills/productivity/notion/scripts/sync_hashgifted_shortlist_to_notion.py`

Example upsert:

```bash
/opt/hermes/.venv/bin/python operations/hashgifted-ops-manager/scripts/upsert_creator_to_notion.py creator.json
```

Example JSON:

```json
{
  "name": "Jane Example",
  "handle": "jane.example",
  "instagram": "https://www.instagram.com/jane.example/",
  "location": "30km out of Brisbane",
  "stage": "Shortlisted",
  "application_status": "Shortlisted",
  "decision": "Shortlist",
  "decision_confidence": "High",
  "followers": 18500,
  "engagement_rate": 0.031,
  "visual_review_status": "Reviewed",
  "brand_fit": "Strong",
  "content_quality": "Good",
  "reel_ability": "Good",
  "audience_fit": "Good",
  "engagement_quality": "Good",
  "brand_safety": "Clear",
  "content_themes": ["Home", "Motherhood", "Lifestyle"],
  "visual_style": ["Natural Light", "Neutral", "Warm"],
  "visual_evidence": "Warm home/family feed with natural-light reels and plausible bouquet scenes.",
  "mark_reviewed_today": true
}
```
