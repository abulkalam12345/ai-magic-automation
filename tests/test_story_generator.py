import importlib.util
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

MODULE = Path(__file__).parents[1] / "src" / "story_generator.py"
SPEC = importlib.util.spec_from_file_location("story_generator", MODULE)
generator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generator)


def signal(**overrides):
    item = {
        "title": "Ocean cleanup innovation",
        "summary": "A community develops a new way to restore a polluted shoreline.",
        "source_name": "Example Research Feed",
        "source_url": "https://example.org/feed.xml",
        "url": "https://example.org/story",
        "published_at": "2026-10-11T10:00:00+00:00",
        "research_signal_score": 81.5,
        "signal_label": "fresh_research_signal_not_verified_platform_trend",
    }
    item.update(overrides)
    return item


class StoryGeneratorTests(unittest.TestCase):
    def test_build_brief_preserves_attribution_and_draft_safety(self):
        script, metadata = generator.build_story_brief(signal(), date(2026, 10, 12), "morning")
        self.assertIn("https://example.org/story", script)
        self.assertIn("Example Research Feed", script)
        self.assertEqual(metadata["research_status"], "signal_only_not_verified_platform_trend")
        self.assertFalse(metadata["publishing"]["enabled"])
        self.assertTrue(metadata["publishing"]["requires_explicit_video_approval"])

    def test_rejects_unverified_trend_claim_label(self):
        with self.assertRaisesRegex(ValueError, "unverified"):
            generator.validate_signal(signal(signal_label="verified_trend"))

    def test_rejects_unsafe_article_url(self):
        for url in ("javascript:alert(1)", "/relative", "https://user:pass@example.org/story"):
            with self.subTest(url=url), self.assertRaisesRegex(ValueError, "HTTP"):
                generator.validate_signal(signal(url=url))

    def test_rejects_missing_source_attribution(self):
        with self.assertRaisesRegex(ValueError, "source_name"):
            generator.validate_signal(signal(source_name=" "))

    def test_generate_selects_highest_ranked_signal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = {
                "status": "research_signals_only_not_verified_social_trends",
                "items": [
                    signal(title="Lower ranked", research_signal_score=10),
                    signal(title="Higher ranked", research_signal_score=90),
                ],
            }
            source = root / "signals.json"
            source.write_text(json.dumps(payload), encoding="utf-8")
            path = generator.generate(source, root / "out", date(2026, 10, 12), "evening")
            metadata = json.loads((path / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["topic"], "Higher ranked")
            self.assertTrue((path / "story.md").is_file())

    def test_rejects_wrong_input_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "signals.json"
            source.write_text(json.dumps({"status": "verified_trends", "items": [signal()]}))
            with self.assertRaisesRegex(ValueError, "status"):
                generator.generate(source, Path(tmp) / "out", date(2026, 10, 12), "morning")


if __name__ == "__main__":
    unittest.main()
