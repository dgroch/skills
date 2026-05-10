# Hashgifted Intents

Use these intent names consistently across Hashgifted skills and runtime adapters. Add new intents here before consuming them in lifecycle skills.

## Navigation

| Intent | Operator action | Expected context |
| --- | --- | --- |
| `Open campaign applicants` | `navigate(url)` | `campaign applicants` |
| `Open applicants tab` | `click_action(intent)` | `campaign applicants` |
| `Open applicant details` | `click_action(intent)` | applicant detail panel |
| `Open creator thread` | `click_action(intent)` or `navigate(url)` | `creator thread` |
| `Open creator profile` | `click_action(intent)` | `creator profile` |
| `Open first Instagram profile` | `open_in_new_tab(intent)` | external social profile |
| `Open first TikTok profile` | `open_in_new_tab(intent)` | external social profile |
| `Open completed gallery` | `click_action(intent)` or `navigate(url)` | `completed gallery` |
| `Open exclusion list` | `click_action(intent)` or `navigate(url)` | `exclusion list` |

## Reading

| Intent | Operator action | Minimum fields |
| --- | --- | --- |
| `active applicant profile` | `read_card(intent)` | `name`, `handle`, `location`, `follower_count`, `platforms`, `bio`, `application_text`, `status` |
| `active applicant detail panel` | `read_card(intent)` | `name`, `review_count`, `response_time`, `platform_stats`, `application_text`, `notes` |
| `active applicant social signals` | `read_card(intent)` | `location`, `bio`, `recent_content_pattern`, `engagement_quality`, `brand_safety_flags`, `aesthetic_fit` |
| `creator summary` | `read_card(intent)` | `name`, `handle`, `status`, `profile_url`, `social_links` |
| `campaign status` | `read_card(intent)` | `campaign_name`, `status`, `target_selected`, `selected_count`, `applicant_count` |
| `applicants queue status` | `read_card(intent)` | `applicant_count`, `active_tab`, `queue_empty` |
| `active thread` | `read_thread()` | messages with author, timestamp, body, attachments |
| `completed assets` | `read_gallery()` | asset type, source URL, thumbnail URL, caption, creator handle when visible |
| `delivery address` | `read_field(intent)` | delivery string if visible |

## Applicant Actions

| Intent | Risk | Evidence | Notes |
| --- | --- | --- | --- |
| `Shortlist creator` | medium | after | Use only if campaign flow supports shortlist. |
| `Select creator` | high | before and after | Requires approval outside `auto`. Confirm creator identity first. |
| `Decline creator` | high | before and after | Requires approval outside `auto`. Log reason. |
| `Accept this creator` | high | after | Usually a confirmation modal after select. |
| `Next applicant` | low | none | Use `wait_for_change("next applicant loaded")` after. |

## Messaging

| Intent | Operator action | Risk | Notes |
| --- | --- | --- | --- |
| `Message composer` | `compose_message(text)` | medium | Multiline text must remain a draft until `send_message`. |
| `Send message` | `send_message()` | high | Approval-gated outside `auto`. Screenshot draft before send. |
| `message sent` | `wait_for_change(intent)` | low | Confirm the sent bubble appears once. |
| `next applicant loaded` | `wait_for_change(intent)` | low | Re-read active applicant after this wait. |

## Completion And Exclusion

| Intent | Risk | Evidence | Notes |
| --- | --- | --- | --- |
| `Mark complete` | high | before and after | Use for delivered or ghost paths only when lifecycle rules are satisfied. |
| `Add creator to exclusion list` | high | before and after | Use for ghosted creators or score below threshold. |
| `Confirm exclusion` | high | after | Modal confirmation if present. |
| `Change campaign status` | high | before and after | Avoid in early skills unless campaign-level lifecycle explicitly requires it. |

## Asset Capture

| Intent | Operator action | Notes |
| --- | --- | --- |
| `highest resolution completed image` | `extract_media_url(intent)` | Prefer original image when gallery exposes multiple sizes. |
| `highest resolution completed video` | `extract_media_url(intent)` | Prefer the largest playable reel/video source. |
| `download completed asset` | `download_url(url, dest_path)` | Idempotency check before download. |
| `story link in thread` | `read_thread()` | Dispatch to story capture immediately; do not attempt browser capture inside Hashgifted. |

## Ambiguity Rules

Stop and flag when:

- Two visible creators could match the same name or handle.
- The active creator changed after a navigation or modal.
- The action button text is missing or visually ambiguous.
- The page is not in the expected context after one retry.
- A sent message is not visible after send.
