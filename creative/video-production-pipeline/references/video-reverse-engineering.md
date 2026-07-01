# Video Reverse-Engineering Workflow

Break down an existing video shot-by-shot and recreate it using AI generation tools. Popularized by @theaidecode and similar creators for "stealing" winning ad creatives.

## Pipeline Overview

```
1. ACQUIRE   — Download source video (yt-dlp, manual)
2. ANALYZE   — Frame extraction + AI vision breakdown
3. PROMPT    — Generate per-shot Higgsfield prompts from breakdown
4. GENERATE  — Produce keyframes + animate each shot
5. ASSEMBLE  — Stitch in timeline order matching reference pacing
```

## Step 1: Acquire Source Video

```bash
# Instagram, YouTube, TikTok, Twitter, etc.
/opt/data/bin/yt-dlp -o "/tmp/source_video.%(ext)s" "<url>"
```

yt-dlp is installed at `/opt/data/bin/yt-dlp` and handles Instagram posts/reels, YouTube, TikTok, and most social platforms.

## Step 2: Extract Frames for Analysis

```bash
# 1 frame per second (good for short videos)
ffmpeg -i source.mp4 -vf "fps=1" -q:v 2 frames/frame_%03d.jpg

# 1 frame per 2 seconds (sparser, good for longer videos)
ffmpeg -i source.mp4 -vf "fps=0.5" -q:v 1 frames/frame_%03d.jpg
```

Then analyze frames with a vision-capable model to extract:
- Camera angle and movement per shot (dolly, pan, tracking, static, handheld)
- Shot composition and framing (wide, medium, close-up, POV)
- Subject positioning and action
- Lighting direction, color temperature, mood
- Duration and pacing per shot
- Transitions between shots (cut, dissolve, match cut)

### Analysis Prompts

**For Gemini (gemini.google.com, supports video upload directly):**
```
Watch this video and break down every shot in a table:
- Shot number
- Duration (seconds)
- Camera angle and movement
- Composition and framing
- Subject/action description
- Lighting and mood
- Transition from previous shot
```

**For frame-by-frame AI analysis (when video upload isn't available):**
```
Analyze this frame from a video sequence. Describe:
1. Camera angle (high/low/eye-level) and framing (wide/medium/close-up)
2. Subject position and apparent action
3. Lighting direction, color temperature, and mood
4. Any visible motion blur suggesting camera movement
```

## Step 3: Generate Per-Shot Prompts

From the shot breakdown, create Higgsfield prompts for each shot:

**Keyframe prompt** (for `soul_cinematic` or `text2image_soul_v2`):
- Describe the static composition: subject, framing, lighting, mood
- Include aspect ratio matching the source (9:16 for mobile ads, 16:9 for cinematic)

**Motion prompt** (for `veo3_1_lite` or `seedance_2_0`):
- Describe camera movement ONLY (not the scene — the keyframe carries that)
- Use restrained language: "nearly static", "slow push-in", "gentle lateral drift"
- Duration should match the source shot's pacing

### Example Shot Breakdown → Prompts

| Source Shot | Keyframe Prompt | Motion Prompt | Duration |
|---|---|---|---|
| Wide establishing, static, warm golden hour | "Wide establishing shot, [subject] in [location], golden hour backlighting, warm amber tones, cinematic 9:16" | "Locked off camera, minimal ambient movement" | 3s |
| Medium tracking, subject walking left-to-right | "Medium shot, [subject] in profile, natural daylight, shallow depth of field" | "Slow lateral tracking shot, left to right" | 4s |
| Close-up, hands holding product | "Extreme close-up of hands holding [product], soft diffused lighting, shallow DOF" | "Very subtle breathing motion, nearly static" | 2s |

## Step 4: Generate Each Shot

```bash
# Generate keyframe
KEYFRAME_UUID=$(HOME=/opt/data/home higgsfield generate create soul_cinematic \
  --prompt "<keyframe prompt>" \
  --aspect_ratio 9:16 --resolution 2k --wait 2>&1 | grep -oP 'https?://[^\s"]+')

# Upload keyframe for animation
UPLOAD_UUID=$(HOME=/opt/data/home higgsfield upload create /tmp/keyframe.png 2>&1 | grep -oP '[0-9a-f-]{36}')

# Animate
HOME=/opt/data/home higgsfield generate create veo3_1_lite \
  --prompt "<motion prompt>" \
  --start-image "$UPLOAD_UUID" \
  --aspect_ratio 9:16 \
  --duration 4 \
  --wait
```

For identity-preserving recreations (same person across shots), use `flux_kontext` for subsequent appearances of the same character.

## Step 5: Assemble

Download all generated clips and stitch using the storyboard-to-video pipeline (see `references/storyboard-to-video-pipeline.md` for normalize + concat steps).

Match the reference video's pacing by trimming each clip to the source shot's duration.

## Alternative: Claude Desktop + Higgsfield MCP

The original @theaidecode workflow uses Claude Desktop with the Higgsfield MCP connector:

1. Claude Desktop → Settings → Connectors → Add Custom Connector → Name: `Higgsfield`
2. Upload video directly to Claude chat
3. Prompt: "Watch this video, break it down scene by scene, then generate Higgsfield prompts to recreate each shot"
4. Claude generates and executes prompts via MCP — no CLI needed

This is a single-window workflow but requires Claude Desktop (not available in Hermes). The CLI equivalent above produces the same results.

## Reverse-Engineering Competitor Ads (E-commerce)

For recreating winning ads with your own product:

1. **Find a winner** — look for high engagement metrics (views, shares, comments)
2. **Download and break down** using the pipeline above
3. **Swap the product** — use your product images as references in keyframe prompts
4. **Swap the talent** — generate new AI avatars via Higgsfield Marketing Studio:
   ```bash
   HOME=/opt/data/home higgsfield marketing-studio avatars list
   HOME=/opt/data/home higgsfield generate create marketing_studio_video \
     --prompt "<rebuilt script>" \
     --avatars '[{"id":"<avatar_id>","type":"preset"}]' \
     --product_ids '[<product_id>]' \
     --mode ugc --duration 15 --aspect_ratio 9:16 --wait
   ```
5. **Change the script** — don't copy verbatim; rebuild with your brand voice while keeping the structural DNA (hook pattern, shot rhythm, CTA placement)

## Pitfalls

- **Don't copy scripts verbatim** — recreate the structural pattern (hook → problem → solution → CTA) with original copy
- **Motion prompts should be minimal** — the AI over-interprets "dynamic" and "dramatic". Use "nearly static" as default.
- **Match aspect ratio to source** — 9:16 for mobile-first ads, 16:9 for YouTube/cinematic
- **Pacing matters more than individual shots** — the rhythm of cuts is what makes an ad work. Time your clips to match the reference's edit points.
- **Vision must be working** — frame analysis requires a vision-capable model. If Gemini vision is misconfigured, use `yt-dlp` to get audio transcript as supplementary context.
