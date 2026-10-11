"""Fail-closed evidence gate for evaluating video-generation providers.

This validates a local evidence manifest only. It never contacts a provider,
handles credentials, submits jobs, enables generation, or permits auto-publishing.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

REQUIRED_EVIDENCE = (
    "official_free_tier_terms_url",
    "official_model_docs_url",
    "official_license_terms_url",
    "official_data_handling_url",
    "free_without_payment_method",
    "paid_fallback_disabled",
    "commercial_use_permitted",
    "prompt_and_output_data_terms_clear",
    "quota_daily_units",
    "quota_unit",
    "per_request_limit",
    "model_id",
    "output_width",
    "output_height",
    "min_duration_seconds",
    "max_duration_seconds",
)
URL_FIELDS = (
    "official_free_tier_terms_url",
    "official_model_docs_url",
    "official_license_terms_url",
    "official_data_handling_url",
)


def _https_url(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    from urllib.parse import urlparse
    try:
        parsed = urlparse(value)
        return (
            parsed.scheme == "https"
            and bool(parsed.hostname)
            and not parsed.username
            and not parsed.password
        )
    except ValueError:
        return False


def validate_manifest(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Manifest must be a JSON object."]
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1.")
    if not isinstance(data.get("provider"), str) or not data["provider"].strip():
        errors.append("provider must be a non-empty string.")
    evidence = data.get("evidence")
    if not isinstance(evidence, dict):
        return errors + ["evidence must be a JSON object."]
    for field in REQUIRED_EVIDENCE:
        if field not in evidence:
            errors.append(f"Missing evidence field: {field}.")
    for field in URL_FIELDS:
        if field in evidence and not _https_url(evidence[field]):
            errors.append(f"{field} must be an absolute HTTPS URL.")
    for field in (
        "free_without_payment_method",
        "paid_fallback_disabled",
        "commercial_use_permitted",
        "prompt_and_output_data_terms_clear",
    ):
        if field in evidence and evidence[field] is not True:
            errors.append(f"{field} must be true and supported by official terms.")
    for field in ("quota_daily_units", "per_request_limit", "output_width", "output_height"):
        value = evidence.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            errors.append(f"{field} must be a positive integer.")
    for field in ("min_duration_seconds", "max_duration_seconds"):
        value = evidence.get(field)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value <= 0:
            errors.append(f"{field} must be a positive finite number.")
    if isinstance(evidence.get("output_width"), int) and isinstance(evidence.get("output_height"), int):
        if evidence["output_width"] * 16 != evidence["output_height"] * 9:
            errors.append("Output dimensions must be exact 9:16 portrait.")
    low, high = evidence.get("min_duration_seconds"), evidence.get("max_duration_seconds")
    if isinstance(low, (int, float)) and not isinstance(low, bool) and isinstance(high, (int, float)) and not isinstance(high, bool):
        if low > high:
            errors.append("min_duration_seconds must not exceed max_duration_seconds.")
        if low > 8 or high < 12:
            errors.append("Documented duration range must include the 8–12 second proof target.")
    if not isinstance(evidence.get("model_id"), str) or not evidence["model_id"].strip():
        errors.append("model_id must be a non-empty exact model identifier.")

    controls = data.get("controls")
    if not isinstance(controls, dict):
        errors.append("controls must be a JSON object.")
    else:
        if controls.get("generation_enabled") is not False:
            errors.append("generation_enabled must remain false until a separately approved manual proof.")
        if controls.get("automatic_publishing_enabled") is not False:
            errors.append("automatic_publishing_enabled must remain false.")
        if controls.get("requires_per_video_human_approval") is not True:
            errors.append("requires_per_video_human_approval must be true.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Path to a provider evidence JSON manifest")
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"ERROR: Cannot read valid manifest: {exc}")
        return 1
    errors = validate_manifest(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Provider evidence manifest is structurally complete.")
    print("This is not provider approval: generation and automatic publishing remain disabled.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
