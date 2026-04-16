"""
video-remix/scripts/remix.py
Main runner — executes the full video remix pipeline with resume support.

Usage: python scripts/remix.py <source_video> "remix prompt" [--with-audio]
"""

import sys
import subprocess
from config import read_state, ensure_dirs

STEPS = [
    ("STATE_DECOMPOSE_COMPLETE", "decompose"),
    ("STATE_ANALYSE_COMPLETE", "analyse"),
    ("STATE_REGENERATE_COMPLETE", "regenerate"),
    ("STATE_GENERATE_COMPLETE", "generate_video"),
    ("STATE_ASSEMBLE_COMPLETE", "assemble"),
]


def run_step(script: str, args: list[str] = None):
    cmd = [sys.executable, f"scripts/{script}.py"] + (args or [])
    print(f"\n{'='*60}")
    print(f"RUNNING: {' '.join(cmd)}")
    print(f"{'='*60}\n")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"\nERROR: {script} failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def main():
    if len(sys.argv) < 3:
        print('Usage: python scripts/remix.py <source_video> "remix prompt" [--with-audio]')
        sys.exit(1)

    source_video = sys.argv[1]
    remix_prompt = sys.argv[2]
    extra_args = sys.argv[3:]
    with_audio = "--with-audio" in extra_args

    ensure_dirs()

    # Determine resume point
    current_state = read_state()
    state_order = [s[0] for s in STEPS]

    if current_state and current_state in state_order:
        resume_idx = state_order.index(current_state) + 1
        print(f"Resuming from checkpoint: {current_state}")
        print(f"Skipping to step {resume_idx + 1} of {len(STEPS)}")
    else:
        resume_idx = 0

    # Execute pipeline
    for i, (checkpoint, script) in enumerate(STEPS):
        if i < resume_idx:
            print(f"Skipping {script} (already complete)")
            continue

        if script == "decompose":
            run_step(script, [source_video])
        elif script == "analyse":
            run_step(script, [remix_prompt])
        elif script == "assemble":
            assemble_args = ["--with-audio"] if with_audio else []
            run_step(script, assemble_args)
        else:
            run_step(script)

    print(f"\n{'='*60}")
    print("REMIX COMPLETE")
    print(f"Output: ./output/remix_final.mp4")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
