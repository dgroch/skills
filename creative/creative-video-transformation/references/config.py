"""
video-remix/scripts/config.py
Shared configuration using the official higgsfield-client SDK.

Auth: Set HF_API_KEY + HF_API_SECRET (or HF_KEY) in environment.
       Set ANTHROPIC_API_KEY for shot analysis.
Install: pip install higgsfield-client anthropic scenedetect[opencv]
"""

import os
import json
from pathlib import Path

# --- Paths ---
WORK_DIR = Path("./work")
KEYFRAMES_DIR = WORK_DIR / "keyframes"
REGEN_DIR = WORK_DIR / "regen_keyframes"
CLIPS_DIR = WORK_DIR / "clips"
AUDIO_DIR = WORK_DIR / "audio"
OUTPUT_DIR = Path("./output")

ALL_DIRS = [KEYFRAMES_DIR, REGEN_DIR, CLIPS_DIR, AUDIO_DIR, OUTPUT_DIR]

# --- API Keys ---
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Higgsfield auth is handled by the SDK via env vars:
#   Option 1: HF_KEY="your-api-key:your-api-secret"
#   Option 2: HF_API_KEY + HF_API_SECRET
# Get credentials from https://cloud.higgsfield.ai/api-keys

# --- Model identifiers ---
# These are the model path strings passed to higgsfield_client.subscribe().
# The exact paths may need adjustment based on the current Higgsfield catalog.
# If a model path returns "not found", check cloud.higgsfield.ai or try
# the slug-style names (e.g. 'nano-banana-2-edit', 'veo3.1-i2v').
IMAGE_EDIT_MODEL = os.environ.get("HF_IMAGE_MODEL", "google/nano-banana-2/edit")
VIDEO_I2V_MODEL = os.environ.get("HF_VIDEO_MODEL", "google/veo/3.1/image-to-video")

# --- Helpers ---

def ensure_dirs():
    for d in ALL_DIRS:
        d.mkdir(parents=True, exist_ok=True)


def load_manifest() -> dict:
    with open(WORK_DIR / "shots_manifest.json") as f:
        return json.load(f)


def save_manifest(data: dict):
    with open(WORK_DIR / "shots_manifest.json", "w") as f:
        json.dump(data, f, indent=2)


def load_remix_plan() -> dict:
    with open(WORK_DIR / "remix_plan.json") as f:
        return json.load(f)


def save_remix_plan(data: dict):
    with open(WORK_DIR / "remix_plan.json", "w") as f:
        json.dump(data, f, indent=2)


def write_state(checkpoint: str):
    with open(WORK_DIR / "state.txt", "w") as f:
        f.write(checkpoint)


def read_state() -> str | None:
    path = WORK_DIR / "state.txt"
    return path.read_text().strip() if path.exists() else None


def quantise_duration(seconds: float) -> int:
    """Map arbitrary duration to nearest Veo 3.1 supported value (4, 6, 8)."""
    if seconds <= 5.0:
        return 4
    elif seconds <= 7.0:
        return 6
    else:
        return 8
