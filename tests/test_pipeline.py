import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).parents[1] / "src" / "pipeline.py"
SPEC = importlib.util.spec_from_file_location("pipeline", MODULE)
pipeline = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pipeline)


def valid_settings():
    return {
        "project": {},
        "generation": {"provider": "verified-demo", "free_only": True, "max_cost_usd": 0},
        "publishing": {"enabled": False, "require_explicit_per_video_approval": True},
        "character": {},
    }


class PreflightTests(unittest.TestCase):
    def test_safe_configuration_passes(self):
        self.assertEqual(pipeline.preflight(valid_settings()), [])

    def test_paid_generation_is_rejected(self):
        settings = valid_settings()
        settings["generation"]["max_cost_usd"] = 1
        self.assertTrue(any("max_cost_usd" in e for e in pipeline.preflight(settings)))

    def test_auto_publishing_is_rejected(self):
        settings = valid_settings()
        settings["publishing"]["enabled"] = True
        self.assertTrue(any("Publishing must remain disabled" in e for e in pipeline.preflight(settings)))

    def test_malformed_settings_sections_fail_closed(self):
        for section in ("project", "generation", "publishing", "character"):
            for value in (None, [], "invalid", True):
                settings = valid_settings()
                settings[section] = value
                with self.subTest(section=section, value=value):
                    errors = pipeline.preflight(settings)
                    self.assertTrue(any(section in error for error in errors))

    def test_non_object_root_is_rejected(self):
        for value in (None, [], "invalid", True):
            with self.subTest(value=value):
                self.assertTrue(pipeline.preflight(value))

    def test_missing_provider_is_rejected(self):
        settings = valid_settings()
        settings["generation"]["provider"] = "not-configured"
        self.assertTrue(any("No generation provider" in e for e in pipeline.preflight(settings)))


if __name__ == "__main__":
    unittest.main()
