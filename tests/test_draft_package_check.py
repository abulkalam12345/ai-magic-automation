import importlib.util
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parents[1]
FACTORY_SPEC = importlib.util.spec_from_file_location("content_factory", ROOT / "src" / "content_factory.py")
factory = importlib.util.module_from_spec(FACTORY_SPEC)
FACTORY_SPEC.loader.exec_module(factory)

CHECK_SPEC = importlib.util.spec_from_file_location("draft_package_check", ROOT / "src" / "draft_package_check.py")
checker = importlib.util.module_from_spec(CHECK_SPEC)
CHECK_SPEC.loader.exec_module(checker)


class DraftPackageCheckTests(unittest.TestCase):
    def make_package(self, root):
        return factory.build_package(date(2026, 10, 13), "morning", root / "drafts", root / "history.json")

    def test_generated_package_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = self.make_package(Path(tmp))
            self.assertEqual(checker.validate_package(package), [])

    def test_publishing_enabled_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = self.make_package(Path(tmp))
            path = package / "metadata.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["publishing"]["enabled"] = True
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertTrue(any("Publishing must remain disabled" in e
                                for e in checker.validate_package(package)))

    def test_unverified_trend_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = self.make_package(Path(tmp))
            path = package / "metadata.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["trend_status"] = "live_trend"
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertTrue(any("evergreen seeds" in e
                                for e in checker.validate_package(package)))

    def test_missing_thumbnail_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = self.make_package(Path(tmp))
            (package / "thumbnail.svg").unlink()
            self.assertTrue(any("thumbnail.svg" in e for e in checker.validate_package(package)))

    def test_video_must_not_be_claimed_as_generated(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = self.make_package(Path(tmp))
            path = package / "metadata.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["video"] = "final.mp4"
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertTrue(any("rendered video" in e
                                for e in checker.validate_package(package)))


if __name__ == "__main__":
    unittest.main()
