# AI Video Clone Package — Template

Use this structure when producing a clone package markdown file. It captures all cognitive work (deconstruction, JSON, prompts, commands) so execution can resume later even if generation tools are temporarily blocked.

## Structure

```markdown
# [Brand] Ad Clone — [Name/ID]

## Source Video
- **Creator:** [handle] (@[username])
- **URL:** [TikTok/Instagram URL]
- **Duration:** [N seconds]
- **Location:** [video setting]
- **Engagement:** [likes | comments | saves | shares]
- **Hashtags:** [from source]
- **Caption:** [from source]
- **Notion entry:** [Local ID, database name]

---

## Step 2: Scene-by-Scene Deconstruction (ALL Scenes)

*Method: [browser frame-stepping | Gemini upload | concept metadata | yt-dlp+ffmpeg+vision]*

### Scene Breakdown

| Scene | Time | Visual | Camera | Text Overlay | Audio/Dialogue | Function |
|---|---|---|---|---|---|---|
| 1 (Hook) | 0-3s | [describe] | [shot type] | [exact text] | [audio] | hook |
| 2 (Setup) | 3-7s | [describe] | [shot type] | [exact text] | [audio] | setup |
| 3 (Reaction) | 7-12s | [describe] | [shot type] | [exact text] | [audio] | proof |
| 4 (CTA) | 10-12s | [describe] | [shot type] | [exact text] | [audio] | cta |

### Key Structural Observations
1. **Format:** [e.g. POV street casting, unboxing, tutorial]
2. **Pattern Interrupt:** [what grabs attention]
3. **Beat Structure:** [sequence summary]
4. **Tone:** [authentic? polished? educational?]
5. **Audio:** [voiceover script? ambient? music? face-to-camera?]

---

## Step 3-4: First Frame + AI Actor Replacement

### Fig & Bloom Adaptation
> [quoted from Notion research database if available]

### First Frame Specification
**Composition:** Vertical 9:16
**Subject:** [detailed description]
**Lighting:** [warm/desaturated/natural Australian/etc.]
**Mood:** [emotional tone]

### AI UGC Actor Specification
```
Actor: [gender, age range, appearance]
Imperfections: [list 3-4 specific flaws — these are critical for realism]
Wardrobe: [clothing]
Demeanor: [personality traits]
Hands: [visible details — working hands, not manicured]
Setting: [adapted location, not the original]
```

---

## Step 7: Brand Product Integration

### Fig & Bloom Product Reference
- **Product:** [name, price]
- **Image URL:** [Shopify CDN URL]
- **Local path:** /tmp/fab_products/[name].jpg
- **Description:** [flower varieties, packaging style, colours]
- **Integration notes:** [how product is held/displayed in the scene]

---

## Step 5-6: JSON Scene Descriptions (Claude Step)

```json
{
  "campaign": "[ID]",
  "title": "[hook line]",
  "format": "9:16 vertical",
  "duration_seconds": [N],
  "brand": {
    "name": "Fig & Bloom",
    "palette": ["Noir #1a1a1a", "Clay #b5651d", "White #faf8f5"],
    "grade": "[colour description]"
  },
  "actor": { ... },
  "scenes": [
    {
      "scene": 1,
      "timestamp": "0-2s",
      "shot_type": "[type]",
      "focus": "[focal point]",
      "action": "[describe action]",
      "environment": "[setting]",
      "colours": ["..."],
      "mood": "[emotion]",
      "copy_overlay": { "text": "...", "style": "...", "position": "..." } | null,
      "audio": "[audio description — dialogue script, ambient, music]",
      "function": "hook|setup|proof|cta"
    }
  ]
}
```

---

## Step 8: Per-Scene Keyframe Generation Prompts

### Scene 1 Keyframe
**Model:** soul_cinematic | text2image_soul_v2
```
[HUGE STACK of detailed scene description with actor, setting, lighting,
mood, brand product details, imperfections. Include Fig & Bloom packaging
description. Explicit instruction for realism.]
```

### Scene 2 Keyframe
**Model:** soul_cinematic | text2image_soul_v2
```
[Scene 2 specific keyframe prompt...]
```

[... one per scene ...]

---

## Step 9: Per-Scene Video Generation Commands

### Scene 1 — Kling 3.0 with native audio
```bash
# Upload keyframe
UUID1=$(HOME=/opt/data/home higgsfield upload create /tmp/scene1_keyframe.png 2>&1)

# Generate video with sound
HOME=/opt/data/home higgsfield generate create kling3_0 \
  --prompt "[scene 1 action + dialogue + accent instructions]" \
  --start-image "$UUID1" \
  --aspect_ratio 9:16 \
  --duration 5 \
  --sound on \
  --mode std \
  --wait --wait-timeout 300s

# Download
curl -sL "<cloudfront_url>" -o /tmp/scene1_video.mp4
```

### Scene 2 — Seedance 2.0 with audio
```bash
# Upload keyframe
UUID2=$(HOME=/opt/data/home higgsfield upload create /tmp/scene2_keyframe.png 2>&1)

# Generate video
HOME=/opt/data/home higgsfield generate create seedance_2_0 \
  --prompt "[scene 2 description]" \
  --start-image "$UUID2" \
  --aspect_ratio 9:16 \
  --duration 5 \
  --resolution 1080p \
  --mode fast \
  --generate_audio true \
  --genre drama \
  --wait --wait-timeout 300s

curl -sL "<cloudfront_url>" -o /tmp/scene2_video.mp4
```

[... one per scene ...]

---

## Step 10: Voiceover Script (ElevenLabs)

### Voice Selection
- **Voice:** Arabella (aEO01A4wXwd1O8GPgGlF) — young Australian female
- **Model:** eleven_multilingual_v2
- **Local output:** /tmp/voiceover.mp3

### Script
```
[Full voiceover script with timing cues per scene]
Scene 1 (0-5s): "Me when I get flowers. Like, I'm literally brushing my teeth and I still can't put them down."
Scene 2 (5-10s): "...But somehow doing laundry is easier with lilies."
[... etc ...]
```

### Generation Command
```bash
ELEVEN_KEY=$(grep "^ELEVENLABS_API_KEY=*** /opt/data/.env | cut -d= -f2-)
curl -s -X POST "https://api.elevenlabs.io/v1/text-to-speech/aEO01A4wXwd1O8GPgGlF" \
  -H "xi-api-key: $ELEVEN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text":"[full script]","model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.5,"similarity_boost":0.75,"style":0.4,"use_speaker_boost":true}}' \
  -o /tmp/voiceover.mp3
```

---

## Step 10: Background Music (Sonilo)

```bash
HOME=/opt/data/home higgsfield generate create sonilo_music \
  --prompt "[genre, mood, tempo, instrumentation description]" \
  --duration [N] \
  --wait --wait-timeout 120s

curl -sL "<cloudfront_url>" -o /tmp/sonilo_music.m4a
```

---

## Step 11: Audio Mixing + Caption Burning (Per Scene)

### Per-Scene Audio Mix
```bash
ffmpeg -y \
  -i /tmp/scene[N]_video.mp4 \
  -i /tmp/voiceover.mp3 \
  -i /tmp/sonilo_music.m4a \
  -filter_complex "[1:a]volume=1.0[voice];[2:a]volume=0.25[music];[0:a]volume=0.3[ambient];[voice][music][ambient]amix=inputs=3:duration=shortest:dropout_transition=0[aout]" \
  -map "0:v" -map "[aout]" \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 192k \
  -shortest \
  /tmp/scene[N]_mixed.mp4
```

### Per-Scene Caption Burn
```bash
ffmpeg -y -i /tmp/scene[N]_mixed.mp4 \
  -vf "drawtext=text='[exact caption text]':fontcolor=white:fontsize=48:x=30:y=h-th-80:borderw=3:bordercolor=black@0.6:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" \
  -c:a copy \
  -c:v libx264 -preset fast -crf 23 \
  /tmp/scene[N]_final.mp4
```

---

## Step 12: Final Concatenation

```bash
cat > /tmp/concat_list.txt << 'EOF'
file '/tmp/scene1_final.mp4'
file '/tmp/scene2_final.mp4'
file '/tmp/scene3_final.mp4'
file '/tmp/scene4_final.mp4'
EOF

ffmpeg -y -f concat -safe 0 -i /tmp/concat_list.txt \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 192k \
  /tmp/clone_final.mp4
```

---

## Status Table

| Step | Status | Needs |
|---|---|---|
| Source video identified from [source] | ✅ Done | — |
| Scene-by-scene deconstruction (ALL scenes) | ✅ Done | — |
| First frame + AI actor spec | ✅ Done | — |
| JSON scene descriptions | ✅ Done | — |
| Fig & Bloom product images sourced | ✅ Done | — |
| Per-scene keyframe generation | ⏳ Blocked | [blocker] |
| Per-scene video generation (with audio) | ⏳ Blocked | [blocker] |
| Voiceover generation (ElevenLabs) | ⏳ Blocked | [blocker] |
| Background music (sonilo) | ⏳ Blocked | [blocker] |
| Audio mixing + caption burning | ⏳ Blocked | [blocker] |
| Final concatenation | ⏳ Blocked | [blocker] |
```

## Notes

- The clone package is the **deliverable when tools are blocked** — it captures all cognitive work so execution can resume later
- The JSON scene descriptions serve as a **thinking tool**, not as a literal API input — video models take natural-language prompts, but the JSON ensures all scene elements (action, environment, mood, copy overlays, audio) are present
- **Every scene gets its own keyframe, its own video generation, and its own caption burn** — then they are concatenated at the end
- **Audio mixing levels:** voice 1.0, music 0.15-0.25, ambient 0.2-0.3 — adjust per content
- **Caption position:** lower-left is the most common TikTok style: `x=30:y=h-th-80`
- Always adapt the setting to Australian context for Fig & Bloom (Bondi not Santa Monica, etc.)