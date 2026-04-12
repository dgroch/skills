---
name: higgsfield-api
description: >
  Reference skill for generating images and videos via the Higgsfield AI API.
  Covers authentication, the async request lifecycle (submit → poll → download),
  webhook integration, the Python SDK (higgsfield-client), file uploads, and
  model selection for text-to-image and image-to-video pipelines. Use this skill
  whenever an agent needs to generate images from text prompts, animate still
  images into video, upload source images to Higgsfield, poll or manage generation
  requests, or configure webhook delivery for completed assets. Also use when
  debugging Higgsfield API errors, choosing between SDK and raw REST, selecting
  models (Soul, DoP, Kling, Seedance, Seedream, FLUX, Reve), or integrating
  Higgsfield into any content pipeline. This is a reference skill — it teaches
  the agent how to talk to Higgsfield, not what creative assets to produce.
  Consuming skills (like ad-creative-builder or ai-video-generation) define
  the "what".
version: 1.0.0
author: CSTMR
license: MIT
metadata:
  tags: [API, Higgsfield, Image Generation, Video Generation, AI Media, Reference]
---

# Higgsfield API

## Overview

Higgsfield is a unified API gateway to 100+ generative media models for image,
video, voice, and audio. All models share a single async request-response
pattern: submit a job, poll (or receive a webhook), then download the output.

**Base URL:** `https://platform.higgsfield.ai`
**Dashboard / API keys:** `https://cloud.higgsfield.ai`
**Docs:** `https://docs.higgsfield.ai`

## Authentication

Every request requires an `Authorization` header with your API key and secret:

```
Authorization: Key {api_key}:{api_key_secret}
```

Generate credentials at https://cloud.higgsfield.ai.

For the Python SDK, set environment variables:

```bash
# Option A — single combined key
export HF_KEY="your-api-key:your-api-secret"

# Option B — separate values
export HF_API_KEY="your-api-key"
export HF_API_SECRET="your-api-secret"
```

> **Security:** Never commit credentials. Use env vars or a secrets manager.

## Request Lifecycle

Higgsfield is fully asynchronous. Every generation follows this flow:

1. **Submit** — POST to `/{model_id}` with your payload. Returns `request_id`.
2. **Poll** — GET `/requests/{request_id}/status` until terminal status.
3. **Download** — On `completed`, extract URLs from `images[]` or `video`.

### Statuses

| Status        | Terminal? | Billed? | Description                                    |
|---------------|-----------|---------|------------------------------------------------|
| `queued`      | No        | No      | Waiting in queue. Can be cancelled.             |
| `in_progress` | No        | No      | Actively generating. Cannot cancel.             |
| `completed`   | Yes       | Yes     | Output ready. URLs valid for ≥7 days.           |
| `failed`      | Yes       | No      | Error occurred. Credits refunded.               |
| `nsfw`        | Yes       | No      | Content moderation rejection. Credits refunded. |

### Cancellation

POST `/requests/{request_id}/cancel` — only works while `queued`.
Returns `202 Accepted` on success, `400 Bad Request` otherwise.

## Endpoints (REST)

### Submit a generation

```
POST https://platform.higgsfield.ai/{model_id}
Authorization: Key {key}:{secret}
Content-Type: application/json

{
  "prompt": "...",
  ... model-specific params
}
```

Response:

```json
{
  "status": "queued",
  "request_id": "d7e6c0f3-...",
  "status_url": "https://platform.higgsfield.ai/requests/{request_id}/status",
  "cancel_url": "https://platform.higgsfield.ai/requests/{request_id}/cancel"
}
```

### Check status

```
GET https://platform.higgsfield.ai/requests/{request_id}/status
Authorization: Key {key}:{secret}
```

Completed image response adds `"images": [{"url": "..."}]`.
Completed video response adds `"video": {"url": "..."}`.

## Webhooks

Append `?hf_webhook={url}` to the submit endpoint to receive an HTTP POST
on terminal status (`completed`, `failed`, `nsfw`). This eliminates polling.

```
POST https://platform.higgsfield.ai/{model_id}?hf_webhook=https://your-server.com/hook
```

### Webhook payload shapes

**Completed (image):**
```json
{"status": "completed", "request_id": "...", "images": [{"url": "..."}]}
```

**Completed (video):**
```json
{"status": "completed", "request_id": "...", "video": {"url": "..."}}
```

**Failed:**
```json
{"status": "failed", "request_id": "...", "error": "..."}
```

**NSFW:**
```json
{"status": "nsfw", "request_id": "..."}
```

### Webhook requirements

- Endpoint must accept POST and return 2xx promptly (<10 s).
- Retries continue for up to 2 hours on non-2xx responses.
- Implement idempotency using `request_id` (duplicate deliveries possible).
- Use HTTPS.
- If webhook delivery fails, fall back to polling the `status_url`.

## Python SDK

```bash
pip install higgsfield-client
```

Requires Python ≥ 3.8. Supports both sync and async.

### Pattern 1 — Submit and wait (simplest)

```python
import higgsfield_client

result = higgsfield_client.subscribe(
    'bytedance/seedream/v4/text-to-image',
    arguments={
        'prompt': 'A serene lake at sunset with mountains',
        'resolution': '2K',
        'aspect_ratio': '16:9',
    }
)
print(result['images'][0]['url'])
```

### Pattern 2 — Submit, poll, track progress

```python
import higgsfield_client

ctrl = higgsfield_client.submit(
    'bytedance/seedream/v4/text-to-image',
    arguments={
        'prompt': 'Football ball',
        'resolution': '2K',
        'aspect_ratio': '16:9',
    },
    webhook_url='https://example.com/webhook'  # optional
)

for status in ctrl.poll_request_status():
    if isinstance(status, higgsfield_client.Queued):
        print('Queued')
    elif isinstance(status, higgsfield_client.InProgress):
        print('In progress')
    elif isinstance(status, higgsfield_client.Completed):
        print('Completed')
    elif isinstance(status, (higgsfield_client.Failed,
                             higgsfield_client.NSFW,
                             higgsfield_client.Cancelled)):
        print('Terminal non-success')

result = ctrl.get()
print(result['images'][0]['url'])
```

### Pattern 3 — Callbacks

```python
import higgsfield_client

result = higgsfield_client.subscribe(
    'bytedance/seedream/v4/text-to-image',
    arguments={'prompt': '...', 'resolution': '2K', 'aspect_ratio': '16:9'},
    on_enqueue=lambda rid: print(f'Enqueued: {rid}'),
    on_queue_update=lambda s: print(f'Status: {s}'),
)
```

### Pattern 4 — Manage existing requests

```python
ctrl = higgsfield_client.submit(...)

ctrl.status()   # check current status
ctrl.get()      # block until complete, return result
ctrl.cancel()   # cancel if still queued
```

### File uploads (for image-to-video)

```python
import higgsfield_client

# From bytes
with open('photo.jpg', 'rb') as f:
    url = higgsfield_client.upload(f.read(), 'image/jpeg')

# From file path
url = higgsfield_client.upload_file('photo.jpg')

# From PIL Image
from PIL import Image
img = Image.open('photo.jpg')
url = higgsfield_client.upload_image(img, format='jpeg')
```

Use the returned `url` as `image_url` in image-to-video requests.

### Async variants

All sync functions have async counterparts — prefix with `async_`:

```python
import higgsfield_client

result = await higgsfield_client.async_subscribe(...)
ctrl = await higgsfield_client.async_submit(...)
url = await higgsfield_client.async_upload(data, content_type)
```

## Models

Higgsfield hosts 100+ models. Browse all at https://cloud.higgsfield.ai/explore.
Key models referenced in docs:

### Text-to-image

| Model ID                              | Notes                          |
|---------------------------------------|--------------------------------|
| `higgsfield-ai/soul/standard`        | Flagship text-to-image         |
| `reve/text-to-image`                 | Versatile general-purpose      |
| `bytedance/seedream/v4/text-to-image`| High-quality, supports 2K      |
| `bytedance/seedream/v4/edit`         | Image editing                  |

Common parameters: `prompt`, `aspect_ratio` (e.g. `"16:9"`),
`resolution` (e.g. `"720p"`, `"2K"`).

### Image-to-video

| Model ID                                          | Notes                      |
|---------------------------------------------------|----------------------------|
| `higgsfield-ai/dop/standard`                     | Higgsfield native          |
| `higgsfield-ai/dop/preview`                      | Preview tier               |
| `bytedance/seedance/v1/pro/image-to-video`       | Professional grade         |
| `kling-video/v2.1/pro/image-to-video`            | Cinematic animations       |

Common parameters: `image_url`, `prompt` (motion description),
`duration` (seconds, e.g. `5`).

## Prompting Best Practices

### Text-to-image

- Be specific: style, mood, colours, composition.
- Specify artistic style: "photorealistic", "watercolour", "digital art".
- Include quality modifiers: "highly detailed", "8k", "professional".
- Include camera/lens details for photorealistic work.

### Image-to-video (motion prompts)

- Describe the movement explicitly: pan, zoom, rotation, orbit.
- Set pace: "slowly", "smoothly", "quickly".
- Specify camera motion: "camera pans left", "zooms in".
- Add atmosphere: "wind blowing", "water flowing", "lights flickering".

### Source image tips (image-to-video)

- Use high-resolution, minimally compressed source images (PNG or high-quality JPEG).
- Clear subjects with good composition animate best.
- Match source aspect ratio to desired output aspect ratio.

## Output Retention

Generated files are stored for a minimum of 7 days. Download and persist
to your own storage promptly — URLs may expire after the retention window.

## Error Handling Checklist

1. **Auth errors** — Verify `Authorization: Key {key}:{secret}` format.
2. **`failed` status** — Retry with adjusted prompt or parameters. Credits refunded.
3. **`nsfw` status** — Content moderation triggered. Revise prompt. Credits refunded.
4. **Webhook not firing** — Ensure endpoint is publicly reachable, returns 2xx
   within 10 s, and handles retries idempotently. Fall back to polling.
5. **Cancel returns 400** — Request already moved past `queued` state.
6. **Rate limits** — Check your plan limits in the dashboard. Contact
   support@higgsfield.ai for enterprise limits.

## Integration Patterns

### Poll-based (simple scripts, one-off jobs)

Use `higgsfield_client.subscribe()` — blocks until complete.

### Webhook-based (production pipelines)

Append `?hf_webhook=...` to submit endpoint. Process results in your
webhook handler. Implement idempotency and fall back to polling on failure.

### Batch processing

Submit multiple requests, store `request_id` values, poll or receive
webhooks for each. Higgsfield auto-scales — no concurrency limits on
your side beyond your plan's rate limits.

## What This Skill Does NOT Cover

- Creative direction or prompt writing for specific campaigns (see
  consuming skills like `ad-creative-builder`).
- Video editing, timeline assembly, or post-production (see
  `ai-video-generation` if available).
- Billing, pricing, or plan selection — check the dashboard.
- Models beyond Higgsfield (e.g. direct Runway, Pika, etc.).
