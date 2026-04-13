---
name: creative-email-template-builder
description: Create, build, and deploy email campaigns and automated flows in Klaviyo
  from a modular HTML/CSS component library. 
version: 1.0.0
author: Dan Groch
license: MIT
metadata:
  hermes:
    tags: [Email, Klaviyo, Marketing, Campaign, Flow, Template]
    related_skills: [ad-creative-builder, ai-image-generation]
---

# Email Template Builder

## Overview

Build and deploy email campaigns and automated flows in Klaviyo by
assembling modular HTML/CSS components, applying brand configuration,
and managing the full approval-to-send lifecycle via Klaviyo's API.
This skill also runs periodic campaign performance reviews to surface
insights that improve future emails.

Use this skill whenever someone asks to: create an email campaign, build a Klaviyo email, design an email template, set up a welcome series, build an abandoned cart flow, draft a promotional email, create a Mother's Day / seasonal campaign, review email performance, analyse campaign metrics, build email flows, set up email automation, produce an EDM, or any request involving email marketing through Klaviyo. Also triggers for: "send an email to our list", "set up a drip sequence", "what's working in our emails", "build a flow for X", "create a campaign for [event/sale/launch]", or references to email components like hero blocks, product grids, CTA strips, or email layouts.  This skill covers the full lifecycle: design → approval → build in Klaviyo → review → send/activate. It also covers periodic campaign performance analysis.

## Prerequisites

Before execution, the following must be available:

- **Klaviyo API key**: Private key with scopes: `templates:read`,
  `templates:write`, `campaigns:read`, `campaigns:write`, `flows:read`,
  `flows:write`, `metrics:read`, `lists:read`, `segments:read`.
  Stored in environment as `KLAVIYO_API_KEY`.
- **Brand config document**: A brand guide file containing at minimum:
  logo URL, colour palette (hex values for primary, secondary, accent,
  background, text), typography (font families, sizes, weights for
  headings, body, CTA), tone-of-voice rules, social media URLs, legal
  footer text, and any words/phrases to avoid.
  Read from `references/brand-config/` or passed in at agent setup.
- **Component library**: The HTML/CSS email component library at
  `references/components/`. If the library does not exist yet, Phase 0
  must run first.
- **Recipient list or segment**: A Klaviyo list or segment ID for
  the campaign audience. For flows, the trigger configuration.

## Scope

### In scope

- Assembling emails from modular HTML/CSS components
- Creating and updating Klaviyo templates via API
- Creating Klaviyo campaigns, assigning templates, scheduling sends
- Creating Klaviyo flows via API (beta — metric-triggered, date-triggered)
- Generating approval mockups for human review
- Applying brand configuration to all email output
- Subject line and preview text generation
- Periodic campaign performance analysis (monthly)
- Iterating on email content based on reviewer feedback

### Out of scope — delegate or escalate

- **Generating photography or illustrations** → `ai-image-generation`
- **Building ad creatives** → `ad-creative-builder`
- **Writing long-form copy from scratch** → copywriting skill or human brief
- **Managing Klaviyo account settings** (billing, domain auth, deliverability) → human
- **A/B test creation within flows** → not supported by Klaviyo API; manual in UI
- **Updating existing flow structures via API** → Klaviyo API limitation; escalate to human for structural changes to live flows
- **List/segment creation or management** → separate concern; request list ID from operator

## Architecture: Component Library

The component library is the source of truth for all email builds.
Each component is a self-contained HTML/CSS block that accepts brand
config variables. Components use inline CSS (email client compatibility)
with CSS custom properties replaced at build time.

### Component structure

```
references/components/
├── COMPONENTS.md          # Registry of all components
├── _base/
│   ├── reset.html         # Email client reset styles
│   ├── wrapper.html       # Outer table structure (600px)
│   └── responsive.html    # Media queries for mobile
├── header/
│   ├── header-logo.html   # Logo + optional nav links
│   └── header-minimal.html # Logo only, centered
├── hero/
│   ├── hero-full-image.html    # Full-width image with overlay text
│   ├── hero-split.html         # Image left/right, text opposite
│   └── hero-text-only.html     # Headline + subhead, no image
├── content/
│   ├── text-block.html         # Body copy with optional subhead
│   ├── product-grid-2col.html  # 2-column product cards
│   ├── product-grid-3col.html  # 3-column product cards
│   ├── product-single.html     # Single featured product
│   ├── testimonial.html        # Quote with attribution
│   └── image-text-row.html     # Image + text side by side
├── cta/
│   ├── cta-button.html         # Centred button, configurable colour
│   ├── cta-strip.html          # Full-width colour band with button
│   └── cta-dual.html           # Two buttons side by side
├── social/
│   └── social-follow.html      # Social media icon row
├── footer/
│   ├── footer-standard.html    # Links + legal + unsubscribe
│   └── footer-minimal.html     # Unsubscribe + address only
└── spacer/
    └── spacer.html             # Configurable height spacer
```

### Component conventions

- Every component accepts a `brand` object: `{colors, fonts, logo_url,
  social_urls, legal_text}`.
- All CSS is inline. No `<style>` blocks in components (except media
  queries in `responsive.html`, which wraps the full email).
- Images use absolute URLs. No relative paths.
- All components include `{% unsubscribe %}` or equivalent Klaviyo tag
  where legally required (footer components).
- Product components support Klaviyo template variables:
  `{{ item.title }}`, `{{ item.image_url }}`, `{{ item.price }}`, etc.
- Components are assembled by concatenation: wrapper → header → body
  blocks → footer, wrapped in responsive media queries.

### Initialising the component library (Phase 0)

If the component library does not exist:

1. Check for prior emails in Klaviyo via `GET /api/templates/` — pull
   up to 10 most recent templates as reference for the brand's style.
2. Build each component as a parameterised HTML file using the brand
   config and any stylistic patterns found in prior emails.
3. Save to `references/components/` with a `COMPONENTS.md` registry.
4. Seek approval: "I've created the email component library based on
   your brand guide and existing templates. Please review."

Do not proceed with any campaign build until the component library
exists and has been approved.

## Process

### Phase 1: Parse Brief

**Entry conditions:** A campaign or flow request has been received.

1. Extract from the brief:
   
   - **Type**: one-off campaign or automated flow
   - **Campaign purpose**: promotional, seasonal, announcement, transactional, nurture
   - **Audience**: list ID, segment ID, or flow trigger description
   - **Content elements**: headline, body copy, CTA text, product references, images
   - **Subject line and preview text** (if provided; otherwise generate in Phase 2)
   - **Send timing**: specific date/time, or "as soon as approved"
   - **For flows**: trigger event, time delays, number of emails in sequence

2. Identify missing required fields.

**Decision tree:**

- If campaign type and audience are missing → ask one clarifying question.
  Do not proceed without both.
- If copy is missing but purpose is clear → draft copy in Phase 2 using
  brand voice from the brand config. Flag that copy was agent-generated.
- If it's a flow request → extract the full sequence: how many emails,
  what triggers each, time delays between them. If the sequence is
  unclear, ask: "How many emails in this flow, and what triggers them?"
- If product references are mentioned but no product data is provided →
  check if Klaviyo has a product feed configured. If yes, use dynamic
  product blocks. If no, request product details.

**Quality gate:** Campaign type, audience identifier, and either
provided copy or enough context to generate copy are confirmed.

### Phase 2: Design Email

**Entry conditions:** Brief is parsed and complete.

1. **Select components** from the library based on the brief:
   
   - Promotional email: hero-full-image → product-grid → cta-strip → footer
   - Announcement: hero-text-only → text-block → cta-button → footer
   - Seasonal campaign: hero-full-image → text-block → product-grid → cta-strip → social-follow → footer
   - Welcome flow (email 1): hero-split → text-block → cta-button → social-follow → footer
   - Abandoned cart: hero-text-only → product-single (dynamic) → cta-button → footer
   
   These are starting patterns. Adjust based on the brief's content
   needs. If no pattern fits, compose from individual components.

2. **Generate or refine copy:**
   
   - If subject line is not provided → generate 3 options. Each must be
     under 50 characters. Apply brand voice rules from brand config.
   - If preview text is not provided → generate to complement the subject
     line. Under 90 characters.
   - If body copy was provided → use it verbatim. Do not edit unless it
     exceeds component character limits.
   - If body copy was not provided → draft based on brief purpose and
     brand voice. Flag clearly: "Copy is agent-generated — please review."

3. **Assemble the email HTML:**
   
   - Start with `wrapper.html` and `reset.html`.
   - Insert selected components in order, populating brand config values.
   - Replace all brand variables with values from the brand config.
   - Wrap in `responsive.html` media queries.
   - Insert Klaviyo-specific tags: `{% unsubscribe %}`, `{{ email }}`
     profile variables, any dynamic product feed references.
   - For flows: build each email in the sequence as a separate template.

4. **Generate approval mockup:**
   
   - Render the assembled HTML as a preview image (use a headless
     browser or Klaviyo's template render endpoint).
   - If rendering tools are unavailable, provide the raw HTML with a
     note: "Please preview this HTML in a browser or paste into
     Klaviyo's template editor to review."

5. **Present for approval:**
   
   - Show the mockup alongside: subject line options, preview text,
     component list used, and any copy flagged as agent-generated.
   - For flows: present the full sequence with timing between emails.

**Decision tree:**

- If the reviewer approves → proceed to Phase 3.
- If the reviewer requests changes → apply changes, regenerate mockup,
  re-present. Track revision count.
- If more than 5 revision rounds → flag: "We're on revision 6. Would
  it help to revisit the brief or try a different layout approach?"
- If the reviewer requests a component that doesn't exist in the
  library → create the component, add it to `COMPONENTS.md`, then
  use it. Do not block on library gaps.

**Quality gate:** Explicit approval received ("approved", "looks good",
"go ahead", or equivalent).

### Phase 3: Build in Klaviyo

**Entry conditions:** Design is approved.

**For campaigns:**

1. **Create template in Klaviyo:**
   
   ```
   POST /api/templates/
   {
     "data": {
       "type": "template",
       "attributes": {
         "name": "[Brand]-[Campaign]-[Date]",
         "editor_type": "CODE",
         "html": "<assembled HTML from Phase 2>"
       }
     }
   }
   ```
   
   Capture the returned `template_id`.

2. **Create campaign:**
   
   ```
   POST /api/campaigns/
   ```
   
   Include: campaign name, audience (list/segment IDs), send strategy
   (immediate or scheduled with datetime), subject line, preview text.
   Capture the returned `campaign_id` and `campaign_message_id`.

3. **Assign template to campaign message:**
   
   ```
   POST /api/campaign-message-assign-template/
   ```
   
   Link the `template_id` to the `campaign_message_id`.

4. **Verify the build:**
   
   - Fetch the campaign back via `GET /api/campaigns/{id}` and confirm
     template is assigned, audience is set, and status is "draft".
   - If any field is missing or incorrect → diagnose and retry.
     Maximum 3 retry attempts before escalating.

**For flows:**

1. **Create templates** for each email in the sequence (same as above).

2. **Build the flow definition:**
   
   - Define the trigger (metric-triggered or date-triggered).
   - Define actions: send-email actions with template IDs, time-delay
     actions between emails.
   - Assign temporary IDs to each action.

3. **Create the flow:**
   
   ```
   POST /api/flows/
   ```
   
   Note: this endpoint is in beta. All flows are created in "draft"
   status by default.

4. **Verify:** Fetch the flow back and confirm all actions and
   templates are correctly linked.

**Decision tree:**

- If the Klaviyo API returns an error → log the error, diagnose
  (common issues: invalid list ID, malformed HTML, missing required
  fields). Fix and retry. Maximum 3 retries.
- If a rate limit is hit → back off with exponential delay (1s, 2s,
  4s, max 30s). Retry up to 5 times.
- If the Flows API beta endpoint fails → escalate: "The flow needs
  to be created manually in Klaviyo's UI. I've prepared the templates
  and flow structure — here's the spec."

**Quality gate:** Campaign or flow exists in Klaviyo in "draft" status
with all templates assigned and audience configured.

### Phase 4: Pre-Send Review

**Entry conditions:** Campaign/flow is built in Klaviyo in draft status.

1. **Send a test email** (if supported via API or instruct the
   reviewer to send a test from Klaviyo's UI).

2. **Present for final review:**
   
   - Provide the Klaviyo campaign/flow URL for the reviewer to inspect.
   - Summarise: audience size (via recipient estimation endpoint if
     available), subject line, send time, and any warnings.
   - For flows: list all emails in sequence with timing.

3. **Request explicit send approval:**
   "The campaign is built and ready in Klaviyo. Please review in the
   Klaviyo editor and confirm: (1) approve to send/activate, or
   (2) request changes."

**Decision tree:**

- If approved to send → proceed to Phase 5.
- If changes requested → return to Phase 2 or Phase 3 depending on
  whether the change is content (Phase 2) or configuration (Phase 3).
- If the reviewer wants to send manually from Klaviyo UI → acknowledge
  and close. The skill's job is done.

**Quality gate:** Explicit send/activate approval received.

### Phase 5: Send / Activate

**Entry conditions:** Send approval received.

**For campaigns:**

1. Schedule or send immediately:
   
   ```
   POST /api/campaign-send-jobs/
   ```
   
   Include the campaign ID and send strategy.

2. Confirm the send job was created successfully. Fetch the campaign
   status to verify it moved from "draft" to "scheduled" or "sending".

**For flows:**

1. Update flow status to "live":
   
   ```
   PATCH /api/flows/{id}/
   ```
   
   Set status to "live".

2. Confirm the status update.

**Post-send:**

- Log: campaign/flow name, send time, audience, template ID.
- Report to the operator: "Campaign '[name]' has been sent to [audience]
  at [time]." or "Flow '[name]' is now live."

**Quality gate:** Campaign status is "sent" or "sending". Flow status
is "live".

### Phase 6: Campaign Performance Review (Periodic)

**Entry conditions:** This phase runs on a monthly schedule or when
explicitly requested. At least one campaign must have been sent in the
review period.

1. **Pull campaign performance data:**
   Use the Reporting API (`POST /api/campaign-values-reports/`) to
   fetch statistics for campaigns sent in the last 30 days:
   
   - Open rate, click rate, unsubscribe rate
   - Revenue attributed (if conversion metric is configured)
   - Bounce rate, spam complaint rate

2. **Pull flow performance data:**
   Use `POST /api/flow-values-reports/` for active flows:
   
   - Same metrics as above, broken down by flow and by message.

3. **Analyse and surface insights.** Structure the analysis around:
   
   - **Subject lines**: Which subject lines had the highest open rates?
     What patterns emerge (length, tone, urgency, personalisation)?
   - **CTAs**: Which CTA text/placement drove the most clicks?
   - **Design patterns**: Which component layouts correlated with
     higher engagement? (Cross-reference template structure with
     click/open data.)
   - **Headlines**: Which headline styles increased open-to-click rate?
   - **Send timing**: Did send time/day affect open rates?
   - **Audience segments**: Which segments had highest/lowest engagement?

4. **Produce a performance report** with:
   
   - Top 3 performing campaigns/flows and why
   - Bottom 3 performing and what to change
   - Recommended actions for next month's emails
   - Any concerning trends (rising unsubscribe rate, declining opens)

5. **Update internal learnings.** Append key findings to
   `references/performance-insights.md` so future email builds can
   reference what has historically worked for this brand.

**Decision tree:**

- If no campaigns were sent in the period → report: "No campaigns
  sent in the last 30 days. No performance data to analyse."
- If the Reporting API returns errors → fall back to the Query Metric
  Aggregates endpoint. Note that metric-aggregate data is event-time
  based, not send-time based, so results may differ slightly from
  Klaviyo's UI.
- If performance data suggests a fundamental problem (e.g., >1% spam
  complaint rate, <10% open rate consistently) → escalate with
  specific recommendations. These may require deliverability or list
  hygiene work outside this skill's scope.

**Quality gate:** Report is produced and delivered to the operator.
`performance-insights.md` is updated.

## Edge Cases & Recovery

- **Brand config is incomplete (e.g., missing font or colour):**
  Use sensible defaults (system sans-serif, #333333 text, #ffffff
  background) and flag every default used. Do not guess brand colours.

- **Klaviyo API key lacks required scopes:**
  Detect from 403 responses. Report exactly which scope is missing
  and how to add it: "The API key needs the `templates:write` scope.
  Add it in Klaviyo → Settings → API Keys → [key name] → Edit scopes."

- **Template HTML exceeds Klaviyo's size limits:**
  Klaviyo can clip emails in Gmail at ~102KB. If assembled HTML exceeds
  90KB, reduce image count or simplify components. Report the issue
  and the current size.

- **Dynamic product feed not configured:**
  If the brief references products but no Klaviyo product feed exists,
  use static product components with hardcoded values. Flag: "Using
  static product data. Set up a Klaviyo product feed for dynamic
  content in future emails."

- **Reviewer is unresponsive:**
  After presenting for approval, wait. Do not proceed without approval.
  After 48 hours with no response, send a single follow-up: "The email
  campaign is still awaiting your review. Let me know if you'd like
  changes or if I should proceed." Do not send more than one follow-up.

- **HTML renders differently across email clients:**
  The component library uses battle-tested email HTML patterns (tables
  for layout, inline CSS, MSO conditionals for Outlook). If a
  rendering issue is reported, diagnose by client and fix in the
  component library — not in the individual campaign template.

- **Flow needs structural changes after creation:**
  The Klaviyo API does not support updating flow definitions after
  creation. Escalate: "This change requires editing the flow directly
  in Klaviyo's UI. Here's what needs to change: [specifics]."

- **Multiple brands sharing this skill:**
  Each brand's config is isolated. Never mix brand assets. When
  switching brands, fully reload the brand config. Verify the logo
  URL, colours, and legal text match the active brand before building.

## Quality Criteria

**Excellent output:**

- Email renders correctly in Gmail, Apple Mail, Outlook (desktop and
  mobile) — no broken tables, no missing images, no clipped content
- Brand is immediately recognisable (colours, typography, logo)
- Subject line is under 50 characters and compelling
- Preview text complements (not repeats) the subject line
- CTA is clear, prominent, and above the fold
- Mobile-responsive layout stacks gracefully
- Klaviyo tags are correctly placed (`{% unsubscribe %}`, profile
  variables, dynamic content blocks)
- Campaign is correctly configured: right audience, right send time
- Performance insights reference specific data, not vague observations
- All agent-generated copy is clearly flagged for reviewer awareness

**Poor output:**

- Broken layout in major email clients
- Missing or wrong brand elements (wrong logo, off-brand colours)
- Subject line over 50 characters or generic ("Check this out!")
- CTA buried below the fold or unclear
- Missing `{% unsubscribe %}` tag (legal compliance issue)
- Campaign sent to wrong audience or at wrong time
- Performance report with no actionable recommendations
- Agent-generated copy presented as if it were client-provided

## Anti-Patterns

- **Skipping the component library.** Every email must be assembled
  from components. Do not write one-off HTML from scratch — it creates
  inconsistency and makes future emails harder to build.

- **Sending without explicit approval.** Never schedule or send a
  campaign without the reviewer's explicit go-ahead. "Looks okay"
  is approval. Silence is not.

- **Hardcoding brand values.** Colours, fonts, and logos come from
  the brand config, not from memory or prior emails. If the brand
  config changes, all future emails should reflect it automatically.

- **Ignoring mobile.** Every email must be tested for mobile rendering.
  If the responsive wrapper is missing, the email is not ready.

- **Generating copy without flagging it.** If you wrote the subject
  line, headline, or body copy, say so. The reviewer needs to know
  what was human-provided vs agent-generated.

- **Using the drag-and-drop editor via browser automation for builds.**
  The component library + API approach is deterministic and repeatable.
  Browser automation for the drag-and-drop editor is fragile. Use the
  API's CODE editor type.

- **Running performance analysis without enough data.** A campaign
  sent to 50 people does not produce statistically meaningful results.
  Note sample size limitations in the report.

- **Mixing brand configs.** When building for Brand A, every asset
  (logo, colours, footer, legal text) must come from Brand A's config.
  Double-check before every build.

## Klaviyo API Reference

For all Klaviyo API details — authentication, endpoints, request
formats, error handling, rate limiting, and known gotchas — read the
`klaviyo-api` skill. This skill delegates all API mechanics to that
shared reference.

Key reference files for this skill's use cases:

- `klaviyo-api/references/templates.md` — creating and managing templates
- `klaviyo-api/references/campaigns.md` — creating and sending campaigns
- `klaviyo-api/references/flows.md` — creating automated flows
- `klaviyo-api/references/reporting.md` — pulling performance metrics
