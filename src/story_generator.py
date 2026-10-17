"""Turn attributed RSS/Atom research signals into original, reviewable story briefs.

This is deterministic template generation, not an AI model and not fact reporting.
It preserves source attribution and never labels a feed mention as a verified trend.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import tempfile
import urllib.parse
from datetime import date
from pathlib import Path


def _safe_http_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = urllib.parse.urlparse(value.strip())
        return parsed.scheme in {"http", "https"} and bool(parsed.hostname) and not parsed.username and not parsed.password
    except ValueError:
        return False


def _required_text(item: dict, field: str, limit: int = 2000) -> str:
    value = item.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Signal field '{field}' must be a non-empty string.")
    value = value.strip()
    if len(value) > limit:
        raise ValueError(f"Signal field '{field}' exceeds {limit} characters.")
    return value


def _markdown_text(value: str) -> str:
    """Render untrusted feed text as plain Markdown text, not active markup."""
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"([\\`*_{}\[\]()#+.!|>~-])", r"\\\1", value)
    return value


def validate_signal(item: object) -> dict:
    if not isinstance(item, dict):
        raise ValueError("Each research signal must be a JSON object.")
    title = _required_text(item, "title", 240)
    summary = _required_text(item, "summary", 2000)
    source_name = _required_text(item, "source_name", 160)
    source_url = _required_text(item, "source_url", 2048)
    article_url = _required_text(item, "url", 2048)
    if not _safe_http_url(source_url) or not _safe_http_url(article_url):
        raise ValueError("Signal source_url and url must be absolute HTTP(S) URLs without credentials.")
    label = _required_text(item, "signal_label", 100)
    if label != "fresh_research_signal_not_verified_platform_trend":
        raise ValueError("Only explicitly labeled, unverified research signals are accepted.")
    score = item.get("research_signal_score", 0)
    if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score):
        raise ValueError("research_signal_score must be a finite number.")
    published_at = item.get("published_at")
    if published_at is not None and not isinstance(published_at, str):
        raise ValueError("published_at must be a string or null.")
    return {**item, "title": title, "summary": summary, "source_name": source_name,
            "source_url": source_url, "url": article_url, "signal_label": label,
            "research_signal_score": score}


def build_story_brief(signal: dict, day: date, slot: str) -> tuple[str, dict]:
    signal = validate_signal(signal)
    if slot not in {"morning", "evening"}:
        raise ValueError("slot must be morning or evening")
    topic = signal["title"]
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")[:48] or "research-story"
    story_id = f"{day.isoformat()}-{slot}-research-{slug}"
    safe_topic = _markdown_text(topic)
    source_name = _markdown_text(signal["source_name"])
    script = f"""# WonderVexa Original Story Brief

**ID:** {story_id}  
**Date / slot:** {day.isoformat()} / {slot}  
**Status:** DRAFT — human review required  
**Research status:** Research idea only; not a verified social-platform trend  
**Generation mode:** Deterministic story template; not an AI-written factual explainer

## Research idea (internal reference only)
- **Discovery headline (internal label only — do not reuse or paraphrase):** {safe_topic}
- **Source:** {source_name}
- **Source feed:** {signal["source_url"]}
- **Original article for human fact-checking:** {signal["url"]}

The feed summary is deliberately not reproduced in this script. Use the article only to understand the broad subject or question. Extract no article paragraphs, distinctive phrasing, narrative structure, images, video, or audio.

## Original WonderVexa script direction
Treat the discovery headline only as a pointer to the broad subject. First abstract the subject into a general idea; then write an independently created fictional magical transformation. Never reuse or closely paraphrase the headline. Build a new subject, setting, visual sequence, hook, and payoff. Do not retell the article, imitate its headline, use named people or brands, or present the fictional scene as a real event.

## 10-second vertical story
- **0–2s — Hook:** Introduce an original visual mystery related only to the broad idea.
- **2–5s — Build:** Show a fictional subject facing a simple visual problem.
- **5–8s — Magic reveal:** Resolve it with one readable blue-and-gold transformation.
- **8–10s — Payoff:** Hold on the original transformed scene and show WonderVexa.

## Production prompt
Create an original fictional fantasy visual, vertical 9:16, cinematic close-up, coherent continuous motion, blue magical energy ring with subtle gold particles, consistent subject design, readable transformation, no text baked into footage, no recognizable copyrighted characters, no living-artist imitation, no logos or real-person likenesses.

## Editorial and originality checks
- A human editor must read the original source and independently verify any factual claim before adding it.
- This template is not an AI model and does not independently research, verify facts, or write a bespoke factual script.
- Use only an abstracted broad idea; do not reuse or closely paraphrase the discovery headline. Write all narration and scene descriptions independently.
- Do not reproduce article wording, substantial summaries, images, video, audio, or distinctive creative structure.
- Keep source links for internal verification and attribution.
- Do not call a research signal a verified trend.
- Human review required before video generation or publication.
"""
    metadata = {
        "id": story_id, "channel": "WonderVexa", "date": day.isoformat(),
        "slot": slot, "status": "draft", "topic": topic,
        "research_status": "signal_only_not_verified_platform_trend",
        "signal_label": signal["signal_label"],
        "source_name": signal["source_name"], "source_url": signal["source_url"],
        "article_url": signal["url"], "published_at": signal.get("published_at"),
        "research_signal_score": signal["research_signal_score"],
        "publishing": {"enabled": False, "requires_explicit_video_approval": True},
    }
    return script, metadata


def generate(signals_path: Path, output_dir: Path, day: date, slot: str) -> Path:
    try:
        payload = json.loads(signals_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"Could not read valid UTF-8 signal JSON: {exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        raise ValueError("Signal file must contain an object with an items array.")
    if payload.get("status") != "research_signals_only_not_verified_social_trends":
        raise ValueError("Signal file status is missing or not approved for research-only use.")
    candidates = [validate_signal(item) for item in payload["items"]]
    if not candidates:
        raise ValueError("No research signals are available.")
    candidates.sort(key=lambda item: item["research_signal_score"], reverse=True)
    script, metadata = build_story_brief(candidates[0], day, slot)
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / metadata["id"]
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing story package: {destination}")
    staging = Path(tempfile.mkdtemp(prefix=".story-package-", dir=output_dir))
    try:
        (staging / "story.md").write_text(script, encoding="utf-8")
        (staging / "metadata.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        # Publish the complete package directory in one same-filesystem rename.
        # A consumer sees either no package or both complete files, never a half-write.
        if destination.exists():
            raise FileExistsError(f"Refusing to overwrite existing story package: {destination}")
        staging.rename(destination)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--signals", type=Path, required=True)
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--slot", choices=("morning", "evening"), required=True)
    parser.add_argument("--output", type=Path, default=Path("output/research-stories"))
    args = parser.parse_args()
    path = generate(args.signals, args.output, date.fromisoformat(args.date), args.slot)
    print(f"Research story brief created: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
