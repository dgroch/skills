# Video Generation APIs

Reference for programmatic video generation via Gemini API and Higgsfield CLI.

## Gemini API — Veo 3.1

**Access:** Via `GEMINI_API_KEY` in `/opt/data/.env`

**Available models:**
- `veo-3.1-generate-preview` — Full quality
- `veo-3.1-fast-generate-preview` — Faster generation
- `veo-3.1-lite-generate-preview` — Fastest/cheapest (tested: 6s 720p video with audio in ~30s)
- `veo-3.0-generate-001` / `veo-3.0-fast-generate-001` — Previous generation
- `veo-2.0-generate-001` — Older generation

**API endpoint:** `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:predictLongRunning?key={api_key}`

**Duration constraint:** 4-8 seconds inclusive. Values outside this range return 400 error.

**Aspect ratios:** 16:9, 9:16

**Request format:**
```json
{
  "instances": [
    {
      "prompt": "A beautiful bouquet of fresh pink roses being delivered to a doorstep..."
    }
  ],
  "parameters": {
    "sampleCount": 1,
    "aspectRatio": "16:9",
    "durationSeconds": 6
  }
}
```

**Response:** Returns an operation name (e.g., `models/veo-3.1-lite-generate-preview/operations/abc123`)

**Polling pattern:**
```python
poll_url = "https://generativelanguage.googleapis.com/v1beta/{operation_name}?key={api_key}"
for attempt in range(40):  # 10 min max
    time.sleep(15)
    resp = requests.get(poll_url)
    data = resp.json()
    if data.get("done"):
        # Extract video
        response = data.get("response", {})
        predictions = response.get("predictions", [])
        for pred in predictions:
            # Video may be base64-encoded or a URI
            b64 = pred.get("bytesBase64Encoded", "")
            if b64:
                video_data = base64.b64decode(b64)
                # Save to file
            else:
                # Check for URI
                uri = pred.get("uri", pred.get("videoUri", ""))
                if uri:
                    # Download from URI
```

**Video specs (tested with veo-3.1-lite):**
- Resolution: 1280×720
- Frame rate: 24fps
- Audio: AAC 48kHz (native synchronized audio generation)
- Codec: H.264
- Format: MP4

**Note:** "Gemini Omni" as a distinct model is NOT in the API yet (as of May 2026). Google said "API coming in the coming weeks" at I/O on May 19. Veo 3.1 is the rendering engine behind Omni.

## Higgsfield CLI — Video Models

**Command:** `HOME=/opt/data/home higgsfield generate create {model} --prompt "..." --start-image {path_or_id} --duration {seconds} --wait`

**Key video models:**
- `seedance_2_0` — Highest visual fidelity, multi-shot
- `veo3_1` / `veo3_1_lite` — Google Veo 3.1 (same engine as Gemini API)
- `kling3_0` — Strong motion consistency
- `marketing_studio_video` — Commercial ads with avatars

**Duration:** Check model specs with `HOME=/opt/data/home higgsfield model get {model} --json`

**Aspect ratio:** Use `--aspect_ratio 16:9` or `--aspect_ratio 9:16`

**Image-to-video:** Use `--start-image {path_or_upload_id}` to animate a reference image

**Upload workflow:**
```bash
HOME=/opt/data/home higgsfield upload create /path/to/image.png
# Returns upload UUID
HOME=/opt/data/home higgsfield generate create veo3_1_lite --prompt "..." --start-image {uuid} --duration 6 --wait
```

## Gemini API — Image Generation (Imagen 4.0)

**Models:**
- `imagen-4.0-generate-001` — Standard quality
- `imagen-4.0-fast-generate-001` — Faster generation (tested for storyboards)
- `imagen-4.0-ultra-generate-001` — Highest quality

**API endpoint:** `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:predict?key={api_key}`

**Request format:**
```json
{
  "instances": [
    {
      "prompt": "Cinematic still frame, vertical 9:16 aspect ratio..."
    }
  ],
  "parameters": {
    "sampleCount": 1,
    "aspectRatio": "9:16"
  }
}
```

**Response:** Returns base64-encoded image in `predictions[0].bytesBase64Encoded`

**Use case:** Storyboard keyframes, concept art, visual references for video generation

## Testing Patterns

**Text-to-video (Gemini Veo 3.1):**
```python
# Generate 6-second clip
payload = {
    "instances": [{"prompt": "..."}],
    "parameters": {"sampleCount": 1, "aspectRatio": "16:9", "durationSeconds": 6}
}
resp = requests.post(url, json=payload)
operation_name = resp.json()["name"]
# Poll every 15s until done
# Save base64 video to .mp4
```

**Image-to-video (Higgsfield):**
```bash
# Upload reference image
uuid=$(HOME=/opt/data/home higgsfield upload create /tmp/keyframe.png)
# Generate video
HOME=/opt/data/home higgsfield generate create veo3_1_lite --prompt "Animate this..." --start-image $uuid --duration 6 --wait
```

**Storyboard workflow:**
1. Generate keyframes with Imagen 4.0 (8 frames for 15s cut)
2. Review with user
3. Animate each keyframe with Veo 3.1 image-to-video
4. Stitch in post (or deliver as separate clips)
