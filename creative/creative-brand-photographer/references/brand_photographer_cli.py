#!/usr/bin/env python3
"""
Brand Photographer — CLI

Brand-agnostic CLI for the Brand Photographer agent. Select which
configured brand to work for, then choose a shot (or run the full
brand-specific grid) through the generate → critique → revise loop.

Usage:
    python3 brand_photographer_cli.py [brand_id] [shot_index]

    # Interactive
    python3 brand_photographer_cli.py

    # Direct
    python3 brand_photographer_cli.py bower 1

Environment:
    OPENROUTER_API_KEY or (HF_KEY + HF_SECRET)
    ANTHROPIC_API_KEY
"""

import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from brand_photographer_api import BrandPhotographer, BrandNotConfiguredError  # noqa: E402


def pick_brand() -> str:
    brands = BrandPhotographer.list_brands()
    if not brands:
        print("ERROR: No brands configured. Run the onboarding flow to add one.")
        sys.exit(1)

    if len(sys.argv) > 1 and sys.argv[1] in brands:
        return sys.argv[1]

    print("\n  Configured brands:")
    for i, b in enumerate(brands, 1):
        cfg = BrandPhotographer.load_brand_config(b)
        print(f"    {i}. {cfg['brand_name']} ({b}) — {cfg.get('description', '')[:60]}")
    print("    0. Exit")

    choice = input("\n  Select brand (number): ").strip()
    if choice == "0":
        sys.exit(0)
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(brands):
            return brands[idx]
    except ValueError:
        pass
    print("Invalid choice")
    sys.exit(1)


def pick_shot(photographer: BrandPhotographer) -> tuple[str, str]:
    """Return (shot_id, ratio). Empty shot_id means 'run the full grid'."""
    library = photographer.get_library()
    grid_pattern = photographer.config["grid_pattern"]

    print(f"\n  Shots in {photographer.config['brand_name']}'s library:")
    for i, entry in enumerate(library, 1):
        s = entry.get("score")
        score_str = f"{s}/10" if s else "draft"
        print(f"    {i}. {entry.get('shot_name', entry['shot_id'])} [{score_str}]")
    print(f"    {len(library)+1}. Run full grid ({len(grid_pattern)} shots)")
    print("    0. Exit")

    choice_raw = sys.argv[2] if len(sys.argv) > 2 else input("\n  Select shot (number): ").strip()
    if choice_raw == "0":
        sys.exit(0)
    try:
        idx = int(choice_raw) - 1
        if idx == len(library):
            return ("", "")  # full grid
        if 0 <= idx < len(library):
            entry = library[idx]
            return (entry["shot_id"], entry.get("ratio", "3:4"))
    except ValueError:
        pass
    print("Invalid choice")
    sys.exit(1)


def main():
    brand_id = pick_brand()
    try:
        photographer = BrandPhotographer(brand_id=brand_id)
    except BrandNotConfiguredError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    summary = photographer.brand_summary()
    print("\n" + "=" * 60)
    print("  BRAND PHOTOGRAPHER")
    print(f"  Brand: {summary['brand_name']} ({summary['brand_id']})")
    print(f"  Backend: {summary['backend']} · Model: {summary['model']}")
    print(f"  Critic: {summary.get('critic_mode', 'api')} mode")
    print(f"  Threshold: {summary['pass_threshold']}/10 · Max iterations: {summary['max_iterations']}")
    print(f"  Library: {summary['library_size']} prompts")
    print("=" * 60)

    shot_id, ratio = pick_shot(photographer)

    if not shot_id:
        print("\n  Running full grid...")
        results = photographer.generate_grid()
    else:
        print(f"\n  Running shot: {shot_id}")
        results = [photographer.generate(shot_id, ratio=ratio or "3:4")]

    print("\n" + "=" * 60)
    print("  SESSION COMPLETE")
    print("=" * 60)
    for r in results:
        score = r.get("score", "?")
        url = r.get("image_url", "")
        print(f"  • {r.get('shot_id')}: {score}/10 — {url}")


if __name__ == "__main__":
    main()
