# Video Remix — SKILL.md

## Purpose

Transform an existing video into a new video with specified changes (character, scene, script, style) using a single high-level prompt. The pipeline decomposes the source into shots, regenerates keyframe visuals via Nano Banana 2 Edit, then generates new video clips via Veo 3.1 — all through the Higgsfield platform.

---

## Entry Conditions

- Source video file exists (MP4, MOV, or WEBM).
- High-level remix prompt provided by the user (e.g. "Change the character to a woman in her 30s, set the scene in Tokyo at night, keep the same pacing").
- Higgsfield credentials set (`HF_KEY` or `HF_API_KEY_ID` + `HF_API_KEY_SECRET`).
- `claude` CLI available on PATH (no `ANTHROPIC_API_KEY` required — uses Paperclip's native Claude session).
- FFmpeg and Python 3.10+ available on host.

Run `python scripts/test_connection.py` first. IF any check fails → HARD STOP and surface the failing check to the user.

---

## Pipeline Overview

```
INPUT: source_video.mp4 + "remix prompt"
  │
  ├─ 1. DECOMPOSE ──→ shots[] with keyframes + metadata
  │
  ├─ 2. ANALYSE ─────→ per-shot descriptions + remix instructions
  │
  ├─ 3. REGENERATE ──→ new keyframe images (Nano Banana 2 Edit)
  │
  ├─ 4. GENERATE ────→ new video clips (Veo 3.1 I2V)
  │
  └─ 5. ASSEMBLE ────→ final_remix.mp4
```

---

## Step 1: DECOMPOSE

**Script:** `scripts/decompose.py`

**Actions:**
1. Run PySceneDetect on the source video with `ContentDetector` (threshold 27.0).
2. For each detected shot, extract:
   - Start/end timestamps
   - Duration in seconds
   - Keyframe image (frame at 30% into the shot — avoids transition artefacts)
   - Shot index (zero-padded, e.g. `shot_001`)
3. Extract the audio track as a separate WAV file (if present).
4. Write `shots_manifest.json` including inferred aspect ratio.

**Quality Gate:**
- Minimum 1 shot detected. IF zero → lower threshold to 20.0 and retry ONCE. IF still zero → fall back to treating the entire video as a single shot and warn the user.
- Every keyframe image must be > 10 KB (not a black/corrupt frame). IF corrupt → re-extract at 50% mark. IF still corrupt → skip shot and log a warning.

**Output checkpoint:** `STATE_DECOMPOSE_COMPLETE`
- `./work/keyframes/shot_NNN.png`
- `./work/audio/source_audio.wav` (optional)
- `./work/shots_manifest.json`

---

## Step 2: ANALYSE

**Script:** `scripts/analyse.py` (calls Claude via the `claude` CLI subprocess — no `ANTHROPIC_API_KEY` required)

**Actions:**
1. Load `shots_manifest.json`.
2. For each keyframe, send image + the user's high-level remix prompt to Claude with this system prompt:

```
You are a video production assistant. You will receive:
- A keyframe image from an existing video shot
- A high-level remix brief from the director
- The shot index and duration target

For this shot, produce a JSON object with:
{
  "shot_index": "shot_001",
  "original_description": "Brief description of what's in the keyframe",
  "nano_banana_prompt": "Precise image edit prompt that applies the remix brief…",
  "veo_prompt": "Motion/action prompt for video generation…",
  "duration_seconds": 4
}

CRITICAL RULES:
- duration_seconds MUST be one of 4, 6, or 8 (Veo 3.1 constraint).
- shot_index MUST match the id the user provides.
- Respond with the JSON object only — no fences, no preamble.
```

3. Parse the response (strip fenced blocks defensively) and collect per-shot plans into `remix_plan.json`. Shot IDs that fail 3 attempts are recorded in `failed_shots` and skipped.

**Quality Gate:**
- Every shot plan has non-empty `nano_banana_prompt`, `veo_prompt`, and a `duration_seconds` in {4, 6, 8}.
- `shot_index` is force-corrected to match the manifest ID before saving.

**Output checkpoint:** `STATE_ANALYSE_COMPLETE`
- `./work/remix_plan.json`

---

## Step 3: REGENERATE (Nano Banana 2 Edit)

**Script:** `scripts/regenerate.py`

**Actions:**
1. Load `remix_plan.json`.
2. For each shot, upload the original keyframe via `higgsfield_client.upload_file()`.
3. Call `higgsfield_client.subscribe(IMAGE_EDIT_MODEL, arguments={...})` with:
   - `images_list`: `[original_keyframe_url]` (plus the hero reference URL once the first shot completes — see below).
   - `prompt`: the shot's `nano_banana_prompt`.
   - `aspect_ratio`: 16:9, 9:16, or 1:1 inferred from the source.
   - `resolution`: `"2K"` by default (configurable via `HF_IMAGE_RESOLUTION`; valid values `"1K"` / `"2K"` / `"4K"` — case-sensitive uppercase K).
4. The SDK handles polling internally — `subscribe()` blocks until a terminal status.
5. Download the result image to `./work/regen_keyframes/shot_NNN.png`.
6. Process shots sequentially with a 2 s courtesy delay.

### Character consistency — hero reference

Nano Banana 2 Edit accepts up to 14 images in `images_list`. To keep character identity stable across independently regenerated shots:

1. Regenerate shot 0 normally (`images_list=[source_keyframe]`).
2. Capture its output URL as the **hero reference** and persist it to `remix_plan.json`.
3. For every subsequent shot, pass `images_list=[source_keyframe, hero_reference]`.

The first generated frame becomes the visual contract for character appearance. This is less strict than Higgsfield's Soul ID (which requires ~20 training photos and a separate model) but works entirely within the Nano Banana 2 call and costs no extra credits.

**Quality Gate:**
- Submission returns a valid image URL. IF not → up to 3 attempts with exponential backoff (15 s, 30 s).
- Downloaded image must be > 10 KB.

**Terminal status handling (SDK status classes, NOT exceptions):**
`subscribe()` may return a status dataclass on terminal non-success. Use `isinstance(result, higgsfield_client.NSFW)` — do NOT `try/except` the status classes. Only `HiggsfieldClientError` and `CredentialsMissedError` are exceptions.

**Failure Modes:**
| Failure | Detection | Recovery |
|---------|-----------|----------|
| Rate limit / transient | SDK raises `HiggsfieldClientError` | Retry with exponential backoff (up to 3 attempts) |
| NSFW | `isinstance(result, NSFW)` | Hard fail that shot; user must rephrase the prompt |
| Generation failed | `isinstance(result, Failed)` | Hard fail that shot; retry works sometimes (prompt ambiguity) |
| Download timeout | `requests.Timeout` | Fail shot; next run resumes with cached files intact |
| Character drift | visual review | Hero-reference pattern above; if still drifting, hand-edit `images_list` for the offending shots |

**Output checkpoint:** `STATE_REGENERATE_COMPLETE`
- `./work/regen_keyframes/shot_NNN.png` (one per shot)

---

## Step 4: GENERATE (Veo 3.1 I2V)

**Script:** `scripts/generate_video.py`

**Actions:**
1. Load `remix_plan.json`.
2. For each shot, upload the regenerated keyframe via `higgsfield_client.upload_file()`.
3. Call `higgsfield_client.subscribe(VIDEO_I2V_MODEL, arguments={...})` with:
   - `image_url`: the uploaded keyframe URL (singular, not a list).
   - `prompt`: the shot's `veo_prompt`.
   - `duration`: 4, 6, or 8 (integer seconds).
   - `resolution`: `"1080p"` by default (configurable via `HF_VIDEO_RESOLUTION`; valid `"720p"` / `"1080p"`).
   - `aspect_ratio`: matches source (16:9, 9:16, or 1:1).
4. The SDK handles polling — expect 1–5 minutes per clip.
5. Download the result to `./work/clips/shot_NNN.mp4`.
6. Process sequentially with a 5 s courtesy delay.

**Quality Gate:**
- FFprobe confirms the clip is playable (duration > 0.5 s, has a video stream).
- Duration within ±1.5 s of target (logs a warning beyond that; a zero-length clip fails the shot).
- Up to 3 attempts with exponential backoff (30 s, 60 s).

**Failure Modes:**
| Failure | Detection | Recovery |
|---------|-----------|----------|
| Content filter | `isinstance(result, NSFW)` | Rephrase `veo_prompt` in plan and re-run (resume skips completed shots) |
| Terminal failure | `isinstance(result, Failed/Cancelled)` | Retry; if persistent, simplify motion prompt |
| Wrong duration | FFprobe mismatch | Warn only — Veo occasionally trims |
| Character drift from keyframe | visual review | Prefer subtle motion prompts ("slow push" > "character turns") |

**Output checkpoint:** `STATE_GENERATE_COMPLETE`
- `./work/clips/shot_NNN.mp4` (one per shot)

---

## Step 5: ASSEMBLE

**Script:** `scripts/assemble.py`

**Actions:**
1. Collect clips in shot-index order.
2. Apply crossfade transitions via FFmpeg `xfade` (default 0.3 s; disable with `--crossfade=0`).
3. Write video-only intermediate to `./output/remix_video_only.mp4`.
4. IF `--with-audio` → re-mux the source audio stream over the assembled video (`-map` ensures we take Veo's visual + source's audio, never Veo's audio).
5. Encode with H.264 (CRF 18, `yuv420p`, `+faststart`). Drop audio if the source had none.
6. Write the final to `./output/remix_final.mp4`.

**Quality Gate:**
- FFprobe confirms the final file has a valid video stream with duration > 0.
- A warning (not a hard fail) if total duration drifts more than 20% from the source — Veo's duration quantisation causes small drift.

**Output checkpoint:** `STATE_ASSEMBLE_COMPLETE`
- `./output/remix_final.mp4`

---

## What a Junior Gets Wrong

1. **Treating SDK status classes as exceptions.** `higgsfield_client.NSFW`, `Failed`, `Cancelled`, `Queued`, `InProgress`, `Completed` are dataclasses used with `isinstance()`, not exceptions. Wrapping them in `try/except` catches nothing. The actual exception classes are `HiggsfieldClientError` and `CredentialsMissedError`.

2. **Guessing parameter casing.** Nano Banana 2 resolution is `"2K"` with a capital K, not `"2k"`. Veo resolution is `"1080p"` lowercase. These are specific — wrong casing fails validation.

3. **Confusing `image_url` with `images_list`.** Nano Banana 2 Edit takes `images_list` (array, up to 14). Veo 3.1 I2V takes `image_url` (single string). Swapping them fails validation.

4. **Extracting keyframes at shot boundaries instead of interior.** Frames at cut points are often blended/transitional. Extract at 30% into the shot, not frame 0.

5. **Sending the same generic prompt to every shot.** Each shot needs a prompt tailored to its specific composition, angle, and content — that's the whole point of Step 2.

6. **Ignoring Veo's duration quantisation.** Veo 3.1 only supports 4 s, 6 s, or 8 s clips. A 5.2 s source shot must map to 6 s. Don't try arbitrary durations — you'll get errors or truncated output.

7. **Not handling character consistency across shots.** Nano Banana drifts when regenerated independently. Use the hero-reference pattern (`images_list=[source, hero]`) or, for higher fidelity across a long video, train a Soul ID and switch to Soul I2I.

8. **Running all API calls in parallel.** Higgsfield rate-limits aggressively. Sequential with delays is slower but reliable. Only parallelise if you've confirmed your plan's concurrency limits.

9. **Forgetting that Veo's I2V may not replicate the keyframe exactly.** The clip interprets the image, not replicates it frame-for-frame. Prompt motion carefully — "camera slowly pushes in" preserves fidelity better than "character suddenly turns".

10. **Forgetting `-map` when re-muxing.** Without explicit stream maps, FFmpeg will grab whatever audio track it finds first — which may be the (usually silent) audio from Veo. Always `-map 0:v:0 -map 1:a:0`.

---

## Resume Logic

On failure or interruption, check the latest `STATE_*` checkpoint:

| Checkpoint | Resume from |
|-----------|-------------|
| `STATE_DECOMPOSE_COMPLETE` | Step 2 (Analyse) |
| `STATE_ANALYSE_COMPLETE` | Step 3 (Regenerate) |
| `STATE_REGENERATE_COMPLETE` | Step 4 (Generate) |
| `STATE_GENERATE_COMPLETE` | Step 5 (Assemble) |

Within Steps 3 and 4, resume is per-shot: existing output files that pass size/FFprobe validation are skipped. Delete a specific output file to force that shot to re-run.

To force a full re-run, delete the `work/` directory.

---

## Environment Variables

```
# Higgsfield auth (choose one):
HF_KEY="your-api-key-id:your-api-key-secret"
# OR (Paperclip-native format):
HF_API_KEY_ID=your-api-key-id
HF_API_KEY_SECRET=your-api-key-secret

# Claude for shot analysis:
# No ANTHROPIC_API_KEY required — uses the `claude` CLI available in the
# Paperclip environment.

# Optional overrides:
HF_IMAGE_MODEL=google/nano-banana-2/edit         # default; catalog slug may differ
HF_VIDEO_MODEL=google/veo/3.1/image-to-video     # default; catalog slug may differ
HF_PROBE_MODEL=bytedance/seedream/v4/text-to-image  # known-good model for auth test
HF_IMAGE_RESOLUTION=2K                           # 1K | 2K | 4K
HF_VIDEO_RESOLUTION=1080p                        # 720p | 1080p
ANTHROPIC_MODEL=claude-sonnet-4-6                # analysis model (used by claude CLI)
```

Get Higgsfield credentials at https://cloud.higgsfield.ai/api-keys. Inspect the catalog for the authoritative model slugs if the defaults 404.

## Dependencies

```
pip install higgsfield-client scenedetect[opencv] anthropic requests
# FFmpeg must be installed system-wide
```

## Unverified Model Paths

`google/nano-banana-2/edit` and `google/veo/3.1/image-to-video` are educated guesses based on the slug shape of other Higgsfield models (e.g. `bytedance/seedream/v4/text-to-image`, `bytedance/seedance/v1/pro/image-to-video`). The only slug confirmed from the SDK README is `bytedance/seedream/v4/text-to-image`. If a default returns HTTP 404, inspect the catalog on https://cloud.higgsfield.ai and override with `HF_IMAGE_MODEL` / `HF_VIDEO_MODEL`. Run `python scripts/test_connection.py --probe-models` to exercise the configured slugs live.
