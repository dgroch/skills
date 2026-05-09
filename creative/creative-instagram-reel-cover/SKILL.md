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

- Light, bright, editorial, botanical, romantic, and premium — not warm/red.
- Premium florist meets fashion/editorial magazine.
- Elegant but approachable: polished, organic, heartfelt, modern, and a little vintage.
- Balance soft natural photography with clean graphic discipline.
- Final cover should feel grid-ready, not like an arbitrary video screenshot.

### Colour and finish

- Core palette: white, cream, soft grey, pale stone, charcoal used sparingly.
- Botanical palette: fresh eucalyptus, sage, olive, muted leaf green.
- Floral accents: blush, dusty pink, soft cream, coral used lightly; burgundy/muted red only if present in the source, never amplified.
- Overall grade should be airy, clean, light, and bright. Avoid warm/red casts, heavy beige filters, cold blue casts, neon, crunchy HDR, or unrealistic saturation.

### Composition

- Final output is **4:5 vertical**, usually `1080x1350`.
- Prefer generous negative space and clean edges.
- Prefer complete bouquets/florals, elegant hands, refined styling, and emotional human moments.
- Avoid floor/cabinet clutter, awkward crop cutoffs, motion blur, text overlays, stickers, progress bars, and Reels UI artefacts.
- Preserve the real bouquet/product; enhancement should improve the image, not redesign the arrangement.

## Fig & Bloom Photography Edit Style

Use this as the reusable editor preamble for feed covers:

> Editorial lifestyle photography with a soft documentary edge. Natural light, neutral-to-earthy palette, considered negative space, premium and lived-in rather than commercial/glossy. Warm off-white, bone, soft greige, charcoal, deep ink-navy neutrals; sage/eucalyptus grey-green, terracotta, dusty rose, blush, and muted burgundy botanical accents. Saturation pulled back ~15–20%, medium-low contrast, lifted near-blacks, soft highlight roll-off, subtle matte grain, minimal sharpening. Whites are warm-leaning but clean; avoid clinical blue-white, yellow/beige casts, HDR, hard strobes, orange-teal grading, oversaturated greens, heavy vignettes, glossy retouching, plastic skin, and true-black shadows.


## Required Tools

The bundled script expects:

- `uvx` so it can run `yt-dlp` without a permanent install.
- `ffmpeg` and `ffprobe`.
- `GEMINI_API_KEY` / `GOOGLE_API_KEY` for direct Google Gemini API access to Nano Banana Pro. Nano Banana Pro enhancement is **enabled by default**. Do not use OpenRouter unless explicitly requested with `--ai-backend openrouter`.

Optional:

- `REEL_COVER_IMAGE_MODEL`, default `google/gemini-3-pro-image-preview` (Nano Banana Pro).
- `REEL_COVER_AI_BACKEND`, default `gemini-api` for direct Google access. Other values: `nanobanana-pro` alias for direct Google, `openrouter` only when explicitly requested, `openai-api`, `external`, `none`.
- `REEL_COVER_AI_EDIT_CMD` for a custom image-to-image finishing/upscale command when using `--ai-backend external`.
- `REEL_COVER_CROP_MODE`, default `none`. Use `auto` only when you intentionally want deterministic pre-crop candidates.
- `REEL_COVER_NUM_OPTIONS`, default `3`, because taste is subjective and a small batch gives the user alternatives.
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

### 4. Optional crop candidate selection

Pre-crop is **not mandatory**. Default production mode is `REEL_COVER_CROP_MODE=none`: extract the selected full frame and let the image model compose the 4:5 cover. This avoids locking the output into a deterministic crop before the taste/aesthetic pass.

Use `--crop-mode auto` only when explicit pre-crop alternates are useful. For a 9:16 Reel source (`1080x1920`), candidate crops include:

```text
100% width: crop=1080:1350:x:y
92% width:  crop=994:1242:x:y, then upscale to 1080x1350
84% width:  crop=907:1134:x:y, then upscale to 1080x1350
76% width:  crop=821:1026:x:y, then upscale to 1080x1350
```

Keep crop contact sheets for auditability. Do not treat the highest deterministic crop score as taste; it is only a candidate-ordering aid.

### 5. Base input preparation

The script prepares either:

- a full selected frame (`--crop-mode none`, default), or
- one or more crop-candidate inputs (`--crop-mode auto`).

For batch mode, generate `--num-options` final covers. Default is `3`.

Guidelines:

- Lift exposure/clean whites first; keep the image light and bright.
- Preserve realistic flowers without pushing reds/warmth; whites should stay clean, not yellow or beige.
- Improve clarity/sharpness without crunchy halos.
- Preserve the actual arrangement/product.

### 6. Default Nano Banana Pro enhancement + 3-option batch

AI image enhancement is the default because it is how the final image is made consistent with the Fig & Bloom social-feed rubric. The default finisher is **Nano Banana Pro** (`google/gemini-3-pro-image-preview`) via direct Google Gemini API, not GPT Image 2 and not OpenRouter. Generate **3 final options by default** so one can land; if none land, the user can request another batch. The 3 options should come from **three unique source shots** by default, not three generations from the same frame.

Default backend/model:

```bash
REEL_COVER_AI_BACKEND=gemini-api
REEL_COVER_IMAGE_MODEL=google/gemini-3-pro-image-preview
REEL_COVER_CROP_MODE=none
REEL_COVER_NUM_OPTIONS=3
```

The built-in edit prompt is conservative:

```text
Enhance this Instagram Reel still into a premium Fig & Bloom feed cover.
Editorial lifestyle photography with a soft documentary edge: natural light, neutral-to-earthy palette, considered negative space, premium and lived-in rather than commercial/glossy. Use warm off-white/bone/soft greige neutrals with botanical sage/eucalyptus grey-green, dusty rose/blush, muted burgundy, terracotta, charcoal, and deep ink-navy accents. Pull saturation back ~15–20%; use medium-low contrast, lifted near-black shadows, soft highlight roll-off, subtle matte grain, and no clarity boost. Whites should be warm-leaning but clean, not clinical blue-white, yellow, beige-heavy, red, or blown. Preserve real bouquet/product geometry, skin, composition, and tactile texture. Strict source fidelity: the cover must look like a refined frame from the supplied video, not a newly staged florist image. Preserve exact visible bouquet/wrap/person/hand/card/vase/background geometry and camera perspective. If absent in the input frame, do not add it: no new vase, card, pedestal, plinth, table, wall texture, flowers, stems, hands, props, text, logos, or layout. Remove captions, stickers, UI, and text overlays where safe. Avoid HDR, hard strobes, orange-teal grading, oversaturated greens, heavy vignette, glossy retouching, plastic skin, true-black shadows, text/logos, new flowers, or corporate stock-photo polish. Output must remain a 4:5 vertical cover.
```

Nano Banana Pro may return a different 4:5-ish size, so the script always normalizes each final option back to exact `1080x1350`.

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

1. **Letting deterministic metrics be taste.** Do not. Use deterministic scoring only to remove unusable frames/crops or order candidates; taste should come from visual review/model critique/user batches.
2. **Returning three near-duplicates.** Do not. A batch should cover three distinct source shots/moments: e.g. human/lifestyle, bouquet close-up, gifting/product story.
3. **Skipping Nano Banana Pro enhancement.** The default output should be AI-enhanced against the social-feed rubric unless debugging or explicitly disabled.
4. **Making crop mandatory.** Do not force a deterministic pre-crop. Default to full-frame AI composition and generate crop candidates only as optional alternates.
5. **Over-editing flowers.** Vibrancy is good; neon petals and changed bouquet ingredients are not.
6. **Treating Instagram as reliably scrapable.** Public downloads may work today and fail tomorrow. Keep the downloader replaceable.
7. **Letting Nano Banana hallucinate a staged florist scene.** Reject outputs that introduce new vases, cards, pedestals, tables, wall textures, flowers, hands, or arrangements. The final must read as a real source frame, just refined.
8. **Leaving Reels UI/text overlays in the processed cover.** Remove captions, stickers, subtitles, progress bars, and UI where safe; otherwise reject that frame.
9. **Calling a failed frame-processing run successful.** Verify the final file exists and is exact `1080x1350` before returning it.
10. **Ignoring rights/access.** Only download content the user is allowed to use.

## Verification Checklist

- [ ] Reel downloaded or user provided an accessible video file.
- [ ] Labelled contact sheet generated for auditability.
- [ ] Frame selected with `ffmpeg_heuristic_no_gemini` metrics.
- [ ] 4:5 crop candidates generated and scored without Gemini.
- [ ] GPT Image enhancement ran by default, or `--no-ai-enhance` was intentionally used for debugging.
- [ ] Final cover exists and is exact `1080x1350` or another explicitly requested 4:5 size.
- [ ] Final cover has no obvious text overlays, motion blur, awkward crop, or over-processed colours.
- [ ] Report JSON saved with URL, selected frame, crop, enhancement method, and output paths.
