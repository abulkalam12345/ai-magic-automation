"""Validate a generated WonderVexa draft package before artifact upload.

This is an offline integrity/safety check. It does not render, generate, or publish media.
"""
from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


def validate_package(package: Path) -> list[str]:
    errors: list[str] = []
    required = ("script.md", "metadata.json", "thumbnail.svg")
    for name in required:
        path = package / name
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"Required file is missing or empty: {name}")
    if errors:
        return errors

    try:
        metadata: dict[str, Any] = json.loads(
            (package / "metadata.json").read_text(encoding="utf-8")
        )
    except (json.JSONDecodeError, UnicodeDecodeError):
        return ["metadata.json must contain valid UTF-8 JSON."]

    script = (package / "script.md").read_text(encoding="utf-8")
    svg_path = package / "thumbnail.svg"
    try:
        root = ET.parse(svg_path).getroot()
        if not root.tag.endswith("svg"):
            errors.append("thumbnail.svg root element must be SVG.")
    except ET.ParseError:
        errors.append("thumbnail.svg must be well-formed XML.")

    for key in ("id", "channel", "date", "slot", "status", "topic", "title",
                "description", "long_tail_keywords", "hashtags", "thumbnail",
                "trend_status", "publishing"):
        if key not in metadata:
            errors.append(f"metadata.json is missing required field: {key}")

    if errors:
        return errors

    if metadata["channel"] != "WonderVexa":
        errors.append("Channel must be WonderVexa.")
    if metadata["status"] != "draft":
        errors.append("Package status must remain draft.")
    if metadata["slot"] not in ("morning", "evening"):
        errors.append("Slot must be morning or evening.")
    if metadata["thumbnail"] != "thumbnail.svg":
        errors.append("Thumbnail metadata must point to thumbnail.svg.")
    if metadata.get("video") is not None:
        errors.append("Draft package must not claim to contain a rendered video.")
    if metadata["trend_status"] != "evergreen_seed_not_live_trend_verified":
        errors.append("Unverified idea-bank topics must be labeled as evergreen seeds.")
    publishing = metadata["publishing"]
    if not isinstance(publishing, dict) or publishing.get("enabled") is not False:
        errors.append("Publishing must remain disabled.")
    elif publishing.get("requires_explicit_video_approval") is not True:
        errors.append("Explicit per-video approval must be required.")
    if not isinstance(metadata["long_tail_keywords"], list) or not metadata["long_tail_keywords"]:
        errors.append("At least one long-tail keyword is required.")
    if (not isinstance(metadata["hashtags"], list) or not metadata["hashtags"]
            or any(not isinstance(tag, str) or not re.fullmatch(r"#[A-Za-z0-9_]+", tag)
                   for tag in metadata["hashtags"])):
        errors.append("Hashtags must be a non-empty list of valid #tags.")
    if metadata["topic"] not in script:
        errors.append("Script must include the metadata topic.")
    if metadata["title"] not in metadata["description"] and not metadata["description"].strip():
        errors.append("Description must not be empty.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path, help="Path to one generated draft package")
    args = parser.parse_args()
    errors = validate_package(args.package)
    if errors:
        print("DRAFT PACKAGE CHECK FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("DRAFT PACKAGE CHECK PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
