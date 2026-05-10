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
- Hard gates: location, follower minimums, platform, and category exclusions.
- Deliverables as free text.
- Target selected count.
- Posting deadline. Default to `7 days from receipt of gift` unless the marketer overrides.
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
- Deliverables: keep them in the Campaign record. Brief pages can include format guidance, but should not feel like homework.

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
   - `Notes` containing objective, shortlist calibration, and any one-off guidance.
4. Create one Briefs row per concept with:
   - `Brief Name`
   - `Status` = `Published`
   - `Concept Hook`
   - page content following `references/brief-template.md`
5. Link Briefs to the Campaign through the Campaign `Briefs` relation or the Brief `Campaigns Using This Brief` relation.
6. Leave `Brief.Public Link` empty unless the marketer provides a public Notion URL.

## Brief Writing Standards

Mirror the seeded examples:

- Start with a short italic note that the brief is for Fig & Bloom creators and is meant to be quick on a phone.
- Lead with feeling, not requirements.
- Use a story arc with on-screen text per scene.
- Keep talking points in the creator's voice, not brand voice.
- Give visuals to capture.
- Offer hook and caption options.
- End with format guidance.

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

Use this exact reminder:

```text
Flip Share-to-web on each new brief in Notion before shortlist/selection starts; paste the public URL into Brief.Public Link.
```

## Failure Modes

- Notion schema mismatch: fetch the database schema again and adapt property names.
- Missing Notion access: stop and ask the marketer to grant access or provide record details.
- Relation write fails: create the records, report the link failure, and include the URLs for manual linking.
- Share-to-web requested: explain that the Notion API does not expose that toggle and it must be done manually.
