---
name: hashgifted-browser-adapter-map
description: Concrete Hashgifted adapter map for translating portable browser_operator intents into Hashgifted page contexts, semantic UI targets, evidence points, and runtime adapter expectations. Use when building, refactoring, reviewing, or debugging Hashgifted browser automation, especially Playwright + Browserbase, Hermes, Claude-in-Chrome, Camofox, or other implementations of the reference-browser-operator interface.
---

# Hashgifted Browser Adapter Map

Use this skill when a Hashgifted workflow needs concrete UI meaning while staying portable. Read `reference-browser-operator` first, then use this adapter map to resolve Hashgifted-specific intents without leaking runtime calls into consuming skills.

## Operating Boundary

Keep three layers separate:

- Skill layer: business workflow written in `browser_operator` vocabulary.
- Adapter layer: Hashgifted intent map in this skill.
- Runtime layer: Playwright + Browserbase, Hermes, Claude-in-Chrome, Camofox, or another implementation.

If a consuming skill contains `page.click`, selectors, pixel coordinates, MCP browser tool names, or manual sleeps, refactor those details into a runtime adapter.

## References

- Read `references/hashgifted-intents.md` when implementing or reviewing a Hashgifted flow.
- Read `references/runtime-adapters.md` when choosing Playwright, Browserbase, Hermes, Camofox, or visual browser fallbacks.
- Read `references/gift-view-observations.md` when implementing Hashgifted campaign page navigation or applicant shortlisting.

## Page Contexts

Represent Hashgifted pages by context, not by brittle selectors:

- `campaign applicants`: applicant queue for a campaign.
- `creator thread`: in-platform conversation with one creator.
- `creator profile`: creator details, social links, and application data.
- `completed gallery`: completed post/reel asset gallery.
- `campaign settings`: campaign-level configuration, target counts, exclusions, and completion controls.
- `exclusion list`: list or control surface used to block future creator selection.

Adapters should confirm the active context before acting. If the page shape is ambiguous, take a screenshot and stop in `assist` mode.

## Implementation Pattern

For each Hashgifted intent, adapters should store:

```json
{
  "intent": "Select creator",
  "contexts": ["campaign applicants", "creator profile"],
  "operator_action": "click_action",
  "risk": "high",
  "evidence_before": true,
  "evidence_after": true,
  "fallback": "ask for human confirmation if the select control is not unambiguous"
}
```

Selectors are allowed only in runtime adapter code or private runtime configuration, never in SKILL.md bodies for business workflows.

## Approval Gates

Treat these intents as approval-gated outside explicit `auto` mode:

- `Select creator`
- `Decline creator`
- `Send message`
- `Mark complete`
- `Add creator to exclusion list`
- `Change campaign status`

Low-risk reads such as `read_thread`, `read_card("active applicant profile")`, and `read_gallery` may run automatically.

## Evidence

Capture evidence before and after high-risk actions:

- Before: active page context, creator identity, current status, message draft if applicable.
- After: changed status, sent message visible in thread, gallery item captured, or exclusion status visible.

Use the audit schema from `hashgifted-ops-manager/references/audit-log.md` for run records.
