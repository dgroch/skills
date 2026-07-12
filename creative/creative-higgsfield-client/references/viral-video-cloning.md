# Viral Video Cloning Workflow

End-to-end pipeline for faithfully reproducing a real viral video using
Higgsfield image generation + Seedance 2.0 video animation.

## Critical Definition

**Cloning ≠ generic generation.** "Clone a viral video" means faithfully
reproducing a *specific real video's* composition, shots, subjects, lighting,
mood, and text overlays — NOT generating a vaguely on-theme scene from a text
prompt. If you skip the source video, deconstruction, and shot-by-shot
matching, you are not cloning. You are just generating. The user will notice
and be frustrated.

## Prerequisites

- `yt-dlp` on PATH or at `/opt/data/bin/yt-dlp` (for downloading source videos)
- `ffmpeg` (for frame extraction)
- `vision_analyze` tool (for shot-by-shot deconstruction)
- Higgsfield CLI authenticated (see SKILL.md Bootstrap)

## Pipeline

### 1. Source a viral video

From the Fig & Bloom Creative Research Notion DB (public link in memory) or
any URL the user provides. When the Notion API integration lacks access to
the database, scrape the public page via `browser_navigate` +
`browser_console` — walk the DOM for text blocks containing "TikTok" and
extract parent row containers. Each row has: title, category, creator, date,
emotional drivers, adaptation notes, hook type, views/likes/shares, local ID
(TikTok video ID), and platform.

Pick by engagement (views + likes) and relevance to the brand. Show the user
which one you picked and why before proceeding.

### 2. Download the original

```bash
/opt/data/bin/yt-dlp -o /tmp/original_viral.mp4 "https://www.tiktok.com/@{handle}/video/{video_id}"
```

For Instagram reels:
```bash
/opt/data/bin/yt-dlp -o /tmp/original_reel.mp4 "https://www.instagram.com/reel/{reel_id}/"
```

### 3. Extract frames for deconstruction

```bash
mkdir -p /tmp/viral_frames
# Get duration first
ffprobe -v quiet -print_format json -show_format /tmp/original_viral.mp4
# Extract every 2 seconds
for t in 0 2 4 6 8 10 12 14 16; do
  ffmpeg -ss $t -i /tmp/original_viral.mp4 -vframes 1 -q:v 2 /tmp/viral_frames/frame_${t}s.png 2>/dev/null
done
```

### 4. Deconstruct shot-by-shot with vision_analyze

For each extracted frame, call `vision_analyze` asking for:
- Composition (framing, rule of thirds, depth)
- Camera angle (eye-level, low, high, handheld)
- Subject(s) — what they're wearing, doing, holding
- Text overlays (read ALL text exactly, including emojis)
- Lighting (natural, artificial, warm/cool, bokeh)
- Mood / emotional tone

Build a structured beat sheet from the results:
- Shot duration and count
- Setting/location
- Subject description
- Camera style (handheld, tripod, selfie, drone)
- Text overlay content
- Lighting design
- Overall mood

### 5. Generate matching keyframe with soul_cinematic

Write a detailed prompt that captures ALL deconstructed elements:
composition, camera angle, subject, setting, lighting, mood. Use the exact
visual language from the deconstruction — don't paraphrase into generic terms.

```bash
HOME=/opt/data/home /opt/data/bin/higgsfield generate create soul_cinematic \
  --prompt "[detailed deconstruction prompt from step 4]" \
  --aspect_ratio 9:16 \
  --wait --wait-timeout 120s
```

**Verify the keyframe** with `vision_analyze` before animating — does it match
the original's composition, subject, lighting, and mood? If not, regenerate
with adjusted prompt.

### 6. Upload and animate with Seedance 2.0

```bash
# Upload keyframe
UUID=$(HOME=/opt/data/home /opt/data/bin/higgsfield upload create /tmp/clone_keyframe.png 2>&1)

# Generate video
HOME=/opt/data/home /opt/data/bin/higgsfield generate create seedance_2_0 \
  --prompt "[motion description from deconstruction — camera movement, subject action, atmosphere]" \
  --start-image "$UUID" \
  --aspect_ratio 9:16 \
  --duration 5 \
  --resolution 1080p \
  --mode fast \
  --genre drama \
  --wait --wait-timeout 300s
```

### 7. Download and deliver

```bash
curl -sL "<cloudfront_url>" -o /tmp/clone_video.mp4
```

Present the original and clone side-by-side with a beat sheet comparison table
showing what matched and what still needs post-production (text overlays,
duration extension, multi-shot stitching).

## Limitations & Post-Production

- **Text overlays**: Seedance 2.0 cannot render text. Add overlays in
  post-production (ffmpeg, CapKit, or editor).
- **Duration**: Seedance 2.0 produces 5s clips. For longer videos matching
  the original's full duration, generate multiple shots and stitch.
- **Multi-shot**: Each Seedance run = one shot. For multi-shot clones, generate
  separate keyframes for each shot, animate each, then stitch with ffmpeg.
- **Multi-shot stitching with ffmpeg**:
  ```bash
  # Create a concat list
  echo "file '/tmp/clone_shot1.mp4'" > /tmp/concat_list.txt
  echo "file '/tmp/clone_shot2.mp4'" >> /tmp/concat_list.txt
  ffmpeg -f concat -safe 0 -i /tmp/concat_list.txt -c copy /tmp/clone_final.mp4
  ```

## Proven Examples

| Source | Format | Views | Clone Approach |
|--------|--------|-------|----------------|
| @sagenblooms_ "Give Your Mom the Bouquet She Deserves" | Event/social, outdoor evening, string lights | 7.6M | soul_cinematic keyframe → Seedance 2.0 i2v, drama genre |
| @youraveragesminolistener "Receiving Beautiful Lilies" | UGC selfie, bathroom, brushing teeth with lilies | 5M | soul_cinematic keyframe → Seedance 2.0 i2v, drama genre |
