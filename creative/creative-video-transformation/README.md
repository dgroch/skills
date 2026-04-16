# Video Remix

An OpenClaw skill that transforms an existing video into a new video with specified changes — character, scene, script, style — from a single high-level prompt.

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

# Optional — override default model paths if they don't resolve
export HF_IMAGE_MODEL="google/nano-banana-2/edit"
export HF_VIDEO_MODEL="google/veo/3.1/image-to-video"
```

## Usage

```bash
python scripts/remix.py <source_video> "<remix prompt>" [--with-audio]
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
| `--with-audio` | Overlay the original video's audio track onto the final output |
| `--crossfade <seconds>` | Crossfade duration between shots (default: 0.3s, set 0 to disable) |

## Pipeline stages

| Step | Script | Output |
|------|--------|--------|
| 1. Decompose | `decompose.py` | `work/keyframes/`, `work/shots_manifest.json` |
| 2. Analyse | `analyse.py` | `work/remix_plan.json` |
| 3. Regenerate | `regenerate.py` | `work/regen_keyframes/` |
| 4. Generate video | `generate_video.py` | `work/clips/` |
| 5. Assemble | `assemble.py` | `output/remix_final.mp4` |

You can run any step independently if you want to iterate on one stage without redoing the rest.

## Resume on failure

The pipeline writes a checkpoint after each stage. Re-running `remix.py` with the same arguments skips completed steps and resumes from where it failed. Within Steps 3 and 4, resume is per-shot — already-generated files are skipped.

To force a full re-run, delete the `work/` directory.

## File structure

```
video-remix/
├── SKILL.md                       # Methodology + failure modes + what juniors get wrong
├── README.md                      # This file
└── scripts/
    ├── remix.py                   # Main runner with resume support
    ├── config.py                  # Shared helpers, paths, model IDs
    ├── decompose.py               # PySceneDetect + FFmpeg keyframe extraction
    ├── analyse.py                 # Claude expands remix prompt per shot
    ├── regenerate.py              # Nano Banana 2 Edit via higgsfield-client
    ├── generate_video.py          # Veo 3.1 I2V via higgsfield-client
    └── assemble.py                # FFmpeg concat with crossfades
```

## Costs

Rough estimate per shot (based on Higgsfield pricing as of early 2026):

| Step | Credits | Approx USD |
|------|---------|-----------|
| Nano Banana 2 Edit (2K) | ~8 | $0.50 |
| Veo 3.1 I2V (1080p, 4-8s) | ~20-40 | $1.25-$2.50 |
| **Total per shot** | **~28-48** | **~$1.75-$3** |

A 30-second source video with 10 shots costs ~$20-30 to remix. Start with short test clips before running on long inputs.

## Known limitations

- **Veo duration quantisation.** Clips are forced to 4s, 6s, or 8s. A 5.2s source shot becomes 6s — the final video's total length may drift ±20% from the source.
- **Character consistency across shots.** Nano Banana 2 Edit preserves character identity well within a single generation but can drift across independent shot regenerations. For strict consistency, consider generating one "hero" keyframe first and using it as a second reference image in subsequent shots (the model supports up to 14 images).
- **Model path strings.** The default model paths (`google/nano-banana-2/edit`, `google/veo/3.1/image-to-video`) are educated guesses. If the SDK returns "model not found", check the current catalog at cloud.higgsfield.ai and override via env vars.
- **Rate limits.** The pipeline runs sequentially with built-in delays (2s between image gens, 5s between video gens). Parallelising would hit Higgsfield rate limits on most plans.
- **Audio.** The pipeline can overlay original audio but does not generate new voiceover. For new scripts/dialogue, run a separate TTS pass after assembly.

## Troubleshooting

**"Model not found"** — Your model path is wrong for the current catalog. Log into cloud.higgsfield.ai, find the correct slug, and set `HF_IMAGE_MODEL` or `HF_VIDEO_MODEL`.

**"401 Unauthorized"** — Check `HF_API_KEY` and `HF_API_SECRET` are set correctly. Regenerate keys at https://cloud.higgsfield.ai/api-keys if needed.

**"402 Payment Required"** — Top up credits at cloud.higgsfield.ai/credits.

**`NSFW` errors from the SDK** — The content filter rejected a prompt. Check `work/remix_plan.json` for the offending shot and rephrase its `nano_banana_prompt` or `veo_prompt`, then re-run (resume will pick up where it left off).

**Zero shots detected** — Your source video may be a single continuous shot. The script falls back to treating the whole video as one shot. For manual control, edit `work/shots_manifest.json` before running step 2.

**Character drift between shots** — See the "Known limitations" note above. Manually add a reference image URL to the `images_list` argument in `regenerate.py` for affected shots.

## How to extend

- **Different video models.** Swap Veo for Kling 3.0, Sora 2, or WAN 2.6 by changing `HF_VIDEO_MODEL` and adjusting the `arguments` dict in `generate_video.py` — each model has slightly different parameter names.
- **Different image models.** Nano Banana 2 Edit is used here for its in-context editing. For pure style transfer, swap to Higgsfield Soul I2I. For multi-reference character consistency, Flux Kontext Dev I2I supports up to 10 images.
- **New voiceover.** After `assemble.py`, add a TTS step (ElevenLabs, OpenAI TTS) that generates audio from a script and mixes it over the video.
- **Batch mode.** Wrap `remix.py` in a loop for processing multiple source videos with different prompts.

## References

- Higgsfield Python SDK: https://github.com/higgsfield-ai/higgsfield-client
- Higgsfield model catalog: https://cloud.higgsfield.ai
- Veo 3.1 on Higgsfield: https://higgsfield.ai/veo3.1
- Nano Banana 2: https://higgsfield.ai/nano-banana-2
- PySceneDetect: https://www.scenedetect.com

## License

Internal use only. Part of Dan Groch's OpenClaw agent toolkit.
