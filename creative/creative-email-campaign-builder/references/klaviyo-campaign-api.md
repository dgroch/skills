# Klaviyo Campaign API Flow (4-Step)

**Date:** 2026-05-27
**Source:** Session testing with Klaviyo API v2024-10-15
**Status:** Verified working end-to-end

## The 4-Step Flow

Klaviyo requires a specific sequence to create a campaign with HTML content:

### Step 1: Create Template with HTML

```bash
POST /api/templates/
{
  "data": {
    "type": "template",
    "attributes": {
      "name": "v5-engine: {Campaign Name}",
      "html": "{full_html}",
      "editor_type": "CODE"
    }
  }
}
```

**Response:** Returns `data.id` (template ID, e.g., `Tkmggz`)

**Pitfalls:**
- `editor_type` must be uppercase `"CODE"` not `"code"`
- HTML goes in the template, NOT in the campaign message content
- Template must be valid HTML (DOCTYPE, proper structure)

### Step 2: Create Campaign with Message Attributes

```bash
POST /api/campaigns/
{
  "data": {
    "type": "campaign",
    "attributes": {
      "name": "{Campaign Name}",
      "audiences": {
        "included": ["{segment_id}"],
        "excluded": []
      },
      "campaign-messages": {
        "data": [{
          "type": "campaign-message",
          "attributes": {
            "channel": "email",
            "content": {
              "subject": "{subject}",
              "preview_text": "{preview}",
              "from_email": "{email}",
              "from_label": "{label}"
            }
          }
        }]
      }
    }
  }
}
```

**Pitfalls:**
- `campaign-messages` is an **attribute** not a relationship — must be in `attributes`, not `relationships`
- `audiences` is **required** — use `{ included: [id], excluded: [] }` format
- `status` is **NOT** a valid create field (remove it)
- The response contains both `campaign.id` and `message.id` in `relationships.campaign-messages.data[0].id`

### Step 3: Assign Template to Campaign Message

```bash
POST /api/campaign-message-assign-template
{
  "data": {
    "type": "campaign-message",
    "id": "{message_id}",
    "relationships": {
      "template": {
        "data": {
          "type": "template",
          "id": "{template_id}"
        }
      }
    }
  }
}
```

**Pitfalls:**
- Endpoint is `/api/campaign-message-assign-template` (not `/api/campaign-messages/{id}/template`)
- Klaviyo **clones** the template — the campaign gets a new template ID (visible in response)
- This is a POST, not PATCH

### Step 4: Cleanup Original Template

```bash
DELETE /api/templates/{template_id}/
```

**Why:** Klaviyo cloned the template in Step 3, so the original is now orphaned. Delete it to avoid clutter.

## Complete Implementation

See `v5-engine/klaviyo.js` for the working implementation. Key functions:
- `createTemplate(name, html)` — Step 1
- `createCampaign(name, audienceId, messageAttrs)` — Step 2
- `assignTemplate(messageId, templateId)` — Step 3
- `deleteTemplate(templateId)` — Step 4
- `createCampaignDraft(opts)` — Orchestrates all 4 steps

## Available Audiences

### Lists (from `/api/lists`):
- `THh7qN` — RH | Newsletter (default fallback)
- `RGH24r` — RH | Weddings
- `S5pEXa` — RH | Customer
- `TXR2Lr` — RH | Prop Shop
- `V2NVR7` — RH | Moments in Bloom Email List

### Segments (from `/api/segments`):
- `Rsqd9r` — [RH] 120-Day Engaged
- `RS7rrj` — RH | Purchasers Past 18 Months
- `SVjLzR` — [RH] Exclusion Segment

## Known Issues

1. **404 after template creation** — Wait 2-3 seconds before assigning template (Klaviyo propagation delay)
2. **Template cloning** — The assign-template endpoint creates a clone (visible as "Clone of {name}" in response). Original can be deleted.
3. **Content in template, not message** — HTML goes in the template. Campaign message content only needs subject/preview/from fields.
