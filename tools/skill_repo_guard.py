#!/usr/bin/env python3
"""Guard a Git-backed Hermes external skill directory against drift and shadows."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

FRONTMATTER_NAME = re.compile(r"(?m)^name:\s*[\"']?([^\"'\n]+)")
CLUTTER_DIRS = {"node_modules", "__pycache__", ".pytest_cache"}
CLUTTER_SUFFIXES = {".bak", ".backup", ".tmp", ".orig"}


def inventory_skills(root: Path) -> dict[str, Path]:
    root = root.resolve()
    result: dict[str, Path] = {}
    for skill_file in sorted(root.rglob("SKILL.md")):
        if ".git" in skill_file.parts or any(part in CLUTTER_DIRS for part in skill_file.parts):
            continue
        text = skill_file.read_text(errors="ignore")[:4000]
        match = FRONTMATTER_NAME.search(text)
        if not match:
            raise ValueError(f"missing skill name: {skill_file}")
        name = match.group(1).strip()
        if name in result:
            raise ValueError(f"duplicate skill name {name}: {result[name]} and {skill_file.parent}")
        result[name] = skill_file.parent
    return result


def find_shadows(repo_root: Path, profile_skills: Path) -> list[dict[str, object]]:
    canonical = inventory_skills(repo_root)
    local = inventory_skills(profile_skills)
    return [
        {"name": name, "canonical": canonical[name], "shadow": local[name]}
        for name in sorted(canonical.keys() & local.keys())
    ]


def config_has_external_dir(config_path: Path, repo_root: Path) -> bool:
    if not config_path.is_file():
        return False
    target = str(repo_root.resolve())
    for raw in config_path.read_text(errors="ignore").splitlines():
        value = raw.strip().removeprefix("-").strip().strip("\"").strip("'")
        if value.rstrip("/") == target.rstrip("/"):
            return True
    return False


def find_generated_clutter(repo_root: Path) -> list[Path]:
    found: list[Path] = []
    for path in repo_root.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_dir() and path.name in CLUTTER_DIRS:
            found.append(path)
        elif path.is_file() and path.suffix.lower() in CLUTTER_SUFFIXES:
            found.append(path)
    return sorted(found)


def render_alerts(alerts: Iterable[dict[str, str]]) -> str:
    items = list(alerts)
    if not items:
        return ""
    lines = ["SKILL REPOSITORY DRIFT"]
    lines.extend(f"- {item['code']}: {item['detail']}" for item in items)
    return "\n".join(lines)


def divergence_alerts(counts_text: str) -> list[dict[str, str]]:
    counts = counts_text.split()
    local_only, remote_only = int(counts[0]), int(counts[1])
    alerts: list[dict[str, str]] = []
    if local_only:
        alerts.append({"code": "unpushed_commits", "detail": f"{local_only} commits"})
    if remote_only:
        alerts.append({"code": "repository_behind", "detail": f"{remote_only} commits"})
    return alerts


def run_git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )
    if check and result.returncode:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def load_manifest(path: Path) -> dict:
    data = json.loads(path.read_text())
    if data.get("version") != 1 or data.get("mode") != "external_dir":
        raise ValueError("manifest must use version 1 and mode external_dir")
    return data


def audit(manifest_path: Path, fetch: bool = False, include_shadows: bool = True) -> list[dict[str, str]]:
    manifest_path = manifest_path.resolve()
    manifest = load_manifest(manifest_path)
    repo = (manifest_path.parent / manifest["repository"]).resolve()
    alerts: list[dict[str, str]] = []

    if fetch:
        result = subprocess.run(["git", "fetch", "origin", "--prune"], cwd=repo, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if result.returncode:
            alerts.append({"code": "fetch_failed", "detail": result.stderr.strip().splitlines()[-1]})

    dirty = run_git(repo, "status", "--porcelain=v1").splitlines()
    if dirty:
        alerts.append({"code": "repository_dirty", "detail": f"{len(dirty)} paths"})

    branch = run_git(repo, "branch", "--show-current")
    if not branch:
        alerts.append({"code": "detached_head", "detail": run_git(repo, "rev-parse", "--short", "HEAD")})

    try:
        alerts.extend(divergence_alerts(run_git(repo, "rev-list", "--left-right", "--count", "HEAD...origin/main")))
    except (RuntimeError, ValueError, IndexError):
        alerts.append({"code": "remote_comparison_failed", "detail": "cannot compare HEAD with origin/main"})

    clutter = find_generated_clutter(repo)
    if clutter:
        sample = ", ".join(str(p.relative_to(repo)) for p in clutter[:5])
        alerts.append({"code": "repository_clutter", "detail": sample})

    try:
        inventory_skills(repo)
    except ValueError as exc:
        alerts.append({"code": "repository_skill_inventory_invalid", "detail": str(exc)})

    for profile in manifest["profiles"]:
        profile_root = Path(profile["skills_root"]).resolve()
        config = Path(profile["config"]).resolve()
        name = profile["name"]
        if not config_has_external_dir(config, repo):
            alerts.append({"code": "external_dir_missing", "detail": name})
        if include_shadows:
            try:
                for shadow in find_shadows(repo, profile_root):
                    alerts.append({"code": "skill_shadow", "detail": f"{name}:{shadow['name']}"})
            except ValueError as exc:
                alerts.append({"code": "profile_skill_inventory_invalid", "detail": f"{name}:{exc}"})
    return alerts


def remove_shadows(manifest_path: Path, execute: bool) -> list[str]:
    manifest_path = manifest_path.resolve()
    manifest = load_manifest(manifest_path)
    repo = (manifest_path.parent / manifest["repository"]).resolve()
    blockers = audit(manifest_path, fetch=True, include_shadows=False)
    if blockers:
        raise RuntimeError(render_alerts(blockers))
    removed: list[str] = []
    for profile in manifest["profiles"]:
        root = Path(profile["skills_root"]).resolve()
        for item in find_shadows(repo, root):
            shadow = Path(item["shadow"]).resolve()
            if root not in shadow.parents or not (shadow / "SKILL.md").is_file():
                raise RuntimeError(f"unsafe shadow path: {shadow}")
            removed.append(str(shadow))
            if execute:
                shutil.rmtree(shadow)
    return removed


def default_manifest() -> Path:
    return Path(__file__).with_name("skill-repo-manifest.json")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["audit", "preflight", "remove-shadows"])
    parser.add_argument("--manifest", type=Path, default=default_manifest())
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        if args.command in {"audit", "preflight"}:
            text = render_alerts(audit(args.manifest, fetch=args.fetch))
            if text:
                print(text)
                return 1
            return 0
        removed = remove_shadows(args.manifest, args.execute)
        if not args.execute:
            for path in removed:
                print(f"WOULD REMOVE SHADOW: {path}")
        else:
            for path in removed:
                print(f"REMOVED SHADOW: {path}")
        return 0
    except Exception as exc:
        print(f"SKILL REPOSITORY GUARD ERROR: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
