"""Optional, disabled-by-default RSS research stage for scheduled draft runs."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "trend_feeds.json"
SIGNALS = ROOT / "output" / "trend-research" / "signals.json"
STORIES = ROOT / "output" / "research-stories"


def load_config() -> dict:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read trend feed configuration: {exc}") from exc
    if not isinstance(config, dict) or not isinstance(config.get("enabled"), bool):
        raise ValueError("Trend feed config must be an object with boolean enabled.")
    feeds = config.get("feeds")
    if not isinstance(feeds, list):
        raise ValueError("Trend feed config feeds must be a list.")
    if not isinstance(config.get("max_age_hours", 72), int) or isinstance(config.get("max_age_hours", 72), bool) or config.get("max_age_hours", 72) <= 0:
        raise ValueError("max_age_hours must be a positive integer.")
    for feed in feeds:
        if not isinstance(feed, dict) or not isinstance(feed.get("name"), str) or not feed["name"].strip() or not isinstance(feed.get("url"), str):
            raise ValueError("Each feed must contain a non-empty name and URL.")
        # Fetcher enforces HTTPS, host-safe redirects, size and timeout limits.
        if not feed["url"].startswith("https://"):
            raise ValueError("Every configured feed URL must use HTTPS.")
    return config


def main() -> int:
    config = load_config()
    if not config["enabled"]:
        print("RSS research skipped: config/trend_feeds.json is disabled.")
        return 0
    if not config["feeds"]:
        print("RSS research skipped: no reviewed feed sources are configured.")
        return 0

    command = [
        sys.executable, str(ROOT / "src" / "trend_research.py"),
        "--output", str(SIGNALS),
        "--max-age-hours", str(config.get("max_age_hours", 72)),
    ]
    for feed in config["feeds"]:
        command.extend(["--feed", f'{feed["name"].strip()}={feed["url"].strip()}'])
    result = subprocess.run(command, cwd=ROOT, check=False)
    if result.returncode == 2:
        print("RSS research completed with no fresh usable signals; evergreen drafts remain unchanged.")
        return 0
    if result.returncode != 0:
        print(f"RSS research failed with exit code {result.returncode}; scheduled draft run will fail closed.")
        return result.returncode

    for slot in ("morning", "evening"):
        result = subprocess.run([
            sys.executable, str(ROOT / "src" / "story_generator.py"),
            "--signals", str(SIGNALS), "--slot", slot,
            "--output", str(STORIES),
        ], cwd=ROOT, check=False)
        if result.returncode != 0:
            return result.returncode
        package = STORIES / next(
            path.name for path in STORIES.glob(f"*-{slot}-research-*")
            if (path / "metadata.json").is_file()
        )
        result = subprocess.run([
            sys.executable, str(ROOT / "src" / "story_package_check.py"), str(package)
        ], cwd=ROOT, check=False)
        if result.returncode != 0:
            return result.returncode
    print("Research-only story briefs created and validated; no video or publishing action occurred.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
