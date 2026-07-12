# Storyboard-to-Video Pipeline

Production pattern for creating video from approved storyboard keyframes using Higgsfield i2v and FFmpeg assembly.

## Pipeline Overview

```
1. UPLOAD    — higgsfield upload create <image> → UUID
2. GENERATE  — higgsfield generate create <model> --start-image <uuid> --wait → MP4 URL
3. DOWNLOAD  — curl -sL <url> -o slate_N_raw.mp4
4. NORMALIZE — ffmpeg trim + scale to 1080x1920 @ 24fps
5. STITCH    — ffmpeg concat → final cut
```

## Step 1: Upload Keyframes

```bash
HOME=/opt/data/home higgsfield upload create /path/to/keyframe.png
# Returns: <uuid>
```

Upload all keyframes before generating. Record UUIDs in order.

## Step 2: Generate Image-to-Video Clips

```bash
# Veo 3.1 Lite — fast, good quality, supports 4/6/8s
HOME=/opt/data/home higgsfield generate create veo3_1_lite \
  --prompt "Nearly static cinematic shot. Minimal movement. Locked off camera." \
  --start-image <uuid> \
  --aspect_ratio 9:16 \
  --duration 4 \
  --wait

# Seedance 2.0 — highest quality, supports arbitrary durations
HOME=/opt/data/home higgsfield generate create seedance_2_0 \
  --prompt "Slow cinematic push-in. Dramatic palette shift." \
  --start-image <uuid> \
  --aspect_ratio 9:16 \
  --duration 6 \
  --mode fast \
  --wait
```

**Model selection:**
- Use `veo3_1_lite` for most slates (faster, ~60s per clip)
- Use `seedance_2_0` for hero frames that need more motion or higher quality (~3-4 min per clip)

**Motion prompts:** Keep restrained. "Nearly static", "locked off camera", "minimal movement" for most shots. Only give the hero frame real camera motion ("slow dolly push").

**Output:** Direct CloudFront MP4 URL on success. Job UUID on NSFW/failure.

## Step 3: Download

```bash
curl -sL "<cloudfront_url>" -o slate_N_raw.mp4
```

## Step 4: Normalize with FFmpeg

```bash
ffmpeg -y -i slate_N_raw.mp4 \
  -t <target_duration> \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" \
  -r 24 \
  -c:v libx264 -preset medium -crf 18 \
  -an \
  -pix_fmt yuv420p \
  slate_N_norm.mp4
```

**Key params:**
- `-t` — trim to exact target duration (e.g., 2s, 1s)
- `scale + pad` — ensure uniform 1080×1920 with black letterboxing
- `-an` — strip audio (add sound design separately)
- `-pix_fmt yuv420p` — required for concat compatibility

## Step 5: Concatenate

```bash
# Create concat list
cat > concat_list.txt << 'EOF'
file 'slate_1_norm.mp4'
file 'slate_2_norm.mp4'
file 'slate_3_norm.mp4'
EOF

# Concatenate
ffmpeg -y -f concat -safe 0 -i concat_list.txt -c copy final_cut.mp4
```

## Batch Pipeline Script Pattern

For 8+ slates, write a Python script that:
1. Defines slates as `(filename, uuid, target_duration, model, prompt)` tuples
2. Uploads all images first (record UUIDs)
3. Generates clips sequentially with 2s delays
4. Handles NSFW retries (rewrite prompt removing medical/violent vocabulary)
5. Normalizes and concatenates

**Timing:** ~10 minutes for 8 slates using Veo 3.1 Lite (mix in one Seedance 2.0 for hero frame).

## Handling NSFW on Medical Imagery

If a hospital/medical scene triggers NSFW:
1. Remove all medical words: "hospital", "IV", "patient", "gown", "bed", "clinical"
2. Replace with neutral: "quiet room", "bed with white sheets", "tape on wrist"
3. If Veo still triggers, switch to Seedance 2.0 (different filter sensitivity)
4. Last resort: generate as "minimalist bedroom" — the keyframe image carries the context

## Character Continuity

For multi-slate sequences featuring the same person:
1. Generate the first appearance with a standard prompt
2. Use `flux_kontext` model for subsequent appearances — it accepts a reference image and maintains identity while changing lighting/mood
3. Upload the first frame as reference: `higgsfield upload create frame_1.png` then `higgsfield generate create flux_kontext --image <uuid> --prompt "Same person, warm amber light..."`

## Product Grounding

To feature real products in keyframes:
1. Download product images from Shopify CDN or Notion manifest
2. Upload to Higgsfield: `higgsfield upload create product.png`
3. Generate keyframe with product as reference: `higgsfield generate create soul_cinematic --image <product_uuid> --prompt "..." --aspect_ratio 9:16 --wait`
4. The `soul_cinematic` model best incorporates reference images into cinematic compositions
