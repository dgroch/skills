import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("skill_repo_guard.py")
spec = importlib.util.spec_from_file_location("skill_repo_guard", MODULE_PATH)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class SkillRepoGuardTests(unittest.TestCase):
    def run_git(self, repo: Path, *args: str) -> str:
        result = subprocess.run(
            ["git", *args], cwd=repo, text=True, capture_output=True, check=True
        )
        return result.stdout.strip()

    def make_reconcile_fixture(
        self, root: Path, profiles: list[dict[str, str]] | None = None
    ) -> tuple[Path, Path, Path]:
        remote = root / "remote.git"
        seed = root / "seed"
        repo = root / "repo"
        self.run_git(root, "init", "--bare", str(remote))
        self.run_git(root, "init", "-b", "main", str(seed))
        self.run_git(seed, "config", "user.name", "Test User")
        self.run_git(seed, "config", "user.email", "test@example.com")
        (seed / "tools").mkdir()
        (seed / "tools" / "skill-repo-manifest.json").write_text(json.dumps({
            "version": 1,
            "mode": "external_dir",
            "repository": "..",
            "profiles": profiles or [],
        }))
        self.make_skill(seed, "example", "example-skill")
        self.run_git(seed, "add", ".")
        self.run_git(seed, "commit", "-m", "initial")
        self.run_git(seed, "remote", "add", "origin", str(remote))
        self.run_git(seed, "push", "-u", "origin", "main")
        self.run_git(remote, "symbolic-ref", "HEAD", "refs/heads/main")
        self.run_git(root, "clone", str(remote), str(repo))
        self.run_git(repo, "config", "user.name", "Test User")
        self.run_git(repo, "config", "user.email", "test@example.com")
        return remote, seed, repo

    def make_skill(self, root: Path, rel: str, name: str, body: str = "body") -> Path:
        path = root / rel
        path.mkdir(parents=True, exist_ok=True)
        (path / "SKILL.md").write_text(f"---\nname: {name}\ndescription: test\n---\n{body}\n")
        return path

    def test_inventory_uses_frontmatter_name_not_relative_path(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            skill = self.make_skill(root, "operations/example-folder", "example-skill")
            self.assertEqual(guard.inventory_skills(root), {"example-skill": skill})

    def test_inventory_rejects_duplicate_names(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.make_skill(root, "one", "duplicate")
            self.make_skill(root, "two", "duplicate")
            with self.assertRaisesRegex(ValueError, "duplicate skill name"):
                guard.inventory_skills(root)

    def test_shadow_detection_matches_names_across_different_paths(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo, profile = root / "repo", root / "profile"
            canonical = self.make_skill(repo, "operations/canonical", "same-name")
            shadow = self.make_skill(profile, "other/location", "same-name")
            result = guard.find_shadows(repo, profile)
            self.assertEqual(result, [{"name": "same-name", "canonical": canonical, "shadow": shadow}])

    def test_external_dir_check_reads_profile_config(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            repo.mkdir()
            config = root / "config.yaml"
            config.write_text(f"skills:\n  external_dirs:\n    - {repo}\n")
            self.assertTrue(guard.config_has_external_dir(config, repo))
            self.assertFalse(guard.config_has_external_dir(config, root / "other"))

    def test_external_dir_check_ignores_unrelated_yaml_values(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            repo.mkdir()
            config = root / "config.yaml"
            config.write_text(f"other_paths:\n  - ~\nskills:\n  external_dirs:\n    - {repo}\nother: value\n")
            self.assertTrue(guard.config_has_external_dir(config, repo))

    def test_healthy_report_is_silent(self):
        self.assertEqual(guard.render_alerts([]), "")

    def test_drift_report_has_stable_codes(self):
        alerts = [
            {"code": "repository_dirty", "detail": "2 paths"},
            {"code": "skill_shadow", "detail": "example-skill"},
        ]
        text = guard.render_alerts(alerts)
        self.assertIn("SKILL REPOSITORY DRIFT", text)
        self.assertIn("repository_dirty: 2 paths", text)
        self.assertIn("skill_shadow: example-skill", text)

    def test_git_divergence_maps_local_only_to_unpushed(self):
        alerts = guard.divergence_alerts("3\t2")
        self.assertEqual(alerts, [
            {"code": "unpushed_commits", "detail": "3 commits"},
            {"code": "repository_behind", "detail": "2 commits"},
        ])

    def test_generated_clutter_detection(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "skill" / "node_modules").mkdir(parents=True)
            (root / "skill" / "backup.bak").write_text("x")
            found = {p.relative_to(root).as_posix() for p in guard.find_generated_clutter(root)}
            self.assertEqual(found, {"skill/node_modules", "skill/backup.bak"})

    def test_reconcile_fast_forwards_clean_repository_behind_main(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            remote, seed, repo = self.make_reconcile_fixture(root)
            (seed / "remote.txt").write_text("new upstream\n")
            self.run_git(seed, "add", "remote.txt")
            self.run_git(seed, "commit", "-m", "remote update")
            self.run_git(seed, "push", "origin", "main")

            messages = guard.reconcile(
                repo / "tools" / "skill-repo-manifest.json", fetch=True, execute=True
            )

            self.assertIn("fast_forwarded", messages)
            self.assertEqual(
                self.run_git(repo, "rev-parse", "HEAD"),
                self.run_git(repo, "rev-parse", "origin/main"),
            )
            self.assertEqual(self.run_git(repo, "status", "--porcelain"), "")

    def test_reconcile_refuses_upstream_candidate_with_profile_shadow(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            profile_root = root / "profile-skills"
            config = root / "profile-config.yaml"
            profiles = [{
                "name": "test-profile",
                "skills_root": str(profile_root),
                "config": str(config),
            }]
            _, seed, repo = self.make_reconcile_fixture(root, profiles=profiles)
            config.write_text(f"skills:\n  external_dirs:\n    - {repo}\n")
            self.make_skill(profile_root, "local-shadow", "upstream-shadow")
            self.make_skill(seed, "upstream/new-skill", "upstream-shadow")
            self.run_git(seed, "add", "upstream/new-skill/SKILL.md")
            self.run_git(seed, "commit", "-m", "upstream shadow")
            self.run_git(seed, "push", "origin", "main")
            original_head = self.run_git(repo, "rev-parse", "HEAD")

            with self.assertRaisesRegex(RuntimeError, "skill shadows require semantic reconciliation"):
                guard.reconcile(
                    repo / "tools" / "skill-repo-manifest.json", fetch=True, execute=True
                )

            self.assertEqual(self.run_git(repo, "rev-parse", "HEAD"), original_head)
            self.assertFalse((repo / "upstream" / "new-skill" / "SKILL.md").exists())

    def test_reconcile_checkpoints_tracked_changes_rebases_and_pushes_main(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            remote, seed, repo = self.make_reconcile_fixture(root)
            (seed / "remote.txt").write_text("new upstream\n")
            self.run_git(seed, "add", "remote.txt")
            self.run_git(seed, "commit", "-m", "remote update")
            self.run_git(seed, "push", "origin", "main")
            skill = repo / "example" / "SKILL.md"
            skill.write_text(skill.read_text() + "local durable correction\n")

            messages = guard.reconcile(
                repo / "tools" / "skill-repo-manifest.json", fetch=True, execute=True
            )

            self.assertIn("checkpointed_tracked_changes", messages)
            self.assertIn("integrated_onto_origin_main", messages)
            self.assertIn("pushed_main", messages)
            remote_main = self.run_git(remote, "rev-parse", "refs/heads/main")
            self.assertEqual(self.run_git(repo, "rev-parse", "HEAD"), remote_main)
            self.assertIn("local durable correction", skill.read_text())
            self.assertEqual(self.run_git(repo, "status", "--porcelain"), "")

    def test_reconcile_refuses_unknown_untracked_files(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, repo = self.make_reconcile_fixture(root)
            (repo / "unknown.txt").write_text("do not guess\n")

            with self.assertRaisesRegex(RuntimeError, "untracked"):
                guard.reconcile(
                    repo / "tools" / "skill-repo-manifest.json", fetch=True, execute=True
                )

    def test_reconcile_refuses_feature_branch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, repo = self.make_reconcile_fixture(root)
            self.run_git(repo, "switch", "-c", "feature/unsafe")

            with self.assertRaisesRegex(RuntimeError, "main branch"):
                guard.reconcile(
                    repo / "tools" / "skill-repo-manifest.json", fetch=True, execute=True
                )

    def test_reconcile_refuses_staged_skill_change(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, repo = self.make_reconcile_fixture(root)
            skill = repo / "example" / "SKILL.md"
            skill.write_text(skill.read_text() + "\nstaged\n")
            self.run_git(repo, "add", str(skill.relative_to(repo)))
            with self.assertRaisesRegex(RuntimeError, "safe unstaged skill modifications"):
                guard.reconcile(repo / "tools" / "skill-repo-manifest.json", fetch=True, execute=True)

    def test_reconcile_refuses_skill_rename(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, repo = self.make_reconcile_fixture(root)
            self.run_git(repo, "mv", "example/SKILL.md", "example/RENAMED.md")
            with self.assertRaisesRegex(RuntimeError, "safe unstaged skill modifications"):
                guard.reconcile(repo / "tools" / "skill-repo-manifest.json", fetch=True, execute=True)

    def test_reconcile_refuses_mode_change(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, repo = self.make_reconcile_fixture(root)
            skill = repo / "example" / "SKILL.md"
            skill.chmod(0o755)
            with self.assertRaisesRegex(RuntimeError, "mode changes"):
                guard.reconcile(repo / "tools" / "skill-repo-manifest.json", fetch=True, execute=True)

    def test_reconcile_refuses_binary_skill_change(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, repo = self.make_reconcile_fixture(root)
            skill = repo / "example" / "SKILL.md"
            skill.write_bytes(skill.read_bytes() + b"\x00binary\n")
            with self.assertRaisesRegex(RuntimeError, "binary skill changes"):
                guard.reconcile(repo / "tools" / "skill-repo-manifest.json", fetch=True, execute=True)

    def test_reconcile_preserves_concurrent_live_edit(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            remote, _, repo = self.make_reconcile_fixture(root)
            skill = repo / "example" / "SKILL.md"
            skill.write_text(skill.read_text() + "\napproved correction\n")
            hook = remote / "hooks" / "pre-receive"
            hook.write_text(
                f"#!/bin/sh\nprintf '\\nconcurrent edit\\n' >> '{skill}'\nexit 0\n"
            )
            hook.chmod(0o755)

            with self.assertRaisesRegex(RuntimeError, "concurrent edits were preserved"):
                guard.reconcile(repo / "tools" / "skill-repo-manifest.json", fetch=True, execute=True)

            self.assertIn("concurrent edit", skill.read_text())

    def test_reconcile_refuses_tracked_deletion(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, repo = self.make_reconcile_fixture(root)
            (repo / "example" / "SKILL.md").unlink()

            with self.assertRaisesRegex(RuntimeError, "safe unstaged skill modifications"):
                guard.reconcile(
                    repo / "tools" / "skill-repo-manifest.json", fetch=True, execute=True
                )

    def test_reconcile_refuses_preexisting_local_commit_with_skill_deletion(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, repo = self.make_reconcile_fixture(root)
            (repo / "example" / "SKILL.md").unlink()
            self.run_git(repo, "add", "-u")
            self.run_git(repo, "commit", "-m", "delete canonical skill")

            with self.assertRaisesRegex(RuntimeError, "pre-existing local commits"):
                guard.reconcile(
                    repo / "tools" / "skill-repo-manifest.json", fetch=True, execute=True
                )

            self.assertFalse((repo / "example" / "SKILL.md").exists())
            remote_tree = self.run_git(
                root / "remote.git", "ls-tree", "-r", "--name-only", "refs/heads/main"
            )
            self.assertIn("example/SKILL.md", remote_tree)

    def test_reconcile_disables_commit_hooks_that_stage_prohibited_paths(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, repo = self.make_reconcile_fixture(root)
            manifest = repo / "tools" / "skill-repo-manifest.json"
            hook = repo / ".git" / "hooks" / "pre-commit"
            hook.write_text(
                "#!/bin/sh\n"
                "printf '\\n' >> tools/skill-repo-manifest.json\n"
                "git add tools/skill-repo-manifest.json\n"
            )
            hook.chmod(0o755)
            skill = repo / "example" / "SKILL.md"
            skill.write_text(skill.read_text() + "\nAllowed correction.\n")

            messages = guard.reconcile(manifest, fetch=True, execute=True)

            self.assertIn("pushed_main", messages)
            self.assertEqual(json.loads(manifest.read_text())["version"], 1)
            self.assertEqual(self.run_git(repo, "status", "--porcelain"), "")
            changed = self.run_git(repo, "show", "--format=", "--name-only", "HEAD")
            self.assertEqual(changed, "example/SKILL.md")

    def test_reconcile_disables_candidate_post_commit_hook(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, seed, repo = self.make_reconcile_fixture(root)
            (seed / "upstream.txt").write_text("upstream\n")
            self.run_git(seed, "add", "upstream.txt")
            self.run_git(seed, "commit", "-m", "upstream")
            self.run_git(seed, "push", "origin", "main")
            hook = repo / ".git" / "hooks" / "post-commit"
            hook.write_text(
                "#!/bin/sh\n"
                "rm -f example/SKILL.md\n"
                "git add -A\n"
                "git -c core.hooksPath=/dev/null commit -m 'malicious hook deletion' >/dev/null\n"
            )
            hook.chmod(0o755)
            skill = repo / "example" / "SKILL.md"
            skill.write_text(skill.read_text() + "\nAllowed correction.\n")

            guard.reconcile(
                repo / "tools" / "skill-repo-manifest.json", fetch=True, execute=True
            )

            remote_tree = self.run_git(
                root / "remote.git", "ls-tree", "-r", "--name-only", "refs/heads/main"
            )
            self.assertIn("example/SKILL.md", remote_tree)
            remote_log = self.run_git(
                root / "remote.git", "log", "--format=%s", "refs/heads/main"
            )
            self.assertNotIn("malicious hook deletion", remote_log)

    def test_reconcile_disables_worktree_post_checkout_hook(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, repo = self.make_reconcile_fixture(root)
            marker = root / "post-checkout-ran"
            hook = repo / ".git" / "hooks" / "post-checkout"
            hook.write_text(f"#!/bin/sh\nprintf ran > '{marker}'\n")
            hook.chmod(0o755)
            skill = repo / "example" / "SKILL.md"
            skill.write_text(skill.read_text() + "\nAllowed correction.\n")

            guard.reconcile(
                repo / "tools" / "skill-repo-manifest.json", fetch=True, execute=True
            )

            self.assertFalse(marker.exists())
            remote_tree = self.run_git(
                root / "remote.git", "ls-tree", "-r", "--name-only", "refs/heads/main"
            )
            self.assertIn("example/SKILL.md", remote_tree)

    def test_reconcile_refuses_guard_infrastructure_change(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, repo = self.make_reconcile_fixture(root)
            manifest = repo / "tools" / "skill-repo-manifest.json"
            manifest.write_text(manifest.read_text() + "\n")

            with self.assertRaisesRegex(RuntimeError, "skill-owned"):
                guard.reconcile(manifest, fetch=True, execute=True)

    def test_invalid_upstream_candidate_does_not_replace_live_checkout(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, seed, repo = self.make_reconcile_fixture(root)
            original_head = self.run_git(repo, "rev-parse", "HEAD")
            (seed / "broken.py").write_text("def invalid(:\n")
            self.run_git(seed, "add", "broken.py")
            self.run_git(seed, "commit", "-m", "broken upstream")
            self.run_git(seed, "push", "origin", "main")

            with self.assertRaisesRegex(RuntimeError, "syntax validation failed"):
                guard.reconcile(
                    repo / "tools" / "skill-repo-manifest.json", fetch=True, execute=True
                )

            self.assertEqual(self.run_git(repo, "rev-parse", "HEAD"), original_head)
            self.assertFalse((repo / "broken.py").exists())
            self.assertEqual(self.run_git(repo, "status", "--porcelain"), "")


if __name__ == "__main__":
    unittest.main()
