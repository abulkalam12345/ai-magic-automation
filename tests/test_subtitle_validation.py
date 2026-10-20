import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).parents[1] / "src" / "subtitle_check.py"
SPEC = importlib.util.spec_from_file_location("subtitle_check", MODULE)
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class SubtitleValidationTests(unittest.TestCase):
    def test_first_hindi_video_english_srt_passes(self):
        srt = Path(__file__).parents[1] / "examples" / "first-hindi-video" / "captions-en.srt"
        self.assertEqual(checker.validate_srt(srt), [])

    def test_rejects_overlapping_cues(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.srt"
            path.write_text(
                "1\n00:00:00,000 --> 00:00:03,000\nFirst cue\n\n"
                "2\n00:00:02,500 --> 00:00:04,000\nSecond cue\n",
                encoding="utf-8",
            )
            self.assertTrue(any("overlaps" in error for error in checker.validate_srt(path)))

    def test_rejects_empty_subtitle_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.srt"
            path.write_text("1\n00:00:00,000 --> 00:00:01,000\n", encoding="utf-8")
            self.assertTrue(any("text is empty" in error for error in checker.validate_srt(path)))

    def test_rejects_invalid_time_range(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad-time.srt"
            path.write_text("1\n00:00:02,000 --> 00:00:01,000\nText\n", encoding="utf-8")
            self.assertTrue(any("after start" in error for error in checker.validate_srt(path)))


if __name__ == "__main__":
    unittest.main()
