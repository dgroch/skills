---
name: reference-browser-operator
description: Reference skill defining the abstract browser_operator interface — the named actions consuming skills use to drive a web browser. Decouples skills from any specific browser runtime (Claude-in-Chrome, Cowork, Hermes/Computer Use, Playwright). Consuming skills MUST reference these named actions rather than calling runtime-specific browser tools directly. Read this once before authoring or refactoring any browser-driven skill.
---

# Reference: browser_operator interface for hashgifted

The abstract action vocabulary every browser-driven skill should be written against. The runtime executing the skill — Claude-in-Chrome, Cowork, Hermes — provides its own implementation.

Skills describe **intent**. The runtime resolves **how**.

## Why this exists

A SKILL.md that hard-codes `mcp__Claude_in_Chrome__computer` calls only runs in Claude-in-Chrome. The same workflow written against `click_action("decline button")` runs anywhere a runtime adapter exists. We pay a small cost in determinism for full portability.

## How to consume

In a consuming skill:

- Reference this skill in its frontmatter or body: *"Browser actions follow `reference-browser-operator`."*
- Use the action names below as a verb vocabulary — not as tool calls. Example: *"`click_action("Select")` then `confirm_modal("Accept this creator")`."*
- Don't include runtime-specific tool names. No `mcp__...`, no `computer.click(x, y)`, no `page.click(selector)` — those belong in adapters, not skills

## The interface — v1

### Navigation & context

- **`navigate(url)`** — go to URL. Waits for page load
- **`confirm_context(url_pattern)`** → `bool` — assert current page matches the expected pattern. Skill should branch on this rather than assume
- **`current_url()`** → `string`
- **`back()`** / **`forward()`** — browser history nav

### Tabs

- **`open_in_new_tab(url_or_intent)`** → `tab_id` — open a link in a new tab. Accepts a URL or an intent like *"first Instagram link in the profile"*
- **`switch_tab(tab_id)`**
- **`close_tab(tab_id)`**
- **`current_tab()`** → `tab_id`

### Reading

- **`read_card(intent)`** → `dict` — extract structured fields from a visible card. Example: `read_card("applicant profile")` returns `{name, handle, follower_count, bio, application_text}`. The runtime decides what fields belong to that intent
- **`read_thread()`** → `list[message]` — read all messages in the active conversation. Each `message` has `{author, timestamp, body, attachments}`
- **`read_gallery()`** → `list[asset]` — list assets in the current gallery view. Each `asset` has `{type, url, thumbnail_url, caption}`
- **`read_field(intent)`** → `string` — read a single named field. Example: `read_field("delivery address")`
- **`screenshot()`** → `image` — useful for visual verification or evidence

### Interaction

- **`click_action(intent)`** — semantic click. Example: `click_action("Decline button")` or `click_action("first Instagram link")`
- **`compose_message(text)`** — focus the active composer, type the text. Multiline-aware: newlines in `text` produce real newlines, not premature sends
- **`send_message()`** — send the currently composed message
- **`fill_field(intent, value)`** — find a form field by intent, type the value
- **`confirm_modal(intent)`** — handle a confirmation modal by clicking the named confirm button. Example: `confirm_modal("Accept this creator")`

### Synchronisation

- **`wait_for_change(intent, timeout_seconds=10)`** — block until something happens. Example: `wait_for_change("next applicant loaded")`. Times out and returns false rather than hanging

### Assets

- **`download_url(url, dest_path)`** — pull a binary from a known URL to disk. Used for assets where the URL is already known
- **`extract_media_url(intent)`** → `url` — find a media element on the current page and return its source URL. Used for stories, embedded videos, etc., where the URL isn't directly clickable

## Conventions

- **Intent strings are descriptive, not selectors.** `"Decline button"` not `"button[data-action='decline']"`. Adapters do the resolution
- **Failure is explicit.** Every action returns a status. Skills branch on it, don't assume success
- **Idempotency where possible.** `navigate(url)` to the current URL is a no-op
- **No coordinates in skills.** The existing `hashgifted-inbox-triage` has hard-coded pixel coordinates — those move to the Claude-in-Chrome adapter, not the skill
- **No `sleep(n)` in skills.** Use `wait_for_change(intent)` instead — adapters can implement it as polling, event listening, or timeouts as appropriate

## Runtime adapters

Each runtime maintains its own mapping from this vocabulary to its concrete tools:

- **Claude-in-Chrome adapter** — uses `find` for intent resolution, `computer` for clicks/typing, `read_page` for structured reads, tabs MCP for tab management. Pixel coordinates live here as caches, not in skills
- **Cowork adapter** — currently delegates to Claude-in-Chrome under the hood; same surface
- **Hermes / Computer Use adapter** — uses Anthropic Computer Use API directly. Intent strings pass through to the model, which handles visual reasoning
- **Hermes / Playwright adapter** *(future, deterministic-only)* — requires a per-skill intent-to-selector map. Trades portability for speed/cost. Use only for high-volume deterministic flows

## Out of scope

- Authentication. Each runtime handles its own session state. Skills assume logged-in
- File system. `download_url` writes to disk; everything beyond is the consuming skill's job (organising in Drive, syncing to brand-cdn, embedding in Notion)
- Anything not browser-related — Notion writes, Drive writes, Slack messages, etc. Those use their own MCPs

## Versioning

This is v1 of the interface. Breaking changes get a major bump. Adding a new action is non-breaking. Consuming skills should pin to a major version in their frontmatter once we go past v1:

```yaml
browser_operator_version: 1
```

## Quick example — what a skill looks like against this interface

> 1. `navigate("https://brands.hashgifted.com/gift-view/{campaign_id}")`
> 2. `confirm_context("brands.hashgifted.com/gift-view")` — bail if false
> 3. For each applicant card at top of Applicants list:
>    - `read_card("applicant profile")` → `applicant`
>    - Decide Decline / Shortlist / Select (see Decision framework)
>    - `compose_message(rendered_template)`
>    - `send_message()`
>    - `click_action("{decision} button")`
>    - If Select: `confirm_modal("Accept this creator")`
>    - `wait_for_change("next applicant loaded")`
> 4. Stop when target hit or queue empty

No tool names. No coordinates. Runs anywhere there's an adapter.
