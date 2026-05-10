# Runtime Adapters

Keep this file about implementation choices. Business skills should not load it unless they are building or debugging an adapter.

## Recommended Production Stack

Use Playwright on Browserbase for production Hashgifted operation.

- Playwright provides deterministic DOM-aware control, network waits, downloads, and repeatable assertions.
- Browserbase provides persistent sessions, remote debugging, replay, and fewer local browser issues.
- Store Hashgifted session state in Browserbase. Do not put credentials in skill files.
- Emit screenshots, trace links, and replay URLs into the audit log for high-risk actions.

## Exploration Stack

Use Hermes, Claude-in-Chrome, or another visual browser runtime for exploration and one-off assisted diagnosis.

- Use visual reasoning to discover page shape and intent names.
- Convert discoveries into the adapter map before using them in production.
- Do not paste pixel coordinates back into consuming skills.

## Fallback Stack

Use Camofox only when Hashgifted or Instagram-adjacent surfaces become automation-hostile.

- Keep the same `browser_operator` surface.
- Treat Camofox-specific settings as runtime configuration.
- Increase evidence capture and approval gates while confidence is low.

## Adapter Responsibilities

Runtime adapters are responsible for:

- Resolving semantic intents to selectors, accessibility locators, text locators, or visual actions.
- Managing logged-in sessions.
- Waiting for UI changes without fixed sleeps.
- Producing screenshots and trace evidence.
- Returning explicit statuses for every action.
- Redacting sensitive cookies, tokens, addresses, and private message contents from shared logs where required.

## Suggested Return Shape

```json
{
  "ok": true,
  "action": "click_action",
  "intent": "Select creator",
  "context": "campaign applicants",
  "evidence": ["browserbase_trace_url", "screenshot_after"],
  "warning": null
}
```

Use `ok: false` with a clear error code for failures: `context_mismatch`, `intent_ambiguous`, `auth_required`, `rate_limited`, `network_error`, `ui_changed`, `not_found`, `timeout`, `approval_required`.
