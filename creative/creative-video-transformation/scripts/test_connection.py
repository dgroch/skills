"""
Pre-flight check for the video remix pipeline.

Validates:
  - Python version
  - FFmpeg + FFprobe on PATH
  - Required SDKs import (higgsfield_client, scenedetect, requests)
  - HF auth env vars (HF_KEY or HF_API_KEY_ID + HF_API_KEY_SECRET)
  - claude CLI available and responsive (no ANTHROPIC_API_KEY required)
  - Higgsfield auth (upload a small in-memory PNG)
  - Configured model paths (does NOT run a full generation — credits-free probe)

Usage: python scripts/test_connection.py [--probe-models]

The `--probe-models` flag additionally submits the cheapest possible job
against each configured model and cancels it immediately if possible. This
consumes a small amount of credits (at most one text-to-image + one queued
slot). Omit if you don't want to spend credits.
"""

import argparse
import io
import os
import shutil
import subprocess
import sys
import time

from config import (
    ANTHROPIC_MODEL,
    IMAGE_EDIT_MODEL,
    PROBE_T2I_MODEL,
    VIDEO_I2V_MODEL,
    have_higgsfield_creds,
)

OK = "[ ok ]"
FAIL = "[fail]"
WARN = "[warn]"
SKIP = "[skip]"


class Check:
    def __init__(self):
        self.failures = 0
        self.warnings = 0

    def ok(self, label: str, detail: str = ""):
        print(f"{OK} {label}" + (f" — {detail}" if detail else ""))

    def fail(self, label: str, detail: str = ""):
        self.failures += 1
        print(f"{FAIL} {label}" + (f" — {detail}" if detail else ""))

    def warn(self, label: str, detail: str = ""):
        self.warnings += 1
        print(f"{WARN} {label}" + (f" — {detail}" if detail else ""))

    def skip(self, label: str, detail: str = ""):
        print(f"{SKIP} {label}" + (f" — {detail}" if detail else ""))


def check_python(c: Check):
    if sys.version_info >= (3, 10):
        c.ok("Python", f"{sys.version_info.major}.{sys.version_info.minor}")
    else:
        c.fail("Python", f"{sys.version_info.major}.{sys.version_info.minor} (need >= 3.10)")


def check_binary(c: Check, name: str):
    path = shutil.which(name)
    if not path:
        c.fail(name, "not on PATH")
        return
    try:
        result = subprocess.run(
            [name, "-version"], capture_output=True, text=True, timeout=5
        )
        version = result.stdout.splitlines()[0] if result.stdout else "unknown"
        c.ok(name, version[:70])
    except subprocess.SubprocessError as e:
        c.fail(name, str(e))


def check_imports(c: Check):
    for pkg in ("higgsfield_client", "scenedetect", "requests"):
        try:
            __import__(pkg)
            c.ok(f"import {pkg}")
        except ImportError as e:
            c.fail(f"import {pkg}", str(e))


def check_env(c: Check):
    if have_higgsfield_creds():
        c.ok("Higgsfield credentials set")
    else:
        c.fail("HF_KEY / HF_API_KEY_ID+HF_API_KEY_SECRET", "not set")


def check_claude_cli(c: Check):
    """Verify the claude CLI is available and responds (no API key needed)."""
    path = shutil.which("claude")
    if not path:
        c.fail("claude CLI", "not on PATH")
        return
    try:
        result = subprocess.run(
            ["claude", "-p", "--model", ANTHROPIC_MODEL, "Say 'ok' and nothing else."],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            reply = result.stdout.strip()[:40]
            c.ok(f"claude CLI ({ANTHROPIC_MODEL})", f"replied: {reply}")
        else:
            c.fail("claude CLI", (result.stderr or result.stdout).strip()[:120])
    except subprocess.TimeoutExpired:
        c.fail("claude CLI", "timed out after 30 s")
    except Exception as e:
        c.fail("claude CLI", str(e)[:120])


def _tiny_png() -> bytes:
    # 1x1 red PNG, hand-assembled to avoid a Pillow dependency.
    return bytes.fromhex(
        "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
        "890000000d49444154789c63f8cfc0f01f0005000100ff5c2d3d400000000049"
        "454e44ae426082"
    )


def check_higgsfield_upload(c: Check):
    try:
        import higgsfield_client
    except ImportError:
        c.skip("Higgsfield upload", "SDK not installed")
        return
    if not have_higgsfield_creds():
        c.skip("Higgsfield upload", "no credentials")
        return
    try:
        url = higgsfield_client.upload(_tiny_png(), "image/png")
        if isinstance(url, str) and url.startswith("http"):
            c.ok("Higgsfield upload", url[:70])
        else:
            c.fail("Higgsfield upload", f"unexpected return: {url!r}")
    except Exception as e:
        c.fail("Higgsfield upload", str(e)[:120])


def probe_model(c: Check, model: str, arguments: dict, label: str):
    try:
        import higgsfield_client
    except ImportError:
        c.skip(f"probe {label}", "SDK not installed")
        return
    try:
        ctrl = higgsfield_client.submit(model, arguments=arguments)
    except higgsfield_client.HiggsfieldClientError as e:
        msg = str(e)
        lower = msg.lower()
        if "404" in msg or "not found" in lower:
            c.fail(f"model path '{model}'", "model not found — check catalog")
        elif "400" in msg or "validation" in lower or "invalid" in lower:
            # Validation error — model exists but our probe args were incomplete.
            c.ok(f"model path '{model}'", "recognised (args rejected, as expected for probe)")
        else:
            c.fail(f"model path '{model}'", msg[:120])
        return
    except Exception as e:
        c.fail(f"model path '{model}'", f"unexpected: {e}"[:120])
        return

    # Submission accepted — model path is recognised by the API.
    request_id = getattr(ctrl, "request_id", None) or "unknown"
    c.ok(f"model path '{model}'", f"accepted submission {request_id}")

    # Try to cancel so we don't burn credits on the probe. Only works while
    # the job is still queued. Swallow errors; worst case the job completes
    # and is billed normally.
    try:
        time.sleep(1)
        ctrl.cancel()
        c.ok(f"cancel probe {label}", f"request {request_id}")
    except Exception as e:
        c.warn(f"cancel probe {label}", f"{e}"[:80] + " (may have been billed)")


def check_model_paths(c: Check, probe: bool):
    print(f"\nConfigured models:")
    print(f"  image edit  : {IMAGE_EDIT_MODEL}")
    print(f"  video i2v   : {VIDEO_I2V_MODEL}")
    print(f"  auth probe  : {PROBE_T2I_MODEL}")

    if not probe:
        print("  (re-run with --probe-models to test these paths live)")
        return

    if not have_higgsfield_creds():
        c.skip("model probes", "no credentials")
        return

    # 1. Known-good text-to-image — validates auth path end-to-end.
    probe_model(c, PROBE_T2I_MODEL, {
        "prompt": "a single red dot on white",
        "resolution": "1K",
        "aspect_ratio": "1:1",
    }, label="t2i (auth check)")

    # 2. Configured image-edit model. We don't upload a reference image —
    #    the submission will likely fail validation if required, but a 404
    #    on the path distinguishes "unknown model" from "bad args".
    probe_model(c, IMAGE_EDIT_MODEL, {
        "prompt": "no-op",
        "images_list": [],
        "resolution": "1K",
        "aspect_ratio": "1:1",
    }, label="image edit")

    # 3. Configured video model.
    probe_model(c, VIDEO_I2V_MODEL, {
        "prompt": "no-op",
        "image_url": "",
        "duration": 4,
        "resolution": "720p",
        "aspect_ratio": "16:9",
    }, label="video i2v")


def main():
    parser = argparse.ArgumentParser(description="Pre-flight connection test")
    parser.add_argument(
        "--probe-models",
        action="store_true",
        help="submit and cancel tiny jobs against each model (uses a small amount of credits)",
    )
    args = parser.parse_args()

    c = Check()
    print("=== Binaries ===")
    check_python(c)
    check_binary(c, "ffmpeg")
    check_binary(c, "ffprobe")

    print("\n=== Python packages ===")
    check_imports(c)

    print("\n=== Environment ===")
    check_env(c)

    print("\n=== Live checks ===")
    check_claude_cli(c)
    check_higgsfield_upload(c)

    print("\n=== Models ===")
    check_model_paths(c, args.probe_models)

    print(f"\nSummary: {c.failures} failure(s), {c.warnings} warning(s)")
    sys.exit(1 if c.failures else 0)


if __name__ == "__main__":
    main()
