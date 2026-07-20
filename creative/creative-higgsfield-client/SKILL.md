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
2. **Set HOME for auth:** The CLI looks for credentials in `$HOME/.config/higgsfield/credentials.json`. On this system, credentials live at `/opt/data/home/.config/higgsfield/credentials.json`, so you MUST prefix all commands with `HOME=/opt/data/home`:
   ```bash
   HOME=/opt/data/home higgsfield account status
   ```
3. Run `HOME=/opt/data/home higgsfield account status`. If it fails with `Session expired` / `Not authenticated`, follow the **Device Auth Flow** below — do NOT just ask the user to run it themselves; the agent can drive the flow end-to-end.

Skip both checks if `HOME=/opt/data/home higgsfield account status` prints account info.

**Account:** admin@figandbloom.com.au — creator plan, ~4,600+ credits (as of May 2026).

## Image Generation

```bash
HOME=/opt/data/home higgsfield generate create <model_id> --prompt "..." [--image <path-or-id>] [--aspect_ratio 16:9] [--quality ...] --wait
```

`--wait` blocks until the job completes and prints the result URL. Use `--wait-timeout 20m` for longer jobs.

**Params are model-specific** — not all image models accept `--resolution`. `soul_cinematic`, for example, does NOT accept `--resolution` (its native output is already ~2K). Check accepted params with `higgsfield model get <model_id> --json` before passing optional flags.

### Key image models

| Model ID | Best for |
|----------|----------|
| `soul_cinematic` | Editorial/cinematic stills, photorealistic storyboards |
| `gpt_image_2` | Graphic design, UI, banners, typography, end cards |
| `nano_banana_2` | Top quality 4K, text/diagrams, character/cartoon |
| `text2image_soul_v2` | Portraits, fashion, UGC, editorial |
| `soul_location` | Locations, environments, no-people scenes |
| `seedream_v4_5` | Vector illustrations, face edit + scene swap |
| `marketing_studio_image` | Commercial/product/ads |

### Using reference images

Media flags accept a local file path (auto-uploaded) or a UUID:

```bash
HOME=/opt/data/home higgsfield generate create nano_banana_2 --prompt "..." --image ./ref.png --wait
```

### Soul character + product reference workflow

When generating a person with a trained Soul character who must also carry/show a specific product, do **not** assume one generation can satisfy both identity and product fidelity.

Observed pattern with `text2image_soul_v2`:
- `--soul-id <id>` works for the character identity.
- `--image <product_ref>` is limited to one reference and can cause the model to over-focus on the product, sometimes returning a product-only/studio bouquet image instead of the requested person/location scene.

Preferred sequence for branded character/product ads:
1. Generate the character/location keyframe first with `text2image_soul_v2 --soul-id <id>` and no product image, writing the product composition in the prompt.
2. Visually check that the face, pose, and location are present. If the product blocks the face, regenerate with explicit placement instructions (e.g. "bouquet lower/diagonal, face unobscured").
3. Use an image-edit model such as `seedream_v4_5` with two inputs — the generated character keyframe plus the product reference — to correct bouquet/product details and wrapping.
4. Downscale huge edit outputs for review/vision checks before analysis or delivery.

### Batch generation

Not a built-in flag — submit multiple `generate create` calls.

## Video Generation

```bash
HOME=/opt/data/home higgsfield generate create <model_id> --prompt "..." [--start-image <path-or-id>] [--duration 5] --wait
```

### Key video models

| Model ID | Best for |
|----------|----------|
| `seedance_2_0` | Highest visual fidelity, multi-shot, identity preservation |
| `veo3_1` | Google Veo 3.1 full quality |
| `veo3_1_lite` | Google Veo 3.1 Lite — fastest, cheapest, tested: 6s 720p + audio in ~30s |
| `kling3_0` | Multi-shot, audio, motion transfer |
| `marketing_studio_video` | Commercial/product/branded ads with avatars |

### Media flags

| Flag | Purpose |
|------|---------|
| `--image <path-or-id>` | Reference image (style/content reference for image gen) |
| `--start-image <path-or-id>` | First frame (image-to-video) — **use this for i2v, not `--medias`** |
| `--end-image <path-or-id>` | Last frame (transitions) |
| `--video <path-or-id>` | Reference video |
| `--audio <path-or-id>` | Audio for lipsync/soundtrack |

**Critical:** The `--medias` flag exists in model schemas but does NOT accept a bare UUID string or JSON list. For image-to-video, always use `--start-image` instead.

### Image-to-video pattern

Upload the keyframe first, get a UUID, then use `--start-image`:

```bash
UUID=$(HOME=/opt/data/home higgsfield upload create /tmp/keyframe.png 2>&1 | grep -oP '[0-9a-f-]{36}')
HOME=/opt/data/home higgsfield generate create veo3_1_lite \
  --prompt "Subtle cinematic movement..." \
  --start-image "$UUID" \
  --aspect_ratio 9:16 \
  --duration 4 \
  --wait
```

For higher fidelity (slower, ~3-4 min), use `seedance_2_0` with `--resolution 1080p --mode fast --genre drama`.

**Quick single-shot pipeline:** `soul_cinematic` keyframe → upload → `seedance_2_0` i2v → deliver MP4. See `references/quick-keyframe-to-video.md` for the streamlined end-to-end pattern (~2 min total).

### Video model parameters

| Model | Duration | Aspect Ratio | Extras |
|-------|----------|-------------|--------|
| `veo3_1_lite` | 4, 6, 8 | 16:9, 9:16, auto | `generate_audio` (bool) |
| `veo3_1` | 4, 6, 8 | 16:9, 9:16, auto | `generate_audio` (bool) |
| `seedance_2_0` | integer (default 5) | auto, 16:9, 9:16, 4:3, 3:4, 1:1, 21:9 | `resolution` (480p/720p/1080p), `mode` (std/fast), `genre` (auto/action/horror/comedy/noir/drama/epic) |
| `kling3_0` | varies | varies | — |

### `flux_kontext` — Identity-preserving image edits

Best model for maintaining character identity while changing lighting, mood, or environment. Upload a reference face/scene, generate a new image with the same person in different conditions.

```bash
HOME=/opt/data/home higgsfield generate create flux_kontext \
  --prompt "Same woman from reference, now in warm amber light..." \
  --image <uploaded_uuid> \
  --aspect_ratio 9:16 \
  --wait
```

Use for: storyboard continuity (same actor across slates), palette shifts (cool → warm), wardrobe/background swaps while keeping identity.

## Marketing Studio

Branded image/video generation with avatars + products.

### Quick ad video workflow

1. **Fetch product:** `HOME=/opt/data/home higgsfield marketing-studio products fetch --url <url> --wait`
2. **Pick avatar:** `HOME=/opt/data/home higgsfield marketing-studio avatars list`
3. **Generate:**
   ```bash
   HOME=/opt/data/home higgsfield generate create marketing_studio_video \
     --prompt "..." \
     --avatars '[{"id":"<avatar_id>","type":"preset"}]' \
     --product_ids '[<product_id>]' \
     --mode ugc \
     --duration 15 \
     --aspect_ratio 9:16 \
     --wait
   ```

Modes: `ugc`, `tutorial`, `ugc_unboxing`, `hyper_motion`, `product_review`, `tv_spot`, `wild_card`, `ugc_virtual_try_on`, `virtual_try_on`.

## Video Analysis (Higgsfield MCP)

Higgsfield MCP now supports **video analysis** — upload a reference video and get a structured breakdown of shots, camera work, and creative elements. This is the foundation for the parametric beat sheet workflow.

### Workflow

1. **Upload reference video** via Higgsfield MCP connector (Claude Desktop or Paperclip)
2. **Claude analyzes** the video frame-by-frame using Gemini vision
3. **Output:** Structured beat sheet with:
   - Per-shot breakdowns (camera angle, shot type, composition, lighting, mood)
   - Template variables (`{COLORGRADE}`, `{BRANDED_OBJECTS}`, `{SIGNATURE_ACTION}`, etc.)
   - Compact beat sheet summary for quick reference

### Use cases

- Reverse-engineer competitor ads to understand their structure
- Extract reusable templates from successful campaigns
- Build a library of proven video formats (UGC, product reveal, lifestyle)
- Parametrize creative elements for rapid reskinning across products/campaigns

### Integration with creative-video-transformation

The video analysis output feeds directly into the **Step 2b: Parametric Beat Sheet** workflow in `creative-video-transformation`. Use analysis to extract the template, then use the transformation pipeline to generate new variations.

See `creative-video-transformation` skill for the full beat sheet variable taxonomy and output format.

## File Uploads

```bash
higgsfield upload create <file_path>
```

Returns an upload UUID. Use the UUID in media flags for subsequent generations.

## Model Discovery

```bash
HOME=/opt/data/home higgsfield model list          # all models (table format)
HOME=/opt/data/home higgsfield model list --json   # JSON format
HOME=/opt/data/home higgsfield model get <model_id> --json  # model params/schema
```

### Available Models (as of May 2026)

**Image generation:**
- `soul_cinematic` — Editorial/cinematic stills, photorealistic (best for storyboards)
- `text2image_soul_v2` — Portraits, fashion, UGC, editorial
- `gpt_image_2` — Graphic design, UI, banners, typography (good for end cards)
- `nano_banana_2` — Top quality 4K, text/diagrams, character/cartoon
- `seedream_v4_5` — Vector illustrations, face edit + scene swap
- `marketing_studio_image` — Commercial/product/ads
- `soul_location` — Locations, environments, no-people scenes
- Plus: `flux_2`, `flux_kontext`, `grok_image`, `image_auto`, `kling_omni_image`, `ms_image`, `nano_banana`, `nano_banana_flash`, `openai_hazel`, `seedream_v5_lite`, `z_image`, `cinematic_studio_2_5`

**Video generation:**
- `seedance_2_0` — Highest visual fidelity, multi-shot, identity preservation
- `veo3_1` — Google Veo 3.1 (full quality)
## File Uploads

```bash
HOME=/opt/data/home higgsfield upload create <file_path>
```

Returns an upload UUID. Use the UUID in media flags for subsequent generations.

## Job Management

```bash
HOME=/opt/data/home higgsfield generate list --json       # past jobs
HOME=/opt/data/home higgsfield generate get <id> --json   # specific job details
HOME=/opt/data/home higgsfield generate wait <id>         # rejoin a running job
```

## Soul-ID (Personalized Generation)

Train a face reference for consistent character generation:

```bash
HOME=/opt/data/home higgsfield soul-id train --name "..." --image <upload_id>...
HOME=/opt/data/home higgsfield soul-id list
HOME=/opt/data/home higgsfield soul-id status <soul_id>
```

Use with: `HOME=/opt/data/home higgsfield generate create text2image_soul_v2 --prompt "..." --soul-id <id> --wait`

## Account & Credits

```bash
HOME=/opt/data/home higgsfield account status    # plan + credits
HOME=/opt/data/home higgsfield account balance   # credit balance
```

## Error Handling

1. **`Session expired`** — Run `higgsfield auth login`.
2. **`Missing required params: prompt`** — Provide a prompt.
3. **`Invalid values: aspect_ratio=...`** — Check allowed values via `higgsfield model get <model_id>`.
4. **`failed` job status** — Retry with adjusted prompt. Credits refunded.
5. **`nsfw` status** — Content moderation. Revise prompt. Credits refunded.

## Authentication

Higgsfield stores credentials in `$HOME/.config/higgsfield/credentials.json`. In Hermes environments, the active HOME may differ from where credentials are stored. If `higgsfield account status` fails with "Not authenticated" despite credentials existing, prefix commands with the correct HOME:

```bash
HOME=/opt/data/home higgsfield account status
HOME=/opt/data/home higgsfield generate create <model> ...
```

Verify auth with: `HOME=/opt/data/home higgsfield account status`

### Device Auth Flow (when credentials are missing or expired)

`higgsfield auth login` uses an **interactive device code flow**: it prints a URL like `https://higgsfield.ai/device?code=XXXX`, opens a browser, and waits for the user to sign in and approve. The CLI has a **60-second default timeout** — not enough time for the user to click the link, sign in, and approve.

**Agent-driven auth pattern (proven):**

1. Write a wrapper script that redirects output to a file:
   ```bash
   echo '#!/bin/bash
   export HOME=/opt/data/home
   /opt/data/bin/higgsfield auth login > /tmp/higgs_auth_output.txt 2>&1
   echo "EXIT_CODE=$?" >> /tmp/higgs_auth_output.txt' > /tmp/higgs_auth.sh
   chmod +x /tmp/higgs_auth.sh
   ```
2. Start it in the background via `terminal(background=true)` with `notify_on_complete=true`.
3. After 3 seconds, read `/tmp/higgs_auth_output.txt` to extract the device URL.
4. **Present the URL as a clickable link** in the Telegram message — not plain text. The user needs to click it, sign in with `admin@figandbloom.com.au`, and approve the device auth.
5. Once the user confirms "done", verify with `HOME=/opt/data/home higgsfield account status`.

**Key points:**
- The background process stays alive indefinitely (no 60s timeout when run via background), giving the user time to approve.
- **Always present auth URLs as clickable markdown links** (`[https://...](https://...)`) — the user explicitly prefers clickable links over copy-paste URLs.
- The CLI binary may not be on `$PATH`; use the full path `/opt/data/bin/higgsfield` if needed.

## Pitfalls

- **`higgsfield auth login` has a 60-second timeout** — insufficient for interactive device auth when the user must click a link and sign in. Run it in the background (output redirected to a file) so it stays alive while the user approves. See **Device Auth Flow** in the Authentication section above.
- **NSFW/moderation can be triggered by attached reference media, not just prompt text** — If an otherwise-safe image-to-video prompt is rejected only when `--video <reference.mp4>` is attached, retry without the video media and translate the motion into explicit prompt language (e.g. "takes several steps across frame, then makes one graceful turning step"). Keep the start image and simplify sensitive wording. Do not conclude the concept is unsafe until you have tested the no-reference-media prompt.
- **NSFW filter on medical/hospital imagery** — Veo 3.1 Lite and Seedance 2.0 both trigger NSFW on prompts containing "hospital", "IV", "hospital gown", "patient in bed", etc. Workaround: rephrase to neutral language ("quiet room with a bed", "woman resting", "medical tape on wrist" → "tape on wrist"). The image itself doesn't trigger — only the prompt text. If NSFW fires, rewrite the prompt removing all medical vocabulary and retry.
- **Soul/image-reference priority trap** — `text2image_soul_v2` accepts at most one image reference. When combining a Soul ID with a product reference, the product reference can dominate and produce a product-only image with no person/scene. Safer pattern: generate the Soul/person/location keyframe first with `--soul-id` and no product image; then run an edit model (e.g. `seedream_v4_5`) with the keyframe plus product reference to correct product/wrapping details.
- **`--medias` flag does not work** — despite appearing in `higgsfield model get` output, the `--medias` parameter rejects both bare UUIDs and JSON lists. For image-to-video, use `--start-image <uuid>` instead.
- **Higgsfield API 502 errors** — transient, usually clears within 30-60 seconds. Add retry logic with 15s backoff in batch pipelines.
- **Output is a CloudFront URL** — successful generations return a direct `https://d8j0ntlcm91z4.cloudfront.net/...` MP4 URL. Download with `curl -sL <url> -o output.mp4`.
- **Veo 3.1 Lite duration is 4, 6, or 8** — not arbitrary. Seedance 2.0 accepts integer durations (default 5).

## Pitfalls

- **HOME must be /opt/data/home** — Credentials are at `/opt/data/home/.config/higgsfield/credentials.json`. Default HOME=/opt/data will fail with "Not authenticated" even though credentials exist. Always prefix: `HOME=/opt/data/home higgsfield ...`
- **`soul_cinematic` is the best model for storyboard keyframes** — produces photorealistic editorial stills at ~2K natively (no `--resolution` flag needed; the param is rejected with "Unknown params: resolution"). Use for film storyboard frames, not `text2image_soul_v2` which is more portrait-focused. Accepted params: `aspect_ratio`, `quality`, `prompt`, `medias`, `custom_reference_id`.
- **`gpt_image_2` for graphic design** — end cards, text-heavy layouts, UI mockups. Better than image models at rendering text.
- **Model list `--json` output may have empty model IDs** — Use plain `higgsfield model list` (table format) for reliable model names, then `model get <id> --json` for schema details.
- **`generate create --json` may return a bare UUID array** — Current async CLI builds can return `["<job-id>"]` rather than an object such as `{"id":"<job-id>"}`. Batch runners must accept all three safe shapes: a bare UUID string, an object with `id`, or a non-empty list whose first item is either shape. Persist the recovered job ID before calling `generate wait` so a restart never resubmits a billed job.
- **`--wait` blocks the shell** — For batch generation of multiple frames, run jobs without `--wait`, collect job IDs, then poll with `higgsfield generate wait <id>` or `higgsfield generate get <id> --json`.
- **"Cloning" means faithful reproduction of a specific real video, not generic on-theme generation** — When the user asks to clone a viral video, they expect: source video download → frame-by-frame deconstruction → keyframe matching the original's exact composition → animation. Skipping the source video and generating from a text prompt produces a generic scene the user will reject. Always start from a real reference video. See `references/viral-video-cloning.md`.

## Viral Video Cloning

When the user asks to "clone a viral video," this means **faithfully reproducing
a specific real video** — its composition, shots, subjects, lighting, mood, and
text overlays. NOT generating a vaguely on-theme scene from a text prompt.

**Full workflow:** source video → yt-dlp download → ffmpeg frame extraction →
vision_analyze shot-by-shot deconstruction → soul_cinematic keyframe matching
the original's composition → Seedance 2.0 i2v animation → deliver side-by-side
with beat sheet comparison.

See `references/viral-video-cloning.md` for the complete end-to-end pipeline
with commands, deconstruction methodology, and proven examples.

## Topaz Image Restoration and Caption Removal

- **Topaz image models require uploaded-media objects, not `--image` or a local string in `--input_image`** — Upload first, then pass `--input_image '{"id":"<upload-uuid>","type":"media_input"}'`. Topaz parameter names retain underscores (`--input_image`, `--output_width`, `--output_height`), not hyphens.
  ```bash
  ID=$(HOME=/opt/data/home higgsfield upload create ./input.jpg)
  HOME=/opt/data/home higgsfield generate create topaz_image_generative \
    --input_image "{\"id\":\"$ID\",\"type\":\"media_input\"}" \
    --output_width 1536 --output_height 2048 --model "Recovery V2" \
    --creativity 1 --texture 1 --prompt "Faithfully restore..." --wait
  ```
- **Topaz generative upscale does not reliably remove burned-in captions even when prompted** — Use Topaz first for restoration, then a precise `gpt_image_2` edit (`--image <topaz-output> --resolution 2k --quality high`) telling it to remove only the overlay and reconstruct the obscured area. Visually verify both overlay removal and preservation of authentic photographed logos.

## What This Skill Does NOT Cover

- Creative direction or prompt writing for specific campaigns (see consuming skills).
- Video editing, timeline assembly, or post-production.
- Billing, pricing, or plan selection — check the dashboard.
- Models beyond Higgsfield.
