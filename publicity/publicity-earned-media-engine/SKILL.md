---
name: publicity-earned-media-engine
description: Build founder thought-leadership, data-PR storytelling, media lists, and journalist pitch packages for Herald-style PR work. Use for earned media strategy, founder POV pitches, Australian Gifting Report concepts, media-list building, journalist outreach drafts, and PR handovers.
---

# Earned Media Engine

This skill helps Herald turn Fig & Bloom's strategic POV into evidence-backed earned media without inventing claims or overreaching.

## Trigger

Use when asked to create:

- founder thought-leadership briefs;
- data-PR concepts such as the Australian Gifting Report;
- media lists for design, retail, business, gifting, startup, or local press;
- journalist pitch emails;
- press angles for Bower, sympathy, corporate gifting, Birthday Club, or occasion programs.

Always run `reference-pr-ethics-guardrail` and `reference-brand-voice-guardrail` before external use.

## Inputs

- Business objective and target audience.
- News hook or timing reason.
- Founder POV or thesis.
- Evidence available: order data, customer quotes, product launches, partnerships, founder notes, trend data.
- Target outlet categories and geography.
- Sensitivity flags: grief, funeral, charity, medical, bereavement, customer data.

## Workflow

### 1. Define the Story Spine

Use this structure:

| Field | Prompt |
|---|---|
| Thesis | What does Fig & Bloom believe that is sharp enough to be quoted? |
| Why now | What makes this timely rather than evergreen marketing? |
| Proof | What evidence can be shown without privacy or ethics risk? |
| Human angle | Who is affected, helped, or represented? |
| Business angle | Why does this matter commercially or culturally? |
| Visual angle | What can a journalist show? |

### 2. Choose PR Angle

Pick one primary angle:

- Founder POV: design-led florist taking on dispatch-led flower delivery.
- Data story: anonymised gifting behaviour, timing, occasions, spend bands, or sentiment patterns.
- Cause-led: grief literacy and better sympathy support.
- Product/program: Birthday Club, corporate gifting, Bower value launch.
- Partnership: credible co-branded gift or care partnership after written confirmation.

### 3. Build Media List

Create a media list with 20-30 targets. For each target record:

- journalist name;
- outlet;
- beat;
- geography;
- recent relevant coverage;
- why this angle fits;
- contact source;
- priority: A/B/C;
- outreach status.

Do not scrape private emails from dubious sources. Use public mastheads, outlet contact pages, journalist bios, legitimate media databases, or direct social links.

### 4. Draft Pitch

Pitch format:

```markdown
Subject: [clear, specific, not clickbait]

Hi [name],

[One sentence showing why this is relevant to their beat.]

[Founder POV or news hook in one short paragraph.]

[Proof points: 2-3 bullets. No unsourced claims.]

[Offer: interview, data snapshot, images, product sample if appropriate and disclosed.]

Best,
[sender]
```

Keep it short. Do not attach large files in the first outreach unless requested.

### 5. Prepare Handover

Output a handover with:

- story spine;
- media list;
- pitch variants;
- evidence ledger;
- assets needed;
- risks and approvals;
- follow-up schedule.

## Quality Gates

- Every factual claim appears in an evidence ledger.
- The pitch gives a journalist a story, not a product ad.
- No fake quotes, fake customers, fake partners, or fake urgency.
- Data is anonymised and explained plainly.
- Sympathy or bereavement content has passed tone review.
- Bower references have passed brand separation review.

## Output Format

```markdown
# Earned Media Package - [Angle]

## Story Spine
[table]

## Media List
[20-30 row table]

## Pitch Drafts
[primary + 1-2 variants]

## Evidence Ledger
[claim/source/permission table]

## Risks and Approvals
[items]

## Handover Notes
[what Herald owns next]
```
