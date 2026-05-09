---
name: creative-instagram-reel-cover
description: Use when turning an Instagram Reel URL into an aesthetic 4:5 feed cover by downloading the reel, extracting still frames, using Gemini/vision critique to choose the best shot, refining crop/colour/sharpness, and returning a polished cover image for a curated grid.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  tags: [Creative, Instagram, Reels, Covers, Gemini, Video, Florist, Social]
  related_skills: [creative-brand-photographer, creative-video-transformation, creative-higgsfield-client, creative-asset-adapter]
---

# Instagram Reel Cover Builder

## Overview

This skill converts an Instagram Reel URL into a polished **4:5 Instagram feed cover**. It is designed for brands where the grid has to feel deliberate, premium, and visually cohesive — especially Fig & Bloom's fashion-editorial florist direction.

The workflow is:

1. Download the Reel video.
2. Extract still frames/contact sheets.
3. Use Gemini or another multimodal critic to choose the most aesthetic frame.
4. Generate 4:5 crop candidates and select the strongest crop.
5. Apply a tasteful enhancement pass: crop, upscale/resize, white balance/colour lift, vibrancy, contrast, and sharpening.
6. Return the final cover image and a small audit trail.

This is a **cover-selection and finishing** workflow, not a full video editing workflow.

## When to Use

Use this skill when the user asks to:

- make an Instagram Reel cover from a URL;
- choose the best still frame from a Reel or short video;
- make the Instagram grid look more aesthetic/cohesive;
- produce a 4:5 feed image from video footage;
- use Gemini/video understanding to pick a hero shot;
- clean up a Reel cover with colour, white balance, vibrancy, crop, or upscale.

Do not use this when:

- the user wants to generate a Reel/video from scratch — use `creative-higgsfield-client` or `creative-video-transformation`;
- the user wants static brand photography generation from prompts/seeds — use `creative-brand-photographer`;
- the user wants quote/review/graphic tiles — use the creative builder/graphic skills.

## Artistic Direction: Fig & Bloom Default

When the brand is Fig & Bloom, use the brand-photographer art direction as the judging rubric:

- The image should feel like **fashion magazine meets premium florist**.
- Flowers must be vivid and true-to-life; avoid muted/desaturated grades.
- Lighting should be warm, clean, and premium — not cold/blue, harsh, or flat.
- Prefer editorial negative space and calm composition over busy snapshots.
- Bouquet/florals should be the hero, ideally with refined styling or elegant hands.
- Avoid awkward motion, blurred hands, cropped-off florals, text overlays, messy backgrounds, or strong Reels UI artifacts.
- Final feed cover should be **4:5 vertical**; for Instagram this is usually `1080x1350`.

If a configured brand exists, read its equivalent `art-direction.md`, `colour-system.md`, and `grid-spec.md` before scoring frames.

## Required Tools

The bundled script expects:

- `uvx` so it can run `yt-dlp` without a permanent install.
- `ffmpeg` and `ffprobe`.
- `OPENROUTER_API_KEY` for Gemini multimodal frame/crop selection.

Optional:

- `REEL_COVER_MODEL`, default `google/gemini-2.5-flash`.
- `REEL_COVER_AI_EDIT_CMD` for an external image-to-image finishing/upscale command if available.

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
ffmpeg -y -i source.mp4 -vf 'fps=1,scale=360:-1' frames/frame_%03d.jpg
```

Create a labelled contact sheet so the vision model cannot miscount frames:

```bash
ffmpeg -y -i frame.jpg -vf "drawbox=...,drawtext=text='001':..." labelled/frame_001.jpg
ffmpeg -y -pattern_type glob -i 'labelled/*.jpg' \
  -vf 'scale=240:-1,tile=5x5:padding=4:margin=4:color=white' contact_sheet_labeled.jpg
```

### 3. Frame selection prompt

Use Gemini/multimodal vision on the labelled contact sheet. Ask for strict JSON:

```text
This contact sheet has visible numeric labels on each frame. Pick the single best numbered frame for a 4:5 Instagram feed cover for a premium florist/fashion editorial grid. Prefer clean completed floral arrangement, sharpness, elegant hands/styling, warm attractive colour, no awkward motion, no blur, no text overlays. Return strict JSON: best_label, timestamp_seconds, why, crop_notes, runners_up.
```

For Fig & Bloom, add:

```text
Apply Fig & Bloom direction: premium florist/fashion editorial, vivid true-to-life florals, warm clean light, calm negative space, no generic stock-photo energy.
```

### 4. Crop candidate selection

For a 9:16 Reel source (`1080x1920`), a safe full-width 4:5 cover is usually:

```text
crop_width = source_width
crop_height = source_width * 5 / 4
```

For 1080-wide video, this gives `1080x1350`. But full-width crops can leave too much wall/floor or include distracting side props. Generate both safe and tighter editorial crop candidates:

```text
full-width:  crop=1080:1350:x:y
90% width:   crop=972:1215:x:y, then upscale to 1080x1350
80% width:   crop=864:1080:x:y, then upscale to 1080x1350
```

Vary `x` and `y` enough to test centred and subject-focused crops, then make a crop contact sheet and ask Gemini which position is strongest for the brand. This is usually better than a blind centre crop.

### 5. Enhancement Pass

Default non-generative enhancement uses `ffmpeg`:

```bash
ffmpeg -y -ss <timestamp> -i source.mp4 -frames:v 1 \
  -vf "crop=<w>:<h>:<x>:<y>,scale=1080:1350:flags=lanczos,eq=brightness=0.015:contrast=1.08:saturation=1.16:gamma=1.02,unsharp=5:5:0.7:3:3:0.3" \
  -q:v 2 instagram_reel_cover_4x5.jpg
```

Guidelines:

- Lift vibrancy, but preserve realistic flowers.
- Warm the image subtly; do not make whites yellow.
- Improve clarity/sharpness without crunchy halos.
- Preserve the actual arrangement/product. Do not hallucinate new flowers unless the user explicitly asks for generative editing.

### Optional AI finishing command

If an external image-to-image editor/upscaler is available, expose it as:

```bash
REEL_COVER_AI_EDIT_CMD='your-command --input {input} --output {output} --prompt {prompt}'
```

The prompt should be conservative:

```text
Polish this Instagram Reel still as a premium florist feed cover. Preserve the exact bouquet, vase, room, and composition. Improve white balance, natural warmth, flower vibrancy, local contrast, fine detail, and subtle upscale. Remove video compression artifacts only. Do not add objects, text, logos, new flowers, or change the arrangement.
```

Always compare the AI-finished image against the source crop. If it changes the bouquet/product materially, reject it and use the deterministic ffmpeg enhancement.

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

1. **Unlabelled contact sheets cause frame-number hallucination.** Always draw visible labels before asking Gemini to choose.
2. **Blind centre crop cuts off the subject.** Generate crop candidates and have the critic choose.
3. **Over-editing flowers.** Vibrancy is good; neon petals and changed bouquet ingredients are not.
4. **Treating Instagram as reliably scrapable.** Public downloads may work today and fail tomorrow. Keep the downloader replaceable.
5. **Using Reels UI/text overlays as a cover.** Avoid captions, stickers, progress bars, or awkward mid-transition frames.
6. **Calling a failed frame-processing run successful.** Verify the final file exists and is `1080x1350` before returning it.
7. **Ignoring rights/access.** Only download content the user is allowed to use.

## Verification Checklist

- [ ] Reel downloaded or user provided an accessible video file.
- [ ] Labelled contact sheet generated.
- [ ] Gemini/vision selected a labelled frame with rationale.
- [ ] 4:5 crop candidates generated and selected.
- [ ] Final cover exists and is `1080x1350` or another explicitly requested 4:5 size.
- [ ] Final cover has no obvious text overlays, motion blur, awkward crop, or over-processed colours.
- [ ] Report JSON saved with URL, model, selected frame, crop, and output paths.
