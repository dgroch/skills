# Clone Rubric & Critic Prompt

This is the scoring instrument for the **Loop Engineering Layer** of `ai-video-clone-workflow`. Load it at every critique checkpoint (keyframe critic + final critic). The critic's job is to be a **harsh, evidence-citing reviewer** — not a cheerleader. The loop only converges if the critique is honest.

## How to run a critique

1. Gather evidence with tools — do NOT eyeball it:
   - **Visual dimensions** (1, 2, 3, 4, 5, 7): call `vision_analyze` on the candidate (keyframe image or a frame extracted from the final video) with the dimension's question.
   - **Audio dimension** (6): `ffprobe -show_streams <file>` to confirm an audio stream exists; listen-check the voiceover accent if needed.
   - **Technical dimension** (8): `ffprobe -show_streams -show_format <file>` for resolution, aspect ratio, codec, duration; visually scan scene boundaries for concat seams.
2. Score each dimension **0–5** using the anchors below.
3. **Cite the evidence** for every score (the vision_analyze observation or the ffprobe value). A score with no evidence is invalid.
4. Apply the gate: **every dimension must be ≥ 4 to pass.** Any dimension < 4 → write a revision note and loop.
5. Track iterations. After **3 failed iterations on the same stage**, STOP and escalate to the user with: the failing dimensions, the evidence, the candidates produced, and a recommended next step.

## Scoring anchors (0–5 per dimension)

### 1. Scene completeness
- **5** — Every scene/cut in the source is reproduced; scene count matches exactly.
- **4** — All major scenes present; a very minor beat merged or trimmed.
- **3** — One scene missing or collapsed.
- **0 (hard-fail)** — Single-scene clone of a multi-scene source.

### 2. Composition fidelity
- **5** — Each scene matches source framing, camera angle, lighting direction, and subject position.
- **4** — Close match; minor framing/lighting drift that doesn't read as a different shot.
- **3** — Recognisable but loose; angle or lighting noticeably off.
- **0 (hard-fail)** — Generic generation that ignores the source's shot structure.

### 3. Identity fit
- **5** — Talent is squarely from the approved casting matrix, suits the campaign/occasion, and has realistic flaws (skin texture, asymmetry).
- **4** — On-matrix and demographically appropriate; flaws present but subtle.
- **3** — On-matrix but a poor fit for the occasion, or borderline plastic.
- **0 (hard-fail)** — Off-list ethnicity (e.g. African-American instead of Sudanese/Somali/Nigerian), OR a smooth plastic AI actor with no flaws.

**Approved matrix:** Caucasian women (blonde or brunette) · Asian · sub-continental · African (Sudanese/Somali/Nigerian features, NOT African-American). Women are the default talent for flower content. Rotate groups across the content library.

### 4. Product fidelity
- **5** — Real Fig & Bloom product, WRAPPED (white tissue + black botanical line-art + cream satin ribbon with logo), matches the catalogue product, no vase.
- **4** — Clearly Fig & Bloom wrapped bouquet; minor wrap/ribbon detail drift.
- **3** — Wrapped bouquet but packaging doesn't match the catalogue product.
- **0 (hard-fail)** — Generic flowers, a glass vase / water container, or the wrong product entirely.

### 5. Captions
- **5** — Present, exact correct text, centered, lower-third (~72%), approved style, fully inside the safe zone.
- **4** — Present and correct; minor position/size nit.
- **3** — Present but mis-styled, slightly off-position, or a small text error.
- **0 (hard-fail)** — Missing captions (when the source had them), text runs off-screen, or wrong text. *(N/A if the source genuinely had no captions — score 5 and note it.)*

### 6. Audio
- **5** — Appropriate audio bed; voiceover accent correct (Australian where scripted); music on-brand and well-balanced.
- **4** — Audio present and acceptable; minor mix/level nit.
- **3** — Audio present but muddled, wrong levels, or off-accent.
- **0 (hard-fail)** — Silent clone when the source had audio. *(Exception: intentional `-an` handoff for the user to finish audio elsewhere — score per-intent and note it, do not auto-fail.)*

### 7. Brand polish
- **5** — Editorial, premium, unmistakably on-brand for Fig & Bloom; nothing cheap or gimmicky.
- **4** — On-brand; one small polish nit.
- **3** — Acceptable but generic; lacks editorial quality.
- **0 (hard-fail)** — Cheap/gimmicky elements shipped as final (e.g. `sonilo_music` cheap audio in a delivered cut).

### 8. Technical
- **5** — Correct 9:16, consistent resolution across scenes, clean concat, no artifacts or seams.
- **4** — Technically sound; a barely-perceptible nit.
- **3** — Minor visible issue (slight resolution mismatch, a soft seam).
- **0 (hard-fail)** — Resolution mismatch, visible concat seams, or file corruption.

## Critic prompt (paste into the critique step)

> You are a harsh creative director reviewing an AI video clone for Fig & Bloom. Score the candidate against all 8 rubric dimensions (Scene completeness, Composition fidelity, Identity fit, Product fidelity, Captions, Audio, Brand polish, Technical) on a 0–5 scale. For EACH dimension you MUST: (a) state the evidence you observed (cite the specific vision_analyze observation or ffprobe value), (b) give the score, (c) if below 4, give a specific, actionable fix the next generation pass can execute directly. Do not be generous — a 5 means flawless. Apply hard-fail rules (any listed hard-fail = 0). End with a verdict: PASS (all dimensions ≥ 4) or REVISE (list the failing dimensions). If this is the 3rd failed iteration, recommend escalating to the user instead of looping again.

## Revision note format (output of a failed critique)

```
[FAIL] Dimension N (<name>) — score X/5
Evidence: <what vision_analyze / ffprobe actually showed>
Fix: <concrete change for the next GENERATE pass — model, prompt edit, flag, ffmpeg param>
```

One block per failing dimension. The next GENERATE pass consumes these notes directly. Vague notes ("improve quality", "make it nicer") are invalid — they don't converge the loop.

## Iteration cap & escalation

- **MAX_ITERS = 3** per stage (keyframe stage and final stage are counted separately).
- On hitting the cap without a PASS, STOP. Send the user: the persistently-failing dimension(s), the evidence, the best candidate(s) so far, and a recommended decision (e.g. "accept with this known limitation", "switch model", "re-source the product photo"). Do not silently keep burning credits.
