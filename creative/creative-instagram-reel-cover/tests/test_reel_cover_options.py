import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "reel_cover_from_instagram.py"
spec = importlib.util.spec_from_file_location("reel_cover", SCRIPT)
reel_cover = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reel_cover)


class CoverOptionTests(unittest.TestCase):
    def test_build_cover_options_can_skip_precrop(self):
        crops = [{"label": "C1", "path": "/tmp/crop1.jpg"}]

        options = reel_cover.build_cover_options(
            raw_frame_path=Path("/tmp/full-frame.jpg"),
            crop_candidates=crops,
            crop_mode="none",
            num_options=3,
        )

        self.assertEqual(len(options), 3)
        self.assertTrue(all(o["path"] == "/tmp/full-frame.jpg" for o in options))
        self.assertTrue(all(o["crop"] is None for o in options))
        self.assertEqual([o["label"] for o in options], ["option_1", "option_2", "option_3"])

    def test_build_cover_options_returns_multiple_crop_options_when_requested(self):
        crops = [
            {"label": "C1", "path": "/tmp/crop1.jpg", "metrics": {"score": 90}},
            {"label": "C2", "path": "/tmp/crop2.jpg", "metrics": {"score": 80}},
            {"label": "C3", "path": "/tmp/crop3.jpg", "metrics": {"score": 70}},
            {"label": "C4", "path": "/tmp/crop4.jpg", "metrics": {"score": 60}},
        ]

        options = reel_cover.build_cover_options(
            raw_frame_path=Path("/tmp/full-frame.jpg"),
            crop_candidates=crops,
            crop_mode="auto",
            num_options=3,
        )

        self.assertEqual([o["path"] for o in options], ["/tmp/crop1.jpg", "/tmp/crop2.jpg", "/tmp/crop3.jpg"])
        self.assertEqual([o["crop"]["label"] for o in options], ["C1", "C2", "C3"])

    def test_rank_distinct_frame_options_spreads_across_video_and_caps_duplicates(self):
        frame_choice = {
            "best_label": "015",
            "timestamp_seconds": 14.0,
            "metrics": {"score": 95},
            "runners_up": [
                {"label": "016", "timestamp_seconds": 15.0, "metrics": {"score": 94}},
                {"label": "014", "timestamp_seconds": 13.0, "metrics": {"score": 93}},
                {"label": "022", "timestamp_seconds": 21.0, "metrics": {"score": 90}},
                {"label": "012", "timestamp_seconds": 11.0, "metrics": {"score": 88}},
            ],
        }

        ranked = reel_cover.rank_distinct_frame_options(frame_choice, num_options=3, min_gap_seconds=3.0)

        self.assertEqual([r["label"] for r in ranked], ["015", "022", "012"])
        self.assertTrue(all(abs(a["timestamp_seconds"] - b["timestamp_seconds"]) >= 3.0 for i, a in enumerate(ranked) for b in ranked[i + 1:]))

    def test_nanobanana_prompt_explicitly_removes_captions_and_overlays(self):
        prompt = reel_cover.nanobanana_prompt(Path("/tmp/input.jpg")).lower()

        self.assertIn("remove", prompt)
        self.assertIn("captions", prompt)
        self.assertIn("text overlays", prompt)


if __name__ == "__main__":
    unittest.main()
