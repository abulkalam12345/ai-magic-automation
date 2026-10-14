"""Regression checks for the first-proof creative and continuity contract."""

import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


class FirstProofDocumentationTests(unittest.TestCase):
    def read_doc(self, name):
        return (ROOT / "docs" / name).read_text(encoding="utf-8")

    def test_storyboard_keeps_single_flower_and_vertical_target(self):
        storyboard = self.read_doc("FIRST_PROOF_STORYBOARD.md")
        self.assertIn("10 seconds, vertical 9:16", storyboard)
        self.assertIn("one single delicate wilted bluebell-like flower", storyboard)
        self.assertIn("No provider has passed", storyboard)
        self.assertIn("explicitly approves the exact video", storyboard)

    def test_reference_frame_spec_has_identity_and_safety_rules(self):
        reference = self.read_doc("FIRST_PROOF_REFERENCE_FRAME.md")
        for required in (
            "Exactly one bluebell-like flower",
            "blue-violet petals",
            "thin, elegant ribbon of blue and warm-gold light",
            "No people, hands, extra flowers, text, logos",
            "Do not enter payment details",
            "No generation is run until the user approves",
        ):
            with self.subTest(required=required):
                self.assertIn(required, reference)

    def test_two_clip_plan_uses_actual_clip_a_end_frame_as_clip_b_start(self):
        plan = self.read_doc("FIRST_PROOF_CLIP_PLAN.md")
        self.assertIn("extract its actual final frame", plan)
        self.assertIn("Use that exact frame as Clip B's image-to-video starting frame", plan)
        self.assertIn("Expected first frame", plan)
        self.assertIn("actual first frame matches Clip A's extracted final frame", plan)
        self.assertIn("never imply that the clips are one continuous generation", plan)

    def test_provider_and_publication_remain_blocked_in_first_proof_docs(self):
        plan = self.read_doc("FIRST_PROOF_CLIP_PLAN.md")
        gate = self.read_doc("VIDEO_PROVIDER_GATE.md")
        self.assertIn("no generation authorized", plan)
        self.assertIn("Do not generate until the user approves", plan)
        self.assertIn("Never enable automatic publishing", gate)
        self.assertIn("No paid fallback", gate)


if __name__ == "__main__":
    unittest.main()
