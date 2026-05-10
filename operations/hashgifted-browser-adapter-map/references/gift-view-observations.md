# Hashgifted Gift View Observations

Observed via Browserbase + Playwright against `brands.hashgifted.com/gift-view/{campaign_id}` on 2026-05-10. Treat these as adapter hints, not business-skill instructions.

## Authentication

- Use `BROWSERBASE_HASHGIFTED_CONTEXT_ID` from local `.env` for authenticated Browserbase sessions.
- Start production sessions with the saved Browserbase Context. If navigation redirects to `/login`, stop and request manual re-auth.
- Do not run multiple sessions against the same Browserbase Context at the same time.

## Campaign Page

- Campaign URLs follow `https://brands.hashgifted.com/gift-view/{campaign_id}`.
- Page title is `#gifted`.
- Top campaign tabs are `role=tab` elements:
  - `#tab-waves`: `Matches`
  - `#tab-creative`: `Creative`
  - `#tab-audience`: `Audience`
  - `#tab-platforms`: `Platforms`
  - `#tab-tone-selector`: `Tone Selector`
  - `#tab-automated-details`: `Automated Details`
  - `#tab-completed-content`: `Completed content`
- The Matches page shows status counts for `Applicants`, `Shortlist`, `Selected`, and `Declined`.
- There are `All`, `Read`, and `Unread` filters inside the applicant list surface.

## Applicant List

- The applicant list is inside `#scrollBox`.
- Applicant rows are visible as `#scrollBox [role=button]` elements whose text includes follower and engagement fields.
- Each visible row has action buttons scoped within the row:
  - `button.reject-button-{index}` with text `Decline`
  - `button.shortlist-button-{index}` with text `Shortlist`
  - `button.select-button-{index}` may exist with empty visible text
- The numeric suffix changes with current visible list order. Do not use the suffix as a creator identity. Scope actions to the row after confirming the row text/name.
- Prefer semantic Playwright locators scoped to the active row over global `button.shortlist-button-0` style selectors.

## Applicant Detail

- Clicking an applicant row opens or updates a detail/notes panel on the same URL.
- The detail panel includes profile summary data such as review count, response time, platform stats, and application text.
- Important: clicking a row may mark an applicant as read. For strict read-only discovery, inspect DOM only and do not click rows unless the user allows read-state changes.
- Initial DOM inspection did not expose Instagram/TikTok profile URLs as plain anchors in the applicant list. Social/profile exploration may require opening the applicant detail/profile control first.

## Risk Notes

- `Stop applications`, `Save`, and `Close` controls are visible near campaign setup/edit surfaces. Treat them as high-risk and out of scope for applicant shortlisting.
- `Decline` is high-risk. Use approval gates and evidence.
- `Shortlist` is medium-risk. It does not contact the creator, but it changes campaign state.
- `Select` exists in the DOM on applicant rows but belongs to the separate creator-selection workflow, not `hashgifted-creator-shortlist`.
