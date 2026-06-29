---
name: ai-video-clone-workflow
description: "Clone/replicate an existing video (competitor ad or your own winner) using AI actors. Multi-scene, native audio, captions, brand product integration. Reference-seed prompting, camera/hands + capture-realism hard-fail gates, a per-clip motion critic, and a Brand Profile + MCP/CLI adapter for multi-brand, multi-runtime use."
version: 3.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [creative, ai-video, ugc, seedance, higgsfield, ad-cloning, video-production, audio, captions, multi-scene, brand-profile, mcp]
---

# AI Video Clone Workflow

## Overview
End-to-end process for cloning/replicating an existing video (competitor ad, winning creative, or your own) using AI actors. Extracted from @ericdoesecom's Instagram reel tutorial (Seedance 2.0 method), extended with multi-scene support, native audio generation, caption burning, and brand product integration.

**Use cases:**
- Rip competitor winning ads and recreate them with your own AI UGC actor
- Create variations of your own winning ads for different customer avatars
- Clone a viral format but swap in Fig & Bloom product and branding

> **Brand- and runtime-agnostic.** This skill reads a **Brand Profile** (see "Brand Profile" near the end) instead of hardcoding Fig & Bloom, and speaks **named operations** mapped to either the Hermes `higgsfield` CLI or Cowork MCP tools (see "Runtime Adapter"). Every Fig & Bloom value below is the **shipped example profile**, not a hard dependency.

## 🎯 Prompting Rules (R1–R8) — read this first

These eight rules are the real IP of this skill. They exist because a full production run
spent ~7 review cycles fixing the *same class* of problems by hand: the model **drifted
from references we supplied**, **degraded the image to fake "realism,"** and **broke
physical/camera logic** a human notices instantly. Bake them into every GENERATE prompt and
critic gate so the first pass is already right. Each step and template references these by ID.

Two framing principles carry through everything:

1. **If you gave the model a reference, don't describe what's in it — name it ("this exact X") and let the reference carry it.** Describing a seeded element is what makes the model re-invent it.
2. **Real phone footage is a crystal-clear, perfectly-captured image of an *imperfect world* — not an imperfect (grainy/soft) image.** Put the imperfection in the scene and the moment, never in the image quality.

**R1 — Reference-seed prompting.** When a reference image is supplied for an element, **do
not describe that element's appearance in words** — name it: *"a woman holding **this exact
bouquet** (reference image 2) — reproduce the bouquet, its wrapping, printed wordmark and
ribbon exactly as shown; do not redraw, recolour or restyle."* Describe only what is NOT in a
reference (pose, scene, light, action). Pick a **clean, true-colour reference** — a warm/pink-cast
reference is what pushed a white wrap to dusty pink; prefer a neutral/dark-background product
shot and sanity-check its colour first. Keep negative constraints (e.g. "no glass vase") —
negatives still help; it's positive *re-description* of a seeded element that hurts.

**R2 — Realism = a perfect image of an imperfect world.** Prompt for a **crystal-clear,
razor-sharp, well-exposed, true-colour** modern-flagship-phone capture (including good
low-light clarity). **Ban these words** from realism prompts: grain, grainy, sensor noise,
soft focus, hazy, blurry, faded, lo-fi, vintage, "blown highlights," degraded. Put realism in
the **world**: candid unposed moment; a genuinely lived-in/messy room in sharp detail; natural
un-retouched skin texture (sharp, well-lit); authentic arm-extended selfie geometry. Tagline:
*"a crystal-clear, perfectly-captured phone selfie of a real, imperfect, lived-in moment."* The
only acceptable blur is the natural motion blur of genuine fast movement (e.g. a spin).

**R3 — Handheld motion.** Animation must read as a real handheld phone: subtle natural shake,
micro-jitter, slight sway/drift, small unstabilised reframing. **Match camera energy to the
beat** (more on a laugh/peak, minimal on a quiet hold). **Avoid:** smooth gimbal, stabilised,
tripod, cinematic dolly, slow-motion glide.

**R4 — Camera & hands logic (HARD).** In a selfie/handheld piece the **phone occupies one hand
at all times**, and for a selfie the **extended arm should be visible in frame**. Therefore
**no action may require a hand that is holding the phone** (no "touching the flowers" with the
second hand while already holding the bouquet → both hands busy → no one is filming). A **true
selfie spin** = the phone travels *with* the body: the extended arm stays in frame, the face
stays framed, the room sweeps behind. **If a full 360 can't keep the arm believable, fall back
to a ¾ or ½ turn** rather than ship the break.

**R5 — Model routing + bake-off.** For **branded products with printed text/wordmarks**, route
to **text-strong** image models. Bake-off winner: **GPT Image 2 (`gpt_image_2`)**, with GPT
Image 1.5 (`gpt_image`) close; `nano_banana_2` and `flux_kontext` lost on the wordmark. When
fidelity matters and you're unsure, **run a one-keyframe bake-off across 2–4 models and pick
the winner before committing the set.** Naming gotcha: request **`nano_banana_pro`** to get the
strong nano_banana_2 engine — requesting `nano_banana_2` by name can silently downgrade to
`nano_banana_flash`; verify the engine in the job record. A printed wordmark may be **very
close, not pixel-perfect**; for a hero still that must be exact, **composite the real product
image in post** rather than burning more generations.

**R6 — Brand voice & assets (parameterised).** Pull voice rules, banned words, palette, logo
lockup, talent reference, product source and music source from the **Brand Profile**, not
hardcoded. (Fig & Bloom example: AU English; no exclamation marks; no em-dashes; banned words
luxury/elevate/curate/curated/stunning/gorgeous and "blooms" as a noun; the free card is a
"gold-foiled greeting card," never "handwritten"; palette Clay `#D8CCBE`; "For Moment Makers"
stacked-logo close.)

**R7 — Caption = original, in-spirit.** Reproduce the source caption's **format and function**
(placement, style, the *kind* of hook), but **write original caption copy in the source's
spirit, in the brand's voice.** Only reproduce verbatim text that is the user's own — lifting a
competitor's literal caption is an originality/IP risk and usually off-brand.

**R8 — Licensed music only for the final.** Use a licensed source (Epidemic Sound) for final
brand audio, never cheap AI music (`sonilo_music`). Make the music **source** a Brand-Profile input.

## ⚡ Loop Engineering Layer (run this AROUND the whole pipeline)

**This skill is not a linear checklist — it is a critic-driven loop.** Do not hand the user a clone after a single pass. Wrap the entire Step 1→12 pipeline in a generate → critique → revise loop that runs until the output satisfies the rubric (or hits the iteration cap and escalates to the user).

### The Loop

```
1. PLAN      → deconstruct source, write the clone spec (scenes, casting, captions, audio)
2. GENERATE  → produce the candidate output for the current stage
3. CRITIQUE  → score the candidate against the RUBRIC using vision_analyze / ffprobe (be a harsh critic, not a cheerleader)
4. GATE      → every rubric dimension ≥ threshold?
                 YES → advance to next stage (or deliver if final)
                 NO  → write specific, actionable revision notes → GOTO 2
5. CAP       → if iterations on a stage exceed MAX_ITERS (default 3) without passing,
                 STOP and escalate to the user with the failing dimensions + candidates
```

**Three critic checkpoints are mandatory** (cheap to run, save credits):
- **Keyframe critic** (after Step 8, before animating): score each keyframe against its scene spec and rubric Dims 1–10 + 12. Never animate a keyframe that fails — animation multiplies the error and burns credits. **Dims 9 (camera/hands) and 10 (capture realism) are hard-fail — a both-hands-busy or degraded-"realism" frame is never surfaced to the user.**
- **Motion critic** (Step 9.5, between animate and concat): sample frames across each clip and score Dims 9 & 11 on **multi-frame evidence** — the worst breaks (a selfie arm vanishing mid-spin) appear only in motion. See Step 9.5.
- **Final critic** (after Step 12): score the assembled video against the full rubric before delivery.

### The Rubric

Score each dimension **0–5**. **Pass threshold = 4** on every dimension. Any dimension < 4 forces a revision loop. Full rubric with scoring anchors and the critic prompt lives in `references/clone-rubric.md` — load it at the critique step.

| # | Dimension | What "5" looks like | Hard-fail (auto 0) |
|---|---|---|---|
| 1 | **Scene completeness** | Every scene in the source is reproduced; count matches | Single-scene clone of a multi-scene source |
| 2 | **Composition fidelity** | Each scene matches source framing, angle, lighting, subject position | Generic generation that ignores source structure |
| 3 | **Identity fit** | Talent is from the approved casting matrix and suits the demographic | Off-list ethnicity, or AI-plastic actor with no flaws |
| 4 | **Product fidelity** | Real Fig & Bloom product, WRAPPED (no glass vase), packaging matches catalogue | Generic flowers, glass vase, or wrong product |
| 5 | **Captions** | Present, correct text, centered, lower-third, approved style, on-screen safe | Missing captions, off-screen, or wrong text |
| 6 | **Audio** | Has audio bed; voiceover accent correct; music on-brand (or intentionally `-an` for handoff) | Silent clone when source had audio (unless handoff) |
| 7 | **Brand polish** | Editorial, premium, on-brand; no cheap/gimmicky elements | `sonilo_music`-style cheap audio shipped as final |
| 8 | **Technical** | Correct 9:16, resolution consistent, clean concat, no artifacts/seams | Resolution mismatch, visible concat seams, corruption |
| 9 | **Camera/hands logic (R4)** ⛔ *hard-fail* | Phone plausibly in one hand throughout every shot AND motion; selfie arm visible; no action frees/occupies both hands | Any frame where nobody could be holding the camera (both hands busy; selfie arm vanished mid-move) |
| 10 | **Capture realism (R2)** ⛔ *hard-fail* | Sharp, clean, well-exposed, true colour; imperfection lives in the world/subject | Image grainy/soft/degraded to fake "realism" |
| 11 | **Motion authenticity (R3)** | Reads as real handheld; energy matches the beat | Gimbal-smooth/cinematic glide; or warped background in a spin |
| 12 | **Source essence (Step 0)** | The clone reproduces the hook mechanism + emotional arc, not just surface shots | Generic generation that ignores *why* the source worked |

**Dims 9 & 10 are hard-fail (auto-0): a frame that fails either is regenerated before a human sees it.** Dims 9 and 11 must be scored on **multi-frame evidence** by the Motion Critic (Step 9.5), not a single still. Dim 4 (Product fidelity) now requires the **reference-seed method (R1)** and a **clean reference** — see `references/clone-rubric.md`.

The critic must **cite evidence** for each score (the vision_analyze observation or ffprobe value), not just assert a number. A score without evidence is invalid — re-run the critique.

### Revision Notes Format

When a dimension fails, write a revision note the next GENERATE pass can act on directly:

```
[FAIL] Dimension 4 (Product fidelity) — score 2/5
Evidence: vision_analyze reports bouquet in a clear glass vase with water.
Fix: regenerate keyframe with gpt_image_2, pass the clean product photo as the reference,
     prompt "this exact bouquet (reference image N), reproduce exactly as shown", keep the
     negative "no glass vase, no water container" — do NOT describe the wrap/ribbon (R1).
```

Vague notes ("make it better") are not allowed — they don't converge. See `references/clone-rubric.md` for the full critic prompt that enforces this.

## 🎭 Casting / Identity Matrix (Fig & Bloom shopper demographics)

> This matrix is the **example profile's** `talent.mode: casting_matrix` config (see Brand
> Profile). Another brand supplies its own demographics or a `fixed_reference` spokesmodel.
> **"Flaws required" is global** regardless of profile.

When casting the AI talent, choose an identity that fits Fig & Bloom's shopper demographics. **Rotate across these groups** for a diverse content library — don't default to the same identity every time. Match the identity to the campaign/occasion where relevant.

**Approved identities:**

| Group | Specifics | Notes |
|---|---|---|
| Caucasian women | Blonde **or** brunette hair | The honey-blonde default — but actively rotate in brunette |
| Asian | East/Southeast Asian identities | |
| Sub-continental | South Asian / Indian subcontinent identities | |
| African | **Sudanese, Somali, Nigerian** features | **NOT** African-American identities — use African-born/East/West African features |

**Casting rules:**
- **Relevance first** — pick the identity that best suits the campaign, occasion, and demographic being targeted, not at random.
- **Diversity across the library** — rotate groups across clones so the content set reflects the full shopper base.
- **Flaws are mandatory regardless of identity** — skin texture, asymmetry, natural quirks (see Step 4). A plastic actor fails Dimension 3 of the rubric.
- **Women are the default talent** for Fig & Bloom flower content (matches the gifting-recipient demographic), unless the source format or campaign calls for a man.
- This matrix feeds **Dimension 3 (Identity fit)** of the rubric — a clone cast outside this matrix fails the critic.

## Tools Required
- **Gemini** (with custom Gem or manual prompting) — video deconstruction + actor replacement
- **Claude** — JSON scene description generation
- **Higgsfield CLI** — image generation, video generation with native audio, music generation, TTS
- **ElevenLabs API** (direct) — Australian accent voiceover generation
- **ffmpeg** — multi-scene concatenation, caption burning, audio mixing

## Critical Pitfalls

### Pitfall #1: Never Generate Without a Source Video
**The #1 failure mode is skipping source selection and deconstruction.** Generating a video from a text prompt alone — without downloading an actual viral video, extracting its frames, and deconstructing its composition — is **original generation, not cloning**. The user will immediately notice the difference: a clone reproduces the source video's shot structure, camera angles, lighting, text overlays, and emotional beats; a generic generation does none of this.

**Always follow the full pipeline:** select a real viral video → download it → extract frames → deconstruct shot-by-shot → build a beat sheet → generate keyframes that match the original → verify the keyframe matches → animate. If you don't have a source video URL yet, **stop and find one first** — do not generate from imagination.

### Pitfall #2: Single-Scene Generation of a Multi-Scene Source
**The #2 failure mode is generating only ONE keyframe and ONE video segment when the source video has multiple scenes/cuts.** A viral video often has 3-5 distinct scenes with different locations, camera angles, or actions. Generating a single 5-second segment only clones the opening shot — the rest of the video's narrative arc is lost.

**Always deconstruct ALL scenes.** Generate a keyframe per scene, animate each separately, then concatenate with ffmpeg. See the Multi-Scene Cloning section below.

### Pitfall #3: Missing Captions and Text Overlays
The original video likely has text overlays (captions, quotes, CTA text). These are part of the viral format — they must be reproduced. See the Caption Burning section.

### Pitfall #4: Silent Videos
The original video likely has audio — voiceover dialogue, face-to-camera speech, background music, or ambient sound. A silent clone is immediately noticeable. Generate audio WITH the video where possible (Kling 3.0 `--sound on`, Seedance 2.0 `--generate_audio true`, Veo 3.1 Lite `--generate_audio true`), and add voiceover/music in post-production where needed. See the Audio Generation section.

### Pitfall #5: Product Fidelity — wrong model AND describing a seeded reference
Two distinct mistakes wreck branded-product fidelity, and the run hit both:

1. **Wrong model.** `soul_cinematic` generates beautiful keyframes but does NOT faithfully
   reproduce branded products or printed wordmarks. Route branded product to a **text-strong**
   model — **GPT Image 2 (`gpt_image_2`)** won the bake-off (R5).
2. **Describing a seeded reference (R1).** Even with the real photo attached, *describing* the
   wrap ("white tissue with botanical illustrations", "blush-pink") makes the model re-invent
   it — wrong pattern, drifted colour, garbled wordmark. **Name it, don't describe it.**

**Fix: GPT Image 2 with the product photo as `--image`, and "this exact bouquet" prompting —
no wrap description.** Pick a clean, true-colour reference (R1):

```bash
# Upload a CLEAN, true-colour product photo (neutral/dark bg — not a warm/pink-cast shot)
PRODUCT_UUID=$(HOME=/opt/data/home higgsfield upload create /tmp/fab_products/osaka.jpg)

# Generate keyframe WITH the product reference — name it, do NOT describe the wrap
HOME=/opt/data/home higgsfield generate create gpt_image_2 \
  --prompt "<pose/scene/light only>. She holds this exact bouquet (reference image) — reproduce it, its wrapping, printed wordmark and ribbon exactly as shown; do not redraw, recolour or restyle. Wrapped bouquet only, no glass vase, no water container." \
  --image "$PRODUCT_UUID" \
  --aspect_ratio 9:16 \
  --quality high \
  --resolution 2k \
  --wait --wait-timeout 120s
```

**⚠️ GPT Image 2 `--medias` requires an array, not a string.** Passing `--medias "uuid"` fails with "Invalid types: medias should be array, got string". Use `--image <uuid>` (singular) instead — the CLI auto-wraps it correctly.

**Bake off when unsure (R5).** When wordmark fidelity matters, generate one keyframe across
2–4 candidates and pick the winner before committing the set. **Naming gotcha:** request
**`nano_banana_pro`** to actually get the strong nano_banana_2 engine — requesting
`nano_banana_2` by name can silently downgrade to `nano_banana_flash`; verify the engine in the
job record. `flux_kontext` lost on wordmarks (use it only to harmonise/edit an existing frame).
A wordmark may be near-exact, not pixel-perfect — **composite the real product** for an exact
hero still.

### Pitfall #5.5: Logo / Brand Mark on Non-Product Props (Aprons, Signage) — Seed, Don't Describe

**When the brand mark is on an apron, a wall sign, packaging, or any non-product prop,
the same "name it, don't describe it" rule applies — but you must seed with a real photo
of that specific branded item.** Describing the logo in text (even with "Fig & Bloom"
in the prompt) always produces a wrong font, wrong layout, or garbled letters.

**Fix: upload a real photo where the logo is large and clear, pass as `--image`, and say
"this exact logo."**

```bash
# Upload a real photo that clearly shows the apron logo
LOGO_UUID=$(HOME=/opt/data/home higgsfield upload create /tmp/fab_logo_seeds/apron_closeup.jpg)

higgsfield generate create gpt_image_2 \
  --prompt "...THE APRON LOGO MUST EXACTLY MATCH the logo shown in the reference image — this exact logo, same layout, same font, same style..." \
  --image "$LOGO_UUID" ...
```

Key rules:
- **Never describe the logo** (font, layout, colour, text content) — the model will render your description instead of copying the reference.
- **Do say "this exact logo"** — this instructs the model to copy the reference image's logo.
- **Pick a seed image where the logo is large and clear.** Search the Asset Library for close-up apron shots. A distant shot where the logo is a blurry white blob won't reproduce.
- **Logo seed vs environment seed:** if one photo captures both the logo and the environment, use it alone. If not, generate the keyframe with the logo seed as `--image` (logo fidelity is harder to fix in post than environment), then pass the keyframe itself as `--start-image` for animation.

### Pitfall #5.6: Action Mechanics — Read the Source Motion, Don't Assume

**The #1 action-fidelity failure: assuming the motion is a straight lift when it's actually
a prying/rocking motion.** Observed on the "Florists will understand this pain" reel (June 2026):
the source shows a florist separating two nested buckets stuck by vacuum seal. The natural
assumption is "she's lifting a heavy bucket." The actual motion is **prying** — the inner
bucket is tilted 10-15° off vertical, her hands are at **different heights** (one high, one
low) creating leverage, and she's **rocking the bucket sideways** to break the seal, not
straight-lifting.

**How to catch it:** when deconstructing the source, explicitly ask vision_analyze across
multiple frames: *"Is the object tilted or straight? Are the hands at different heights? Is
the motion prying/rocking or straight-lifting?"* The angle and hand-height differential are
visible in every frame but easy to miss if you only ask "what is she doing?"

**How to prompt it:** include the specific mechanics in both the keyframe prompt and the
animation prompt:
- "inner bucket TILTED AT A 15-DEGREE ANGLE — not straight vertical"
- "hands at DIFFERENT HEIGHTS on the rim — one hand high, one hand low — creating PRYING LEVERAGE"
- "ROCKING and TWISTING the bucket sideways to break the vacuum seal, not a straight lift"
- "pry one side up, then the other"

Generic motion language ("straining," "lifting," "pulling") produces a generic straight-lift.
Mechanics-specific language produces the correct motion.

## Step-by-Step Process

### Step 1: Source Your Video (or Concept Metadata)

Find the video you want to copy — a competitor's winning ad or one of your own performers.

**Fig & Bloom Creative Research database:** The Notion "Fig & Bloom Creative Research" database (public mirror: `https://abrupt-paneer-687.notion.site/351fdc24425f81be976ec417a1b9c365`) contains 30+ viral TikTok videos with engagement metrics (views, likes, shares), emotional drivers, and Fig & Bloom adaptation notes. Browse it to pick the highest-engagement video that fits the campaign.

**Notion API 404 fallback:** The Notion API may return 404 if the database isn't shared with the integration. In that case, open the public Notion page URL in the browser and extract rows via `browser_console` JavaScript:
```js
(() => {
  const all = document.querySelectorAll('*');
  const out = [];
  for (const el of all) {
    if (el.childElementCount === 0 && el.innerText && el.innerText.includes('TikTok')) {
      let parent = el;
      while (parent && parent.childElementCount < 3) {
        parent = parent.parentElement;
      }
      if (parent) {
        const t = parent.innerText;
        if (!out.includes(t) && t.length > 30) {
          out.push(t.substring(0, 600));
        }
      }
    }
  }
  return JSON.stringify(out);
})()
```
Each row contains the video title, category, creator handle, Local ID (TikTok video ID), views, likes, and adaptation notes. Construct the TikTok URL as `https://www.tiktok.com/@{handle}/video/{local_id}`.

**Alternative — work from concept metadata when the video isn't downloadable:** If the source video is behind an auth wall (TikTok login, Google Drive sign-in) or you already have a structured deconstruction, you can skip the Gemini video upload. The Fig & Bloom Paperclip routine populates a Notion "Ad Concepts" database (`data_source_id: cee45a98-19c8-4f46-98ae-97e4ab7dbe51`) with fields that map directly to the deconstruction output: Pattern Interrupt, Proof, Visual Direction, CTA, Format, Lens, Audience, and Occasion. Each row is a ready-made scene deconstruction — use it as the Gemini output and jump to Step 5 (Claude JSON). Steps 3-4 (first-frame screenshot + actor swap) become specification exercises rather than Gemini interactions: describe the first frame in detail from the Visual Direction field, and define the AI actor with flaws from imagination.

### Step 0: Source Essence Analysis (run before deconstruction — feeds everything)

Before deconstructing shots, write a short analysis of **why the video works as a whole** —
this is what should drive every creative choice. The shot-by-shot deconstruction (Step 2)
becomes the *execution* of this essence, not a substitute for it. Produce:

- **Hook** — what it is and *why* it earns the next few seconds (a framing? a question? a pattern interrupt?).
- **Emotional arc** — the beat-to-beat curve and where the **peak** is.
- **Pacing & structure**, **sound design**, **how the product is integrated** (presented vs lived-with), and the **close/CTA logic**.

> **🚦 GATE — do not generate keyframes until the hook mechanism and the emotional peak are explicitly named in writing.** This is the difference between a true clone and a generic generation. It is scored as **Dimension 12 (Source essence)** of the rubric. The keyframe on the peak beat carries the emotional payload — note which beat that is.

### Step 2: Deconstruct ALL Scenes (Gemini or frame-stepping)

Upload the video into Gemini and ask it to **deconstruct the video scene by scene**. This breaks down the ad into its component shots, transitions, pacing, and visual structure.

For best results, use a custom Gemini Gem purpose-built for video deconstruction. The original creator (@ericdoesecom) offers his Gem via DM on Instagram.

**When you can't upload to Gemini**, use **yt-dlp + ffmpeg + vision_analyze** (preferred when downloadable):

1. Download: `yt-dlp -o /tmp/original_viral.mp4 "https://www.tiktok.com/@{handle}/video/{local_id}"`
2. Get duration: `ffprobe -v quiet -print_format json -show_format /tmp/original_viral.mp4`
3. Extract frames at 2-second intervals:
```bash
mkdir -p /tmp/viral_frames
for t in 0 2 4 6 8 10 12 14 16; do
  ffmpeg -ss $t -i /tmp/original_viral.mp4 -vframes 1 -q:v 2 /tmp/viral_frames/frame_${t}s.png 2>/dev/null
done
```
4. Deconstruct each frame with `vision_analyze`:
> "Describe this frame in extreme detail: composition, camera angle, subject, text overlays (read ALL text exactly), lighting, mood, setting."

5. Build a **multi-scene beat sheet** — one entry per scene, not just one for the whole video:
```
Duration: Xs, 9:16 vertical
Scene 1 (0-Xs): [setting] | [action] | [camera] | [text overlay] | [audio]
Scene 2 (X-Ys): [setting] | [action] | [camera] | [text overlay] | [audio]
Scene 3 (Y-Zs): [setting] | [action] | [camera] | [text overlay] | [audio]
...
Lighting: [description]
Mood: [emotional tone]
Audio: [voiceover/music/ambient description]
```

**When the video isn't downloadable**, use **browser frame-stepping with vision OCR** — the same method from `media-content-workflows`:

1. `browser_navigate` to the TikTok video URL
2. Locate the `<video>` element and get duration: `(() => { const v = document.querySelectorAll('video')[0]; return {paused: v.paused, duration: v.duration}; })()`
3. Frame-step at 5-second intervals with IIFE-wrapped seeks (see the TikTok section in `media-content-workflows` for exact code patterns)
4. After each seek, call `browser_vision` with: *"Focus ONLY on the vertical TikTok video. What do you see? Who is in frame, what are they doing? Read ALL text overlays exactly."*
5. Record scene, timestamp, visual content, text overlays, and function (hook/proof/CTA) in a table

### Step 3: First Frame + Actor Spec

Take a screenshot of the first frame of the source video (or extract it via ffmpeg). This is the visual reference anchor.

**When working from concept metadata instead:** Write a detailed first-frame specification from the Visual Direction field — composition, subject, lighting, colour palette, actor appearance. This spec becomes the prompt for keyframe generation.

### Step 4: AI Actor Specification

**First, cast the identity from the Casting / Identity Matrix** (see the matrix near the top of this skill). Pick the group that fits the campaign/occasion and demographic — Caucasian (blonde or brunette), Asian, sub-continental, or African (Sudanese/Somali/Nigerian, NOT African-American). Rotate across groups over the content library rather than defaulting to the same identity. This choice is scored as Dimension 3 (Identity fit) of the rubric.

Then define the AI UGC actor with **flaws**. Imperfections (skin texture, asymmetry, natural movement quirks) are what make the AI actor look real rather than plastic. Do NOT skip this — smooth plastic-looking actors are the #1 giveaway and a hard-fail on Dimension 3.

### Step 5-6: JSON Scene Descriptions (Claude)

Create **JSON descriptions of every single scene**. Each scene entry should capture:
- Shot composition, actor action, environment, camera angle
- **Text overlay** (exact text, font style, placement) — if the original has captions, capture them
- **Audio** (voiceover script, ambient sound, music description) — if the original has audio, capture it
- Visual details in structured format

### Step 7: Brand Product Integration (Fig & Bloom)

When cloning for Fig & Bloom, the talent should hold/display actual Fig & Bloom product — not generic flowers. Source real product images from the live Shopify catalogue:

```bash
# Get product images from Shopify products JSON
curl -sL "https://figandbloom.com/products.json?limit=50" -o /tmp/fab_products.json
python3 -c "
import json
with open('/tmp/fab_products.json') as f:
    data = json.load(f)
for p in data.get('products', [])[:12]:
    title = p.get('title', '?')
    images = p.get('images', [])
    for img in images[:2]:
        print(f'{title}: {img.get(\"src\", \"\")}')"
```

Download product images:
```bash
curl -sL "<shopify_cdn_url>" -o /tmp/fab_products/<product>.jpg
```

Pass these as the **product reference image** on the keyframe generation call — and **do not
describe the packaging in words (R1).** Describing a seeded element (the wrap pattern, the
ribbon colour, the wordmark) is what makes the model **re-invent** it: in production, writing
"blush-pink tissue with botanical illustrations" drove a white wrap to dusty pink and garbled
the wordmark across three passes, *even with the real photo attached.* Instead, **name it**:

> a woman holding **this exact bouquet** (reference image N) — reproduce the bouquet, its
> wrapping, printed wordmark and ribbon **exactly as shown**; do not redraw, recolour or
> restyle. The bouquet is **wrapped, not in a glass vase** — no water container.

Describe only what is NOT in the reference: pose, scene, light, action. See
`references/prompt-templates.md` for the ready-to-paste product-keyframe template.

**Pick a clean, true-colour reference (R1).** A reference shot with a warm/pink cast is what
pushed the white wrap to pink — prefer a neutral or dark-background product shot and
**sanity-check the reference's colour before using it.** Verify the keyframe against the *real*
product, not against the prompt.

**⚠️ Keep the WRAPPED negative — it still helps.** Image models default to putting flowers in a
glass vase unless told otherwise. The negative constraint stays:

> wrapped bouquet only — **no glass vase, no water container.**

It is positive *re-description* of the seeded wrap that hurts; the negative constraint does not.
So: **reference + "this exact bouquet" + the no-vase negative**, and nothing describing the
wrap, ribbon, or wordmark appearance.

**Wordmark realism (R5):** route branded-product keyframes to a **text-strong** model
(`gpt_image_2`); a printed wordmark may land **near-exact, not pixel-perfect**, which passes —
if a hero still must be exact, **composite the real product image in post**.

### Step 8: Generate Keyframe PER SCENE

Generate a keyframe image for **each scene** in the deconstruction, not just scene 1.

**Model choice matters for product fidelity:**

| Model | Best For | Product Reference | Key Flag |
|---|---|---|---|
| `gpt_image_2` | **Primary** — branded product / printed wordmark (bake-off winner, R5) | YES — pass product photo as `--image <uuid>` | `--image`, `--quality high`, `--resolution 2k` |
| `gpt_image` (GPT Image 1.5) | Close second for branded product text | YES — `--image <uuid>` | `--image` |
| `nano_banana_pro` | Strong general 4K / character | YES — `--input_images` (array) | **request `nano_banana_pro`, NOT `nano_banana_2`** (silent downgrade to `nano_banana_flash`); verify engine in job record |
| `flux_kontext` | Harmonise / edit an existing frame only | n/a | **Lost on wordmarks — never for hero product text** |
| `soul_cinematic` | Composition-only (no branded product) | NO | `--aspect_ratio` |
| `text2image_soul_v2` | UGC/portrait style | NO | `--aspect_ratio` |

**Bake-off step (R5):** when product/branding fidelity matters and you're unsure, generate
**one** keyframe across 2–4 candidate models, score Dim 4, and commit the winner before
generating the rest of the set. Cheap insurance against a whole bad set.

> **🎞️ Realism callout (R2) — a perfect image of an imperfect world.** Every keyframe prompt
> must ask for a **crystal-clear, razor-sharp, well-exposed, true-colour** modern-flagship-phone
> capture (good low-light clarity included). The client rejected keyframes that chased "realism"
> by **degrading the image**. Put the imperfection in the **world**, not the pixels.
> - **Ban these words from the prompt:** grain, grainy, sensor noise, soft focus, hazy, blurry,
>   faded, lo-fi, vintage, "blown highlights," degraded.
> - **Realism lives in:** a candid unposed moment; a genuinely lived-in/messy room in sharp
>   detail; natural un-retouched skin texture (sharp, well-lit); authentic arm-extended selfie
>   geometry. Drop-in: *"a crystal-clear, perfectly-captured phone selfie of a real, imperfect,
>   lived-in moment."* This is scored as **Dim 10 (Capture realism) — a hard-fail.**

**For product-faithful keyframes (USE THIS FOR FIG & BLOOM):**

```bash
# Upload the real product photo first
PRODUCT_UUID=$(HOME=/opt/data/home higgsfield upload create /tmp/fab_products/osaka.jpg)

# Generate keyframe WITH product reference
HOME=/opt/data/home higgsfield generate create gpt_image_2 \
  --prompt "<scene description. Include 'THE BOUQUET MUST EXACTLY MATCH the reference product image'>" \
  --image "$PRODUCT_UUID" \
  --aspect_ratio 9:16 \
  --quality high \
  --resolution 2k \
  --wait --wait-timeout 120s
```

**For composition-only keyframes:**

```bash
HOME=/opt/data/home higgsfield generate create soul_cinematic \
  --prompt "<detailed scene description from beat sheet>" \
  --aspect_ratio 9:16 \
  --wait --wait-timeout 5m
```

Download and **verify each keyframe** with `vision_analyze` before proceeding:
> "Does this match: [list key compositional elements from the beat sheet for THIS scene]? Compare to the original viral video frame."

Only animate once ALL keyframes are confirmed to match their respective scenes.

### Motion & Camera Logic (R3 + R4) — apply to every animation prompt

Two of the costliest review breaks were *motion* errors a single keyframe can't reveal. Wire
these into every animate prompt (templates in `references/prompt-templates.md`):

- **R3 — Handheld feel.** Direct the motion as a real handheld phone: subtle natural shake,
  micro-jitter, slight sway/drift, small unstabilised reframing, with **energy matched to the
  beat** (more on a laugh/peak, minimal on a quiet hold). **Avoid:** smooth gimbal, stabilised,
  tripod, cinematic dolly, slow-motion glide. Floaty/cinematic motion fails **Dim 11**.
- **R4 — Camera & hands logic (HARD).** The phone occupies **one hand at all times**; for a
  selfie the **extended arm is visible in frame**. **No action may require the hand holding the
  phone.** The two classic breaks: (a) "touching the flowers" with the second hand while already
  holding the bouquet — both hands busy, no one's filming; (b) a full pirouette where the selfie
  arm disappears — reads as an external camera. A **true selfie spin** = the phone travels *with*
  the body (arm stays in frame, face stays framed, room sweeps behind). **If a full 360 can't
  keep the arm believable, fall back to a ¾ or ½ turn.** This is **Dim 9 — a hard-fail**, and the
  Motion Critic (Step 9.5) verifies it across *every* sampled frame, not just the keyframe.

### Step 9: Animate Each Scene (With Audio)

For each scene, upload the keyframe and generate video. Put **R3 + R4** (above) in every motion
prompt, then **choose your audio strategy:**

#### Audio Strategy A: Native Audio Generation (preferred for ambient + speech from prompt)

**Kling 3.0** with `--sound on` — generates video WITH audio (ambient + speech from prompt text):
```bash
HOME=/opt/data/home higgsfield generate create kling3_0 \
  --prompt "<scene description, include dialogue/accent instructions in the prompt>" \
  --start-image "$UUID" \
  --aspect_ratio 9:16 \
  --duration 5 \
  --sound on \
  --mode std \
  --wait --wait-timeout 300s
```

**Seedance 2.0** with `--generate_audio true` (default is True):
```bash
HOME=/opt/data/home higgsfield generate create seedance_2_0 \
  --prompt "<scene description, include dialogue/accent instructions>" \
  --start-image "$UUID" \
  --aspect_ratio 9:16 \
  --duration 5 \
  --resolution 1080p \
  --mode fast \
  --generate_audio true \
  --genre drama \
  --wait --wait-timeout 300s
```

**Veo 3.1 Lite** with `--generate_audio true`:
```bash
HOME=/opt/data/home higgsfield generate create veo3_1_lite \
  --prompt "<scene description>" \
  --aspect_ratio 9:16 \
  --duration 8 \
  --generate_audio true \
  --wait --wait-timeout 300s
```

#### Audio Strategy B: Australian Voiceover via ElevenLabs (for scripted dialogue)

When the talent speaks face-to-camera with a script, generate an Australian-accent voiceover with ElevenLabs API, then mix in post:

```bash
# Available Australian female voices (ElevenLabs):
# Arabella (aEO01A4wXwd1O8GPgGlF) - young, engaging
# Emma (56bWURjYFHyYyVf490Dp) - early 30s, sweet, conversational
# Sophia (LtPsVjX1k0Kl4StEMZPK) - bright, for narration/advertising

# Available Australian male voices:
# Charlie (IKne3meq5aSn9XLyUdCD) - deep, confident, energetic
# FB-Mark Rick (At3GWS0JVOaxoI8KPYt2) - professional
# FB-Mark Simon (cOEV2DrZBBGNLpE74kQu) - professional
# FB-Mark Hamish (LISP4EbsJ719q0dk83aw) - professional
# Logan (Fs34xrsEfYjvCaI7yezn) - generated
# Young Australian Male (6kovhaKzFo5hwd8vksaD)

ELEVEN_KEY=$(grep "^ELEVENLABS_API_KEY=*** /opt/data/.env | cut -d= -f2-)
curl -s -X POST "https://api.elevenlabs.io/v1/text-to-speech/aEO01A4wXwd1O8GPgGlF" \
  -H "xi-api-key: $ELEVEN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text":"<script>","model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.5,"similarity_boost":0.75,"style":0.4,"use_speaker_boost":true}}' \
  -o /tmp/voiceover.mp3
```

#### Audio Strategy C: Post-Production Voice Replacement

For lip-synced voice replacement on generated video, use Higgsfield `voice_change` or `dubbing` models. These require the Higgsfield API directly (CLI media input broken for these models — `input_video` needs an object, not a UUID):

```bash
HF_TOKEN=$(HOME=/opt/data/home higgsfield auth token)
# Upload the video to Higgsfield first
VIDEO_UUID=$(HOME=/opt/data/home higgsfield upload create /tmp/video.mp4)
# Call the API directly:
curl -X POST "https://api.higgsfield.ai/v1/generate" \
  -H "Authorization: Bearer $HF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"job_set_type":"voice_change","params":{"input_video":{"media_id":"'"$VIDEO_UUID"'","type":"media_input"},"voice_id":"aEO01A4wXwd1O8GPgGlF","voice_type":"preset"}}'
```

### Step 9.5: Motion Critic (per clip, between animate and concat) — MANDATORY

The keyframe critic and final critic miss errors that appear **only in motion** — the worst
break (a pirouette where the selfie arm vanished) lives *between* keyframes. After each clip is
animated, **sample frames across the whole clip and critique the motion before assembly.**

1. **Sample frames** every ~0.5–1 s with the helper:
   ```bash
   scripts/sample_clip_frames.sh /tmp/scene1_video.mp4 0.5 /tmp/motion_frames/scene1
   ```
2. **Score with multi-frame evidence** (cite specific frames — never a single still):
   - **Camera/hands logic (R4 / Dim 9):** the selfie arm is present and plausible in **every**
     sampled frame; no frame leaves both hands busy or the camera unheld.
   - **No background warping (Dim 11):** critical for spins generated from a single keyframe.
   - **Continuity:** same person / outfit / product / room across the clip.
3. **Gate:** if it fails, **regenerate the motion (or fall back to a smaller move — ¾/½ turn)
   before assembly.** Do not concat a clip with a Dim 9 break. The Motion Critic scores
   **Dimensions 9 and 11**; feed its revision notes straight into the re-animate prompt.

This is the third mandatory critic checkpoint (keyframe → **motion** → final).

### Step 10: Generate Background Music (when needed)

**⚠️ Pitfall: `sonilo_music` produces cheap-sounding music for premium brands.** AI-generated music from Higgsfield's `sonilo_music` model sounds generic, boppy, and not on-brand for editorial brands like Fig & Bloom. Daniel explicitly rejected it as "cheap and gimmicky." Use licensed music from **Epidemic Sound** instead when brand quality matters.

**Epidemic Sound** — MCP server at `https://www.epidemicsound.com/a/mcp-service/mcp`, auth via `MCP_EPIDEMIC_SOUND_API_KEY` (JWT in `.env`). Search for editorial-grade tracks (acoustic, warm, gentle, ambient). If the MCP server isn't configured in the current Hermes config, deliver the video without music (`-an` in ffmpeg) and let the user add licensed audio in their preferred tool (e.g., Claude, CapCut, Premiere).

When AI-generated music is acceptable (rough drafts, internal review only):

```bash
HOME=/opt/data/home higgsfield generate create sonilo_music \
  --prompt "Warm ukulele acoustic, light, cheerful, lo-fi beat, instrumental, suitable for a casual social media video about flowers" \
  --duration 5 \
  --wait --wait-timeout 120s
```

### Step 11: Concatenate All Scene Videos (concat-first approach)

**Concatenate FIRST, then mix audio and burn captions on the full video.** This is simpler than per-scene processing — 3 ffmpeg passes total instead of 3×N. The voiceover also needs padding to match total duration, which only works on the concatenated video.

```bash
cat > /tmp/concat_list.txt << 'EOF'
file '/tmp/scene1_video.mp4'
file '/tmp/scene2_video.mp4'
file '/tmp/scene3_video.mp4'
file '/tmp/scene4_video.mp4'
EOF

ffmpeg -y -f concat -safe 0 -i /tmp/concat_list.txt \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 192k \
  /tmp/clone_concat.mp4
```

**Important:** All scene videos must have the same resolution and format. If they differ, add `-vf scale=720:1280` before concatenating.

### Step 12: Pad Voiceover + Mix Audio + Burn Captions

#### Voiceover Padding (when voiceover is shorter than total video)

The voiceover will often be shorter than the concatenated video. Pad with silence to match:

```bash
# Example: voiceover is 10.6s, total video is 20s → pad 10s of silence
ffmpeg -y -i /tmp/voiceover.mp3 \
  -af "apad=pad_dur=10" \
  -t 20 \
  -c:a libmp3lame -b:a 128k \
  /tmp/voiceover_padded.mp3
```

#### Audio Mixing (ffmpeg `amix` on the full concatenated video)

Mix three audio sources: native ambient (from Kling/Seedance), voiceover (ElevenLabs), and music (Sonilo):

```bash
ffmpeg -y \
  -i /tmp/clone_concat.mp4 \
  -i /tmp/voiceover_padded.mp3 \
  -i /tmp/sonilo_music.m4a \
  -filter_complex "[1:a]volume=1.0[voice];[2:a]volume=0.15[music];[0:a]volume=0.3[ambient];[voice][music][ambient]amix=inputs=3:duration=first:dropout_transition=0[aout]" \
  -map "0:v" -map "[aout]" \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 192k \
  -shortest \
  /tmp/clone_mixed.mp4
```

Volume levels (tuned from production):
- **Voice: 1.0** — primary audio, must be clearly audible
- **Music: 0.15** — background level, should not compete with voiceover
- **Ambient: 0.3** — subtle ambience from native generation, adds realism

Use `duration=first` (not `shortest`) so the output matches the video length even if music is shorter.

#### Caption Burning — Three Approved Styles

> **✍️ Caption copy = original, in-spirit (R7) — decide the words before the mechanics.**
> Reproduce the source caption's **format and function** (placement, style, the *kind* of hook),
> but **write original copy in the brand's voice** (Brand Profile, R6). Only reproduce verbatim
> text that is the **user's own**. Copying a *competitor's* literal on-screen caption is an
> originality/IP risk and usually off-brand — and the brand's banned-words/voice rules still
> apply to whatever you write. This is scored under **Dimension 5 (Captions)** and **Dimension 8
> (Brand polish)**. The styles below are only the *rendering*; the copy is yours.

**⚠️ CRITICAL: Caption design is NOT optional.** Captions that are too large, left-aligned, or positioned without margin awareness will run off-screen and look amateurish. The `creative-design-discipline` skill governs this — apply its grid, margin, and safe-zone principles to video captions, not just static layouts.

There are **three approved caption styles** for Fig & Bloom video clones, modelled on Instagram Stories text styles (-approved by Daniel June 2026). Choose the style that best matches the source video's caption aesthetic.

**Shared design parameters for 9:16 video (720×1280 base):**

| Parameter | Value | Rationale |
|---|---|---|
| Font size | **28-32px** | Proportional to ~42-48px on 1080 base. Never 48px on 720px frame — it runs off-screen. |
| X position | `(w-text_w)/2` | **Always centered.** Never left-aligned (`x=30`) — long captions run off the right edge. |
| Font | DejaVu Sans Bold | `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf` |
| Comma escaping | Use `\\,` in drawtext text | Commas must be escaped or ffmpeg parses them as filter separators |

---

**⚠️ ffmpeg `drawtext` cannot produce rounded corners.** Its `box=1` draws a sharp-cornered rectangle. For the Instagram-style rounded-corner caption boxes Daniel approved, use **PIL (Python Imaging Library)** to generate transparent PNGs with `rounded_rectangle()`, then overlay them with ffmpeg. See `scripts/generate_captions.py` for a ready-to-run script that produces all three styles.

Use `uvx --from pillow python3 scripts/generate_captions.py` to run (Pillow isn't installed system-wide).

---

**Style A — Instagram Modern Dark** (default for UGC clones)

White bold text on a **fully opaque** dark rounded-rectangle background. Text centered within box, box centered in frame. Positioned as a **lower third** (~72% from top).

ffmpeg fallback (sharp corners, no rounding):
```bash
ffmpeg -y -i /tmp/clone_mixed.mp4 \
  -vf "drawtext=text='caption text':fontcolor=white:fontsize=28:x=(w-text_w)/2:y=h*0.72:box=1:boxcolor=black@1.0:boxborderw=16:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" \
  -c:a copy \
  -c:v libx264 -preset fast -crf 23 \
  /tmp/clone_final.mp4
```

PIL approach (rounded corners — preferred): use `BOX_COLOR=(18,18,18,255)` (fully opaque), `TEXT_COLOR=(255,255,255,255)`, `BOX_RADIUS=12`, `Y_POSITION=int(H*0.72)`.

---

**Style B — Instagram Typewriter** (Daniel's preferred style for Fig & Bloom)

Black bold text on a **fully opaque** white rounded-rectangle background. Text centered within box. Positioned as a **lower third** (~72% from top).

ffmpeg fallback (sharp corners):
```bash
ffmpeg -y -i /tmp/clone_mixed.mp4 \
  -vf "drawtext=text='caption text':fontcolor=black:fontsize=28:x=(w-text_w)/2:y=h*0.72:box=1:boxcolor=white@1.0:boxborderw=16:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" \
  -c:a copy \
  -c:v libx264 -preset fast -crf 23 \
  /tmp/clone_final.mp4
```

PIL approach (rounded corners — preferred): use `BOX_COLOR=(255,255,255,255)` (fully opaque), `TEXT_COLOR=(0,0,0,255)`, `BOX_RADIUS=12`, `Y_POSITION=int(H*0.72)`.

---

**Style C — Classic Meme**

White bold text with a dark outline, no background box. Closest to the original viral video's native TikTok caption style. Positioned lower-center, closer to the bottom (~80% from top).

```bash
ffmpeg -y -i /tmp/clone_mixed.mp4 \
  -vf "drawtext=text='caption text':fontcolor=white:fontsize=32:x=(w-text_w)/2:y=h-th-120:borderw=3:bordercolor=black@0.8:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" \
  -c:a copy \
  -c:v libx264 -preset fast -crf 23 \
  /tmp/clone_final.mp4
```

Key params: No `box=` flag (just text with outline). `borderw=3:bordercolor=black@0.8` for the dark outline. `fontsize=32` (slightly larger than Styles A/B because there's no background box). `y=h-th-120` positions lower in frame.

---

**Per-scene timed captions (all styles):**

When the script is rendered as captions instead of voiceover, use `enable='between(t,start,end)'` to show different text for each scene's time range. Time ranges must match scene boundaries (e.g., 0-5, 5-10, 10-15, 15-20 for four 5-second scenes).

Example with Style B (Typewriter — Daniel's preferred) and 4 scenes, using PIL-generated PNG overlays for rounded corners:

```bash
# Generate caption PNGs with rounded corners (preferred over ffmpeg drawtext)
uvx --from pillow python3 scripts/generate_captions.py --style B --captions "Me when I get flowers|Like, I literally cannot put them down|Still holding them everywhere I go|Honestly? Best gift ever"

# Overlay on concatenated video with per-scene timing
ffmpeg -y -i /tmp/clone_concat.mp4 \
  -i /tmp/caption_scene1.png -i /tmp/caption_scene2.png \
  -i /tmp/caption_scene3.png -i /tmp/caption_scene4.png \
  -filter_complex "[0:v][1:v]overlay=enable='between(t,0,5)'[v1];[v1][2:v]overlay=enable='between(t,5,10)'[v2];[v2][3:v]overlay=enable='between(t,10,15)'[v3];[v3][4:v]overlay=enable='between(t,15,20)'[vout]" \
  -map "[vout]" -an \
  -c:v libx264 -preset fast -crf 23 \
  /tmp/clone_final.mp4
```

Use `-an` to strip all audio when handing off to another tool (e.g., Claude) for final production.

ffmpeg `drawtext` fallback (sharp corners, no rounding) — Style B at `y=h*0.72`:
```bash
ffmpeg -y -i /tmp/clone_mixed.mp4 \
  -vf "drawtext=text='Me when I get flowers':fontcolor=black:fontsize=28:x=(w-text_w)/2:y=h*0.72:box=1:boxcolor=white@1.0:boxborderw=16:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:enable='between(t,0,5)'" \
  -c:a copy -c:v libx264 -preset fast -crf 23 /tmp/clone_final.mp4
```

**⚠️ Escaping commas:** Commas inside drawtext text must be escaped as `\\,` (e.g., `text='Like\\, I literally...'`). Without escaping, ffmpeg parses the comma as a filter separator.

**Font note:** DejaVu Sans Bold at `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`. Noto Color Emoji at `/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf` is available for emoji — but emoji rendering in ffmpeg drawtext can be unreliable; consider a PNG overlay for complex emoji.

**Script-to-caption conversion pattern:** When the voiceover is removed but the script should still be communicated, break the script into per-scene lines and burn them as timed captions using `enable='between(t,start,end)'`.

## Tool Chain (Visual)

```
Source Video
    ↓
STEP 0: Source Essence Analysis (hook + emotional peak) ──[GATE]──
    ↓
Gemini / frame-stepping (deconstruct ALL scenes — executes the essence)
    ↓
Cast identity from Casting Matrix / Brand Profile talent (relevance + rotation)
    ↓
Claude (JSON descriptions of every scene, including audio + text overlays)
    ↓
Source product images (Brand Profile) → pick a CLEAN, true-colour reference (R1)
    ↓
Per-Scene: Generate keyframe (R1 reference-seed, R2 realism, R5 model/bake-off)
    → [KEYFRAME CRITIC vs rubric Dims 1–10,12; Dims 9&10 hard-fail] → verify → animate (R3,R4)
    ↓
STEP 9.5: [MOTION CRITIC] sample frames, score Dims 9 & 11 ──[GATE]── pass? → concat : re-animate
    ↓
Audio: ElevenLabs voiceover (accent) + Epidemic Sound (licensed, R8) — never sonilo for final
    ↓
ffmpeg: Concatenate all scenes FIRST → then mix audio + burn captions ONCE (original copy, R7)
    ↓
[FINAL CRITIC vs full rubric] → pass? deliver public URL : revise & loop (cap 3, then escalate)
    ↓
Final clone video → host as a shareable URL / attach the file (never a widget reference)
```

## Higgsfield Video Model Comparison

| Model | Native Audio | Max Duration | Resolution | Key Params |
|---|---|---|---|---|
| Kling 3.0 | `--sound on` (yes) | 5s default (int) | 720p, 4k mode | `--start-image`, `--sound on/off`, `--mode std/pro/4k` |
| Seedance 2.0 | `--generate_audio true` (default!) | 5s (int) | up to 4k | `--start-image`, `--genre`, `--mode fast/std` |
| Veo 3.1 Lite | `--generate_audio true` | 4/6/8s | — | `--start-image`, `--generate_audio true` |
| Veo 3.1 | No explicit audio param | 4/6/8s | basic/high/ultra | `--input-image`, `--quality` |

**⚠️ Kling 3.0 `medias` array only accepts IMAGE roles (image, start_image, end_image).** Passing `--audio <uuid>` will fail with "medias.1.role: Input should be IMAGE/START_IMAGE/END_IMAGE". The `sound: on` parameter generates audio from the text prompt, NOT from a voice reference. To get a specific voice, use post-production `voice_change` or mix an ElevenLabs voiceover with ffmpeg.

## Higgsfield Audio Models

| Model | Purpose | Key Params |
|---|---|---|
| `text2speech_v2` | TTS with voice selection | `--model` (elevenlabs/minimax/seed_speech/vibe_voice/cozy_voice), `--voice_id`, `--voice_type` (preset/element) |
| `inworld_text_to_speech` | TTS via Inworld | `--prompt`, `--voice` |
| `seed_audio` | Seed Audio 1.0 | `--prompt`, `--format`, `--sample_rate`, `--speaker` |
| `sonilo_music` | AI music generation | `--prompt`, `--duration` |
| `voice_change` | Post-prod voice swap | `--input_video`, `--voice_id`, `--voice_type` (API direct — CLI broken) |
| `dubbing` | Dub to another language | `--input_video`, `--target_language` (18 languages) |

## Key Tips

- **Character flaws = realism.** Always create the AI actor with imperfections. Smooth plastic-looking actors are the #1 giveaway.
- **Multi-scene is non-negotiable.** If the source has 4 scenes, generate 4 keyframes, 4 video segments, and concatenate. A single-scene clone of a multi-scene video is a failed clone.
- **Capture text overlays during deconstruction — but rewrite the copy (R7).** Read ALL text exactly with `vision_analyze` so you can reproduce the caption's **format and function** (placement, style, hook type). Then **write original copy in the brand voice** — only reproduce verbatim text that is the user's own; never lift a competitor's literal caption.
- **Audio principle (user preference):** Generate audio WITH the video wherever possible — native audio is better than post-stitched. Always use `--sound on` (Kling) or `--generate_audio true` (Seedance/Veo) to get ambient sound in the raw video. Then layer scripted voiceover on top via ffmpeg for dialogue that needs accent control.
- **Kling `sound: on` reality check:** In production, Kling's native audio produces ambient sound (room tone, movement) and possibly speech from the prompt — but accent is NOT controlled and dialogue may be muddled. For scripted dialogue with a specific accent, always use ElevenLabs + ffmpeg mix. The native audio is still valuable as ambient bed — don't discard it.
- **Concat-first post-production:** Concatenate all raw scene videos FIRST, then mix audio and burn captions ONCE on the full video. Simpler than per-scene processing — 3 ffmpeg passes total instead of 3×N. See Steps 11-12.
- **Voiceover padding:** When voiceover duration < total video duration, pad with silence: `ffmpeg -i voiceover.mp3 -af "apad=pad_dur=10" -t 20 voiceover_padded.mp3`.
- **Script-wrapper pattern for long generations:** Higgsfield video generation (Kling 3.0, Seedance 2.0) takes 2-3 minutes and exceeds the terminal's 60s default timeout. Write each generation command to a bash script, then run it. For multiple scenes, start each script with `background=true` + `notify_on_complete=true` — this generates all scenes in parallel (~3min total instead of N×3min).
- **ElevenLabs key retrieval:** The key in `/opt/data/.env` may have quotes or trailing spaces. Clean it: `ELEVEN_KEY=$(grep "^ELEVENLABS_API_KEY=" /opt/data/.env | cut -d= -f2- | sed 's/^"//' | sed 's/"$//' | tr -d "'")`.
- **Seedance 2.0 `generate_audio` defaults to True** — you may already be getting audio without realising it. Check with `ffprobe -show_streams`.
- **Brand product imagery (R1)** — source real product photos from the brand's product source (Fig & Bloom example: Shopify CDN `figandbloom.com/products.json`), pick a **clean, true-colour** shot, and pass it as the keyframe **reference image**. **Name it ("this exact bouquet"), do NOT describe the packaging/flowers** — describing a seeded element makes the model re-invent it. Keep only the "no glass vase" negative.
- **Keyframe verification before animation** — call `vision_analyze` on every keyframe before spending generation credits on video.

## Execution Commands

See `references/higgsfield-execution-commands.md` for ready-to-run Higgsfield CLI commands (image generation, upload, video generation, download) with parameter notes and pitfalls.

See `references/clone-package-template.md` for the clone-package output template — use this structure when producing a clone package markdown file that captures all cognitive work so execution can resume later if generation tools are temporarily blocked.

## Real-World Execution Notes

Lessons from running this workflow end-to-end against TikTok videos sourced from a Notion creative research database.

### Finding Source Videos

The Fig & Bloom Paperclip routine populates a Notion **"Fig & Bloom Creative Research"** database (public mirror: `https://abrupt-paneer-687.notion.site/351fdc24425f81be976ec417a1b9c365`) with TikTok ad concepts. Each row has a **Local ID** field containing the TikTok video ID. Construct the direct TikTok URL as:

```
https://www.tiktok.com/@{creator_handle}/video/{local_id}
```

Extract creator handles and Local IDs from the Notion page via `browser_console` — the Notion table renders as DOM rows; query with `[class*="item"]` selectors and parse for `@handle` and numeric IDs.

**TikTok individual video URLs play in-browser without login.** TikTok *search* requires a login wall, but direct `/@handle/video/{id}` URLs render the video player immediately (muted autoplay). No popup to close (unlike Instagram reels).

### Deconstruction Without Gemini Upload

When you can't upload the source video to Gemini (auth, API limits, or the video is only viewable in-browser), use **browser frame-stepping with vision OCR** — the same method from `media-content-workflows`:

1. `browser_navigate` to the TikTok video URL
2. Locate the `<video>` element and get duration: `(() => { const v = document.querySelectorAll('video')[0]; return {paused: v.paused, duration: v.duration}; })()`
3. Frame-step at 5-second intervals with IIFE-wrapped seeks (see the TikTok section in `media-content-workflows` for exact code patterns)
4. After each seek, call `browser_vision` with: *"Focus ONLY on the vertical TikTok video. What do you see? Who is in frame, what are they doing? Read ALL text overlays exactly."*
5. Record scene, timestamp, visual content, text overlays, audio notes, and function (hook/proof/CTA) in a table

This produces the same scene-by-scene breakdown that Gemini would, without any upload or API call.

### Deconstruction via yt-dlp + ffmpeg + vision_analyze (preferred when downloadable)

When the source video is downloadable (TikTok direct URLs, Instagram reels), this method is **more reliable than browser frame-stepping** — you get actual frame images at precise timestamps for structured vision analysis, not viewport screenshots that may capture browser chrome or miss the video frame.

**Step 1 — Download the source video:**
```bash
yt-dlp -o /tmp/original_viral.mp4 "https://www.tiktok.com/@{handle}/video/{local_id}"
```

**Step 2 — Get duration and extract frames at 2-second intervals:**
```bash
ffprobe -v quiet -print_format json -show_format /tmp/original_viral.mp4
mkdir -p /tmp/viral_frames
for t in 0 2 4 6 8 10 12 14 16; do
  ffmpeg -ss $t -i /tmp/original_viral.mp4 -vframes 1 -q:v 2 /tmp/viral_frames/frame_${t}s.png 2>/dev/null
done
```

**Step 3 — Deconstruct each frame with `vision_analyze`:**

For each extracted frame, call `vision_analyze` with a structured question:
> "Describe this frame in extreme detail: composition, camera angle, subject, text overlays (read ALL text exactly), lighting, mood, setting."

**Step 4 — Build a MULTI-SCENE beat sheet:**

Record EACH scene separately — different settings, camera angles, or actions constitute different scenes:
```
Duration: Xs, 9:16 vertical
Scene 1 (0-Xs): [setting] | [action] | [camera] | [text overlay] | [audio]
Scene 2 (X-Ys): [setting] | [action] | [camera] | [text overlay] | [audio]
Scene 3 (Y-Zs): [setting] | [action] | [camera] | [text overlay] | [audio]
Lighting: [description]
Mood: [emotional tone]
Audio: [voiceover/music/ambient]
```

### Higgsfield as Unified Pipeline

The original workflow uses separate tools for image generation (ChatGPT), video generation (Seedance), and final output (Higgsfield). In practice, **Higgsfield CLI handles image AND video AND audio generation**:

| Original Step | Original Tool | Higgsfield Equivalent |
|---|---|---|
| Generate keyframe image | ChatGPT | `higgsfield generate create soul_cinematic --aspect_ratio 9:16` |
| Generate video | Seedance (separate) | `higgsfield generate create seedance_2_0 --start-image $UUID --generate_audio true` |
| Generate video with native audio | — | `higgsfield generate create kling3_0 --start-image $UUID --sound on` |
| Generate voiceover | — | `higgsfield generate create text2speech_v2 --model elevenlabs --voice_id <id>` |
| Generate background music | — | `higgsfield generate create sonilo_music --prompt "..." --duration 5` |
| Voice replacement | — | `higgsfield generate create voice_change --input_video <obj> --voice_id <id>` (API direct) |
| Final output | Higgsfield | Same — `--wait` returns a CloudFront MP4 URL |

### Keyframe Verification (critical — do this before animating)

After generating EACH keyframe image, **verify it matches the original video's composition for THAT scene** before spending video generation credits. A mismatched keyframe wastes a generation and produces a clone that doesn't look like the source.

Call `vision_analyze` on each generated keyframe with:
> "Describe this generated image. Does it match: [list key compositional elements from the beat sheet for THIS scene — setting, lighting, subject position, camera angle, aspect ratio]? Compare to the original viral video composition."

If the keyframe doesn't match, regenerate with an adjusted prompt before proceeding to video generation. Only animate once the keyframe composition is confirmed.

### Fig & Bloom Product Sourcing

Product images are available from the Shopify CDN. Fetch the products JSON and download images:

```bash
curl -sL "https://figandbloom.com/products.json?limit=50" -o /tmp/fab_products.json
python3 -c "
import json
with open('/tmp/fab_products.json') as f:
    data = json.load(f)
for p in data.get('products', [])[:12]:
    title = p.get('title', '?')
    images = p.get('images', [])
    for img in images[:2]:
        if img.get('src'):
            print(f'{title}: {img[\"src\"]}')"
```

Key products (as of June 2026): Osaka ($129), Marseille ($145), Broome ($127), Lucerne ($109), Genoa ($119), Pyrenees ($119), Monaco Pink ($79), Monaco White ($79).

Product photography style: clean studio shots, light blue-grey background, white surface, flowers in branded white tissue wrap with botanical line-art illustration, cream satin ribbon with "Fig & Bloom" logo.

### Brand-World Cloning via Semantic Search (Non-Product Scenes)

When the clone calls for **your real shop, staff, or workspace** — not a product — Shopify
product images won't help. Use the **Fig & Bloom Asset Library semantic search API** to find
real Manifest-backed photos of your workshop, staff in aprons, buckets, interiors, and
behind-the-scenes shots, then pass them as `--image` seeds to `gpt_image_2`. This grounds the
clone in your actual visual world instead of a generic studio.

**Asset Library API:**
- Base URL: `https://asset-library-u70t.onrender.com`
- Endpoint: `GET /api/search?q=<natural-language-query>&cursor=<offset>`
- Returns: `{ "results": [{ "id", "title", "url", "description", "mediaType", "driveLink" }], "nextCursor": ... }`
- Image URLs are Brand CDN (`brand-cdn.figandbloom.workers.dev`) — download with a browser User-Agent.
- Use concrete visual queries: "florist staff apron working", "workshop interior Sydney", "florist bucket black plastic flowers". Prefer `mediaType=image` with valid CDN `url`.

```bash
# Search the asset library
curl -sL "https://asset-library-u70t.onrender.com/api/search?q=florist+staff+apron+working" | python3 -m json.tool | head -20

# Download a seed image
curl -sL -H "User-Agent: Mozilla/5.0" "<cdn_url>" -o /tmp/fab_seeds/apron_closeup.jpg

# Upload to Higgsfield and use as --image seed
SEED_UUID=$(HOME=/opt/data/home higgsfield upload create /tmp/fab_seeds/apron_closeup.jpg)
higgsfield generate create gpt_image_2 --image "$SEED_UUID" ...
```

**When to use this vs Shopify products:** use Shopify `products.json` for bouquets and
wrapping (product fidelity). Use the Asset Library for workshop spaces, staff in aprons,
buckets, shelves, and behind-the-scenes context (environment fidelity). For a clone that
needs both, generate the keyframe with the logo/brand seed as `--image` (hardest to fix in
post), then use the keyframe itself as `--start-image` for animation.

### Clone Package Output Pattern

When generation tools are blocked (auth expired, API key not configured), produce a **clone package markdown file** containing:
- The scene-by-scene deconstruction (table format, ALL scenes)
- The AI actor specification (with realistic flaws)
- The JSON scene descriptions (Claude step)
- Per-scene keyframe image generation prompts (ready to paste)
- Per-scene video generation commands (ready to paste, with audio flags)
- The voiceover script withElevenLabs voice ID
- The sonilo_music prompt for background music
- The ffmpeg caption + audio mixing + concatenation commands
- A status table showing what's complete vs. blocked

This lets execution resume later when auth is restored — all cognitive work is captured and the remaining steps are copy-paste commands.

### Auth Prerequisites

**Higgsfield CLI** credentials live at `/opt/data/home/.config/higgsfield/credentials.json`. The CLI uses `HOME` to locate them — always prefix commands:
```bash
HOME=/opt/data/home higgsfield account status
```

If credentials are expired, re-auth requires browser interaction: `HOME=/opt/data/home higgsfield auth login`. See `references/higgsfield-execution-commands.md` for the background auth flow method.

**ElevenLabs API** key is in `/opt/data/.env` as `ELEVENLABS_API_KEY`. The value may have quotes or trailing spaces — clean it:
```bash
ELEVEN_KEY=$(grep "^ELEVENLABS_API_KEY=*** /opt/data/.env | cut -d= -f2-)
curl -s "https://api.elevenlabs.io/v1/voices" -H "xi-api-key: $ELEVEN_KEY"
```

**Higgsfield API token** (for voice_change/dubbing models that need direct API access):
```bash
HF_TOKEN=$(HOME=/opt/data/home higgsfield auth token)
```

## Brand Profile (multi-user — de-hardcode the brand)

This skill reads a **Brand Profile** instead of hardcoding any brand. **Every Fig & Bloom value
in this skill is the shipped example profile** (`references/brand-profile.example.md`), not a
hard dependency — swap the profile and the pipeline runs unchanged for another brand.

**Required minimum to run:** a source video URL/handle + a product/asset reference source + a
logo + voice rules. Everything else has defaults.

```yaml
brand:
  name: "Fig & Bloom"            # example profile ships as references/brand-profile.example.md
  voice:
    language: en-AU
    banned_words: [luxury, elevate, curate, curated, stunning, gorgeous, "blooms(noun)"]
    rules: ["no exclamation marks", "no em-dashes"]
    tone: "warm, considered, plain"
  product_reference:
    source: "shopify_products_json | url | asset_library | uploaded_files"
    pick_rule: "choose a clean, true-colour shot that shows packaging/branding clearly (R1)"
  talent:
    mode: "casting_matrix | fixed_reference"
    fixed_reference_id: "<optional Soul/model ref>"   # e.g. brand spokesmodel
    flaws_required: true          # global: actor flaws ON, image degradation OFF (R2)
  visual_identity:
    palette: ["#14110F", "#FFFFFF", "#D8CCBE"]
    logo_lockup: "<asset path/url>"
    end_card: "restrained logo, brand tan, no hard sell"
  caption:
    default_style: "B"            # A/B/C as today
    original_copy_required: true  # R7
  music:
    source: "epidemic_sound_mcp"  # licensed only; never cheap AI music for final (R8)
  format:
    aspect: "9:16"
    beat_durations: "match source pacing"
    total_target_s: 15
  delivery:
    host: "public_url"            # MCP media_upload or brand CDN
    variants: ["captioned", "clean_no_caption", "1:1", "4:5"]
  run:
    one_shot: false               # true skips the human storyboard checkpoint if gates pass
```

The **Casting / Identity Matrix** is the `talent.mode: casting_matrix` config — a brand can
supply its own demographics or a `fixed_reference` spokesmodel. **"Flaws required" stays
global** (actor flaws on; image degradation off, R2).

**Storyboard checkpoint (cut iterations).** Before the expensive animation step, present **a
keyframe for every beat as one set** for sign-off — single-frame approvals waste cycles; one
approval covers the look, product fidelity and casting. The checkpoint is **configurable**: on
by default; `run.one_shot: true` skips straight through **if the automated gates pass.**

## Runtime Adapter (portability — CLI today, MCP elsewhere)

This skill was written for the **Hermes CLI** (`HOME=/opt/data/home higgsfield ...`,
`/opt/data/.env`, ElevenLabs via curl). In **Cowork** and for most users those capabilities are
**MCP tools** with no `higgsfield` CLI and no `/opt/data`. Speak **named operations**, then bind
them to whichever runtime you're on (like `reference-browser-operator` does for browsers):

| Operation | Hermes CLI (today) | Cowork MCP (add) |
|---|---|---|
| Import a reference image | `higgsfield upload create` | `media_import_url` → media id |
| Generate keyframe | `higgsfield generate create gpt_image_2 --image ...` | `generate_image(model, aspect_ratio, medias:[ids])` |
| Pick the best model | (model table + bake-off) | `models_explore(action:recommend)` + one-frame bake-off |
| Animate | `higgsfield generate create kling3_0 --start-image` | `generate_video(model, medias:[{value, role:"start_image"}], duration, aspect)` |
| Inspect / repull a result | `--wait` URL | `show_generations` / `job_display` (rawUrl on CloudFront) |
| Music | ElevenLabs/curl + sonilo | **Epidemic Sound MCP** (licensed) |
| Assembly | ffmpeg | ffmpeg in workspace bash; **PIL** for rounded caption PNGs |
| Host final for the user | CloudFront | `media_upload` → public CloudFront URL (or brand CDN) |

**Adapter notes (learned this run):** the assembled file lives in the session sandbox — host it
via `media_upload` to hand the user a **public URL**. The user may be on a **remote client that
can't see desktop widgets**, so **always return a shareable URL / attach the file**, never a
widget reference. All ffmpeg recipes (concat-first, `amix` levels, `+faststart`, comma-escaping,
PIL rounded captions) are correct and runtime-agnostic — keep them. The concrete Hermes CLI
surface lives in `references/higgsfield-execution-commands.md`.

## Source
- Original tutorial: @ericdoesecom Instagram reel (`/reel/DaA5_8ngiZ9/`)
- Hashtags from source: #ecommerce #dropshipping #aiugc #metaads #seedance
- Reel caption: "This is actually insanely powerful 🤯"
- Method captured via frame-stepping (62-second reel, ~3-second intervals, vision OCR on text overlays)
- Real-world execution: ShotSavant TikTok "Flower Wingman" video (7626622272823971086), sourced from Notion Creative Research database
- v2.0.0: Extended with multi-scene support, native audio generation (Kling/Seedance/Veo), ElevenLabs Australian voice pipeline, sonilo_music, ffmpeg caption burning + audio mixing + concatenation, Fig & Bloom product integration
- v2.1.0: Caption design discipline (28px centered, not 48px left-aligned). Product must be WRAPPED not in glass vase (explicit negative constraint in keyframe prompt). Script-to-caption conversion via enable=between(t,start,end). Nano Banana Pro uses --image flag.
- v3.0.0: Hardening + multi-user refactor distilled from the ~7-cycle "first time receiving flowers" run. Added Prompting Rules R1–R8 (reference-seed prompting, realism = perfect image of an imperfect world, handheld motion, camera/hands logic, model routing + bake-off, brand voice/assets, original captions, licensed music). Added Step 0 Source Essence Analysis (hook + peak gate) and Step 9.5 Motion Critic (multi-frame, between animate and concat). Rubric extended to 12 dimensions — Dim 9 (camera/hands) and Dim 10 (capture realism) are hard-fail; Dim 4 now requires reference-seed + a clean reference. Rewrote Step 7 / Pitfall #5 to stop describing seeded references. Added Brand Profile (de-hardcode Fig & Bloom) and a runtime adapter (Hermes CLI ↔ Cowork MCP). New references: prompt-templates.md, brand-profile.example.md; new script: sample_clip_frames.sh.
- v3.1.0: **Pitfall #5.5** — logo/brand mark on non-product props (aprons, signage): never describe, always seed with a real photo + "this exact logo." **Pitfall #5.6** — action mechanics: read the source motion (tilt angle, hand-height differential, prying vs lifting); don't assume "straight lift." Observed on the florist bucket-separation reel: prying/rocking motion, not vertical lift. **Brand-world cloning via semantic search** — use the Asset Library API (`asset-library-u70t.onrender.com`) to find real Manifest-backed photos of the Sydney workshop, staff in aprons, and buckets, then pass as `--image` seeds to ground clones in the real Fig & Bloom visual world.
- v2.2.0: **Loop engineering layer** — generate→critique→revise loop wrapping the whole pipeline with an 8-dimension rubric (pass threshold 4/5), mandatory keyframe + final critic checkpoints, evidence-cited scoring, and a 3-iteration cap before escalating to the user. Full rubric + critic prompt in `references/clone-rubric.md`. **Casting / identity matrix** — approved Fig & Bloom shopper demographics (Caucasian blonde/brunette, Asian, sub-continental, African Sudanese/Somali/Nigerian but NOT African-American), with relevance-first casting + library rotation, wired into Step 4 and rubric Dimension 3. Opaque rounded-corner caption boxes in lower third; Epidemic Sound preferred over cheap sonilo_music for final brand audio.