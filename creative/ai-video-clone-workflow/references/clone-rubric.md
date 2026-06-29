# Clone Rubric & Critic Prompt

This is the scoring instrument for the **Loop Engineering Layer** of `ai-video-clone-workflow`. Load it at every critique checkpoint (keyframe critic + **motion critic** + final critic). The critic's job is to be a **harsh, evidence-citing reviewer** — not a cheerleader. The loop only converges if the critique is honest.

**12 dimensions. Pass = 4 on every dimension. Dims 9 (camera/hands logic) and 10 (capture realism) are HARD-FAIL — a frame that fails either is regenerated before a human sees it.** Dims 9 and 11 must be scored by the **Motion Critic on multi-frame evidence** (frames sampled across the whole clip via `scripts/sample_clip_frames.sh`), never a single still.

## How to run a critique

1. Gather evidence with tools — do NOT eyeball it:
   - **Visual dimensions** (1, 2, 3, 4, 5, 7, 10, 12): call `vision_analyze` on the candidate (keyframe image or a frame extracted from the final video) with the dimension's question. For **Dim 4** confirm the product was reference-seeded (R1), not described, and the reference was clean/true-colour. For **Dim 10** confirm the image is sharp/clean (not degraded to fake realism). For **Dim 12** confirm the Step 0 hook + emotional peak are reproduced.
   - **Audio dimension** (6): `ffprobe -show_streams <file>` to confirm an audio stream exists; listen-check the voiceover accent if needed.
   - **Technical dimension** (8): `ffprobe -show_streams -show_format <file>` for resolution, aspect ratio, codec, duration; visually scan scene boundaries for concat seams.
   - **Motion dimensions** (9, 11) — **Motion Critic, multi-frame:** run `scripts/sample_clip_frames.sh <clip> 0.5 <outdir>` and `vision_analyze` **every** sampled frame. Dim 9: the selfie arm is present and plausible in every frame; no frame leaves both hands busy or the camera unheld. Dim 11: no frame shows background warping; handheld energy reads across the sequence. A single-still pass is invalid for 9 & 11.
2. Score each dimension **0–5** using the anchors below.
3. **Cite the evidence** for every score (the vision_analyze observation, the ffprobe value, or the specific frame numbers for motion). A score with no evidence is invalid.
4. Apply the gate: **every dimension must be ≥ 4 to pass; any Dim 9 or Dim 10 hard-fail blocks delivery outright.** Any dimension < 4 → write a revision note and loop. For a Dim 9/11 motion fail, **regenerate the motion or fall back to a smaller move (¾/½ turn)** before assembly.
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
A "5" requires the **reference-seed method (R1)** and a **clean, true-colour reference**, not a
described one:
- **5** — Real product reproduced from the reference image via "this exact bouquet" prompting
  (the wrap/ribbon/wordmark were **named, not described**); a **clean, true-colour reference**
  was used (neutral/dark bg, no warm/pink cast); WRAPPED (no vase); wordmark legible and correct;
  matches the catalogue product.
- **4** — Clearly the real wrapped product; wordmark **near-exact, not pixel-perfect** (allowed —
  composite the real product in post if a hero still must be exact); minor wrap/ribbon drift.
- **3** — Wrapped bouquet but packaging doesn't match the catalogue product, **or** the prompt
  re-described the seeded element (caps this dimension at 3 even if it looks close — re-describing
  is what drifts colour/wordmark and must be fixed).
- **0 (hard-fail)** — Generic flowers, a glass vase / water container, the wrong product, a
  colour-drifted wrap (e.g. white → dusty pink, usually from a casted reference), or a garbled
  wordmark.

*(Fig & Bloom anchor for the example profile: white tissue + black botanical line-art + cream
satin ribbon with logo — but never type that into the prompt; seed it from the reference (R1).)*

**Source flower ≠ F&B SKU — the substitution decision.** When the source video features a flower Fig & Bloom doesn't actually sell (e.g. a giant pink **peony** bouquet, June 2026), do NOT generate the literal source flower — that hard-fails Dimension 4 (generic, non-shoppable). Instead, **substitute the closest real F&B SKU and surface the trade-off to the user with a single clear question** before generating. The closest-match call is made by pulling `figandbloom.com/products.json` and filtering on tags like `Pretty & Pink` / `Romantic`, then vision-checking candidates. The peony case resolved to the **Osaka** range (blush-pink roses + cream chrysanths + snapdragons reads as "lush pink bouquet" — the emotional beat is identical, the flower species swap is invisible to ~99% of viewers). **Use the largest size variant** for "wow"/reveal shots — Osaka's largest is the **Statement** ($255); there is no "Osaka Wow" SKU despite the user's phrasing, so confirm the actual variant name from `products.json` rather than trusting a colloquial size name. Seed the keyframe with the real product photo via `gpt_image_2 --image <uuid>`. A faithful substitution scores 4 (brand-faithful, shoppable); the literal source flower scores 0.

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

### 9. Camera / hands logic (R4) — ⛔ HARD-FAIL DIMENSION
Score on **multi-frame evidence** (Motion Critic) for any animated clip, not a single still.
- **5** — Phone plausibly in one hand throughout every shot **and** every sampled motion frame;
  selfie arm visible; no action frees or occupies both hands; a spin keeps the arm in frame
  (or correctly falls back to a ¾/½ turn).
- **4** — Logic holds; one borderline frame where the arm is briefly hard to read but still plausible.
- **3** — Ambiguous — a moment where it's unclear who's holding the camera.
- **0 (hard-fail)** — Any frame where nobody could be holding the camera: both hands busy (e.g.
  holding the bouquet AND touching the flowers), or the selfie arm vanished mid-move (reads as an
  external camera). **Regenerate before a human sees it.**

### 10. Capture realism (R2) — ⛔ HARD-FAIL DIMENSION
- **5** — Sharp, clean, well-exposed, true-colour modern-phone capture; all imperfection lives in
  the **world/subject** (lived-in room, un-retouched but sharp skin, candid moment).
- **4** — Clean and sharp; a slight softness that doesn't read as degraded.
- **3** — Slightly flat or muddy exposure/colour, but not deliberately degraded.
- **0 (hard-fail)** — Image grainy / soft-focus / blurry / faded / lo-fi / vintage / blown — i.e.
  the **image** was degraded to fake "realism". (The only allowed blur is the natural motion blur
  of a genuine fast movement.) **Regenerate before a human sees it.**

### 11. Motion authenticity (R3)
Score on **multi-frame evidence** (Motion Critic).
- **5** — Reads as real handheld (subtle shake, micro-jitter, slight drift); energy matches the
  beat (more on a laugh/peak, minimal on a quiet hold).
- **4** — Handheld feel present; energy a touch off the beat.
- **3** — Stiff or slightly floaty; weak handheld character.
- **0 (hard-fail)** — Gimbal-smooth / stabilised / cinematic glide, **or** warped/morphing
  background in a spin generated from a single keyframe.

### 12. Source essence (Step 0)
- **5** — The clone reproduces the **hook mechanism + emotional arc** named in Step 0 — the peak
  lands where it should and the hook earns the first seconds.
- **4** — Hook and arc present; the peak is slightly muted or mistimed.
- **3** — Surface shots reproduced but the emotional logic is thin.
- **0 (hard-fail)** — Generic generation that ignores *why* the source worked (no identifiable
  hook or arc) even if individual shots look fine.

## Critic prompt (paste into the critique step)

> You are a harsh creative director reviewing an AI video clone for the brand. Score the candidate against all 12 rubric dimensions (1 Scene completeness, 2 Composition fidelity, 3 Identity fit, 4 Product fidelity, 5 Captions, 6 Audio, 7 Brand polish, 8 Technical, 9 Camera/hands logic, 10 Capture realism, 11 Motion authenticity, 12 Source essence) on a 0–5 scale. For EACH dimension you MUST: (a) state the evidence you observed (cite the specific vision_analyze observation, ffprobe value, or — for Dims 9 & 11 — the specific sampled frame numbers), (b) give the score, (c) if below 4, give a specific, actionable fix the next generation pass can execute directly. Dims 9 and 10 are HARD-FAIL: if either fails, the candidate is blocked and must be regenerated, never surfaced. For an animated clip you MUST score Dims 9 & 11 from frames sampled across the whole clip, not one still. Do not be generous — a 5 means flawless. Apply hard-fail rules (any listed hard-fail = 0). End with a verdict: PASS (all dimensions ≥ 4, no hard-fail) or REVISE (list the failing dimensions). If this is the 3rd failed iteration, recommend escalating to the user instead of looping again.

## Revision note format (output of a failed critique)

```
[FAIL] Dimension N (<name>) — score X/5
Evidence: <what vision_analyze / ffprobe actually showed>
Fix: <concrete change for the next GENERATE pass — model, prompt edit, flag, ffmpeg param>
```

One block per failing dimension. The next GENERATE pass consumes these notes directly. Vague notes ("improve quality", "make it nicer") are invalid — they don't converge the loop.

## Iteration cap & escalation

- **MAX_ITERS = 3** per stage (keyframe stage, **motion stage**, and final stage are counted separately).
- On hitting the cap without a PASS, STOP. Send the user: the persistently-failing dimension(s), the evidence, the best candidate(s) so far, and a recommended decision (e.g. "accept with this known limitation", "switch model", "re-source the product photo"). Do not silently keep burning credits.
