"""Validate a generated WonderVexa research story brief before human review."""
from __future__ import annotations

import argparse
import json
import re
import urllib.parse
from pathlib import Path

REQUIRED_SECTIONS = (
    "# WonderVexa Original Story Brief",
    "## Research input",
    "## Original story concept",
    "## 10-second vertical story",
    "## Production prompt",
    "## Editorial checks",
)
EXPECTED_SIGNAL_LABEL = "fresh_research_signal_not_verified_platform_trend"


def _valid_http_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = urllib.parse.urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.hostname) and not parsed.username and not parsed.password
    except ValueError:
        return False


def validate_story_package(package_dir: Path) -> list[str]:
    errors: list[str] = []
    metadata_path = package_dir / "metadata.json"
    story_path = package_dir / "story.md"
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [f"metadata.json is missing or invalid: {exc}"]
    if not isinstance(metadata, dict):
        return ["metadata.json must contain a JSON object."]
    try:
        story = story_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"story.md is missing or invalid UTF-8: {exc}"]

    for field in ("id", "date", "topic", "source_name"):
        value = metadata.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"metadata field '{field}' must be a non-empty string.")
    if metadata.get("channel") != "WonderVexa":
        errors.append("channel must be WonderVexa.")
    if metadata.get("status") != "draft":
        errors.append("status must remain draft.")
    if metadata.get("slot") not in {"morning", "evening"}:
        errors.append("slot must be morning or evening.")
    if metadata.get("research_status") != "signal_only_not_verified_platform_trend":
        errors.append("research_status must not claim a verified platform trend.")
    if metadata.get("signal_label") != EXPECTED_SIGNAL_LABEL:
        errors.append("signal_label is missing or invalid.")
    for field in ("source_url", "article_url"):
        if not _valid_http_url(metadata.get(field)):
            errors.append(f"{field} must be an absolute HTTP(S) URL without credentials.")
    publishing = metadata.get("publishing")
    if not isinstance(publishing, dict):
        errors.append("publishing must be an object.")
    else:
        if publishing.get("enabled") is not False:
            errors.append("publishing.enabled must be false.")
        if publishing.get("requires_explicit_video_approval") is not True:
            errors.append("explicit per-video approval must be required.")
    if not isinstance(metadata.get("research_signal_score"), (int, float)) or isinstance(metadata.get("research_signal_score"), bool):
        errors.append("research_signal_score must be numeric.")
    elif not __import__("math").isfinite(metadata["research_signal_score"]):
        errors.append("research_signal_score must be finite.")
    for section in REQUIRED_SECTIONS:
        if section not in story:
            errors.append(f"story.md is missing section: {section}")
    if metadata.get("topic") and metadata["topic"] not in story:
        # Markdown escaping may alter the rendered text, so check the stored title loosely.
        plain = re.sub(r"\\([\\`*_{}\[\]()#+.!|>~-])", r"\1", story)
        if metadata["topic"] not in plain:
            errors.append("metadata topic is not represented in story.md.")
    if "human review required" not in story.lower():
        errors.append("story.md must require human review.")
    if "not a verified social-platform trend" not in story.lower():
        errors.append("story.md must clearly label research as unverified.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path, help="Directory containing story.md and metadata.json")
    args = parser.parse_args()
    errors = validate_story_package(args.package)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Story package is structurally valid: {args.package}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
