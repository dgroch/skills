import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("skill_repo_guard.py")
spec = importlib.util.spec_from_file_location("skill_repo_guard", MODULE_PATH)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class SkillRepoGuardTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
