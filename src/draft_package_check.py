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
        raw_metadata = json.loads(
            (package / "metadata.json").read_text(encoding="utf-8")
        )
    except (json.JSONDecodeError, UnicodeDecodeError):
        return ["metadata.json must contain valid UTF-8 JSON."]
    if not isinstance(raw_metadata, dict):
        return ["metadata.json must contain a JSON object."]
    metadata: dict[str, Any] = raw_metadata

    try:
        script = (package / "script.md").read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ["script.md must contain valid UTF-8 text."]

    svg_path = package / "thumbnail.svg"
    try:
        svg_text = svg_path.read_text(encoding="utf-8")
        if len(svg_text.encode("utf-8")) > 2_000_000:
            errors.append("thumbnail.svg exceeds the 2 MB safety limit.")
        elif "<!DOCTYPE" in svg_text.upper() or "<!ENTITY" in svg_text.upper():
            errors.append("thumbnail.svg must not contain a DOCTYPE or entity declaration.")
        else:
            root = ET.fromstring(svg_text)
            svg_namespace = "http://www.w3.org/2000/svg"
            if root.tag != f"{{{svg_namespace}}}svg":
                errors.append("thumbnail.svg root must use the official SVG namespace.")
            elif (root.attrib.get("width") != "1080"
                  or root.attrib.get("height") != "1920"
                  or root.attrib.get("viewBox") != "0 0 1080 1920"):
                errors.append("thumbnail.svg must use the 1080x1920 portrait canvas.")
            else:
                allowed_tags = {
                    "svg", "defs", "radialGradient", "linearGradient", "stop",
                    "rect", "circle", "text",
                }
                allowed_attributes = {
                    "xmlns", "width", "height", "viewBox", "id", "offset",
                    "stop-color", "cx", "cy", "r", "fill", "stroke",
                    "stroke-width", "opacity", "x", "y", "text-anchor",
                    "font-size", "font-family", "font-weight",
                }
                ids: set[str] = set()
                references: list[str] = []
                for element in root.iter():
                    tag = element.tag.rsplit("}", 1)[-1] if isinstance(element.tag, str) else ""
                    if (tag not in allowed_tags or not isinstance(element.tag, str)
                            or not element.tag.startswith(f"{{{svg_namespace}}}")):
                        errors.append(f"thumbnail.svg contains a disallowed element or namespace: {tag or 'unknown'}.")
                        break
                    for attribute, value in element.attrib.items():
                        # ElementTree expands namespaced attributes to {namespace}local.
                        # Do not strip that namespace: a namespaced fill could otherwise
                        # pass the allowlist intended only for unqualified SVG attributes.
                        if "}" in attribute or ":" in attribute:
                            errors.append("thumbnail.svg must not contain namespaced attributes.")
                            break
                        name = attribute
                        if name not in allowed_attributes:
                            errors.append(f"thumbnail.svg contains a disallowed attribute: {name}.")
                            break
                        if name == "id":
                            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", value) or value in ids:
                                errors.append("thumbnail.svg IDs must be valid and unique.")
                                break
                            ids.add(value)
                        if "url(" in value.lower():
                            if name not in {"fill", "stroke"}:
                                errors.append("thumbnail.svg local paint references are only allowed in fill or stroke.")
                                break
                            match = re.fullmatch(r"url\(#([A-Za-z_][A-Za-z0-9_.-]*)\)", value.strip())
                            if not match:
                                errors.append("thumbnail.svg may only use local fragment paint references.")
                                break
                            references.append(match.group(1))
                    if errors and errors[-1].startswith("thumbnail.svg"):
                        break
                if not errors and any(reference not in ids for reference in references):
                    errors.append("thumbnail.svg references an undefined local paint ID.")
    except (ET.ParseError, UnicodeDecodeError):
        errors.append("thumbnail.svg must be valid UTF-8, well-formed XML.")

    required_fields = (
        "id", "channel", "date", "slot", "status", "topic", "title",
        "description", "long_tail_keywords", "hashtags", "thumbnail",
        "trend_status", "publishing",
    )
    for key in required_fields:
        if key not in metadata:
            errors.append(f"metadata.json is missing required field: {key}")
    if errors:
        return errors

    for key in ("id", "date", "topic", "title", "description"):
        value = metadata[key]
        if not isinstance(value, str) or not value.strip():
            errors.append(f"Metadata field '{key}' must be a non-empty string.")
    if metadata["channel"] != "WonderVexa":
        errors.append("Channel must be WonderVexa.")
    if metadata["status"] != "draft":
        errors.append("Package status must remain draft.")
    if metadata["slot"] not in ("morning", "evening"):
        errors.append("Slot must be morning or evening.")
    date_value = metadata["date"]
    if isinstance(date_value, str):
        try:
            parsed_date = __import__("datetime").date.fromisoformat(date_value)
            if parsed_date.isoformat() != date_value:
                raise ValueError("date must use canonical YYYY-MM-DD format")
            expected_prefix = f"{date_value}-{metadata['slot']}-"
            if isinstance(metadata["id"], str) and not metadata["id"].startswith(expected_prefix):
                errors.append("Draft ID must begin with its date and slot.")
        except ValueError:
            errors.append("Metadata date must be a valid YYYY-MM-DD date.")
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

    keywords = metadata["long_tail_keywords"]
    if (not isinstance(keywords, list) or not keywords
            or any(not isinstance(item, str) or not item.strip() for item in keywords)):
        errors.append("Long-tail keywords must be a non-empty list of non-empty strings.")

    hashtags = metadata["hashtags"]
    if (not isinstance(hashtags, list) or not hashtags
            or any(not isinstance(tag, str) or not re.fullmatch(r"#[A-Za-z0-9_]+", tag)
                   for tag in hashtags)):
        errors.append("Hashtags must be a non-empty list of valid #tags.")

    topic = metadata["topic"]
    if isinstance(topic, str) and topic and topic not in script:
        errors.append("Script must include the metadata topic.")
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
