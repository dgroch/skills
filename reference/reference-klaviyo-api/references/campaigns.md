# Klaviyo Campaigns API

## Overview

Campaigns represent scheduled email/SMS sends. They contain one or more
campaign messages (the actual content) and target specific lists/segments.

**Scopes required:** `campaigns:read`, `campaigns:write`

## Creating a Campaign

### Endpoint

```
POST /api/campaigns/
```

### Critical: campaign-messages is an ATTRIBUTE, not a relationship

The Klaviyo API has a non-obvious structure for campaign creation. The
`campaign-messages` field is nested **inside** `attributes`, not as a
sibling `relationships` object.

**Correct structure:**

```json
{
  "data": {
    "type": "campaign",
    "attributes": {
      "name": "Campaign Name",
      "audiences": {
        "included": ["LIST_ID"],
        "excluded": []
      },
      "campaign-messages": {
        "data": [{
          "type": "campaign-message",
          "attributes": {
            "channel": "email",
            "content": {
              "subject": "Email Subject",
              "preview_text": "Preview text",
              "from_email": "sender@example.com",
              "from_label": "Sender Name"
            }
          }
        }]
      }
    }
  }
}
```

**Common mistakes:**

- ❌ Putting `campaign-messages` in a top-level `relationships` object
- ❌ Using `included-segment-ids` or `included-list-ids` in audiences
  (correct: `included` and `excluded` as plain arrays of IDs)
- ❌ Including `html` directly in the message content (not allowed on create)

### Required fields

- `name` (string) — campaign name
- `audiences` (object) — must have `included` array with at least one
  list/segment ID
- `campaign-messages` (object) — at least one message with `channel`
  and `content` (subject, from_email, from_label required for email)

### Optional fields

- `audiences.excluded` — array of list/segment IDs to exclude
- `send_strategy` — scheduling method (static, throttled, STO)
- `send_options` — smart sending, ignore unsubscribes
- `tracking_options` — click/open tracking, custom params

### Response

Returns the created campaign with ID and auto-generated message IDs:

```json
{
  "data": {
    "type": "campaign",
    "id": "01KSMVMKX2GXBCYSNVN7VR3196",
    "attributes": {
      "name": "Campaign Name",
      "status": "Draft",
      ...
    },
    "relationships": {
      "campaign-messages": {
        "data": [{
          "type": "campaign-message",
          "id": "01KSMVMKXAQXX6YMJEQVJ0VSKD"
        }]
      }
    }
  }
}
```

## Adding HTML Content to a Campaign

Campaigns are created without HTML content. To add HTML:

### Step 1: Create a CODE template with your HTML

```
POST /api/templates/
```

```json
{
  "data": {
    "type": "template",
    "attributes": {
      "name": "Template Name",
      "html": "<!DOCTYPE html>...",
      "editor_type": "CODE"
    }
  }
}
```

**Note:** `editor_type` must be uppercase `"CODE"`. Returns template ID.

### Step 2: Assign the template to the campaign message

```
POST /api/campaign-message-assign-template
```

```json
{
  "data": {
    "type": "campaign-message",
    "id": "MESSAGE_ID_FROM_CAMPAIGN",
    "relationships": {
      "template": {
        "data": {
          "type": "template",
          "id": "TEMPLATE_ID_FROM_STEP_1"
        }
      }
    }
  }
}
```

**Important:** Klaviyo **clones** the template when assigning it. The
response includes a new template ID (the clone). The original template
can be deleted after assignment.

### Step 3: Delete the original template (cleanup)

```
DELETE /api/templates/{template_id}/
```

The campaign now references the cloned template and is ready to send.

## Complete Campaign Creation Flow

```javascript
// 1. Create template with HTML
const template = await klaviyoRequest('POST', '/templates/', {
  data: {
    type: 'template',
    attributes: {
      name: 'Template Name',
      html: fullHtmlString,
      editor_type: 'CODE'
    }
  }
});
const templateId = template.data.data.id;

// 2. Create campaign with message (no HTML yet)
const campaign = await klaviyoRequest('POST', '/campaigns/', {
  data: {
    type: 'campaign',
    attributes: {
      name: 'Campaign Name',
      audiences: { included: ['LIST_ID'], excluded: [] },
      'campaign-messages': {
        data: [{
          type: 'campaign-message',
          attributes: {
            channel: 'email',
            content: {
              subject: 'Subject',
              preview_text: 'Preview',
              from_email: 'sender@example.com',
              from_label: 'Sender'
            }
          }
        }]
      }
    }
  }
});
const campaignId = campaign.data.data.id;
const messageId = campaign.data.data.relationships['campaign-messages'].data[0].id;

// 3. Assign template to message (Klaviyo clones it)
await klaviyoRequest('POST', '/campaign-message-assign-template', {
  data: {
    type: 'campaign-message',
    id: messageId,
    relationships: {
      template: {
        data: { type: 'template', id: templateId }
      }
    }
  }
});

// 4. Delete original template (cleanup)
await klaviyoRequest('DELETE', `/templates/${templateId}/`);
```

## Getting Campaigns

### List campaigns

```
GET /api/campaigns/?filter=equals(messages.channel,'email')
```

**Required filter:** You must filter by channel. Use:
- `equals(messages.channel,'email')` for email campaigns
- `equals(messages.channel,'sms')` for SMS campaigns

### Get single campaign

```
GET /api/campaigns/{campaign_id}/
```

### Get campaign messages

```
GET /api/campaigns/{campaign_id}/campaign-messages/
```

## Updating Campaigns

### Update campaign attributes

```
PATCH /api/campaigns/{campaign_id}/
```

Can update: name, audiences, send_strategy, send_options, tracking_options.

### Update campaign message

```
PATCH /api/campaign-messages/{message_id}/
```

Can update: content (subject, preview_text, from_email, from_label),
channel, render_options.

## Sending Campaigns

### Schedule a campaign

```
POST /api/campaigns/{campaign_id}/send/
```

```json
{
  "data": {
    "type": "campaign-send",
    "attributes": {
      "scheduled_at": "2026-06-01T10:00:00+10:00"
    }
  }
}
```

### Send immediately

Omit `scheduled_at` or set to current time.

## Campaign Statuses

- `Draft` — not yet scheduled or sent
- `Scheduled` — scheduled for future send
- `Queued` — in send queue, not yet sent
- `Sending` — currently sending
- `Sent` — completed
- `Cancelled` — cancelled before send

## Rate Limits

Campaign endpoints use tier M (10/s burst, 150/m steady) for reads
and tier S (3/s burst, 60/m steady) for writes.

## Anti-Patterns

- **Creating campaigns without filtering by channel.** The list endpoint
  requires a channel filter. Always include
  `filter=equals(messages.channel,'email')` or `'sms'`.

- **Trying to include HTML directly in campaign message content.**
  HTML must be added via template assignment, not in the create payload.

- **Using `included-segment-ids` in audiences.** The correct field names
  are `included` and `excluded` (plain arrays of IDs).

- **Forgetting to delete the original template after assignment.**
  Klaviyo clones it, so the original becomes orphaned.

- **Updating a cloned template immediately after assignment.** The
  clone may not be immediately queryable. Wait 2-3 seconds if you
  need to modify the cloned template.
