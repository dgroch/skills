---
name: creative-video-transformation
description: transforms an existing video into a new video with specified changes — character, scene, script, style — from a single high-level prompt.
---

# Creative Video Transformation

## When to use this skill

When a user has a video and wants to transform any aspect of it (the talent, scene, products featured, styling) from a single high-level brief. The skill decomposes the video into shots and reassembles it using generative video AI.

## How it works

```
source.mp4 + "change the character to X, set in Tokyo"
  → shot decomposition (PySceneDetect)
  → per-shot analysis (Claude)
  → keyframe regeneration (Nano Banana 2 Edit via Higgsfield)
  → clip generation (Veo 3.1 I2V via Higgsfield)
  → assembly (FFmpeg)
  → remix_final.mp4
```

The pipeline is fully automated. Checkpoints allow resume on failure.

## Setup

### Dependencies

```bash
pip install higgsfield-client scenedetect[opencv] anthropic requests
```

FFmpeg must be installed system-wide:

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

### Environment variables

```bash
# Higgsfield auth — get keys from https://cloud.higgsfield.ai/api-keys
export HF_API_KEY="your-key"
export HF_API_SECRET="your-secret"
# OR combined:
export HF_KEY="your-key:your-secret"

# Claude for shot analysis
export ANTHROPIC_API_KEY="your-anthropic-key"

# Optional — override defaults if the model paths don't resolve
export HF_IMAGE_MODEL="google/nano-banana-2/edit"
export HF_VIDEO_MODEL="google/veo/3.1/image-to-video"
export HF_IMAGE_RESOLUTION="2K"       # 1K | 2K | 4K (case-sensitive)
export HF_VIDEO_RESOLUTION="1080p"    # 720p | 1080p
export ANTHROPIC_MODEL="claude-sonnet-4-6"
```

### Pre-flight check

Run this first to validate everything is installed and credentials work:

```bash
python scripts/test_connection.py
```

To additionally test that the configured model paths resolve against the Higgsfield catalog (consumes a small amount of credits):

```bash
python scripts/test_connection.py --probe-models
```

## Usage

```bash
python scripts/remix.py <source_video> "<remix prompt>" [--with-audio] [--crossfade 0.3]
```

### Example

```bash
python scripts/remix.py input.mp4 \
  "Change the character to a Japanese woman in her 30s. Set every scene in Tokyo at night with neon lighting. Keep the same pacing and camera framing." \
  --with-audio
```

Output lands at `./output/remix_final.mp4`.

## Flags

| Flag | Purpose |
|------|---------|
| `--with-audio` | Overlay the source video's audio track onto the final output |
| `--crossfade <seconds>` | Crossfade duration between shots (default 0.3 s; set 0 to disable) |

## Pipeline stages

| Step | Script | Output |
|------|--------|--------|
| 1. Decompose | `decompose.py` | `work/keyframes/`, `work/shots_manifest.json` |
| 2. Analyse | `analyse.py` | `work/remix_plan.json` |
| 3. Regenerate | `regenerate.py` | `work/regen_keyframes/` |
| 4. Generate video | `generate_video.py` | `work/clips/` |
| 5. Assemble | `assemble.py` | `output/remix_final.mp4` |

You can run any step independently to iterate on it without redoing the rest.

## Resume on failure

The pipeline writes a checkpoint after each stage. Re-running `remix.py` with the same arguments skips completed steps and resumes where it failed. Within Steps 3 and 4, resume is per-shot — existing valid files are kept.

To force a full re-run, delete the `work/` directory. To re-run a single shot, delete its output file in `work/regen_keyframes/` or `work/clips/`.

## File structure

```
creative-video-transformation/
├── SKILL.md                       # Methodology + failure modes + what juniors get wrong
├── README.md                      # This file
└── scripts/
    ├── remix.py                   # Main runner with resume support
    ├── config.py                  # Shared helpers, paths, model IDs
    ├── decompose.py               # PySceneDetect + FFmpeg keyframe extraction
    ├── analyse.py                 # Claude expands remix prompt per shot
    ├── regenerate.py              # Nano Banana 2 Edit via higgsfield-client
    ├── generate_video.py          # Veo 3.1 I2V via higgsfield-client
    ├── assemble.py                # FFmpeg concat with crossfades
    └── test_connection.py         # Pre-flight: binaries, imports, auth, model paths
```

## Costs

Rough estimate per shot (based on Higgsfield pricing as of early 2026):

| Step | Credits | Approx USD |
|------|---------|-----------|
| Nano Banana 2 Edit (2K) | ~8 | $0.50 |
| Veo 3.1 I2V (1080p, 4–8 s) | ~20–40 | $1.25–$2.50 |
| **Total per shot** | **~28–48** | **~$1.75–$3** |

A 30-second source video with 10 shots costs ~$20–30 to remix. Start with short test clips before running on long inputs. Set `HF_IMAGE_RESOLUTION=1K` while iterating to halve the image-edit cost.

## Known limitations

- **Veo duration quantisation.** Clips are forced to 4 s, 6 s, or 8 s. A 5.2 s source shot becomes 6 s — the final video's total length may drift ±20% from the source.
- **Character consistency across shots.** The pipeline uses a hero-reference pattern (first regenerated frame feeds forward as a second reference image for all later shots — Nano Banana 2 Edit accepts up to 14 images in `images_list`). For stricter identity locking across a long video, train a Higgsfield Soul ID on ~20 photos and swap the image step to Soul I2I.
- **Model path strings.** `google/nano-banana-2/edit` and `google/veo/3.1/image-to-video` are educated guesses. The only slug confirmed in the SDK README is `bytedance/seedream/v4/text-to-image`. If the SDK returns "model not found", inspect the catalogue at https://cloud.higgsfield.ai and override via `HF_IMAGE_MODEL` / `HF_VIDEO_MODEL`. Run `python scripts/test_connection.py --probe-models` to test.
- **Rate limits.** The pipeline runs sequentially with built-in delays (2 s between image gens, 5 s between video gens). Parallelising risks hitting Higgsfield's per-plan limits.
- **Audio.** The pipeline can overlay the source audio but does not generate new voiceover. For new dialogue, run a TTS pass after assembly.

## Troubleshooting

**"Model not found" / 404** — The configured model path isn't in the catalogue. Log into https://cloud.higgsfield.ai, find the correct slug, and set `HF_IMAGE_MODEL` or `HF_VIDEO_MODEL` accordingly.

**"401 Unauthorized"** — Check `HF_API_KEY` and `HF_API_SECRET` (or `HF_KEY`). Regenerate keys at https://cloud.higgsfield.ai/api-keys if needed.

**"402 Payment Required"** — Top up credits at https://cloud.higgsfield.ai/credits.

**Content filter triggered (result is an `NSFW` status instance)** — Check the offending shot in `work/remix_plan.json`, rephrase its `nano_banana_prompt` or `veo_prompt`, then re-run (resume skips completed shots).

**Zero shots detected** — Your source may be a single continuous shot. The script falls back to treating the whole video as one shot. For manual control, edit `work/shots_manifest.json` before running Step 2.

**Character drift between shots** — The hero-reference pattern usually handles this. If a specific shot still drifts, manually edit `work/remix_plan.json` to swap its reference image(s) and re-run just that shot (delete the existing regenerated keyframe first).

## How to extend

- **Different video models.** Swap Veo for Kling 3.0, Sora 2, or WAN 2.6 by changing `HF_VIDEO_MODEL` and adjusting the arguments dict in `generate_video.py` — each model has slightly different parameter names.
- **Different image models.** Nano Banana 2 Edit is used here for its in-context editing. For pure style transfer, swap to Higgsfield Soul I2I. For multi-reference character consistency with a trained identity, use Soul ID.
- **New voiceover.** After `assemble.py`, add a TTS step (ElevenLabs, OpenAI TTS) that generates audio from a script and mixes it over the video.
- **Batch mode.** Wrap `remix.py` in a loop for processing multiple source videos with different prompts. Use separate `work/` directories per run.

## References

- Higgsfield Python SDK: https://github.com/higgsfield-ai/higgsfield-client
- Higgsfield model catalogue: https://cloud.higgsfield.ai
- Veo 3.1 on Higgsfield: https://higgsfield.ai/veo3.1
- Nano Banana 2 on Higgsfield: https://higgsfield.ai/nano-banana-2
- PySceneDetect: https://www.scenedetect.com

## License

Internal use only. Part of Dan Groch's OpenClaw agent toolkit.
