import importlib.util
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parents[1]
def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "src" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

generator = load("story_generator")
checker = load("story_package_check")


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


class StoryPackageCheckTests(unittest.TestCase):
    def make_package(self, root):
        script, metadata = generator.build_story_brief(signal(title="[Ocean] **cleanup**"), date(2026, 10, 12), "morning")
        (root / "story.md").write_text(script, encoding="utf-8")
        (root / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
        return metadata

    def test_accepts_valid_generated_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_package(root)
            self.assertEqual(checker.validate_story_package(root), [])

    def test_rejects_publish_enabled_or_missing_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = self.make_package(root)
            metadata["publishing"]["enabled"] = True
            metadata["publishing"]["requires_explicit_video_approval"] = False
            (root / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
            errors = checker.validate_story_package(root)
            self.assertTrue(any("publishing.enabled" in error for error in errors))
            self.assertTrue(any("explicit per-video approval" in error for error in errors))

    def test_rejects_unsafe_attribution_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = self.make_package(root)
            metadata["article_url"] = "javascript:alert(1)"
            (root / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
            self.assertTrue(any("article_url" in error for error in checker.validate_story_package(root)))

    def test_rejects_missing_story_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_package(root)
            (root / "story.md").write_text("# Incomplete", encoding="utf-8")
            errors = checker.validate_story_package(root)
            self.assertTrue(any("missing section" in error for error in errors))

    def test_rejects_non_object_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "metadata.json").write_text("[]", encoding="utf-8")
            (root / "story.md").write_text("story", encoding="utf-8")
            self.assertTrue(any("JSON object" in error for error in checker.validate_story_package(root)))


if __name__ == "__main__":
    unittest.main()
