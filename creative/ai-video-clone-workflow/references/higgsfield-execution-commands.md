# Higgsfield Execution Commands for Video Clone Workflow

Ready-to-run commands for video generation via the Higgsfield CLI.
All commands require `HOME=/opt/data/home` prefix for auth (credentials live at
`/opt/data/home/.config/higgsfield/credentials.json`).

## Prerequisites

```bash
HOME=/opt/data/home higgsfield account status
```

If credentials are expired, see the Device Login Flow section below.

## Step 7: Generate Keyframe Image (PER SCENE)

Use `soul_cinematic` (best for photorealistic editorial) or `text2image_soul_v2` (best for UGC/portraits).

```bash
HOME=/opt/data/home higgsfield generate create soul_cinematic \
  --prompt "<detailed scene description from the beat sheet>" \
  --aspect_ratio 9:16 \
  --wait --wait-timeout 5m
```

**⚠️ `soul_cinematic` does NOT accept `--resolution`.** Only: `aspect_ratio`, `prompt`, `quality`, `custom_reference_id`, `medias`.

Download: `curl -sL "<result_url>" -o /tmp/scene1_keyframe.png`

### Keyframe Verification (before animating)

Call `vision_analyze` on each keyframe before spending video generation credits:
> "Does this match: [setting, lighting, subjects, camera angle for THIS scene]? Compare to original."

## Upload Keyframe

```bash
UUID=$(HOME=/opt/data/home higgsfield upload create /tmp/scene1_keyframe.png 2>&1 | grep -oP '[0-9a-f-]{36}')
```

## Step 9: Video Generation (With Audio)

### Kling 3.0 with native audio (`--sound on`)

```bash
HOME=/opt/data/home higgsfield generate create kling3_0 \
  --prompt "<scene description with dialogue and accent instructions>" \
  --start-image "$UUID" \
  --aspect_ratio 9:16 \
  --duration 5 \
  --sound on \
  --mode std \
  --wait --wait-timeout 300s
```

**⚠️ Kling 3.0 `medias` only accepts IMAGE roles.** Passing `--audio <uuid>` fails with
"medias.1.role: Input should be IMAGE/START_IMAGE/END_IMAGE". The `sound: on` parameter
generates audio from the text prompt — include dialogue and accent in the prompt text.

### Seedance 2.0 with audio (`--generate_audio true`, default is True)

```bash
HOME=/opt/data/home higgsfield generate create seedance_2_0 \
  --prompt "<scene description with dialogue>" \
  --start-image "$UUID" \
  --aspect_ratio 9:16 \
  --duration 5 \
  --resolution 1080p \
  --mode fast \
  --generate_audio true \
  --genre drama \
  --wait --wait-timeout 300s
```

**Note:** `generate_audio` defaults to `True`. Check with `ffprobe -show_streams <file>.mp4`.

### Veo 3.1 Lite with audio

```bash
HOME=/opt/data/home higgsfield generate create veo3_1_lite \
  --prompt "<scene description>" \
  --aspect_ratio 9:16 \
  --duration 8 \
  --generate_audio true \
  --wait --wait-timeout 300s
```

### Parameter notes

| Parameter | Value | Why |
|---|---|---|
| `--start-image` | UUID from upload | Frame 1; identity, lighting propagate |
| `--duration` | Scene length in seconds | Kling accepts int; Veo accepts 4/6/8 |
| `--sound` / `--generate_audio` | on / true | Native audio generation |
| `--mode` | fast or std | std is higher quality but ~2x longer |
| `--genre` | drama | Matches editorial tone; `auto` also works |

### Timeout handling

Use `background=true` with `notify_on_complete=true` for long generations, or set `timeout=360`.

## Voiceover Generation (ElevenLabs API direct)

Australian accent voices:
- **Arabella** (aEO01A4wXwd1O8GPgGlF) — young female, engaging
- **Emma** (56bWURjYFHyYyVf490Dp) — early 30s female, conversational
- **Sophia** (LtPsVjX1k0Kl4StEMZPK) — young female, bright, for ads
- **Charlie** (IKne3meq5aSn9XLyUdCD) — young male, deep, confident

```bash
ELEVEN_KEY=$(grep "^ELEVENLABS_API_KEY=*** /opt/data/.env | cut -d= -f2-)
curl -s -X POST "https://api.elevenlabs.io/v1/text-to-speech/aEO01A4wXwd1O8GPgGlF" \
  -H "xi-api-key: $ELEVEN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text":"<script>","model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.5,"similarity_boost":0.75,"style":0.4,"use_speaker_boost":true}}' \
  -o /tmp/voiceover.mp3
```

List all available voices: `curl -s "https://api.elevenlabs.io/v1/voices" -H "xi-api-key: $ELEVEN_KEY"`

## Background Music (sonilo_music)

```bash
HOME=/opt/data/home higgsfield generate create sonilo_music \
  --prompt "<genre, mood, tempo, instrumentation>" \
  --duration 5 \
  --wait --wait-timeout 120s
```

Output is a `.m4a` file on CloudFront.

## Audio Mixing (ffmpeg `amix`)

```bash
ffmpeg -y \
  -i /tmp/scene_video.mp4 \
  -i /tmp/voiceover.mp3 \
  -i /tmp/sonilo_music.m4a \
  -filter_complex "[1:a]volume=1.0[voice];[2:a]volume=0.25[music];[0:a]volume=0.3[ambient];[voice][music][ambient]amix=inputs=3:duration=shortest:dropout_transition=0[aout]" \
  -map "0:v" -map "[aout]" \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 192k \
  -shortest \
  /tmp/scene_mixed.mp4
```

Volume levels: voice 1.0, music 0.15-0.25, ambient 0.2-0.3.

## Caption Burning (ffmpeg `drawtext`)

```bash
ffmpeg -y -i /tmp/scene_mixed.mp4 \
  -vf "drawtext=text='caption text':fontcolor=white:fontsize=48:x=30:y=h-th-80:borderw=3:bordercolor=black@0.6:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" \
  -c:a copy \
  -c:v libx264 -preset fast -crf 23 \
  /tmp/scene_final.mp4
```

Fonts: DejaVu Sans Bold (`/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`),
Noto Color Emoji (`/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf`).
Position for 9:16 (720x1280): lower-left `x=30:y=h-th-80`.

## Multi-Scene Concatenation (ffmpeg)

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

All scenes must have the same resolution. If not, add `-vf scale=720:1280`.

## Voice Replacement (voice_change — API direct, CLI broken)

The `voice_change`/`dubbing` models need the Higgsfield REST API directly — the CLI
`input_video` param expects an object, not a UUID string:

```bash
HF_TOKEN=$(HOME...home higgsfield auth token)
VIDEO_UUID=$(HOME=/opt/data/home higgsfield upload create /tmp/video.mp4)
curl -X POST "https://api.higgsfield.ai/v1/generate" \
  -H "Authorization: Bearer *** \
  -H "Content-Type: application/json" \
  -d '{"job_set_type":"voice_change","params":{"input_video":{"media_id":"'"$VIDEO_UUID"'","type":"media_input"},"voice_id":"aEO01A4wXwd1O8GPgGlF","voice_type":"preset"}}'
```

## Download the Output

```bash
curl -sL "<cloudfront_url_from_output>" -o /tmp/clone_final.mp4
```

## Sending Videos to the User

```
**ORIGINAL** (X views, @handle):
MEDIA:/tmp/original_viral.mp4

**CLONE** (Kling 3.0, 1080p, 9:16, native audio + voiceover + music + captions):
MEDIA:/tmp/clone_final.mp4
```

## Auth: Device Login Flow (when credentials are expired)

`higgsfield auth login` has a **60-second default timeout**. Run in background:

```bash
cat > /tmp/higgs_auth.sh << 'EOF'
#!/bin/bash
export HOME=/opt/data/home
/opt/data/bin/higgsfield auth login > /tmp/higgs_auth_output.txt 2>&1
EOF
chmod +x /tmp/higgs_auth.sh
# Start in background (terminal background=true, notify_on_complete=true)
# After 3 seconds, read: cat /tmp/higgs_auth_output.txt
# Present the device URL as a clickable markdown link to the user
```

## Pitfalls

- **`soul_cinematic` does NOT accept `--resolution`** — only `aspect_ratio`, `prompt`, `quality`, `custom_reference_id`, `medias`.
- **NSFW filter on medical/hospital imagery** — Veo 3.1 Lite and Seedance 2.0 both trigger NSFW on "hospital", "IV", "patient in bed". Rephrase to neutral language.
- **`--medias` flag does not work** — use `--start-image <uuid>` for image-to-video.
- **Kling 3.0 `medias` only accepts IMAGE roles** — `--audio` flag is rejected. Use `--sound on` to generate audio from the prompt, or mix separately with ffmpeg.
- **Seedance 2.0 `generate_audio` defaults to True** — you may already be getting audio. Check with `ffprobe -show_streams`.
- **502 errors** — transient. Retry with 15s backoff.
- **Output is a CloudFront URL** — `https://d8j0ntlcm91z4.cloudfront.net/...`.
- **Soul-ID + product reference trap** — `text2image_soul_v2` accepts at most one image reference. Generate the person/location first, then use `seedream_v4_5` to correct product details.
- **Terminal timeout vs processing time** — use `background=true` with `notify_on_complete=true`, or set `timeout=360`.
- **voice_change/dubbing CLI broken** — `input_video` expects an object. Use the Higgsfield REST API directly.