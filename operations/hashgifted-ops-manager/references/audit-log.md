# Audit Log

Every Hashgifted browser operator run should return or append a structured audit record.

## Minimum Schema

```json
{
  "run_id": "2026-05-10T09-45-00Z_hashgifted",
  "skill": "hashgifted-creator-shortlist",
  "mode": "assist",
  "runtime": "playwright-browserbase",
  "campaign": {
    "name": "Campaign Name",
    "hashgifted_url": "https://brands.hashgifted.com/...",
    "notion_id": "optional"
  },
  "creator": {
    "name": "Creator Name",
    "handle": "@handle",
    "notion_id": "optional"
  },
  "actions": [
    {
      "action": "navigate",
      "intent": "Open creator thread",
      "status": "ok",
      "timestamp": "2026-05-10T09:45:10Z"
    }
  ],
  "evidence": [
    {
      "label": "before_send",
      "type": "screenshot",
      "ref": "path-or-runtime-url"
    }
  ],
  "external_updates": [
    {
      "system": "notion",
      "record": "creator",
      "status": "ok"
    }
  ],
  "warnings": []
}
```

## Action Statuses

Use consistent statuses:

- `ok`
- `skipped`
- `approval_required`
- `failed`
- `retry_ok`
- `retry_failed`
- `not_applicable`

## Evidence Rules

Capture evidence for:

- Page context before selecting, declining, excluding, or completing.
- Message draft before sending.
- Sent message after sending.
- Asset card before capture.
- Download or CDN result after capture.

Redact tokens, cookies, private addresses, and unrelated private messages when logs leave the secure environment.

## Warning Codes

Use concise warning codes:

- `context_mismatch`
- `creator_identity_ambiguous`
- `message_not_visible_after_send`
- `notion_write_failed`
- `drive_upload_failed`
- `cdn_sync_failed`
- `ig_session_expired`
- `auth_required`
- `rate_limited`
- `ui_changed`
- `manual_review_required`
