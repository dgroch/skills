---
name: creative-instagram-reel-cover
description: Use when turning an Instagram Reel URL into an aesthetic 4:5 feed cover by downloading the reel, extracting still frames with ffmpeg, selecting the best still/crop with deterministic frame scoring, and using GPT Image enhancement by default to produce a polished brand-consistent cover.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  tags: [Creative, Instagram, Reels, Covers, GPT-Image, Video, Florist, Social]
  related_skills: [creative-brand-photographer, creative-video-transformation, creative-higgsfield-client, creative-asset-adapter]
---

# Instagram Reel Cover Builder

## Overview

This skill converts an Instagram Reel URL into a polished **4:5 Instagram feed cover**. It is designed for brands where the grid has to feel deliberate, premium, and visually cohesive — especially Fig & Bloom's romantic fashion-editorial florist direction.

The workflow is:

1. Download the Reel video.
2. Extract still frames/contact sheets with `ffmpeg`.
3. Select the best still frame using deterministic ffmpeg/Python image metrics — **no Gemini or multimodal frame critic**.
4. Generate 4:5 crop candidates and select the strongest crop using the same deterministic scoring.
5. Apply a default AI enhancement/edit pass with **GPT Image** to enforce feed consistency against the social-feed rubric.
6. Normalize the final deliverable back to exact `1080x1350` 4:5 JPEG and return a report.

This is a **cover-selection and finishing** workflow, not a full video editing workflow.

## When to Use

Use this skill when the user asks to:

- make an Instagram Reel cover from a URL;
- choose the best still frame from a Reel or short video;
- make the Instagram grid look more aesthetic/cohesive;
- produce a 4:5 feed image from video footage;
- clean up a Reel cover with colour, white balance, vibrancy, crop, upscale, or AI enhancement.

Do not use this when:

- the user wants to generate a Reel/video from scratch — use `creative-higgsfield-client` or `creative-video-transformation`;
- the user wants static brand photography generation from prompts/seeds — use `creative-brand-photographer`;
- the user wants quote/review/graphic tiles — use the creative builder/graphic skills.

## Artistic Direction: Fig & Bloom Social Feed Default

The default post-edit direction comes from the Fig & Bloom social feed guidelines moodboard.

### Look / feel

- Romantic, intimate, editorial, botanical, warm, and slightly luxe.
- Premium florist meets fashion/editorial magazine.
- Elegant but approachable: polished, organic, heartfelt, modern, and a little vintage.
- Balance soft natural photography with clean graphic discipline.
- Final cover should feel grid-ready, not like an arbitrary video screenshot.

### Colour and finish

- Core palette: black, white, cream, soft grey, charcoal.
- Botanical palette: eucalyptus, sage, olive, muted leaf green.
- Floral accents: blush, dusty pink, burgundy, coral, soft cream, muted red.
- Warm neutrals: tan, beige, wood tones; avoid cold blue casts.
- Keep tones premium and photographic. Avoid neon, crunchy HDR, or unrealistic saturation.

### Composition

- Final output is **4:5 vertical**, usually `1080x1350`.
- Prefer generous negative space and clean edges.
- Prefer complete bouquets/florals, elegant hands, refined styling, and emotional human moments.
- Avoid floor/cabinet clutter, awkward crop cutoffs, motion blur, text overlays, stickers, progress bars, and Reels UI artefacts.
- Preserve the real bouquet/product; enhancement should improve the image, not redesign the arrangement.

## Required Tools

The bundled script expects:

- `uvx` so it can run `yt-dlp` without a permanent install.
- `ffmpeg` and `ffprobe`.
- `OPENAI_API_KEY` because GPT Image enhancement is **enabled by default**.

Optional:

- `REEL_COVER_IMAGE_MODEL`, default `gpt-image-2`.
- `REEL_COVER_IMAGE_QUALITY`, default `high`.
- `REEL_COVER_AI_EDIT_CMD` for a custom image-to-image finishing/upscale command. If set, it overrides the built-in OpenAI Images edit call.
- `--no-ai-enhance` for debugging only; production/default usage should keep AI enhancement on.

Instagram access notes:

- Public Reel URLs often download via `yt-dlp` unauthenticated.
- Private, age-gated, region-gated, or rate-limited Reels may require cookies. Use `--cookies-from-browser` or an exported cookies file only when the user owns/has legitimate access.
- Do not bypass access controls.

## One-Shot Command

From this skill directory:

```bash
set -a; [ -f /opt/data/.env ] && . /opt/data/.env; set +a
python3 scripts/reel_cover_from_instagram.py \
  'https://www.instagram.com/reel/SHORTCODE/' \
  --brand fig-and-bloom \
  --outdir /opt/data/tmp/reel-cover-run
```

Expected output:

```text
FINAL_COVER=/.../instagram_reel_cover_4x5.jpg
REPORT=/.../report.json
```

Return the image to the user with:

```text
MEDIA:/.../instagram_reel_cover_4x5.jpg
```

## Pipeline Details

### 1. Download

Use `uvx yt-dlp`:

```bash
uvx yt-dlp --no-playlist --restrict-filenames -o 'source.%(ext)s' '<instagram-reel-url>'
```

If this fails because of auth/rate limits, stop and ask for an authenticated export/cookies approach. Do not keep hammering Instagram.

### 2. Extract contact-sheet frames

Default frame sampling is **1 FPS**. Use a higher FPS for very short or fast-cut videos.

```bash
ffmpeg -y -i source.mp4 -vf 'fps=1,scale=540:-1' frames/frame_%03d.jpg
```

Create a labelled contact sheet for human audit/debugging:

```bash
ffmpeg -y -i frame.jpg -vf "drawbox=...,drawtext=text='001':..." labelled/frame_001.jpg
ffmpeg -y -f concat -safe 0 -i inputs.txt \
  -vf 'scale=240:-1,tile=5xN:padding=4:margin=4:color=white' contact_sheet_labeled.jpg
```

### 3. Deterministic frame selection — no Gemini

Because the Reel is already decomposed into frames, do **not** call Gemini or another multimodal critic just to choose a frame. The script scores each extracted still using dependency-free metrics derived from `ffmpeg` raw RGB output:

- focus/detail proxy from neighbour luminance gradients;
- contrast;
- saturation;
- floral/botanical colour signal;
- balanced exposure;
- low black/white clipping;
- transition-edge penalty for the first/last moments.

The report records:

```json
{
  "selection_mode": "ffmpeg_heuristic_no_gemini",
  "frame_choice": {
    "best_label": "019",
    "timestamp_seconds": 18.0,
    "metrics": { "score": 42.3 }
  }
}
```

### 4. Crop candidate selection

For a 9:16 Reel source (`1080x1920`), a safe full-width 4:5 cover is usually:

```text
crop_width = source_width
crop_height = source_width * 5 / 4
```

For 1080-wide video, this gives `1080x1350`. But full-width crops can leave too much wall/floor or include distracting side props. Generate safe and tighter editorial crops:

```text
100% width: crop=1080:1350:x:y
92% width:  crop=994:1242:x:y, then upscale to 1080x1350
84% width:  crop=907:1134:x:y, then upscale to 1080x1350
76% width:  crop=821:1026:x:y, then upscale to 1080x1350
```

Score crop candidates with the same metrics and a small over-zoom penalty. Keep a crop contact sheet for auditability, but do not ask Gemini to choose.

### 5. Deterministic base enhancement

The script first creates a conservative deterministic base cover with `ffmpeg`:

```bash
ffmpeg -y -ss <timestamp> -i source.mp4 -frames:v 1 \
  -vf "crop=<w>:<h>:<x>:<y>,scale=1080:1350:flags=lanczos,eq=brightness=0.015:contrast=1.07:saturation=1.10:gamma=1.015,unsharp=5:5:0.55:3:3:0.2" \
  -q:v 2 instagram_reel_cover_4x5_deterministic.jpg
```

Guidelines:

- Lift vibrancy, but preserve realistic flowers.
- Warm the image subtly; do not make whites yellow.
- Improve clarity/sharpness without crunchy halos.
- Preserve the actual arrangement/product.

### 6. Default GPT Image enhancement

AI image enhancement is the default because it is how the final image is made consistent with the Fig & Bloom social-feed rubric.

Default model:

```bash
REEL_COVER_IMAGE_MODEL=gpt-image-2
```

The built-in edit prompt is conservative:

```text
Enhance this Instagram Reel still into a premium Fig & Bloom feed cover.
Romantic, intimate, editorial, botanical, warm, slightly luxe. Premium fashion-florist feel with realistic flowers, warm clean whites, cream/charcoal/sage/blush/burgundy tones, subtle contrast, and elegant negative space. Preserve the real bouquet/product and composition. Remove only video compression, minor noise, distracting floor/cabinet clutter, and small artefacts where safe. Do not add text, logos, new flowers, neon colour, cartoon styling, or corporate stock-photo polish. Output must remain a 4:5 vertical cover.
```

The image editor may return a different vertical size, so the script always normalizes the final deliverable back to exact `1080x1350`.

Only use `--no-ai-enhance` when debugging the frame/crop algorithm or when the user explicitly asks for deterministic-only output.

## Output Contract

Return:

- final image path;
- source Reel URL;
- selected frame label and timestamp;
- crop offset/box;
- enhancement method;
- report JSON path;
- any caveats, especially Instagram auth/download limitations.

## Common Pitfalls

1. **Reintroducing Gemini for frame choice.** Do not. Frame extraction makes deterministic scoring enough for selection; save AI for the final image-edit consistency pass.
2. **Skipping GPT Image enhancement.** The default output should be AI-enhanced against the social-feed rubric unless debugging or explicitly disabled.
3. **Blind centre crop cuts off the subject.** Generate crop candidates and score them.
4. **Over-editing flowers.** Vibrancy is good; neon petals and changed bouquet ingredients are not.
5. **Treating Instagram as reliably scrapable.** Public downloads may work today and fail tomorrow. Keep the downloader replaceable.
6. **Using Reels UI/text overlays as a cover.** Avoid captions, stickers, progress bars, or awkward mid-transition frames.
7. **Calling a failed frame-processing run successful.** Verify the final file exists and is exact `1080x1350` before returning it.
8. **Ignoring rights/access.** Only download content the user is allowed to use.

## Verification Checklist

- [ ] Reel downloaded or user provided an accessible video file.
- [ ] Labelled contact sheet generated for auditability.
- [ ] Frame selected with `ffmpeg_heuristic_no_gemini` metrics.
- [ ] 4:5 crop candidates generated and scored without Gemini.
- [ ] GPT Image enhancement ran by default, or `--no-ai-enhance` was intentionally used for debugging.
- [ ] Final cover exists and is exact `1080x1350` or another explicitly requested 4:5 size.
- [ ] Final cover has no obvious text overlays, motion blur, awkward crop, or over-processed colours.
- [ ] Report JSON saved with URL, selected frame, crop, enhancement method, and output paths.
