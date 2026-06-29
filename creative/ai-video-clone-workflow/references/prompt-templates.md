# Prompt Templates (R1/R2/R3/R4 pre-wired)

Paste-ready GENERATE prompts for the clone pipeline. Fill `{curly}` slots from the beat sheet
and the Brand Profile. **Never describe a seeded (referenced) element — name it "this exact X"
(R1).** Keep the R2 ban-list out of every realism prompt. The CLI wrappers use the Hermes
`higgsfield` surface; for Cowork, map them through the runtime adapter (SKILL.md → Runtime
Adapter): `generate_image` / `generate_video` with `medias:[…]`.

---

## 1. Keyframe — branded product selfie (R1 + R2 + R5)

> Route to a text-strong model (`gpt_image_2`); pass a **clean, true-colour** product reference.
> Run a 2–4 model bake-off first if wordmark fidelity is uncertain.

**Prompt body (no wrap/wordmark description — R1):**
```
{talent_clause}, holding this exact {product} (reference image {N}) — reproduce the {product},
its wrapping, printed wordmark and ribbon exactly as shown; do not redraw, recolour or restyle.

Scene: {un-referenced scene — room, light, time of day, what she is doing}.
Pose/action: {pose, framing — e.g. arm-extended selfie, slightly awkward angle}.

Capture: a crystal-clear, perfectly-captured phone selfie of a real, imperfect, lived-in moment
— razor-sharp, well-exposed, true-colour, modern flagship phone, good low-light clarity. Natural
un-retouched skin texture, sharp and well-lit. Candid and unposed in a genuinely lived-in {room},
every detail in sharp focus.

Negatives: wrapped {product} only — no glass vase, no water container; no grain, no soft focus,
no blur, no haze, no vintage/lo-fi look, no blown highlights, no degraded image.
```

**CLI wrapper:**
```bash
PRODUCT_UUID=$(HOME=/opt/data/home higgsfield upload create /tmp/fab_products/osaka.jpg)  # clean, true-colour shot
HOME=/opt/data/home higgsfield generate create gpt_image_2 \
  --prompt "<prompt body above>" \
  --image "$PRODUCT_UUID" \
  --aspect_ratio 9:16 --quality high --resolution 2k \
  --wait --wait-timeout 120s
```

- `{talent_clause}` fixed spokesmodel → *"this exact woman (reference image 1)"*; casting-matrix
  actor → *"a {age} {identity} woman with natural, un-retouched skin (visible texture, slight
  asymmetry)"* — flaws on the **actor**, never on the **image** (R2).

---

## 2. Selfie spin — animate (R3 + R4)

> The phone travels WITH the body. Verified by the Motion Critic across every sampled frame.

```
Animate as a real handheld phone selfie. The phone stays in her {hand} hand the entire time; her
extended selfie arm stays visible in frame and her face stays framed as she turns — the room
sweeps behind her. Subtle natural handheld shake and micro-jitter; the only blur is the natural
motion blur of the genuine fast turn.

If a full 360 cannot keep the extended arm believable in every frame, do a ¾ turn instead.

Avoid: smooth gimbal, stabilised, tripod, cinematic dolly, slow-motion glide, the arm leaving
frame, the background warping or morphing.
```

**CLI wrapper (Kling 3.0 with native ambient):**
```bash
HOME=/opt/data/home higgsfield generate create kling3_0 \
  --prompt "<selfie-spin prompt above>" \
  --start-image "$UUID" --aspect_ratio 9:16 --duration 5 --sound on --mode std \
  --wait --wait-timeout 300s
```

---

## 3. Beat motion — quiet/hold or laugh/peak (R3 + R4)

```
Animate as authentic handheld phone footage: subtle shake, micro-jitter, slight sway and small
unstabilised reframing. {energy_clause}. The phone stays in one hand throughout; no action
requires the hand that is holding the phone (the second hand may {allowed_action}, but never both
hands at once).

Avoid: gimbal-smooth, stabilised, tripod, cinematic glide.
```

- **Quiet/hold beat** → `energy_clause` = *"minimal movement, almost still, a calm hold"*.
- **Laugh/peak beat** (the Step 0 emotional peak) → `energy_clause` = *"more movement and bounce,
  matching the laugh — the camera reacts to the moment"*.
- `allowed_action` → *"gesture briefly"*, *"tuck her hair"* — **never** *"hold the bouquet AND
  touch the flowers"* (frees no hand for the phone → R4 hard-fail, Dim 9).

---

## 4. End card (R6)

```
{brand} end card: restrained logo lockup ({logo_lockup}) on brand tan ({palette tan}); calm, no
hard sell; "{end_card tagline}" in brand voice.   # Fig & Bloom example: "For Moment Makers"
```

---

## 5. Caption copy (R7) — write before rendering

Reproduce the source caption's **format/function** (placement, hook type), but write **original
copy in the brand voice**; never lift a competitor's literal caption. Then render with
`scripts/generate_captions.py --style {A|B|C} --captions "line1|line2|..."`.

```
Source caption function: {hook | proof | CTA}, {placement}, {style A/B/C}.
Original copy (brand voice, banned-words clear): "{your line}"
```

---

## Reminders

- **R1:** describe only what is NOT in a reference (pose, scene, light, action). Pick a clean,
  true-colour reference; sanity-check its colour first; verify against the real product.
- **R2 ban-list:** grain, grainy, sensor noise, soft focus, hazy, blurry, faded, lo-fi, vintage,
  blown highlights, degraded.
- **R5 naming gotcha:** request `nano_banana_pro` (not `nano_banana_2`) for the strong engine;
  verify in the job record. Composite the real product for an exact hero still.
