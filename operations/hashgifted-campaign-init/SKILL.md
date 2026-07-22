---
name: hashgifted-campaign-init
description: Initialise Fig & Bloom Hashgifted creator campaigns before they open for applicants by interviewing the marketer, gathering campaign objective, hard gates, deliverables, target selected count, deadline, concepts, and calibration, then creating linked Campaign and Brief records in Notion. Use when asked to launch, kick off, plan, create, or initialise a new Hashgifted gifting campaign. Writes to Notion only; does not operate the Hashgifted browser or publish Notion pages to the web.
---

# Hashgifted Campaign Init

Use this at step 0 of the Hashgifted lifecycle. No Hashgifted campaign needs to exist yet. The output is a complete Notion campaign record plus one or two creator-facing brief records ready for the marketer to share-to-web manually.

## Required References

- Read `hashgifted-ops-manager/references/lifecycle.md` for the creator lifecycle.
- Read `hashgifted-ops-manager/references/brand-aesthetic-rubric.md` for shared Fig & Bloom creator fit language.
- Read `references/notion-schema.md` before writing Notion records.
- Read `references/brief-template.md` before drafting brief page content.

Do not use `browser_operator` in this skill. This skill writes to Notion only.

## Entry Conditions

Use when the marketer says things like:

- "let's launch a campaign"
- "kick off a new gifting round"
- "start a campaign for X"
- "create a Hashgifted campaign brief"

Proceed when no matching Campaigns row exists, or when the marketer explicitly wants a new campaign. If a matching campaign exists, ask whether to update/link it or create a new row.

## Interview

Collect these before creating records. Use AskUserQuestion when available. Do not assume missing answers.

- Campaign name.
- Objective: exactly one of `audience awareness`, `content library`, or `both`.
- Hard gates: location, follower minimums, platform, and category exclusions. Default Fig & Bloom delivery gate: Melbourne, Sydney, and Brisbane metro areas only.
- Deliverables as free text. Default for every newly selected #gifted creator: around five high-resolution aesthetic still photographs featuring the bouquet; approximately 4–6 strong finals is acceptable; no Reel required. Only change this default when Daniel explicitly overrides the campaign.
- Asset mode: exactly one of `supply to Fig & Bloom`, `static/carousel post`, or `both`. Do not assume Instagram posting.
- Target selected count.
- Delivery/posting deadline window (relative). Default to `7 days from receipt of gift` unless the marketer overrides. Stored in `Deadline Window`.
- Absolute delivery/posting deadline date, if the campaign has a fixed cutoff (e.g. tied to Mother's Day or a campaign-end date). Optional. Stored in `Posting Deadline`.
- Concept descriptions. Accept one or two concepts by default.
- One-off calibration, such as "prioritise mums with kids 0-5".

If concept text is vague, push back before writing. Ask for:

- the emotional arc
- the visual moment
- who the creator or viewer should feel for
- what changes between the first frame and the last frame

## Decision Rules

- Reusing an existing Published brief: link the existing brief row; do not duplicate it.
- More than two concepts: confirm explicitly. Programme convention is two max so creators can choose without being overwhelmed.
- One-line concepts: do not pad with generic filler. Ask for better raw material.
- Internal jargon: remove it from creator-facing pages.
- Deliverables: keep the exact photo count guidance and asset mode in the Campaign record. Default to around five high-resolution aesthetic still photographs and no Reel. Brief pages should give light visual guidance without feeling like homework.
- Posting: never infer a public post from the photo deliverable. Record whether the creator supplies files, posts a static/carousel, or does both.

## Notion Write Sequence

Before creating Notion pages, fetch the Notion enhanced Markdown spec resource if the environment requires it.

1. Search Campaigns for a matching `Campaign Name`.
2. Search Briefs for reusable Published briefs if the marketer asks to reuse a concept.
3. Create a Campaigns row with:
   - `Campaign Name`
   - `Status` = `Planning`
   - `Hard Gates`
   - `Deliverables`
   - `Target Selected`
   - `Deadline Window`
   - `Posting Deadline` if the marketer supplied an absolute date; otherwise leave blank for the marketer to fill in once the brand-portal campaign is live.
   - `Hashgifted URL` left blank. Captured by the marketer once the campaign is created in the Hashgifted brand portal.
   - `Notes` containing objective, shortlist calibration, and any one-off guidance.
4. Create one Briefs row per concept with:
   - `Brief Name`
   - `Status` = `Published`
   - `Concept Hook`
   - page content following `references/brief-template.md`
5. Link Briefs to the Campaign through the Campaign `Briefs` relation or the Brief `Campaigns Using This Brief` relation.
6. Leave `Brief.Public Link` empty until each brief has been manually published/shared to web. After the marketer flips Share-to-web, retrieve the page via the Notion API; if `public_url` is present, patch `Brief.Public Link` with that URL.

## Brief Writing Standards

Mirror the seeded examples:

- Start with a short italic note that the brief is for Fig & Bloom creators and is meant to be quick on a phone.
- Lead with feeling, not requirements.
- Ask for around five high-resolution aesthetic still photographs; approximately 4–6 strong finals is acceptable.
- Suggest a varied mix of bouquet hero, floral detail, lifestyle/context, styled scene and alternate composition without making it a rigid shot list.
- Ask for original clean files without watermarks or baked-in text.
- State explicitly whether the photographs are supplied to Fig & Bloom, posted as a static/carousel post, or both.
- State that no Instagram Reel is required unless Daniel explicitly overrides the campaign.
- Include caption direction only when posting is required.
- End with a warm invitation for questions.

Lean wins. The brief is read inside Hashgifted's in-platform link preview.

## Output

Close with:

- Campaign name.
- New or reused brief names and Notion URLs.
- Target selected count and deadline window.
- Hard gates summary.
- What the marketer must do next:
  - flip Share-to-web on each new brief in Notion
  - paste each public URL into `Brief.Public Link`
  - open the campaign for applicants only after public links exist

Use these exact reminders:

```text
Flip Share-to-web on each new brief in Notion before shortlist/selection starts; paste the public URL into Brief.Public Link.
```

```text
After creating the campaign in the Hashgifted brand portal: paste the gift-view URL into Campaign.Hashgifted URL, set Posting Deadline if not already, and flip Status to Open for Applicants. The monitor skill will skip campaigns missing a Hashgifted URL.
```

## Failure Modes

- Notion schema mismatch: fetch the database schema again and adapt property names.
- Missing Notion access: stop and ask the marketer to grant access or provide record details.
- Relation write fails: create the records, report the link failure, and include the URLs for manual linking.
- Share-to-web requested: explain that the Notion API does not expose the toggle and it must be enabled manually. Once enabled, the API may expose `page.public_url`; fetch the page and copy that value into `Brief.Public Link`.
