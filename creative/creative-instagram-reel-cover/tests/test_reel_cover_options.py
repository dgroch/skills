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


if __name__ == "__main__":
    unittest.main()
