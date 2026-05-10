---
name: reference-browser-operator
description: Reference skill defining the portable browser_operator interface for browser-driven skills. Use when authoring, refactoring, reviewing, or executing skills that need browser automation across runtimes such as Playwright, Browserbase, Hermes, Claude-in-Chrome, Camofox, or visual computer-use tools. Consuming skills must express browser work through this vocabulary instead of selectors, coordinates, or runtime-specific tool names.
---

# Reference Browser Operator

Use `browser_operator` as an intent vocabulary, not as executable tool calls. Skills describe what should happen. Runtime adapters decide how to do it.

## Core Rule

Write browser-driven skills against named semantic actions:

```text
navigate("https://brands.hashgifted.com/gift-view/{campaign_id}")
confirm_context("brands.hashgifted.com/gift-view")
read_card("active applicant profile")
click_action("Select creator")
confirm_modal("Accept this creator")
wait_for_change("creator moved to Selected")
```

Do not put runtime-specific calls in reusable skills: no Playwright selectors, CSS paths, MCP tool names, pixel coordinates, sleeps, or computer-use coordinates. Put those in adapters.

## Actions

### Navigation

- `navigate(url)` -> `status`
- `confirm_context(url_pattern_or_intent)` -> `bool`
- `current_url()` -> `string`
- `back()` / `forward()` -> `status`

### Tabs

- `open_in_new_tab(url_or_intent)` -> `tab_id`
- `switch_tab(tab_id)` -> `status`
- `close_tab(tab_id)` -> `status`
- `current_tab()` -> `tab_id`

### Reading

- `read_card(intent)` -> `dict`
- `read_thread()` -> `list[message]`
- `read_gallery()` -> `list[asset]`
- `read_field(intent)` -> `string`
- `screenshot(label?)` -> `image_ref`

Messages use `{author, timestamp, body, attachments}`. Gallery assets use `{type, url, thumbnail_url, caption, source_url}` where available.

### Interaction

- `click_action(intent)` -> `status`
- `compose_message(text)` -> `status`
- `send_message()` -> `status`
- `fill_field(intent, value)` -> `status`
- `confirm_modal(intent)` -> `status`

### Synchronisation

- `wait_for_change(intent, timeout_seconds=10)` -> `bool`
- `wait_until_visible(intent, timeout_seconds=10)` -> `bool`
- `retry_once(action, recover_intent)` -> `status`

Do not use fixed sleeps in skills. If time is genuinely part of the process, express the event being waited for.

### Assets

- `extract_media_url(intent)` -> `url`
- `download_url(url, dest_path)` -> `status`

Keep file organisation, Drive uploads, Notion writes, and CDN sync in the consuming skill or the relevant non-browser skill.

## Run Modes

Every browser-consuming skill should accept a run mode:

- `plan`: inspect current state and report intended actions only.
- `dry_run`: render decisions, messages, filenames, and updates, but do not click, send, upload, or write.
- `assist`: act until a high-risk approval gate, then ask for confirmation.
- `auto`: act without approval only for proven low-risk paths.

Default to `assist` for live Hashgifted operations unless the user explicitly requests another mode.

High-risk actions include creator select, decline, exclusion, message send, mark complete, public posting, and any destructive or irreversible record update.

## Audit Contract

Every run should emit or append a structured audit record. At minimum include:

```json
{
  "run_id": "timestamp-or-uuid",
  "skill": "skill-name",
  "mode": "assist",
  "runtime": "playwright-browserbase",
  "campaign": "campaign-name-or-id",
  "creator": "creator-handle-or-null",
  "actions": [
    {"action": "navigate", "intent": "campaign applicants", "status": "ok"}
  ],
  "evidence": ["screenshot_before", "screenshot_after"],
  "external_updates": [],
  "warnings": []
}
```

Skills may add fields, but should not omit these core fields when browser actions occur.

## Runtime Adapters

Recommended production stack:

- Playwright for deterministic operation.
- Browserbase for persistent sessions, remote debugging, replay, and fewer local browser issues.
- Camofox as a fallback for automation-hostile flows.
- Hermes or other visual browser tools for exploration, diagnosis, and one-off assisted runs.

Adapters may cache selectors or coordinates, but caches are implementation detail. Skills continue to use semantic intents.

## Failure Rules

- Treat every action as returning a status.
- Branch on missing context instead of assuming the page is correct.
- Capture evidence before and after risky actions.
- Retry transient UI failures once.
- Stop and flag when authentication, checkpointing, 2FA, account trust, or platform-rate issues appear.
- Never have a Hashgifted skill repair Instagram authentication. Report: `IG story capture session expired; manual re-auth required.`

## Versioning

This is `browser_operator` v1. Adding actions is non-breaking. Renaming or changing return shapes requires a major version bump.
