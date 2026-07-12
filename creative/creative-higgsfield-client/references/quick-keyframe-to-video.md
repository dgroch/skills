# Quick Keyframe-to-Video (Single Shot)

Streamlined pipeline for generating one cinematic video clip from a prompt — no storyboard, no multi-slate assembly. Useful for rapid prototyping, ad concept tests, or demonstrating the Higgsfield i2v pipeline.

## Pipeline

```
1. GENERATE keyframe  — soul_cinematic → PNG URL
2. DOWNLOAD keyframe  — curl → local PNG
3. UPLOAD keyframe     — higgsfield upload create → UUID
4. GENERATE video      — seedance_2_0 --start-image <UUID> → MP4 URL
5. DOWNLOAD video       — curl → local MP4
```

## Commands

### 1. Generate keyframe

`soul_cinematic` does NOT accept `--resolution` — its native output is already ~2K. Accepted params: `aspect_ratio`, `quality`, `prompt`, `medias`, `custom_reference_id`.

```bash
HOME=/opt/data/home /opt/data/bin/higgsfield generate create soul_cinematic \
  --prompt "Cinematic close-up of [scene]. [Lighting]. [Lens/composition details]." \
  --aspect_ratio 9:16 \
  --wait --wait-timeout 120s
# Output: https://d8j0ntlcm91z4.cloudfront.net/.../<id>.png
```

### 2. Download + 3. Upload

```bash
curl -sL "<cloudfront_url>" -o /tmp/keyframe.png
HOME=/opt/data/home /opt/data/bin/higgsfield upload create /tmp/keyframe.png
# Output: <uuid>
```

### 4. Generate video with Seedance 2.0

```bash
HOME=/opt/data/home /opt/data/bin/higgsfield generate create seedance_2_0 \
  --prompt "Describe the MOTION in the scene: hands moving, camera push-in, light shifting. Keep it specific and cinematic." \
  --start-image "<uuid>" \
  --aspect_ratio 9:16 \
  --duration 5 \
  --resolution 1080p \
  --mode fast \
  --genre drama \
  --wait --wait-timeout 300s
# Output: https://d8j0ntlcm91z4.cloudfront.net/.../<id>.mp4
```

**Timing:** ~20s for keyframe generation, ~90s for Seedance 2.0 video (fast mode, 5s, 1080p). Total ~2 min end-to-end.

### 5. Download

```bash
curl -sL "<cloudfront_url>" -o /tmp/output.mp4
```

## Prompt Tips

- **Keyframe prompt:** Describe the scene as a frozen moment — composition, lighting, lens, mood. Think editorial photography.
- **Video prompt:** Describe the MOTION only — what moves, how the camera moves, how light changes. The keyframe already defines the visual.
- **Genre param:** `drama` gives warm cinematic grading. `auto` lets the model decide. `epic` for grand/sweeping.
- **Duration:** 5s is the sweet spot for a single shot. 3s is too short to register motion. 10s risks model drift.

## Verified Working

Tested June 2026 with Fig & Bloom florist scene:
- `soul_cinematic` keyframe: florist arranging peonies in sunlit shop, 9:16, ~20s
- `seedance_2_0` i2v: `--mode fast --genre drama --resolution 1080p --duration 5`, ~90s
- Output: 2.2MB MP4, 1080p, 5s, cinematic motion
- Credits used: ~2 (keyframe) + ~5-10 (video)
