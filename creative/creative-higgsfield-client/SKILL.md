---
name: creative-higgsfield-client
description: Generate images and videos via the Higgsfield CLI. This is a reference skill — it teaches the agent how to use the `higgsfield` CLI, not what creative assets to produce. Consuming skills (like ad-creative-builder or ugc-photo-generation) define the "what".
version: 3.0.0
author: CSTMR
license: MIT
metadata:
  tags: [CLI, Higgsfield, Image Generation, Video Generation, AI Media, Reference]
---

# Higgsfield CLI

## Overview

Higgsfield is a unified gateway to 30+ generative media models for image
and video. Access is via the `higgsfield` CLI — no REST calls, no API keys
to manage, no polling loops required.

**Dashboard:** `https://cloud.higgsfield.ai`
**Docs:** `https://docs.higgsfield.ai`
**CLI repo:** `https://github.com/higgsfield-ai/cli`

## Bootstrap

Before any other command, verify the CLI is installed and authenticated:

1. If `higgsfield` is not on `$PATH`, install it:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
   ```
2. Run `higgsfield account status`. If it fails with `Session expired` / `Not authenticated`, ask the user to run `higgsfield auth login` (interactive, opens browser).

Skip both checks if `higgsfield account status` prints account info.

## Image Generation

```bash
higgsfield generate create <model_id> --prompt "..." [--image <path-or-id>] [--aspect_ratio 16:9] [--resolution 2k] --wait
```

`--wait` blocks until the job completes and prints the result URL. Use `--wait-timeout 20m` for longer jobs.

### Key image models

| Model ID | Best for |
|----------|----------|
| `gpt_image_2` | Default general — graphic design, UI, banners, typography |
| `nano_banana_2` | Top quality 4K, text/diagrams, character/cartoon |
| `text2image_soul_v2` | Portraits, fashion, UGC, editorial |
| `soul_cast` | Text-only character/avatar |
| `soul_location` | Locations, environments, no-people scenes |
| `seedream_4_5` | Vector illustrations, face edit + scene swap |
| `marketing_studio_image` | Commercial/product/ads |

### Using reference images

Media flags accept a local file path (auto-uploaded) or a UUID:

```bash
higgsfield generate create nano_banana_2 --prompt "..." --image ./ref.png --wait
```

### Batch generation

Not a built-in flag — submit multiple `generate create` calls.

## Video Generation

```bash
higgsfield generate create <model_id> --prompt "..." [--start-image <path-or-id>] [--duration 5] --wait
```

### Key video models

| Model ID | Best for |
|----------|----------|
| `seedance_2_0` | Default all-purpose video, multi-shot, identity preservation |
| `kling3_0` | Multi-shot, audio, motion transfer |
| `marketing_studio_video` | Commercial/product/branded ads |

### Media flags

| Flag | Purpose |
|------|---------|
| `--image <path-or-id>` | Reference image |
| `--start-image <path-or-id>` | First frame (image-to-video) |
| `--end-image <path-or-id>` | Last frame (transitions) |
| `--video <path-or-id>` | Reference video |
| `--audio <path-or-id>` | Audio for lipsync/soundtrack |

## Marketing Studio

Branded image/video generation with avatars + products.

### Quick ad video workflow

1. **Fetch product:** `higgsfield marketing-studio products fetch --url <url> --wait`
2. **Pick avatar:** `higgsfield marketing-studio avatars list`
3. **Generate:**
   ```bash
   higgsfield generate create marketing_studio_video \
     --prompt "..." \
     --avatars '[{"id":"<avatar_id>","type":"preset"}]' \
     --product_ids '[<product_id>]' \
     --mode ugc \
     --duration 15 \
     --aspect_ratio 9:16 \
     --wait
   ```

Modes: `ugc`, `tutorial`, `ugc_unboxing`, `hyper_motion`, `product_review`, `tv_spot`, `wild_card`, `ugc_virtual_try_on`, `virtual_try_on`.

## File Uploads

```bash
higgsfield upload create <file_path>
```

Returns an upload UUID. Use the UUID in media flags for subsequent generations.

## Model Discovery

```bash
higgsfield model list --json          # all models
higgsfield model get <model_id> --json  # model params/schema
```

## Job Management

```bash
higgsfield generate list --json       # past jobs
higgsfield generate get <id> --json   # specific job details
higgsfield generate wait <id>         # rejoin a running job
```

## Soul-ID (Personalized Generation)

Train a face reference for consistent character generation:

```bash
higgsfield soul-id train --name "..." --image <upload_id>...
higgsfield soul-id list
higgsfield soul-id status <soul_id>
```

Use with: `higgsfield generate create text2image_soul_v2 --prompt "..." --soul-id <id> --wait`

## Account & Credits

```bash
higgsfield account status    # plan + credits
higgsfield account balance   # credit balance
```

## Error Handling

1. **`Session expired`** — Run `higgsfield auth login`.
2. **`Missing required params: prompt`** — Provide a prompt.
3. **`Invalid values: aspect_ratio=...`** — Check allowed values via `higgsfield model get <model_id>`.
4. **`failed` job status** — Retry with adjusted prompt. Credits refunded.
5. **`nsfw` status** — Content moderation. Revise prompt. Credits refunded.

## What This Skill Does NOT Cover

- Creative direction or prompt writing for specific campaigns (see consuming skills).
- Video editing, timeline assembly, or post-production.
- Billing, pricing, or plan selection — check the dashboard.
- Models beyond Higgsfield.
