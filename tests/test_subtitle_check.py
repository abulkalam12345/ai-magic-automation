import unittest

from src.subtitle_check import validate_srt


class SubtitleValidationTests(unittest.TestCase):
    def test_accepts_well_formed_subtitles(self):
        srt = "1\n00:00:00,000 --> 00:00:02,000\nHello\n\n2\n00:00:02,000 --> 00:00:04,000\nWorld\n"
        self.assertEqual(validate_srt(srt), [])

    def test_rejects_overlapping_cues(self):
        srt = "1\n00:00:00,000 --> 00:00:03,000\nHello\n\n2\n00:00:02,000 --> 00:00:04,000\nWorld\n"
        self.assertTrue(any("overlaps" in error for error in validate_srt(srt)))

    def test_rejects_invalid_timestamp(self):
        srt = "1\n00:99:00,000 --> 00:00:02,000\nHello\n"
        self.assertTrue(validate_srt(srt))

    def test_rejects_missing_text(self):
        srt = "1\n00:00:00,000 --> 00:00:02,000\n"
        self.assertTrue(validate_srt(srt))


if __name__ == "__main__":
    unittest.main()
