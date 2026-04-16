"""
Main runner for the video remix pipeline. Executes the five steps in
sequence with checkpoint-based resume.

Usage:
  python scripts/remix.py <source_video> "remix prompt" [--with-audio] [--crossfade 0.3]
"""

import argparse
import subprocess
import sys
from pathlib import Path

from config import ensure_dirs, read_state

SCRIPTS_DIR = Path(__file__).resolve().parent

# (checkpoint written when step completes, script filename)
STEPS = [
    ("STATE_DECOMPOSE_COMPLETE", "decompose.py"),
    ("STATE_ANALYSE_COMPLETE", "analyse.py"),
    ("STATE_REGENERATE_COMPLETE", "regenerate.py"),
    ("STATE_GENERATE_COMPLETE", "generate_video.py"),
    ("STATE_ASSEMBLE_COMPLETE", "assemble.py"),
]


def parse_args():
    parser = argparse.ArgumentParser(description="Video remix pipeline")
    parser.add_argument("source_video", help="path to source video")
    parser.add_argument("remix_prompt", help="high-level remix brief")
    parser.add_argument("--with-audio", action="store_true",
                        help="overlay original audio onto the final video")
    parser.add_argument("--crossfade", type=float, default=0.3,
                        help="crossfade duration between shots (seconds)")
    return parser.parse_args()


def run_step(script: str, extra: list[str]):
    cmd = [sys.executable, str(SCRIPTS_DIR / script), *extra]
    print(f"\n{'='*60}\nRUNNING: {' '.join(cmd)}\n{'='*60}\n", flush=True)
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"\nERROR: {script} failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def step_args(script: str, args: argparse.Namespace) -> list[str]:
    if script == "decompose.py":
        return [args.source_video]
    if script == "analyse.py":
        return [args.remix_prompt]
    if script == "assemble.py":
        extra = [f"--crossfade={args.crossfade}"]
        if args.with_audio:
            extra.append("--with-audio")
        return extra
    return []


def main():
    args = parse_args()
    if not Path(args.source_video).exists():
        raise SystemExit(f"ERROR: source video not found: {args.source_video}")
    ensure_dirs()

    state_order = [s[0] for s in STEPS]
    current = read_state()
    resume_idx = state_order.index(current) + 1 if current in state_order else 0
    if current:
        print(f"Resuming from checkpoint: {current}")

    for i, (_, script) in enumerate(STEPS):
        if i < resume_idx:
            print(f"Skipping {script} (already complete)")
            continue
        run_step(script, step_args(script, args))

    print(f"\n{'='*60}\nREMIX COMPLETE\nOutput: ./output/remix_final.mp4\n{'='*60}")


if __name__ == "__main__":
    main()
