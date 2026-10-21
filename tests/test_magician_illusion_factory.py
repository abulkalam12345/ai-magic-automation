"""Regression tests for the magician-led episode pack builder."""
import json
import tempfile
import unittest
from pathlib import Path

from src.magician_illusion_factory import EPISODE, build


class MagicianIllusionFactoryTests(unittest.TestCase):
    def test_builds_complete_editorial_pack_without_media(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = build(Path(tmp) / "episode")
            data = json.loads((out / "episode.json").read_text(encoding="utf-8"))
            production = (out / "production.md").read_text(encoding="utf-8")
            self.assertEqual(data["status"], "editorial_draft_only")
            self.assertEqual(len(data["scenes"]), 6)
            self.assertIn("रुको", production)
            self.assertIn("SHE VANISHED", production)
            self.assertIn("No footage or audio generated", production)
            self.assertFalse((out / "video.mp4").exists())

    def test_character_continuity_and_publication_gate_are_explicit(self):
        self.assertIn("same face", EPISODE["character_lock"])
        self.assertFalse(EPISODE["publishing"]["enabled"])
        self.assertTrue(EPISODE["publishing"]["requires_user_approval_per_video_and_destination"])


if __name__ == "__main__":
    unittest.main()
