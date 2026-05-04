# Video Remix — SKILL.md

## Purpose

Transform an existing video into a new video with specified changes (character, scene, script, style) using a single high-level prompt. The pipeline decomposes the source into shots, regenerates keyframe visuals via Nano Banana 2 Edit, then generates new video clips via Veo 3.1 — all through the Higgsfield platform.

---

## Entry Conditions

- Source video file exists (MP4, MOV, or WEBM).
- High-level remix prompt provided by the user (e.g. "Change the character to a woman in her 30s, set the scene in Tokyo at night, keep the same pacing").
- Higgsfield CLI authenticated (`higgsfield account status` succeeds).
- `claude` CLI available on PATH (no `ANTHROPIC_API_KEY` required — uses Paperclip's native Claude session).
- FFmpeg and Python 3.10+ available on host.

Run `higgsfield account status` first. IF it fails with `Session expired` → ask the user to run `higgsfield auth login`.

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
2. For each shot, run the CLI to generate the edited keyframe:
   ```bash
   higgsfield generate create seedream_4_5 \
     --prompt "<nano_banana_prompt>" \
     --image ./work/keyframes/shot_NNN.png \
     --aspect_ratio 16:9 \
     --resolution 2k \
     --wait --json
   ```
   The CLI auto-uploads the local file. `--wait` blocks until terminal status. `--json` returns machine-readable output with the result URL.
3. Download the result image to `./work/regen_keyframes/shot_NNN.png`.
4. Process shots sequentially with a 2 s courtesy delay.

### Character consistency — hero reference

The image edit step accepts multiple reference images. To keep character identity stable across independently regenerated shots:

1. Regenerate shot 0 normally (single `--image` of the source keyframe).
2. Capture its output URL as the **hero reference** and persist it to `remix_plan.json`.
3. For subsequent shots, pass both the source keyframe and hero reference as `--image` flags.

The first generated frame becomes the visual contract for character appearance. This is less strict than Higgsfield's Soul ID (which requires ~20 training photos and a separate model) but works entirely within the edit call and costs no extra credits.

**Quality Gate:**
- CLI returns a valid result URL. IF not → up to 3 attempts with exponential backoff (15 s, 30 s).
- Downloaded image must be > 10 KB.

**Terminal status handling:**
The CLI exits with non-zero on failure/NSFW. Parse `--json` output for status field.

**Failure Modes:**
| Failure | Detection | Recovery |
|---------|-----------|----------|
| Rate limit / transient | CLI non-zero exit | Retry with exponential backoff (up to 3 attempts) |
| NSFW | JSON status `nsfw` | Hard fail that shot; user must rephrase the prompt |
| Generation failed | JSON status `failed` | Hard fail that shot; retry works sometimes (prompt ambiguity) |
| Download timeout | HTTP timeout | Fail shot; next run resumes with cached files intact |
| Character drift | visual review | Hero-reference pattern above; if still drifting, use Soul ID |

**Output checkpoint:** `STATE_REGENERATE_COMPLETE`
- `./work/regen_keyframes/shot_NNN.png` (one per shot)

---

## Step 4: GENERATE (Veo 3.1 I2V)

**Script:** `scripts/generate_video.py`

**Actions:**
1. Load `remix_plan.json`.
2. For each shot, run the CLI to generate the video clip:
   ```bash
   higgsfield generate create seedance_2_0 \
     --prompt "<veo_prompt>" \
     --start-image ./work/regen_keyframes/shot_NNN.png \
     --duration 6 \
     --aspect_ratio 16:9 \
     --wait --json
   ```
   The CLI auto-uploads the local file. `--wait` blocks until terminal (1–5 min per clip). `--json` returns machine-readable output.
3. Download the result to `./work/clips/shot_NNN.mp4`.
4. Process sequentially with a 5 s courtesy delay.

**Quality Gate:**
- FFprobe confirms the clip is playable (duration > 0.5 s, has a video stream).
- Duration within ±1.5 s of target (logs a warning beyond that; a zero-length clip fails the shot).
- Up to 3 attempts with exponential backoff (30 s, 60 s).

**Failure Modes:**
| Failure | Detection | Recovery |
|---------|-----------|----------|
| Content filter | JSON status `nsfw` | Rephrase `veo_prompt` in plan and re-run (resume skips completed shots) |
| Terminal failure | JSON status `failed` | Retry; if persistent, simplify motion prompt |
| Wrong duration | FFprobe mismatch | Warn only — model occasionally trims |
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

1. **Not using `--wait --json`.** Without `--wait`, the CLI returns immediately with just a job ID. You then need a separate `higgsfield generate wait <id>` call. Always pass `--wait` to block until terminal. Add `--json` for machine-readable output.

2. **Using the wrong media flag.** Image edit uses `--image`. Image-to-video uses `--start-image`. Swapping them fails validation. Check `higgsfield model get <model_id>` for accepted roles.

3. **Extracting keyframes at shot boundaries instead of interior.** Frames at cut points are often blended/transitional. Extract at 30% into the shot, not frame 0.

4. **Sending the same generic prompt to every shot.** Each shot needs a prompt tailored to its specific composition, angle, and content — that's the whole point of Step 2.

5. **Ignoring duration quantisation.** Video models only support specific durations (e.g. 4, 6, or 8 seconds). A 5.2 s source shot must map to 6 s. Check model constraints via `higgsfield model get <model_id>`.

6. **Not handling character consistency across shots.** Image-edit models drift when regenerated independently. Use the hero-reference pattern (pass both source + hero as `--image` flags) or train a Soul ID for higher fidelity.

7. **Running all CLI calls in parallel.** Higgsfield rate-limits aggressively. Sequential with delays is slower but reliable. Only parallelise if you've confirmed your plan's concurrency limits.

8. **Forgetting that I2V may not replicate the keyframe exactly.** The clip interprets the image, not replicates it frame-for-frame. Prompt motion carefully — "camera slowly pushes in" preserves fidelity better than "character suddenly turns".

9. **Forgetting `-map` when re-muxing.** Without explicit stream maps, FFmpeg will grab whatever audio track it finds first — which may be the (usually silent) audio from the video model. Always `-map 0:v:0 -map 1:a:0`.

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
# Higgsfield auth: managed by `higgsfield auth login` — no env vars needed.
# Run `higgsfield account status` to verify.

# Claude for shot analysis:
# No ANTHROPIC_API_KEY required — uses the `claude` CLI available in the
# Paperclip environment.

# Optional overrides:
ANTHROPIC_MODEL=claude-sonnet-4-6                # analysis model (used by claude CLI)
```

## Dependencies

```
pip install scenedetect[opencv] requests
# FFmpeg must be installed system-wide
# Higgsfield CLI must be installed and authenticated
# No anthropic SDK needed — analysis uses the claude CLI
```

## Model Discovery

Use `higgsfield model list --json` to browse available models and `higgsfield model get <model_id> --json` to inspect parameters. The pipeline defaults to `seedream_4_5` for image edit and `seedance_2_0` for image-to-video.
