# Video Remix — SKILL.md

## Purpose

Transform an existing video into a new video with specified changes (character, scene, script, style) using a single high-level prompt. The pipeline decomposes the source into shots, regenerates keyframe visuals via Nano Banana Pro, then generates new video clips via Veo 3.1 — all through the Higgsfield platform.

---

## Entry Conditions

- Source video file exists (MP4, MOV, or WEBM)
- High-level remix prompt provided by user (e.g. "Change the character to a woman in her 30s, set the scene in Tokyo at night, keep the same pacing")
- Higgsfield API key is set in environment (`HIGGSFIELD_API_KEY`)
- Anthropic API key is set in environment (`ANTHROPIC_API_KEY`)
- FFmpeg and Python 3.10+ available on host

IF any entry condition is unmet → HARD STOP. State which condition failed and what the user needs to provide.

---

## Pipeline Overview

```
INPUT: source_video.mp4 + "remix prompt"
  │
  ├─ 1. DECOMPOSE ──→ shots[] with keyframes + metadata
  │
  ├─ 2. ANALYSE ─────→ per-shot descriptions + remix instructions
  │
  ├─ 3. REGENERATE ──→ new keyframe images (Nano Banana Pro)
  │
  ├─ 4. GENERATE ────→ new video clips (Veo 3.1)
  │
  └─ 5. ASSEMBLE ────→ final_remix.mp4
```

---

## Step 1: DECOMPOSE

**Script:** `scripts/decompose.py`

**Actions:**
1. Run PySceneDetect on source video with `ContentDetector` (threshold: 27.0).
2. For each detected shot, extract:
   - Start/end timestamps
   - Duration in seconds
   - Keyframe image (frame at 30% into the shot — avoids transition artifacts)
   - Shot index (zero-padded, e.g. `shot_001`)
3. Extract audio track as separate WAV file.
4. Write `shots_manifest.json` with all metadata.

**Quality Gate:**
- Minimum 1 shot detected. IF zero shots → lower threshold to 20.0 and retry ONCE. IF still zero → HARD STOP, flag video as single-shot and ask user for manual timestamps.
- Every keyframe image must be > 10KB (not a black/corrupt frame). IF corrupt → re-extract at 50% mark. IF still corrupt → skip shot and log warning.

**Output checkpoint:** `STATE_DECOMPOSE_COMPLETE`
- `./work/keyframes/shot_NNN.png` (one per shot)
- `./work/audio/source_audio.wav`
- `./work/shots_manifest.json`

---

## Step 2: ANALYSE

**Executed by:** The orchestrating agent (Claude via Anthropic API)

**Actions:**
1. Load `shots_manifest.json`.
2. For each keyframe, send image + the user's high-level remix prompt to Claude with this system prompt:

```
You are a video production assistant. You will receive:
- A keyframe image from an existing video shot
- A high-level remix brief from the director

For this shot, produce a JSON object with:
{
  "shot_index": "shot_001",
  "original_description": "Brief description of what's in the keyframe",
  "nano_banana_prompt": "Precise image generation prompt that applies the remix brief to this specific shot. Preserve composition and framing. Be specific about character appearance, environment, lighting, and mood.",
  "veo_prompt": "Motion/action prompt for video generation from the new keyframe. Describe camera movement, character action, and ambient motion. Keep it to 2-3 sentences.",
  "duration_seconds": 3.5
}

Respond ONLY with the JSON object. No preamble.
```

3. Collect all shot analyses into `remix_plan.json`.

**Quality Gate:**
- Every shot must have a valid `nano_banana_prompt` and `veo_prompt`. IF any field is empty → re-run analysis for that shot with explicit instruction: "You left a field empty. Fill all fields."
- `duration_seconds` must match source shot duration (±0.5s tolerance).

**Output checkpoint:** `STATE_ANALYSE_COMPLETE`
- `./work/remix_plan.json`

---

## Step 3: REGENERATE (Nano Banana Pro)

**Script:** `scripts/regenerate.py`

**Actions:**
1. Load `remix_plan.json`.
2. For each shot, upload the original keyframe via `higgsfield_client.upload_file()`.
3. Call `higgsfield_client.subscribe()` with:
   - Model: `google/nano-banana-2/edit` (configurable via `HF_IMAGE_MODEL`)
   - Arguments: `images_list` (array with uploaded URL), `prompt`, `aspect_ratio`, `resolution`
4. The SDK handles polling internally — `subscribe()` blocks until complete.
5. Download result image to `./work/regen_keyframes/shot_NNN.png`.
6. Process shots sequentially. Add 2s delay between requests.

**Quality Gate:**
- Response must return HTTP 200 with a valid image URL. IF 429 (rate limit) → exponential backoff starting at 30s, max 3 retries. IF 500 → retry once after 10s. IF persistent failure → HARD STOP on that shot, log error, continue remaining shots.
- Downloaded image must be > 10KB. IF corrupt → retry generation once with slightly rephrased prompt (append "high quality, sharp detail").

**Failure Modes:**
| Failure | Detection | Impact | Recovery |
|---------|-----------|--------|----------|
| Rate limit (429) | HTTP status | Pipeline stalls | Exponential backoff, max 3 retries |
| Bad generation (blurry/wrong) | Manual review or file size < 10KB | Shot quality degrades | Retry with refined prompt |
| API timeout | No response in 120s | Shot skipped | Log + continue, flag for manual redo |
| Character inconsistency | Visual review (not automatable) | Breaks continuity | Add character reference image to prompt |

**Output checkpoint:** `STATE_REGENERATE_COMPLETE`
- `./work/regen_keyframes/shot_NNN.png` (one per shot)

---

## Step 4: GENERATE (Veo 3.1)

**Script:** `scripts/generate_video.py`

**Actions:**
1. Load `remix_plan.json`.
2. For each shot, upload the regenerated keyframe via `higgsfield_client.upload_file()`.
3. Call `higgsfield_client.subscribe()` with:
   - Model: `google/veo/3.1/image-to-video` (configurable via `HF_VIDEO_MODEL`)
   - Arguments: `image_url`, `prompt`, `duration` (4/6/8s), `resolution` ("1080p"), `aspect_ratio`
4. The SDK handles polling — `subscribe()` blocks until complete (may take 1-5 min per clip).
5. Download result to `./work/clips/shot_NNN.mp4`.
6. Process sequentially. Add 5s delay between requests.

**Quality Gate:**
- Generated clip must be playable (FFprobe returns valid duration). IF corrupt → retry once.
- Clip duration must be within ±1s of target. IF too short → log warning (acceptable). IF zero-length → retry.

**Failure Modes:**
| Failure | Detection | Impact | Recovery |
|---------|-----------|--------|----------|
| Content filter rejection | API error message | Shot blocked | Rephrase prompt to remove flagged terms, retry |
| Motion artifacts | Manual review | Quality issue | Regenerate with simpler motion prompt |
| Character drift from keyframe | Visual review | Continuity break | Use multi-reference mode with 2-3 reference images |

**Output checkpoint:** `STATE_GENERATE_COMPLETE`
- `./work/clips/shot_NNN.mp4` (one per shot)

---

## Step 5: ASSEMBLE

**Script:** `scripts/assemble.py`

**Actions:**
1. Build FFmpeg concat file from clips in shot order.
2. IF user wants original audio retained → mix source audio over assembled video.
3. IF user specified new script/voiceover → leave audio for separate processing (out of scope for this skill).
4. Apply crossfade transitions (0.3s default) between clips.
5. Encode final output: H.264, AAC audio, MP4 container.
6. Write to `./output/remix_final.mp4`.

**Quality Gate:**
- Final video duration must be within 20% of source duration. IF wildly different → log warning, don't block.
- FFprobe must confirm valid video+audio streams.

**Output checkpoint:** `STATE_ASSEMBLE_COMPLETE`
- `./output/remix_final.mp4`

---

## What a Junior Gets Wrong

1. **Extracting keyframes at shot boundaries instead of interior.** Frames at cut points are often blended/transitional. Extract at 30% into the shot, not frame 0.

2. **Sending the same generic prompt to every shot.** Each shot needs a prompt tailored to its specific composition, angle, and content. The high-level remix brief must be *interpreted per shot* by the analysis step — that's the whole point of Step 2.

3. **Ignoring Veo's duration quantisation.** Veo 3.1 only supports 4s, 6s, or 8s clips. A 5.2s source shot must be mapped to 6s. Don't try to generate arbitrary durations — you'll get errors or truncated output.

4. **Not handling character consistency across shots.** If the remix changes the character, you need to feed Nano Banana the *same character description* for every shot, not let it drift. Consider generating one "hero" keyframe first, then using it as a reference for subsequent shots.

5. **Running all API calls in parallel.** Higgsfield will rate-limit you hard. Sequential with delays is slower but reliable. Only parallelise if you've confirmed your plan tier supports it.

6. **Forgetting that Veo's image-to-video may not preserve the keyframe exactly.** The generated clip will interpret the image, not replicate it frame-for-frame. Prompt the motion carefully — "camera slowly pushes in" is better than "character suddenly turns" for maintaining visual fidelity to the keyframe.

---

## Resume Logic

On failure or interruption, check for the latest `STATE_*` checkpoint:

| Checkpoint | Resume from |
|-----------|-------------|
| `STATE_DECOMPOSE_COMPLETE` | Step 2 (Analyse) |
| `STATE_ANALYSE_COMPLETE` | Step 3 (Regenerate) |
| `STATE_REGENERATE_COMPLETE` | Step 4 (Generate) |
| `STATE_GENERATE_COMPLETE` | Step 5 (Assemble) |

Within Steps 3 and 4, resume is per-shot: skip shots that already have valid output files.

---

## Environment Variables

```
# Higgsfield auth (choose one):
HF_KEY="your-api-key:your-api-secret"
# OR:
HF_API_KEY=your-api-key
HF_API_SECRET=your-api-secret

# Claude for shot analysis:
ANTHROPIC_API_KEY=your-anthropic-key

# Model overrides (optional — use if default paths don't resolve):
HF_IMAGE_MODEL=google/nano-banana-2/edit
HF_VIDEO_MODEL=google/veo/3.1/image-to-video
```

Get Higgsfield credentials from: https://cloud.higgsfield.ai/api-keys

## Dependencies

```
pip install higgsfield-client scenedetect[opencv] anthropic requests
# FFmpeg must be installed system-wide
```
