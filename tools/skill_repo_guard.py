#!/usr/bin/env python3
"""Guard a Git-backed Hermes external skill directory against drift and shadows."""

from __future__ import annotations

import argparse
import ast
from contextlib import contextmanager
import fcntl
import json
import re
import shutil
import subprocess
import sys
import tempfile
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


def run_git_result(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=repo, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )


@contextmanager
def repository_lock(repo: Path):
    common_dir = Path(run_git(repo, "rev-parse", "--git-common-dir"))
    if not common_dir.is_absolute():
        common_dir = (repo / common_dir).resolve()
    lock_path = common_dir / "skill-repository-reconcile.lock"
    with lock_path.open("w") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("another skill repository reconciliation is active") from exc
        yield


def validate_python_syntax(repo: Path) -> None:
    for path in sorted(repo.rglob("*.py")):
        if ".git" in path.parts or any(part in CLUTTER_DIRS for part in path.parts):
            continue
        try:
            ast.parse(path.read_text(errors="strict"), filename=str(path))
        except (SyntaxError, UnicodeError) as exc:
            raise RuntimeError(f"python syntax validation failed: {path.relative_to(repo)}: {exc}") from exc


def validate_reconcile_candidate(repo: Path, manifest: dict, check_profiles: bool = True) -> None:
    clutter = find_generated_clutter(repo)
    if clutter:
        sample = ", ".join(str(path.relative_to(repo)) for path in clutter[:5])
        raise RuntimeError(f"generated repository clutter requires cleanup: {sample}")
    inventory_skills(repo)
    validate_python_syntax(repo)
    if not check_profiles:
        return
    for profile in manifest["profiles"]:
        profile_root = Path(profile["skills_root"]).resolve()
        config = Path(profile["config"]).resolve()
        if not config_has_external_dir(config, repo):
            raise RuntimeError(f"external skill directory missing for profile: {profile['name']}")
        shadows = find_shadows(repo, profile_root)
        if shadows:
            names = ", ".join(f"{profile['name']}:{item['name']}" for item in shadows[:5])
            raise RuntimeError(f"skill shadows require semantic reconciliation: {names}")


def is_skill_owned_path(repo: Path, relative_path: str) -> bool:
    path = (repo / relative_path).resolve()
    try:
        path.relative_to(repo)
    except ValueError:
        return False
    parent = path.parent
    while parent != repo and repo in parent.parents:
        if (parent / "SKILL.md").is_file():
            return True
        parent = parent.parent
    return (repo / "SKILL.md").is_file()


def safe_tracked_modifications(repo: Path) -> list[str]:
    result = run_git_result(repo, "status", "--porcelain=v1", "-z")
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git status failed")
    entries = [entry for entry in result.stdout.split("\0") if entry]
    if not entries:
        return []
    if len(entries) > 50:
        raise RuntimeError("too many changed paths for automatic reconciliation")
    paths: list[str] = []
    for entry in entries:
        status, relative = entry[:2], entry[3:]
        if status == "??":
            raise RuntimeError(f"untracked path requires classification: {relative}")
        if status != " M":
            raise RuntimeError(
                "only safe unstaged skill modifications can be reconciled automatically"
            )
        if not is_skill_owned_path(repo, relative):
            raise RuntimeError(f"changed path is not skill-owned: {relative}")
        paths.append(relative)
    if run_git(repo, "diff", "--summary"):
        raise RuntimeError("renames, deletions, type changes and mode changes require review")
    for line in run_git(repo, "diff", "--numstat").splitlines():
        if line.startswith("-\t-"):
            raise RuntimeError("binary skill changes require review")
    return paths


@contextmanager
def candidate_worktree(repo: Path):
    path = Path(tempfile.mkdtemp(prefix="skill-reconcile-candidate-"))
    result = run_git_result(repo, "worktree", "add", "--detach", str(path), "origin/main")
    if result.returncode:
        shutil.rmtree(path, ignore_errors=True)
        raise RuntimeError(result.stderr.strip() or "candidate worktree creation failed")
    try:
        yield path
    finally:
        run_git_result(repo, "worktree", "remove", "--force", str(path))
        shutil.rmtree(path, ignore_errors=True)


def reconcile(manifest_path: Path, fetch: bool = False, execute: bool = False) -> list[str]:
    manifest_path = manifest_path.resolve()
    manifest = load_manifest(manifest_path)
    repo = (manifest_path.parent / manifest["repository"]).resolve()
    messages: list[str] = []

    with repository_lock(repo):
        if fetch:
            result = run_git_result(repo, "fetch", "origin", "--prune")
            if result.returncode:
                raise RuntimeError(result.stderr.strip() or "git fetch failed")

        branch = run_git(repo, "branch", "--show-current")
        if branch != "main":
            raise RuntimeError(
                f"automatic reconciliation requires the main branch, found: {branch or 'detached HEAD'}"
            )

        validate_reconcile_candidate(repo, manifest)
        preexisting_local_commits = run_git(
            repo, "rev-list", "origin/main..HEAD"
        ).splitlines()
        if preexisting_local_commits:
            raise RuntimeError(
                "pre-existing local commits require semantic review before reconciliation"
            )
        changed_paths = safe_tracked_modifications(repo)
        if changed_paths:
            if run_git_result(repo, "diff", "--check").returncode:
                raise RuntimeError("unstaged diff check failed")
            if not execute:
                messages.append("would_checkpoint_tracked_changes")
            else:
                checkpoint_parent = run_git(repo, "rev-parse", "HEAD")
                original_patch = run_git_result(
                    repo, "diff", "--binary", "--", *changed_paths
                ).stdout
                if safe_tracked_modifications(repo) != changed_paths:
                    raise RuntimeError("tracked skill changes moved during reconciliation")
                run_git(repo, "add", "--", *changed_paths)
                staged_patch = run_git_result(
                    repo, "diff", "--cached", "--binary", "--", *changed_paths
                ).stdout
                if staged_patch != original_patch or run_git(repo, "diff", "--", *changed_paths):
                    run_git_result(repo, "reset")
                    raise RuntimeError(
                        "tracked skill changes moved while staging; working copy was preserved"
                    )
                staged_status = run_git_result(
                    repo, "status", "--porcelain=v1", "-z"
                ).stdout
                expected_status = "".join(f"M  {path}\0" for path in changed_paths)
                if staged_status != expected_status:
                    run_git_result(repo, "reset")
                    raise RuntimeError(
                        "repository changed while staging; working copy was preserved"
                    )
                result = run_git_result(
                    repo,
                    "-c", "core.hooksPath=/dev/null",
                    "-c", "commit.gpgSign=false",
                    "commit", "-m", "chore: reconcile durable skill repository drift"
                )
                if result.returncode:
                    raise RuntimeError(result.stderr.strip() or "tracked-change checkpoint failed")
                checkpoint_sha = run_git(repo, "rev-parse", "HEAD")
                checkpoint_parents = run_git(repo, "show", "-s", "--format=%P", checkpoint_sha)
                committed_paths = run_git(
                    repo, "diff", "--name-only", checkpoint_parent, checkpoint_sha
                ).splitlines()
                committed_patch = run_git_result(
                    repo, "diff", "--binary", checkpoint_parent, checkpoint_sha, "--", *changed_paths
                ).stdout
                if (
                    checkpoint_parents != checkpoint_parent
                    or committed_paths != changed_paths
                    or committed_patch != original_patch
                ):
                    run_git(repo, "reset", "--mixed", checkpoint_parent)
                    raise RuntimeError(
                        "checkpoint commit differed from the approved patch; working copy was preserved"
                    )
                messages.append("checkpointed_tracked_changes")

        local_only, remote_only = map(
            int, run_git(repo, "rev-list", "--left-right", "--count", "HEAD...origin/main").split()
        )
        if not execute:
            if remote_only:
                messages.append("would_integrate_onto_origin_main" if local_only else "would_fast_forward")
            if local_only:
                messages.append("would_push_main")
            return messages

        if run_git(repo, "status", "--porcelain=v1"):
            raise RuntimeError("repository remained dirty after checkpoint")
        validate_reconcile_candidate(repo, manifest)
        if run_git(repo, "rev-list", "--merges", "origin/main..HEAD"):
            raise RuntimeError("local merge commits require manual reconciliation")
        local_commits = run_git(
            repo, "rev-list", "--reverse", "origin/main..HEAD"
        ).splitlines()

        with candidate_worktree(repo) as candidate:
            for commit in local_commits:
                result = run_git_result(candidate, "cherry-pick", commit)
                if result.returncode:
                    run_git_result(candidate, "cherry-pick", "--abort")
                    raise RuntimeError(
                        "candidate integration conflicted; live checkpoint was preserved"
                    )
            validate_reconcile_candidate(candidate, manifest, check_profiles=False)
            candidate_sha = run_git(candidate, "rev-parse", "HEAD")
            remote_sha = run_git(repo, "rev-parse", "origin/main")
            if candidate_sha != remote_sha:
                result = run_git_result(
                    candidate, "push", "origin", "HEAD:refs/heads/main"
                )
                if result.returncode:
                    raise RuntimeError(result.stderr.strip() or "fast-forward push to main failed")
                messages.append("pushed_main")
                messages.append("integrated_onto_origin_main")
            elif remote_only:
                messages.append("fast_forwarded")

        result = run_git_result(repo, "fetch", "origin", "--prune")
        if result.returncode:
            raise RuntimeError(
                result.stderr.strip() or "post-push fetch failed; live checkpoint preserved"
            )
        remote_sha = run_git(repo, "rev-parse", "origin/main")
        if remote_sha != candidate_sha:
            raise RuntimeError("remote verification failed; live checkpoint preserved")
        checkpoint_sha = run_git(repo, "rev-parse", "HEAD")
        run_git(
            repo, "update-ref", f"refs/skill-reconcile/backups/{checkpoint_sha[:12]}", checkpoint_sha
        )
        if run_git(repo, "status", "--porcelain=v1"):
            raise RuntimeError(
                "live checkout changed during reconciliation; concurrent edits were preserved"
            )
        reset = run_git_result(repo, "reset", "--keep", candidate_sha)
        if reset.returncode:
            raise RuntimeError(
                reset.stderr.strip()
                or "live synchronization refused to overwrite concurrent edits"
            )
        if run_git(repo, "rev-parse", "HEAD") != run_git(repo, "rev-parse", "origin/main"):
            raise RuntimeError("live synchronization failed after verified publication")
        if run_git(repo, "status", "--porcelain=v1"):
            raise RuntimeError("live synchronization left a dirty repository")
        return messages


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
    parser.add_argument("command", choices=["audit", "preflight", "reconcile", "remove-shadows"])
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
        if args.command == "reconcile":
            actions = reconcile(args.manifest, fetch=args.fetch, execute=args.execute)
            if actions:
                prefix = "SKILL REPOSITORY RECONCILED" if args.execute else "SKILL REPOSITORY RECONCILIATION PLAN"
                print(prefix)
                for action in actions:
                    print(f"- {action}")
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
