import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).parents[1] / "src" / "provider_readiness.py"
SPEC = importlib.util.spec_from_file_location("provider_readiness", MODULE)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def valid_manifest():
    return {
        "schema_version": 1,
        "provider": "ExampleProvider",
        "evidence": {
            "official_free_tier_terms_url": "https://example.org/free",
            "official_model_docs_url": "https://example.org/model",
            "official_license_terms_url": "https://example.org/license",
            "official_data_handling_url": "https://example.org/data",
            "free_without_payment_method": True,
            "paid_fallback_disabled": True,
            "commercial_use_permitted": True,
            "prompt_and_output_data_terms_clear": True,
            "quota_daily_units": 100,
            "quota_unit": "seconds",
            "per_request_limit": 1,
            "model_id": "example-video-v1",
            "output_width": 1080,
            "output_height": 1920,
            "min_duration_seconds": 8,
            "max_duration_seconds": 12,
        },
        "controls": {
            "generation_enabled": False,
            "automatic_publishing_enabled": False,
            "requires_per_video_human_approval": True,
        },
    }


class ProviderReadinessTests(unittest.TestCase):
    def test_complete_manifest_passes_structural_gate(self):
        self.assertEqual(gate.validate_manifest(valid_manifest()), [])

    def test_missing_official_evidence_fails_closed(self):
        manifest = valid_manifest()
        del manifest["evidence"]["official_license_terms_url"]
        errors = gate.validate_manifest(manifest)
        self.assertTrue(any("official_license_terms_url" in error for error in errors))

    def test_payment_or_paid_fallback_is_rejected(self):
        manifest = valid_manifest()
        manifest["evidence"]["free_without_payment_method"] = False
        manifest["evidence"]["paid_fallback_disabled"] = False
        errors = gate.validate_manifest(manifest)
        self.assertTrue(any("free_without_payment_method" in error for error in errors))
        self.assertTrue(any("paid_fallback_disabled" in error for error in errors))

    def test_non_9_16_dimensions_are_rejected(self):
        manifest = valid_manifest()
        manifest["evidence"]["output_width"] = 768
        manifest["evidence"]["output_height"] = 1152
        self.assertTrue(any("exact 9:16" in error for error in gate.validate_manifest(manifest)))

    def test_duration_must_cover_proof_target(self):
        manifest = valid_manifest()
        manifest["evidence"]["max_duration_seconds"] = 10
        self.assertTrue(any("include the 8–12" in error for error in gate.validate_manifest(manifest)))

    def test_generation_and_publishing_must_stay_disabled(self):
        manifest = valid_manifest()
        manifest["controls"]["generation_enabled"] = True
        manifest["controls"]["automatic_publishing_enabled"] = True
        errors = gate.validate_manifest(manifest)
        self.assertTrue(any("generation_enabled" in error for error in errors))
        self.assertTrue(any("automatic_publishing_enabled" in error for error in errors))

    def test_rejects_non_object_manifest_and_unsafe_urls(self):
        self.assertTrue(gate.validate_manifest([]))
        manifest = valid_manifest()
        manifest["evidence"]["official_model_docs_url"] = "javascript:alert(1)"
        self.assertTrue(any("official_model_docs_url" in error for error in gate.validate_manifest(manifest)))


if __name__ == "__main__":
    unittest.main()
