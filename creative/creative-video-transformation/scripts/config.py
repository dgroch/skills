"""
Shared configuration for the video remix pipeline.

Auth (Higgsfield):
  HF_KEY="api-key:api-secret"   (single value)
  OR
  HF_API_KEY=api-key
  HF_API_SECRET=api-secret

Auth (Claude):
  ANTHROPIC_API_KEY=...

Install:
  pip install higgsfield-client anthropic scenedetect[opencv] requests
"""

import json
import os
from pathlib import Path

# --- Paths (resolved relative to the current working directory) ---
WORK_DIR = Path("./work")
KEYFRAMES_DIR = WORK_DIR / "keyframes"
REGEN_DIR = WORK_DIR / "regen_keyframes"
CLIPS_DIR = WORK_DIR / "clips"
AUDIO_DIR = WORK_DIR / "audio"
OUTPUT_DIR = Path("./output")
MANIFEST_PATH = WORK_DIR / "shots_manifest.json"
PLAN_PATH = WORK_DIR / "remix_plan.json"
STATE_PATH = WORK_DIR / "state.txt"

ALL_DIRS = [KEYFRAMES_DIR, REGEN_DIR, CLIPS_DIR, AUDIO_DIR, OUTPUT_DIR]

# --- Model identifiers ---
# The Higgsfield SDK passes the model string through as the URL path
# (POST https://platform.higgsfield.ai/{model}). The canonical paths below
# are educated guesses based on the shape of other known slugs
# (e.g. bytedance/seedream/v4/text-to-image). Override via env if the
# catalog at https://cloud.higgsfield.ai uses different slugs.
IMAGE_EDIT_MODEL = os.environ.get("HF_IMAGE_MODEL", "google/nano-banana-2/edit")
VIDEO_I2V_MODEL = os.environ.get("HF_VIDEO_MODEL", "google/veo/3.1/image-to-video")

# Text-to-image model used only by test_connection.py to validate auth.
# This slug is the one documented in the SDK README and is the most likely
# to resolve on any Higgsfield account.
PROBE_T2I_MODEL = os.environ.get("HF_PROBE_MODEL", "bytedance/seedream/v4/text-to-image")

# --- Generation defaults (override via env) ---
# Nano Banana 2 Edit: valid resolutions are "1K", "2K", "4K" (case-sensitive).
IMAGE_RESOLUTION = os.environ.get("HF_IMAGE_RESOLUTION", "2K")
# Veo 3.1: valid resolutions are "720p" or "1080p".
VIDEO_RESOLUTION = os.environ.get("HF_VIDEO_RESOLUTION", "1080p")

# Claude model used by analyse.py. Defaults to the latest Sonnet.
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")

# --- Helpers ---

def ensure_dirs():
    for d in ALL_DIRS:
        d.mkdir(parents=True, exist_ok=True)


def require_env(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise SystemExit(f"ERROR: environment variable {name} is not set")
    return value


def have_higgsfield_creds() -> bool:
    return bool(
        os.environ.get("HF_KEY")
        or (os.environ.get("HF_API_KEY") and os.environ.get("HF_API_SECRET"))
    )


def aspect_ratio_from_info(info: dict) -> str:
    """Map source video width:height onto a Higgsfield-supported ratio.

    Nano Banana 2 and Veo 3.1 both accept 16:9 and 9:16. 1:1 is used when
    the source is close to square to avoid aggressive crops.
    """
    w, h = int(info["width"]), int(info["height"])
    ratio = w / h
    if 0.9 <= ratio <= 1.1:
        return "1:1"
    return "16:9" if ratio > 1.0 else "9:16"


def quantise_duration(seconds: float) -> int:
    """Snap a source-shot duration to Veo 3.1's supported values: 4, 6, or 8."""
    if seconds < 5.0:
        return 4
    if seconds < 7.0:
        return 6
    return 8


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_manifest() -> dict:
    return load_json(MANIFEST_PATH)


def save_manifest(data: dict):
    save_json(MANIFEST_PATH, data)


def load_remix_plan() -> dict:
    return load_json(PLAN_PATH)


def save_remix_plan(data: dict):
    save_json(PLAN_PATH, data)


def write_state(checkpoint: str):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(checkpoint)


def read_state() -> str | None:
    return STATE_PATH.read_text().strip() if STATE_PATH.exists() else None
