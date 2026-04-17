"""
Brand Photographer — Python API Wrapper

A brand-agnostic API for generating brand-consistent AI photography.
The agent (Brand Photographer) loads a single brand configuration at
instantiation time and all subsequent operations are scoped to that
brand. This enforces isolation: no cross-contamination of prompts,
rubrics, libraries, or critiques between brands.

Supports two image generation backends:
  - OpenRouter (default) — Nano Banana 2 / Pro via google/gemini models
  - Higgsfield — Soul via higgsfield-ai/soul/standard

Critic execution priority:
  1. Claude CLI (`claude` command) — preferred when available on PATH.
     Does not require ANTHROPIC_API_KEY to be set.
  2. Anthropic API — fallback when Claude CLI is not available.
     Requires ANTHROPIC_API_KEY.

Usage:
    from brand_photographer_api import BrandPhotographer

    # Load a configured brand (by brand_id)
    photographer = BrandPhotographer(
        brand_id="bower",
        openrouter_key="sk-or-v1-...",
        # anthropic_key only needed if claude CLI is unavailable
    )

    # Generate a single shot
    result = photographer.generate("product_hero")

    # Generate a full 9-post grid
    results = photographer.generate_grid()

    # Generate a campaign set
    results = photographer.generate_campaign(
        "mothers_day",
        flowers=["garden roses", "peonies"],
    )

    # Inspect the brand's prompt library
    library = photographer.get_library()

    # List all configured brands
    brands = BrandPhotographer.list_brands()
"""

import os
import json
import time
import base64
import shutil
import subprocess
import tempfile
import requests
from pathlib import Path
from typing import Optional

# ── Defaults ─────────────────────────────────────────────────────────────

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL_PRO = "google/gemini-3-pro-image-preview"
OPENROUTER_MODEL_NB2 = "google/gemini-3.1-flash-image-preview"

HF_BASE = "https://platform.higgsfield.ai"
HF_MODEL = "higgsfield-ai/soul/standard"

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_CLAUDE_MODEL = "claude-sonnet-4-20250514"

MAX_ITERATIONS = 5
PASS_THRESHOLD = 7
POLL_INTERVAL = 5
POLL_TIMEOUT = 300

VALID_RATIOS = {"9:16", "16:9", "4:3", "3:4", "1:1", "2:3", "3:2"}
RATIO_MAP = {"4:5": "3:4", "5:4": "4:3"}

# Critic execution modes — logged at runtime
CRITIC_MODE_CLI = "cli"
CRITIC_MODE_API = "api"


def _brands_root() -> Path:
    """Root directory holding per-brand configuration.

    Returns a persistent path outside the ephemeral __runtime__ directory so
    that seeds.json, seed images, prompt-library, and outputs survive across
    heartbeat sessions.

    Path structure inside __runtime__:
        .../skills/{companyId}/__runtime__/{skill}/references/brand_photographer_api.py

    Persistent store lives two levels above __runtime__:
        .../skills/{companyId}/data/creative-brand-photographer/brands/

    On first access, any brand directory present in the bundled brands/ tree
    is bootstrapped into the persistent store (copy-once, never overwrite).
    """
    skill_root = Path(__file__).resolve().parent.parent  # __runtime__/{skill}/
    skills_base = skill_root.parent.parent               # .../skills/{companyId}/
    persistent = skills_base / "data" / "creative-brand-photographer" / "brands"
    persistent.mkdir(parents=True, exist_ok=True)

    # Bootstrap: copy any brand dirs that exist in the bundled source but
    # have not yet been initialised in the persistent store.  Never overwrites.
    bundled = skill_root / "brands"
    if bundled.exists():
        for brand_dir in bundled.iterdir():
            if brand_dir.is_dir() and not (persistent / brand_dir.name).exists():
                shutil.copytree(str(brand_dir), str(persistent / brand_dir.name))

    return persistent


def _claude_cli_available() -> bool:
    """Return True if the `claude` CLI is present on PATH."""
    return shutil.which("claude") is not None


class BrandNotConfiguredError(Exception):
    """Raised when the requested brand_id has no configuration."""


class BrandPhotographer:
    """Multi-brand photographer API.

    Each instance is bound to exactly one brand_id. All library writes,
    critiques, and prompt revisions use that brand's assets only.

    Critic execution: Claude CLI is used when available (preferred). Falls back
    to direct Anthropic API calls when CLI is unavailable. ANTHROPIC_API_KEY is
    only required for the API fallback path.

    Args:
        brand_id: Identifier of the brand directory under brands/.
        backend: "openrouter" (default) or "higgsfield".
        openrouter_key: OpenRouter API key.
        model: Override the brand's configured image model.
        hf_key / hf_secret: Higgsfield credentials (if backend=higgsfield).
        anthropic_key: Anthropic API key for API-mode critic fallback.
            Optional when `claude` CLI is available on PATH.
        max_iterations: Override brand's quality-gate iteration cap.
        pass_threshold: Override brand's pass threshold (1-10).
        verbose: Print progress messages.
    """

    def __init__(
        self,
        brand_id: str,
        backend: Optional[str] = None,
        openrouter_key: str = "",
        model: str = "",
        hf_key: str = "",
        hf_secret: str = "",
        anthropic_key: str = "",
        max_iterations: Optional[int] = None,
        pass_threshold: Optional[int] = None,
        verbose: bool = True,
    ):
        self.brand_id = brand_id
        self.verbose = verbose

        # ── Load brand configuration ─────────────────────────────────
        self.brand_dir = _brands_root() / brand_id
        if not self.brand_dir.exists():
            raise BrandNotConfiguredError(
                f"No brand configured at {self.brand_dir}. "
                f"Available brands: {self.list_brands()}. "
                "Complete the onboarding flow to add a new brand."
            )
        config_path = self.brand_dir / "brand.json"
        if not config_path.exists():
            raise BrandNotConfiguredError(
                f"Missing brand.json in {self.brand_dir}. "
                "Run the onboarding flow to generate one."
            )
        self.config = json.loads(config_path.read_text())
        self._validate_config()

        # Brand-scoped paths — NEVER reach across brands
        self.output_dir = self.brand_dir / "outputs"
        self.library_path = self.brand_dir / self.config["references"]["prompt_library"]
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Backend resolution (constructor arg > brand config > default)
        brand_backend = self.config.get("image_backend", {})
        self.backend = backend or brand_backend.get("default", "openrouter")
        self.model = model or brand_backend.get("model", OPENROUTER_MODEL_NB2)

        # Quality gate
        gate = self.config.get("quality_gate", {})
        self.max_iterations = max_iterations if max_iterations is not None else gate.get("max_iterations", MAX_ITERATIONS)
        self.pass_threshold = pass_threshold if pass_threshold is not None else gate.get("pass_threshold", PASS_THRESHOLD)

        # Critic setup
        critic = self.config.get("critic", {})
        self.critic_model = critic.get("model", DEFAULT_CLAUDE_MODEL)
        self.critic_system = self._build_critic_system()

        # ── Critic execution mode ──────────────────────────────────────
        # Prefer Claude CLI; fall back to API only when CLI is absent.
        self._cli_available = _claude_cli_available()
        if self._cli_available:
            self.critic_mode = CRITIC_MODE_CLI
            self._log("[critic] Claude CLI found on PATH — using CLI mode")
            # API key not required but accepted if provided (used only if CLI fails)
            self.anthropic_key = anthropic_key or os.environ.get("ANTHROPIC_API_KEY", "")
        else:
            self.critic_mode = CRITIC_MODE_API
            self._log("[critic] Claude CLI not found — falling back to API mode")
            self.anthropic_key = anthropic_key or os.environ.get("ANTHROPIC_API_KEY", "")
            if not self.anthropic_key:
                raise ValueError(
                    "Anthropic API key required when Claude CLI is unavailable. "
                    "Either install the Claude CLI or set ANTHROPIC_API_KEY."
                )

        self.anthropic_headers = {
            "Content-Type": "application/json",
            "x-api-key": self.anthropic_key,
            "anthropic-version": "2023-06-01",
        } if self.anthropic_key else {}

        # Backend-specific credentials
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

        self._log(f"Brand Photographer configured for '{self.config['brand_name']}' (brand_id={brand_id})")

    # ── Brand discovery ──────────────────────────────────────────────────

    @classmethod
    def list_brands(cls) -> list[str]:
        """Return all configured brand_ids (directories with a brand.json)."""
        root = _brands_root()
        if not root.exists():
            return []
        return sorted(
            d.name for d in root.iterdir()
            if d.is_dir() and (d / "brand.json").exists()
        )

    @classmethod
    def load_brand_config(cls, brand_id: str) -> dict:
        """Return the raw brand.json dict for a brand_id."""
        path = _brands_root() / brand_id / "brand.json"
        if not path.exists():
            raise BrandNotConfiguredError(f"No brand configured at {path}")
        return json.loads(path.read_text())

    # ── Validation & critic construction ─────────────────────────────────

    def _validate_config(self):
        required_top = ["brand_id", "brand_name", "references", "critic", "grid_pattern"]
        for key in required_top:
            if key not in self.config:
                raise ValueError(f"Brand config missing required key: {key}")
        if self.config["brand_id"] != self.brand_id:
            raise ValueError(
                f"brand_id mismatch: directory '{self.brand_id}' vs config '{self.config['brand_id']}'"
            )
        # Required reference files must exist
        for label, filename in self.config["references"].items():
            fpath = self.brand_dir / filename
            if not fpath.exists():
                raise FileNotFoundError(
                    f"Brand '{self.brand_id}' references missing file: {fpath} (label: {label})"
                )

    def _build_critic_system(self) -> str:
        """Build the critic system prompt from brand config + reference docs."""
        brand_name = self.config["brand_name"]
        description = self.config.get("description", "")
        dims = self.config["critic"]["dimensions"]

        rubric_lines = []
        dimension_names = []
        for d in dims:
            name = d["name"].upper()
            dimension_names.append(d["name"])
            rubric_lines.append(f"- {name}: {d['description']}")
        rubric = "\n".join(rubric_lines)

        dims_schema = ",\n    ".join(
            f'"{n}": {{"score": <1-10>, "note": "<15 words max>"}}'
            for n in dimension_names
        )

        return f"""You are a brand photography critic for "{brand_name}" — {description} Evaluate AI-generated images against {brand_name}'s art direction rubric and suggest specific prompt improvements.

{brand_name.upper()} ART DIRECTION RUBRIC:
{rubric}

Respond ONLY with valid JSON (no markdown, no backticks, no preamble):
{{
  "overall_score": <1-10>,
  "dimensions": {{
    {dims_schema}
  }},
  "verdict": "PASS or ITERATE",
  "prompt_revisions": "<If ITERATE: exact words to add/remove/change in the prompt. If PASS: empty string>"
}}"""

    # ── Public API ───────────────────────────────────────────────────────

    def generate(self, shot_id: str, prompt: str = "", ratio: str = "3:4") -> dict:
        """Generate a single image through the quality gate loop."""
        if not prompt:
            prompt = self._lookup_prompt(shot_id)
            if not prompt:
                raise ValueError(
                    f"No prompt for shot_id '{shot_id}' in {self.brand_id}'s library. "
                    "Provide a prompt or add one via the onboarding/expansion flow."
                )
        return self._run_quality_gate(shot_id, prompt, ratio)

    def generate_grid(self, product: str = "", season: str = "") -> list[dict]:
        """Generate a full grid following the brand's grid_pattern."""
        grid_pattern = self.config["grid_pattern"]
        slot_to_shot = self.config.get("slot_to_shot", {})

        results = []
        for slot in grid_pattern:
            shot_id = slot_to_shot.get(slot["slot"], slot["slot"])
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
        self,
        campaign_name: str,
        emotion: str = "",
        flowers: Optional[list[str]] = None,
        products: Optional[list[str]] = None,
        shot_count: int = 5,
    ) -> list[dict]:
        """Generate a campaign asset set using the brand's default shot plan."""
        campaign_plan = self.config.get("campaign_plan") or [
            ("product_hero", "3:4"),
            ("product_closeup", "1:1"),
            ("kitchen_table", "3:4"),
            ("doorstep_arrival", "3:4"),
            ("product_detail", "1:1"),
        ]
        plan = [(s, r) for s, r in campaign_plan][:shot_count]

        results = []
        for shot_id, ratio in plan:
            prompt = self._lookup_prompt(shot_id)
            if not prompt:
                continue

            swap = flowers or products
            if swap:
                prompt = self._apply_subject_swap(prompt, swap)
            if emotion:
                prompt = self._apply_revisions(
                    prompt,
                    f"Thread the emotional tone of '{emotion}' through the mood description.",
                )

            self._log(f"\n  Campaign shot: {shot_id}")
            result = self._run_quality_gate(shot_id, prompt, ratio)
            result["campaign"] = campaign_name
            results.append(result)

        return results

    def get_library(self) -> list[dict]:
        if self.library_path.exists():
            return json.loads(self.library_path.read_text())
        return []

    def get_shot_ids(self) -> list[str]:
        return [item["shot_id"] for item in self.get_library()]

    def brand_summary(self) -> dict:
        """Return a summary of the loaded brand configuration — for agent inspection."""
        return {
            "brand_id": self.brand_id,
            "brand_name": self.config["brand_name"],
            "description": self.config.get("description", ""),
            "product_category": self.config.get("product_category", ""),
            "backend": self.backend,
            "model": self.model,
            "critic_mode": self.critic_mode,
            "critic_dimensions": [d["name"] for d in self.config["critic"]["dimensions"]],
            "pass_threshold": self.pass_threshold,
            "max_iterations": self.max_iterations,
            "library_size": len(self.get_library()),
        }

    # ── Generation backends ──────────────────────────────────────────────

    def _generate_image(self, prompt: str, ratio: str) -> Optional[str]:
        if self.backend == "openrouter":
            return self._generate_openrouter(prompt, ratio)
        return self._generate_higgsfield(prompt, ratio)

    def _generate_openrouter(self, prompt: str, ratio: str) -> Optional[str]:
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
            message = data["choices"][0]["message"]

            images = message.get("images", []) or []
            if images:
                url = images[0].get("image_url", {}).get("url", "")
                if url.startswith("data:image"):
                    path = self._save_base64_image(url)
                    return path if path else url
                elif url.startswith("http"):
                    return url

            content = message.get("content")
            if isinstance(content, list):
                for part in content:
                    if part.get("type") == "image_url":
                        url = part["image_url"]["url"]
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
        ar = RATIO_MAP.get(ratio, ratio)
        if ar not in VALID_RATIOS:
            ar = "3:4"

        request_id = None
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
        if not request_id:
            return None

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

        self._log("    Timeout")
        return None

    # ── Quality gate ─────────────────────────────────────────────────────

    def _run_quality_gate(self, shot_id: str, prompt: str, ratio: str) -> dict:
        best_result = None

        for iteration in range(1, self.max_iterations + 1):
            self._log(f"  Iteration {iteration}/{self.max_iterations}")

            image_ref = self._generate_image(prompt, ratio)
            if not image_ref:
                self._log("    Generation failed")
                continue

            self._log("    Image ready")

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
                self._log("    PASSED")
                self._save_to_library(result)
                return result

            revisions = critique.get("prompt_revisions", "")
            if revisions and iteration < self.max_iterations:
                prompt = self._apply_revisions(prompt, revisions)
                self._log("    Prompt revised")

        if best_result:
            self._save_to_library(best_result)
        return best_result or {
            "shot_id": shot_id, "prompt": prompt, "image_url": "", "score": 0, "iteration": 0,
        }

    # ── Critic — CLI path ────────────────────────────────────────────────

    def _image_ref_to_local_path(self, image_ref: str) -> Optional[str]:
        """Return a local file path for an image ref, downloading if necessary.

        Returns None if the image cannot be resolved to a local file.
        """
        if not image_ref:
            return None

        # Already a local file
        if not image_ref.startswith("http") and not image_ref.startswith("data:"):
            p = Path(image_ref)
            return str(p) if p.exists() else None

        # HTTP URL — download to temp file
        if image_ref.startswith("http"):
            try:
                resp = requests.get(image_ref, timeout=30)
                resp.raise_for_status()
                ext = "jpg"
                ct = resp.headers.get("content-type", "")
                if "png" in ct:
                    ext = "png"
                elif "webp" in ct:
                    ext = "webp"
                tmp = tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False)
                tmp.write(resp.content)
                tmp.close()
                return tmp.name
            except Exception as e:
                self._log(f"    [critic/cli] Failed to download image: {e}")
                return None

        # Base64 data URL — decode to temp file
        if image_ref.startswith("data:image"):
            try:
                header, b64_data = image_ref.split(",", 1)
                ext = "png"
                if "jpeg" in header or "jpg" in header:
                    ext = "jpg"
                elif "webp" in header:
                    ext = "webp"
                tmp = tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False)
                tmp.write(base64.b64decode(b64_data))
                tmp.close()
                return tmp.name
            except Exception as e:
                self._log(f"    [critic/cli] Failed to decode base64 image: {e}")
                return None

        return None

    def _critique_via_cli(self, image_ref: str, shot_name: str, prompt: str) -> Optional[dict]:
        """Run critique using the Claude CLI (`claude --print`)."""
        local_path = self._image_ref_to_local_path(image_ref)
        if not local_path:
            self._log("    [critic/cli] Could not resolve image to local path — skipping CLI critique")
            return None

        user_text = (
            f'Shot type: "{shot_name}". Prompt:\n{prompt}\n\n'
            f"Score against the {self.config['brand_name']} rubric."
        )

        cmd = [
            "claude",
            "--print",
            "--system-prompt", self.critic_system,
            "--image", local_path,
            user_text,
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            # Clean up temp file if we created one
            if image_ref.startswith("http") or image_ref.startswith("data:"):
                try:
                    Path(local_path).unlink(missing_ok=True)
                except Exception:
                    pass

            if result.returncode != 0:
                self._log(f"    [critic/cli] CLI exited with code {result.returncode}: {result.stderr[:200]}")
                return None

            text = result.stdout.strip()
            if not text:
                self._log("    [critic/cli] Empty response from CLI")
                return None

            clean = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)

        except subprocess.TimeoutExpired:
            self._log("    [critic/cli] CLI timed out")
            return None
        except json.JSONDecodeError as e:
            self._log(f"    [critic/cli] JSON parse error: {e}")
            return None
        except Exception as e:
            self._log(f"    [critic/cli] Error: {e}")
            return None

    def _critique_via_api(self, image_ref: str, shot_name: str, prompt: str) -> Optional[dict]:
        """Run critique using the Anthropic API directly."""
        if not self.anthropic_key:
            self._log("    [critic/api] No API key available for fallback")
            return None
        try:
            if image_ref.startswith("data:image") or image_ref.startswith("http"):
                image_content = {
                    "type": "image",
                    "source": {"type": "url", "url": image_ref},
                }
            else:
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
                    "model": self.critic_model,
                    "max_tokens": 1000,
                    "system": self.critic_system,
                    "messages": [{"role": "user", "content": [
                        image_content,
                        {"type": "text", "text": (
                            f'Shot type: "{shot_name}". Prompt:\n{prompt}\n\n'
                            f"Score against the {self.config['brand_name']} rubric."
                        )},
                    ]}],
                },
                timeout=90,
            )
            res.raise_for_status()
            text = "".join(b.get("text", "") for b in res.json().get("content", []))
            clean = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
        except Exception as e:
            self._log(f"    [critic/api] Error: {e}")
            return None

    # ── Critic — dispatch ────────────────────────────────────────────────

    def _critique(self, image_ref: str, shot_name: str, prompt: str) -> Optional[dict]:
        """Critique an image. Tries CLI first; falls back to API on failure."""
        if self._cli_available:
            self._log(f"    [critic] Using CLI path")
            result = self._critique_via_cli(image_ref, shot_name, prompt)
            if result is not None:
                return result
            # CLI attempted but failed — fall back with warning
            self._log("    [critic] CLI critique failed — falling back to API")
            return self._critique_via_api(image_ref, shot_name, prompt)
        else:
            self._log(f"    [critic] Using API path (CLI not available)")
            return self._critique_via_api(image_ref, shot_name, prompt)

    # ── Prompt revision helpers ──────────────────────────────────────────

    def _apply_revisions_via_cli(self, prompt: str, revisions: str) -> Optional[str]:
        """Apply prompt revisions using the Claude CLI."""
        system = (
            "You are a prompt engineer. Apply the requested revisions to the image "
            "generation prompt. Return ONLY the revised prompt text — no explanation, "
            "no markdown, no backticks."
        )
        user_text = (
            f"CURRENT PROMPT:\n{prompt}\n\nREVISIONS TO APPLY:\n{revisions}\n\n"
            "Return the revised prompt."
        )
        cmd = ["claude", "--print", "--system-prompt", system, user_text]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                self._log(f"    [revise/cli] CLI exited with code {result.returncode}: {result.stderr[:200]}")
                return None
            text = result.stdout.strip()
            return text if text else None
        except subprocess.TimeoutExpired:
            self._log("    [revise/cli] CLI timed out")
            return None
        except Exception as e:
            self._log(f"    [revise/cli] Error: {e}")
            return None

    def _apply_revisions_via_api(self, prompt: str, revisions: str) -> Optional[str]:
        """Apply prompt revisions using the Anthropic API."""
        if not self.anthropic_key:
            return None
        try:
            res = requests.post(
                ANTHROPIC_URL,
                headers=self.anthropic_headers,
                json={
                    "model": self.critic_model,
                    "max_tokens": 2000,
                    "system": "You are a prompt engineer. Apply the requested revisions to the image generation prompt. Return ONLY the revised prompt text — no explanation, no markdown, no backticks.",
                    "messages": [{"role": "user", "content": (
                        f"CURRENT PROMPT:\n{prompt}\n\nREVISIONS TO APPLY:\n{revisions}\n\nReturn the revised prompt."
                    )}],
                },
                timeout=30,
            )
            res.raise_for_status()
            return "".join(b.get("text", "") for b in res.json().get("content", [])).strip()
        except Exception:
            return None

    def _apply_revisions(self, prompt: str, revisions: str) -> str:
        """Apply revisions to a prompt. Tries CLI first; falls back to API."""
        if self._cli_available:
            self._log("    [revise] Using CLI path")
            revised = self._apply_revisions_via_cli(prompt, revisions)
            if revised:
                return revised
            self._log("    [revise] CLI failed — falling back to API")
            revised = self._apply_revisions_via_api(prompt, revisions)
            return revised if revised else prompt
        else:
            self._log("    [revise] Using API path (CLI not available)")
            revised = self._apply_revisions_via_api(prompt, revisions)
            return revised if revised else prompt

    def _apply_subject_swap(self, prompt: str, subjects: list[str]) -> str:
        joined = ", ".join(subjects)
        return self._apply_revisions(
            prompt,
            f"Replace the primary subject description with: {joined}. Keep everything else unchanged.",
        )

    def _apply_product_swap(self, prompt: str, product: str) -> str:
        return self._apply_revisions(
            prompt,
            f"Replace the primary product/arrangement description with: {product}. Keep everything else unchanged.",
        )

    def _apply_season_modifier(self, prompt: str, season: str) -> str:
        return self._apply_revisions(
            prompt,
            f"Adjust the prompt to feel like {season}. Modify light quality, foliage, and mood accordingly while keeping the same composition and framing.",
        )

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
            "brand_id": self.brand_id,
            "backend": self.backend,
            "model": self.model if self.backend == "openrouter" else HF_MODEL,
        })
        self.library_path.write_text(json.dumps(library, indent=2))

    def _save_base64_image(self, data_url: str) -> Optional[str]:
        try:
            header, b64_data = data_url.split(",", 1)
            ext = "png"
            if "jpeg" in header or "jpg" in header:
                ext = "jpg"
            elif "webp" in header:
                ext = "webp"
            img_bytes = base64.b64decode(b64_data)
            filename = f"{self.brand_id}_{int(time.time())}.{ext}"
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
