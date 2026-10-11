"""Safe preflight for the AI Magic video pipeline.

This deliberately does not call a paid or unverified generation provider.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ("project", "generation", "publishing", "character")


def load_settings(path: Path) -> dict:
    # Keep the first version dependency-free: JSON is supported directly.
    # YAML settings are parsed only when PyYAML is installed.
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(raw)
    else:
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise RuntimeError("Install PyYAML to read YAML settings, or use JSON.") from exc
        data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ValueError("Settings must be an object.")
    return data


def preflight(settings: dict) -> list[str]:
    errors = [f"Missing settings section: {key}" for key in REQUIRED if key not in settings]
    generation = settings.get("generation", {})
    publishing = settings.get("publishing", {})
    if generation.get("free_only") is not True:
        errors.append("generation.free_only must be true.")
    if generation.get("max_cost_usd") != 0:
        errors.append("generation.max_cost_usd must be 0.")
    if publishing.get("enabled") is not False:
        errors.append("Publishing must remain disabled until explicitly approved.")
    if publishing.get("require_explicit_per_video_approval") is not True:
        errors.append("Per-video approval must be required.")
    if generation.get("provider") in (None, "", "not-configured"):
        errors.append("No generation provider has been configured or verified yet.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Check AI Magic pipeline readiness.")
    parser.add_argument("--config", default=str(ROOT / "config/settings.example.yaml"))
    args = parser.parse_args()
    try:
        settings = load_settings(Path(args.config))
        errors = preflight(settings)
    except Exception as exc:
        print(f"CONFIG ERROR: {exc}")
        return 2
    if errors:
        print("NOT READY — no generation or publishing was started.")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Preflight passed. Provider-specific generation is not implemented by this check.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
