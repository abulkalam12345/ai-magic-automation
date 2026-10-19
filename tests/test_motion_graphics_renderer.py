import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).parents[1] / "src" / "motion_graphics_renderer.py"
SPEC = importlib.util.spec_from_file_location("motion_graphics_renderer", MODULE)
renderer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(renderer)


class NarrationTimingTests(unittest.TestCase):
    def test_narration_is_limited_to_short_video_budget(self):
        text = renderer.build_narration(
            "A Very Long Topic About Magical Golden Trees",
            "This is a long premise with many details that should not all be spoken in a ten second short video."
        )
        self.assertLessEqual(len(text), 130)
        self.assertIn("…", text)

    def test_whitespace_is_normalized(self):
        text = renderer.build_narration("  Golden   Tree! ", "  Let   your wonder   grow. ")
        self.assertEqual(text, "Golden Tree. Let your wonder grow.")

    def test_empty_title_is_rejected(self):
        with self.assertRaises(ValueError):
            renderer.build_narration("   ", "A premise")

    def test_long_title_is_bounded_without_premise(self):
        text = renderer.build_narration("Wonder " * 80, "")
        self.assertLessEqual(len(text), 130)
        self.assertTrue(text.endswith("."))


if __name__ == "__main__":
    unittest.main()
