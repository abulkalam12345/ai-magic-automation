import importlib.util
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

MODULE = Path(__file__).parents[1] / "src" / "content_factory.py"
SPEC = importlib.util.spec_from_file_location("content_factory", MODULE)
factory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(factory)


class ContentFactoryTests(unittest.TestCase):
    def test_package_contains_script_metadata_and_thumbnail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = factory.build_package(date(2026, 10, 12), "morning", root / "drafts", root / "history.json")
            self.assertTrue((out / "script.md").is_file())
            self.assertTrue((out / "thumbnail.svg").is_file())
            metadata = json.loads((out / "metadata.json").read_text())
            self.assertEqual(metadata["channel"], "WonderVexa")
            self.assertFalse(metadata["publishing"]["enabled"])
            self.assertTrue(metadata["long_tail_keywords"])
            self.assertTrue(metadata["hashtags"])

    def test_history_prevents_repeating_used_topic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            history = root / "history.json"
            first = factory.build_package(date(2026, 10, 12), "morning", root / "drafts", history)
            first_topic = json.loads((first / "metadata.json").read_text())["topic"]
            second = factory.build_package(date(2026, 10, 12), "evening", root / "drafts", history)
            second_topic = json.loads((second / "metadata.json").read_text())["topic"]
            self.assertNotEqual(first_topic, second_topic)

    def test_invalid_slot_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                factory.build_package(date(2026, 10, 12), "night", Path(tmp), Path(tmp) / "history.json")


if __name__ == "__main__":
    unittest.main()
