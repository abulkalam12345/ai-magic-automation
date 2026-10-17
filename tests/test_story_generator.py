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

    def test_story_uses_idea_only_and_does_not_reproduce_feed_summary(self):
        original_summary = "UNIQUE ARTICLE SENTENCE: researchers discovered a secret blue crystal engine."
        script, metadata = generator.build_story_brief(
            signal(summary=original_summary),
            date(2026, 10, 17), "morning")
        self.assertIn("Idea cue:", script)
        self.assertIn("Use only the broad idea", script)
        self.assertIn("not an AI model", script)
        self.assertNotIn(original_summary, script)
        self.assertNotIn("secret blue crystal engine", script)
        self.assertEqual(metadata["source_name"], "Example Research Feed")

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

    def test_escapes_untrusted_markdown_in_feed_text(self):
        script, _metadata = generator.build_story_brief(
            signal(title="[click](https://evil.example) **fake trend**"),
            date(2026, 10, 12), "morning")
        self.assertNotIn("[click](", script)
        self.assertNotIn("**fake trend**", script)

    def test_rejects_non_finite_or_boolean_scores(self):
        for score in (float("nan"), float("inf"), True, "high"):
            with self.subTest(score=score), self.assertRaisesRegex(ValueError, "finite number"):
                generator.validate_signal(signal(research_signal_score=score))

    def test_rejects_overlong_title(self):
        with self.assertRaisesRegex(ValueError, "exceeds"):
            generator.validate_signal(signal(title="x" * 241))

    def test_rejects_malformed_url(self):
        with self.assertRaisesRegex(ValueError, "HTTP"):
            generator.validate_signal(signal(url="https://[broken"))

    def test_rejects_wrong_input_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "signals.json"
            source.write_text(json.dumps({"status": "verified_trends", "items": [signal()]}))
            with self.assertRaisesRegex(ValueError, "status"):
                generator.generate(source, Path(tmp) / "out", date(2026, 10, 12), "morning")


    def test_existing_story_package_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = {
                "status": "research_signals_only_not_verified_social_trends",
                "items": [signal()],
            }
            source = root / "signals.json"
            source.write_text(json.dumps(payload), encoding="utf-8")
            output = root / "out"
            package = output / "2026-10-12-morning-research-ocean-cleanup-innovation"
            package.mkdir(parents=True)
            sentinel = package / "keep.txt"
            sentinel.write_text("preserve", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                generator.generate(source, output, date(2026, 10, 12), "morning")
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve")

    def test_story_package_is_published_as_complete_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "signals.json"
            source.write_text(json.dumps({
                "status": "research_signals_only_not_verified_social_trends",
                "items": [signal()],
            }), encoding="utf-8")
            package = generator.generate(source, root / "out", date(2026, 10, 12), "morning")
            self.assertEqual({p.name for p in package.iterdir()}, {"story.md", "metadata.json"})
            self.assertFalse(any(p.name.startswith(".story-package-") for p in package.parent.iterdir()))


if __name__ == "__main__":
    unittest.main()
