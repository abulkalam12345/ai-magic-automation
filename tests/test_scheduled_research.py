import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE = Path(__file__).parents[1] / "src" / "scheduled_research.py"
SPEC = importlib.util.spec_from_file_location("scheduled_research", MODULE)
research = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(research)


class ScheduledResearchTests(unittest.TestCase):
    def test_disabled_config_skips_without_running_fetcher(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "feeds.json"
            config_path.write_text(json.dumps({"enabled": False, "feeds": []}), encoding="utf-8")
            with patch.object(research, "CONFIG", config_path), patch.object(research, "SIGNALS", Path(tmp) / "out" / "signals.json"), patch.object(research, "STORIES", Path(tmp) / "out" / "stories"), patch.object(research.subprocess, "run") as run, patch.object(research.sys, "argv", ["scheduled_research.py"]):
                self.assertEqual(research.main(), 0)
                run.assert_not_called()

    def test_enabled_empty_feed_list_is_safe_noop(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "feeds.json"
            config_path.write_text(json.dumps({"enabled": True, "feeds": []}), encoding="utf-8")
            with patch.object(research, "CONFIG", config_path), patch.object(research, "SIGNALS", Path(tmp) / "out" / "signals.json"), patch.object(research, "STORIES", Path(tmp) / "out" / "stories"), patch.object(research.subprocess, "run") as run, patch.object(research.sys, "argv", ["scheduled_research.py"]):
                self.assertEqual(research.main(), 0)
                run.assert_not_called()

    def test_rejects_non_https_feed(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "feeds.json"
            config_path.write_text(json.dumps({"enabled": True, "feeds": [{"name": "bad", "url": "http://example.org/feed"}]}), encoding="utf-8")
            with patch.object(research, "CONFIG", config_path):
                with self.assertRaisesRegex(ValueError, "HTTPS"):
                    research.load_config()

    def test_rejects_invalid_age(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "feeds.json"
            config_path.write_text(json.dumps({"enabled": True, "feeds": [], "max_age_hours": 0}), encoding="utf-8")
            with patch.object(research, "CONFIG", config_path):
                with self.assertRaisesRegex(ValueError, "positive"):
                    research.load_config()


if __name__ == "__main__":
    unittest.main()
