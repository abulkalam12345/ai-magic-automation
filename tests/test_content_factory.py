import importlib.util
import json
import xml.etree.ElementTree as ET
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
            ET.parse(out / "thumbnail.svg")  # SVG must remain well-formed XML.
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

    def test_invalid_history_shape_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            history = root / "history.json"
            history.write_text('{"not": "a list"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "JSON array"):
                factory.build_package(date(2026, 10, 12), "morning", root / "drafts", history)

    def test_svg_escapes_xml_special_characters(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = list(factory.IDEAS)
            try:
                factory.IDEAS.append(("A&B <Dream>", "A test premise", "test keyword", "Test hook"))
                history = root / "history.json"
                history.write_text(json.dumps([item[0] for item in original]), encoding="utf-8")
                out = factory.build_package(date(2026, 10, 12), "morning", root / "drafts", history)
                ET.parse(out / "thumbnail.svg")
                svg = (out / "thumbnail.svg").read_text(encoding="utf-8")
                self.assertIn("A&amp;B &lt;Dream&gt;", svg)
            finally:
                factory.IDEAS[:] = original

    def test_invalid_slot_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                factory.build_package(date(2026, 10, 12), "night", Path(tmp), Path(tmp) / "history.json")


if __name__ == "__main__":
    unittest.main()
