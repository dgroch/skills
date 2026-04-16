"""
Bower Prompt Lab — Python API Wrapper

Provides a clean Python interface for agents and scripts to use the
prompt lab programmatically without CLI interaction.

Supports two image generation backends:
  - OpenRouter (default) — Nano Banana 2 via google/gemini-3.1-flash-image-preview
  - Higgsfield — Soul via higgsfield-ai/soul/standard

Usage:
    from bower_api import BowerPromptLab

    # OpenRouter (recommended)
    lab = BowerPromptLab(
        openrouter_key="sk-or-v1-...",
        anthropic_key="sk-ant-...",
    )

    # Higgsfield (legacy)
    lab = BowerPromptLab(
        backend="higgsfield",
        hf_key="...",
        hf_secret="...",
        anthropic_key="sk-ant-...",
    )

    # Generate a single shot
    result = lab.generate("product_hero")

    # Generate a full 9-post grid
    results = lab.generate_grid()

    # Generate a campaign set
    results = lab.generate_campaign("mothers_day", flowers=["garden roses", "peonies"])

    # Get the prompt library
    library = lab.get_library()
"""

import os
import json
import time
import base64
import requests
from pathlib import Path
from typing import Optional

# ── Defaults ─────────────────────────────────────────────────────────────

# OpenRouter
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL_PRO = "google/gemini-3-pro-image-preview"
OPENROUTER_MODEL_NB2 = "google/gemini-3.1-flash-image-preview"

# Higgsfield (legacy)
HF_BASE = "https://platform.higgsfield.ai"
HF_MODEL = "higgsfield-ai/soul/standard"

# Anthropic (critic)
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-sonnet-4-20250514"

MAX_ITERATIONS = 5
PASS_THRESHOLD = 7
POLL_INTERVAL = 5
POLL_TIMEOUT = 300

VALID_RATIOS = {"9:16", "16:9", "4:3", "3:4", "1:1", "2:3", "3:2"}
RATIO_MAP = {"4:5": "3:4", "5:4": "4:3"}

# ── Grid Pattern ─────────────────────────────────────────────────────────

GRID_PATTERN = [
    {"slot": "product_closeup",     "type": "product",   "ratio": "1:1"},
    {"slot": "lifestyle_wide",      "type": "lifestyle", "ratio": "3:4"},
    {"slot": "texture_detail",      "type": "detail",    "ratio": "1:1"},
    {"slot": "lifestyle_doorstep",  "type": "lifestyle", "ratio": "3:4"},
    {"slot": "product_hero",        "type": "product",   "ratio": "3:4"},
    {"slot": "packaging_flat",      "type": "detail",    "ratio": "3:4"},
    {"slot": "texture_petal",       "type": "detail",    "ratio": "1:1"},
    {"slot": "lifestyle_table",     "type": "lifestyle", "ratio": "3:4"},
    {"slot": "product_full",        "type": "product",   "ratio": "3:4"},
]

SLOT_TO_SHOT = {
    "product_closeup":    "product_closeup",
    "lifestyle_wide":     "lifestyle_wide",
    "texture_detail":     "texture_stems",
    "lifestyle_doorstep": "doorstep_arrival",
    "product_hero":       "product_hero",
    "packaging_flat":     "packaging_flat",
    "texture_petal":      "product_detail",
    "lifestyle_table":    "kitchen_table",
    "product_full":       "product_full",
}

# ── Critic System Prompt ─────────────────────────────────────────────────

CRITIC_SYSTEM = """You are a brand photography critic for "Bower" — a premium Australian DTC floral brand. Evaluate AI-generated images against Bower's art direction rubric and suggest specific prompt improvements.

BOWER ART DIRECTION RUBRIC:
- LIGHTING: Warm directional natural light (3500-4500K). Soft shadows with dimension. No flat lighting, no flash, no cool/blue casts. Morning or golden hour feel.
- COMPOSITION: 50-60% negative space in warm linen tones. Shallow DOF (f/2.0-3.5). Eye-level or slightly below for hero shots.
- COLOUR: Warm palette — linen (#EDE3D5), terracotta (#BF6B4A), espresso (#2B2220), eucalyptus (#7E9187). +10-15% warm shift. Greens desaturated toward sage. Shadows lifted, never crushed. No cool/blue tones.
- STYLING: Raw linen, warm stone, light timber, matte ceramics. Max 2 props. Never: plastic, bright coloured props, generic glass vases, confetti.
- TECHNICAL: Sharp focus on subject. No AI artefacts (warped hands, impossible physics, uncanny textures). Professional camera quality.
- BRAND ALIGNMENT: Tactile minimalism. Feels like a fashion brand that sells flowers. Warm, considered, quietly confident. NOT: gift shop, bridal, craft market, stock photography.

Respond ONLY with valid JSON (no markdown, no backticks, no preamble):
{
  "overall_score": <1-10>,
  "dimensions": {
    "lighting": {"score": <1-10>, "note": "<15 words max>"},
    "composition": {"score": <1-10>, "note": "<15 words max>"},
    "colour": {"score": <1-10>, "note": "<15 words max>"},
    "styling": {"score": <1-10>, "note": "<15 words max>"},
    "technical": {"score": <1-10>, "note": "<15 words max>"},
    "brand_alignment": {"score": <1-10>, "note": "<15 words max>"}
  },
  "verdict": "PASS or ITERATE",
  "prompt_revisions": "<If ITERATE: exact words to add/remove/change in the prompt. If PASS: empty string>"
}"""


class BowerPromptLab:
    """Python API for the Bower Prompt Lab.

    Args:
        backend: "openrouter" (default) or "higgsfield"
        openrouter_key: OpenRouter API key (for openrouter backend)
        model: OpenRouter model ID. Defaults to Nano Banana 2.
        hf_key: Higgsfield API key (for higgsfield backend)
        hf_secret: Higgsfield API secret (for higgsfield backend)
        anthropic_key: Anthropic API key (for Claude critic)
        output_dir: Where to save generated images
        library_path: Path to prompt library JSON
        max_iterations: Max generate-critique loops per shot
        pass_threshold: Minimum score to pass (1-10)
        verbose: Print progress messages
    """

    def __init__(
        self,
        backend: str = "openrouter",
        openrouter_key: str = "",
        model: str = OPENROUTER_MODEL_NB2,
        hf_key: str = "",
        hf_secret: str = "",
        anthropic_key: str = "",
        output_dir: str = "",
        library_path: str = "",
        max_iterations: int = MAX_ITERATIONS,
        pass_threshold: int = PASS_THRESHOLD,
        verbose: bool = True,
    ):
        self.backend = backend
        self.model = model
        self.max_iterations = max_iterations
        self.pass_threshold = pass_threshold
        self.verbose = verbose

        # Resolve paths relative to this file
        skill_dir = Path(__file__).parent
        self.output_dir = Path(output_dir) if output_dir else skill_dir / "outputs"
        self.library_path = Path(library_path) if library_path else skill_dir / "references" / "prompt-library.json"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Anthropic (critic) — required for both backends
        self.anthropic_key = anthropic_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not self.anthropic_key:
            raise ValueError("Anthropic API key required: set ANTHROPIC_API_KEY or pass anthropic_key")
        self.anthropic_headers = {
            "Content-Type": "application/json",
            "x-api-key": self.anthropic_key,
            "anthropic-version": "2023-06-01",
        }

        # Backend-specific setup
        if self.backend == "openrouter":
            self.openrouter_key = openrouter_key or os.environ.get("OPENROUTER_API_KEY", "")
            if not self.openrouter_key:
                raise ValueError("OpenRouter API key required: set OPENROUTER_API_KEY or pass openrouter_key")
            self.openrouter_headers = {
                "Authorization": f"Bearer {self.openrouter_key}",
                "Content-Type": "application/json",
            }
        elif self.backend == "higgsfield":
            self.hf_key = hf_key or os.environ.get("HF_KEY", "")
            self.hf_secret = hf_secret or os.environ.get("HF_SECRET", "")
            if not self.hf_key or not self.hf_secret:
                raise ValueError("Higgsfield credentials required: set HF_KEY/HF_SECRET")
            self.hf_headers = {
                "Authorization": f"Key {self.hf_key}:{self.hf_secret}",
                "Content-Type": "application/json",
            }
        else:
            raise ValueError(f"Unknown backend: {self.backend}. Use 'openrouter' or 'higgsfield'.")

    # ── Public API ───────────────────────────────────────────────────────

    def generate(self, shot_id: str, prompt: str = "", ratio: str = "3:4") -> dict:
        """Generate a single image through the quality gate loop.

        Args:
            shot_id: Identifier for the shot (used in library storage).
            prompt: The generation prompt. If empty, looks up shot_id in library.
            ratio: Aspect ratio (auto-mapped to valid ratios).

        Returns:
            dict with keys: shot_id, prompt, image_url, score, iteration, critique
        """
        if not prompt:
            prompt = self._lookup_prompt(shot_id)
            if not prompt:
                raise ValueError(f"No prompt found for shot_id '{shot_id}'. Provide a prompt or add to library.")

        return self._run_quality_gate(shot_id, prompt, ratio)

    def generate_grid(self, product: str = "", season: str = "") -> list[dict]:
        """Generate a full 9-post Instagram grid.

        Args:
            product: Optional product/arrangement description to weave in.
            season: Optional season modifier (e.g., "spring", "autumn").

        Returns:
            List of 9 result dicts, one per grid position.
        """
        results = []
        for slot in GRID_PATTERN:
            shot_id = SLOT_TO_SHOT[slot["slot"]]
            prompt = self._lookup_prompt(shot_id)
            if not prompt:
                self._log(f"  Skipping {slot['slot']} — no prompt for {shot_id}")
                continue

            if product:
                prompt = self._apply_product_swap(prompt, product)
            if season:
                prompt = self._apply_season_modifier(prompt, season)

            self._log(f"\n  Grid slot: {slot['slot']} ({slot['type']})")
            result = self._run_quality_gate(shot_id, prompt, slot["ratio"])
            result["grid_slot"] = slot["slot"]
            result["content_type"] = slot["type"]
            results.append(result)

        return results

    def generate_campaign(
        self, campaign_name: str, emotion: str = "", flowers: list[str] = None, shot_count: int = 5
    ) -> list[dict]:
        """Generate a campaign asset set.

        Args:
            campaign_name: Name for the campaign (e.g., "mothers_day").
            emotion: Emotional anchor (e.g., "warm gratitude").
            flowers: List of flower types to feature.
            shot_count: Number of shots (default 5: 2 product, 2 lifestyle, 1 detail).

        Returns:
            List of result dicts.
        """
        plan = [
            ("product_hero", "3:4"),
            ("product_closeup", "1:1"),
            ("kitchen_table", "3:4"),
            ("doorstep_arrival", "3:4"),
            ("product_detail", "1:1"),
        ][:shot_count]

        results = []
        for shot_id, ratio in plan:
            prompt = self._lookup_prompt(shot_id)
            if not prompt:
                continue

            if flowers:
                prompt = self._apply_flower_swap(prompt, flowers)
            if emotion:
                prompt = prompt.replace(
                    "No text, no logos, no watermarks.",
                    f"The mood carries a sense of {emotion}. No text, no logos, no watermarks."
                )

            self._log(f"\n  Campaign shot: {shot_id}")
            result = self._run_quality_gate(shot_id, prompt, ratio)
            result["campaign"] = campaign_name
            results.append(result)

        return results

    def get_library(self) -> list[dict]:
        """Return the current prompt library."""
        if self.library_path.exists():
            return json.loads(self.library_path.read_text())
        return []

    def get_shot_ids(self) -> list[str]:
        """Return all shot IDs in the library."""
        return [item["shot_id"] for item in self.get_library()]

    # ── Generation Backends ──────────────────────────────────────────────

    def _generate_image(self, prompt: str, ratio: str) -> Optional[str]:
        """Generate an image. Returns image URL or base64 data URL, or None on failure."""
        if self.backend == "openrouter":
            return self._generate_openrouter(prompt, ratio)
        else:
            return self._generate_higgsfield(prompt, ratio)

    def _generate_openrouter(self, prompt: str, ratio: str) -> Optional[str]:
        """Generate via OpenRouter (Nano Banana 2). Synchronous — no polling needed."""
        ar = RATIO_MAP.get(ratio, ratio)

        try:
            res = requests.post(
                OPENROUTER_URL,
                headers=self.openrouter_headers,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "modalities": ["image", "text"],
                    "image_config": {"aspect_ratio": ar},
                },
                timeout=120,
            )
            res.raise_for_status()
            data = res.json()

            # Extract image from response
            content = data["choices"][0]["message"]["content"]

            # Content can be a string (base64 data URL) or a list of parts
            if isinstance(content, list):
                for part in content:
                    if part.get("type") == "image_url":
                        url = part["image_url"]["url"]
                        # Save to disk if it's base64
                        if url.startswith("data:image"):
                            path = self._save_base64_image(url)
                            return path if path else url
                        return url
                return None
            elif isinstance(content, str) and "data:image" in content:
                path = self._save_base64_image(content)
                return path if path else content
            else:
                self._log(f"    Unexpected response format: {str(content)[:100]}")
                return None

        except Exception as e:
            self._log(f"    OpenRouter error: {e}")
            return None

    def _generate_higgsfield(self, prompt: str, ratio: str) -> Optional[str]:
        """Generate via Higgsfield Soul. Async — submit then poll."""
        ar = RATIO_MAP.get(ratio, ratio)
        if ar not in VALID_RATIOS:
            ar = "3:4"

        # Submit
        for attempt in range(3):
            try:
                res = requests.post(
                    f"{HF_BASE}/{HF_MODEL}",
                    headers=self.hf_headers,
                    json={"prompt": prompt, "aspect_ratio": ar},
                    timeout=30,
                )
                if res.status_code >= 500 and attempt < 2:
                    time.sleep(10 * (attempt + 1))
                    continue
                res.raise_for_status()
                request_id = res.json()["request_id"]
                break
            except Exception as e:
                if attempt == 2:
                    self._log(f"    Submit error: {e}")
                    return None

        # Poll
        start = time.time()
        while time.time() - start < POLL_TIMEOUT:
            time.sleep(POLL_INTERVAL)
            try:
                res = requests.get(
                    f"{HF_BASE}/requests/{request_id}/status",
                    headers=self.hf_headers,
                    timeout=15,
                )
                data = res.json()
                status = data.get("status", "unknown")
                if status == "completed":
                    return data["images"][0]["url"]
                elif status in ("failed", "nsfw"):
                    self._log(f"    Generation {status}")
                    return None
            except Exception:
                pass

        self._log(f"    Timeout")
        return None

    # ── Quality Gate ─────────────────────────────────────────────────────

    def _run_quality_gate(self, shot_id: str, prompt: str, ratio: str) -> dict:
        """The core generate → critique → revise loop."""
        best_result = None

        for iteration in range(1, self.max_iterations + 1):
            self._log(f"  Iteration {iteration}/{self.max_iterations}")

            # Generate
            image_ref = self._generate_image(prompt, ratio)
            if not image_ref:
                self._log(f"    Generation failed")
                continue

            self._log(f"    Image ready")

            # Critique — pass URL or file path
            critique = self._critique(image_ref, shot_id, prompt)
            if not critique:
                best_result = {
                    "shot_id": shot_id, "prompt": prompt, "image_url": image_ref,
                    "score": None, "iteration": iteration,
                }
                continue

            score = critique.get("overall_score", 0)
            verdict = critique.get("verdict", "ITERATE")
            self._log(f"    Score: {score}/10 — {verdict}")

            result = {
                "shot_id": shot_id, "prompt": prompt, "image_url": image_ref,
                "score": score, "iteration": iteration, "critique": critique,
            }

            if not best_result or (score and (not best_result.get("score") or score > best_result["score"])):
                best_result = result

            if score >= self.pass_threshold or verdict == "PASS":
                self._log(f"    PASSED")
                self._save_to_library(result)
                return result

            # Revise
            revisions = critique.get("prompt_revisions", "")
            if revisions and iteration < self.max_iterations:
                prompt = self._apply_revisions(prompt, revisions)
                self._log(f"    Prompt revised")

        if best_result:
            self._save_to_library(best_result)
        return best_result or {"shot_id": shot_id, "prompt": prompt, "image_url": "", "score": 0, "iteration": 0}

    # ── Critic ───────────────────────────────────────────────────────────

    def _critique(self, image_ref: str, shot_name: str, prompt: str) -> Optional[dict]:
        """Send image to Claude Sonnet for critique. Accepts URL or local file path."""
        try:
            # Build image source — URL or base64 from file
            if image_ref.startswith("data:image") or image_ref.startswith("http"):
                image_content = {
                    "type": "image",
                    "source": {"type": "url", "url": image_ref},
                }
            else:
                # Local file path — read and encode
                img_bytes = Path(image_ref).read_bytes()
                b64 = base64.b64encode(img_bytes).decode("utf-8")
                ext = Path(image_ref).suffix.lstrip(".")
                media_type = f"image/{ext}" if ext in ("png", "jpeg", "jpg", "webp", "gif") else "image/png"
                image_content = {
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": b64},
                }

            res = requests.post(
                ANTHROPIC_URL,
                headers=self.anthropic_headers,
                json={
                    "model": CLAUDE_MODEL,
                    "max_tokens": 1000,
                    "system": CRITIC_SYSTEM,
                    "messages": [{"role": "user", "content": [
                        image_content,
                        {"type": "text", "text": f'Shot type: "{shot_name}". Prompt:\n{prompt}\n\nScore against the Bower rubric.'},
                    ]}],
                },
                timeout=90,
            )
            res.raise_for_status()
            text = "".join(b.get("text", "") for b in res.json().get("content", []))
            clean = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
        except Exception as e:
            self._log(f"    Critique error: {e}")
            return None

    # ── Prompt Revision ──────────────────────────────────────────────────

    def _apply_revisions(self, prompt: str, revisions: str) -> str:
        try:
            res = requests.post(
                ANTHROPIC_URL,
                headers=self.anthropic_headers,
                json={
                    "model": CLAUDE_MODEL,
                    "max_tokens": 2000,
                    "system": "You are a prompt engineer. Apply the requested revisions to the image generation prompt. Return ONLY the revised prompt text — no explanation, no markdown, no backticks.",
                    "messages": [{"role": "user", "content": f"CURRENT PROMPT:\n{prompt}\n\nREVISIONS TO APPLY:\n{revisions}\n\nReturn the revised prompt."}],
                },
                timeout=30,
            )
            res.raise_for_status()
            return "".join(b.get("text", "") for b in res.json().get("content", [])).strip()
        except Exception:
            return prompt

    def _apply_product_swap(self, prompt: str, product: str) -> str:
        return self._apply_revisions(prompt, f"Replace the flower arrangement description with: {product}. Keep everything else unchanged.")

    def _apply_flower_swap(self, prompt: str, flowers: list[str]) -> str:
        flower_str = ", ".join(flowers)
        return self._apply_revisions(prompt, f"Replace the specific flower types with: {flower_str}. Keep everything else unchanged.")

    def _apply_season_modifier(self, prompt: str, season: str) -> str:
        return self._apply_revisions(prompt, f"Adjust the prompt to feel like {season}. Modify light quality, foliage, and mood accordingly while keeping the same composition and framing.")

    # ── Library ──────────────────────────────────────────────────────────

    def _lookup_prompt(self, shot_id: str) -> str:
        library = self.get_library()
        matches = [item for item in library if item.get("shot_id") == shot_id]
        if matches:
            best = max(matches, key=lambda x: x.get("score", 0) or 0)
            return best.get("prompt", "")
        return ""

    def _save_to_library(self, result: dict):
        library = self.get_library()
        library.append({
            "shot_id": result["shot_id"],
            "shot_name": result.get("shot_name", result["shot_id"]),
            "prompt": result["prompt"],
            "image_url": result.get("image_url", ""),
            "score": result.get("score"),
            "iteration": result.get("iteration"),
            "critique": result.get("critique"),
            "campaign": result.get("campaign"),
            "grid_slot": result.get("grid_slot"),
            "backend": self.backend,
            "model": self.model if self.backend == "openrouter" else HF_MODEL,
        })
        self.library_path.write_text(json.dumps(library, indent=2))

    def _save_base64_image(self, data_url: str) -> Optional[str]:
        """Save a base64 data URL to disk. Returns the file path."""
        try:
            # Parse data:image/png;base64,<data>
            header, b64_data = data_url.split(",", 1)
            ext = "png"
            if "jpeg" in header or "jpg" in header:
                ext = "jpg"
            elif "webp" in header:
                ext = "webp"

            img_bytes = base64.b64decode(b64_data)
            filename = f"gen_{int(time.time())}.{ext}"
            path = self.output_dir / filename
            path.write_bytes(img_bytes)
            self._log(f"    Saved: {path}")
            return str(path)
        except Exception as e:
            self._log(f"    Save error: {e}")
            return None

    def _log(self, msg: str):
        if self.verbose:
            print(msg)
