"""Fetch and rank public RSS/Atom signals without claiming they are platform trends.

This adapter is deliberately provider-neutral. It reads only explicitly supplied
HTTPS feeds, preserves source attribution and timestamps, and labels its output
as a research signal rather than a verified social-platform trend.
"""
from __future__ import annotations

import argparse
import email.utils
import json
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

USER_AGENT = "WonderVexaTrendResearch/1.0 (+https://github.com/abulkalam12345/ai-magic-automation)"
MAX_FEED_BYTES = 1_000_000
DEFAULT_TIMEOUT_SECONDS = 12
ATOM = "{http://www.w3.org/2005/Atom}"


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    value = value.strip()
    try:
        parsed = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _text(element: ET.Element, *names: str) -> str:
    for name in names:
        child = element.find(name)
        if child is not None:
            value = child.text or ""
            if value.strip():
                return value.strip()
    return ""


def _safe_article_url(value: str) -> str:
    """Accept only absolute HTTP(S) article links; reject executable or relative URLs."""
    parsed = urllib.parse.urlparse(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return ""
    if parsed.username or parsed.password:
        return ""
    return value.strip()


def _link(item: ET.Element, atom: bool) -> str:
    if atom:
        for child in item.findall(f"{ATOM}link"):
            href = child.attrib.get("href", "").strip()
            safe_href = _safe_article_url(href)
            if safe_href and child.attrib.get("rel", "alternate") == "alternate":
                return safe_href
        return ""
    return _safe_article_url(_text(item, "link"))


def parse_feed(xml_bytes: bytes, source_name: str, source_url: str, fetched_at: datetime | None = None) -> list[dict]:
    """Parse common RSS 2.0 or Atom entries into attributed research signals."""
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise ValueError(f"Invalid feed XML from {source_name}: {exc}") from exc
    fetched = (fetched_at or datetime.now(timezone.utc)).astimezone(timezone.utc)
    atom = root.tag == f"{ATOM}feed"
    if atom:
        entries = root.findall(f"{ATOM}entry")
    else:
        channel = root.find("channel")
        entries = channel.findall("item") if channel is not None else []
    results = []
    for entry in entries:
        if atom:
            title = _text(entry, f"{ATOM}title")
            published = _text(entry, f"{ATOM}published", f"{ATOM}updated")
            summary = _text(entry, f"{ATOM}summary", f"{ATOM}content")
        else:
            title = _text(entry, "title")
            published = _text(entry, "pubDate", "published", "updated")
            summary = _text(entry, "description", "summary")
        link = _link(entry, atom)
        if not title or not link:
            continue
        results.append({
            "title": title,
            "url": link,
            "summary": re.sub(r"\s+", " ", summary)[:500],
            "source_name": source_name,
            "source_url": source_url,
            "published_at": parse_timestamp(published).isoformat() if parse_timestamp(published) else None,
            "fetched_at": fetched.isoformat(),
        })
    return results


class _SameHostHTTPSRedirect(urllib.request.HTTPRedirectHandler):
    """Reject redirects before urllib makes a request to the destination host."""
    def __init__(self, original_host: str):
        super().__init__()
        self.original_host = original_host

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urllib.parse.urlparse(newurl)
        if target.scheme != "https" or target.hostname != self.original_host:
            raise ValueError("Feed redirect to a different host or non-HTTPS URL was blocked.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_feed(source_name: str, source_url: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> list[dict]:
    """Fetch one explicitly configured HTTPS feed; bound response size and redirects."""
    parsed = urllib.parse.urlparse(source_url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("Feed URL must use HTTPS.")
    request = urllib.request.Request(source_url, headers={"User-Agent": USER_AGENT, "Accept": "application/atom+xml, application/rss+xml, application/xml, text/xml"})
    try:
        opener = urllib.request.build_opener(_SameHostHTTPSRedirect(parsed.hostname))
        with opener.open(request, timeout=timeout) as response:
            final = urllib.parse.urlparse(response.geturl())
            if final.scheme != "https" or final.hostname != parsed.hostname:
                raise ValueError("Feed redirect to a different host or non-HTTPS URL was blocked.")
            payload = response.read(MAX_FEED_BYTES + 1)
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Could not fetch {source_name}: {exc}") from exc
    if len(payload) > MAX_FEED_BYTES:
        raise ValueError(f"Feed from {source_name} exceeds {MAX_FEED_BYTES} bytes.")
    return parse_feed(payload, source_name, source_url)


def rank_signals(items: list[dict], now: datetime | None = None, max_age_hours: int = 72) -> list[dict]:
    """Deduplicate links and rank fresh items by recency and independent source count."""
    if max_age_hours <= 0:
        raise ValueError("max_age_hours must be a positive integer.")
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    cutoff = current - timedelta(hours=max_age_hours)
    fresh = []
    for item in items:
        stamp = parse_timestamp(item.get("published_at"))
        if stamp is None or stamp > current + timedelta(hours=2) or stamp < cutoff:
            continue
        fresh.append((item, stamp))
    source_sets: dict[str, set[str]] = {}
    for item, _stamp in fresh:
        title_key = re.sub(r"[^a-z0-9]+", " ", item["title"].lower()).strip()
        source_sets.setdefault(title_key, set()).add(item.get("source_name", ""))
    unique: dict[str, tuple[dict, datetime]] = {}
    for item, stamp in fresh:
        key = item.get("url", "").strip().rstrip("/")
        if not key:
            continue
        old = unique.get(key)
        if old is None or stamp > old[1]:
            unique[key] = (item, stamp)
    ranked = []
    for item, stamp in unique.values():
        title_key = re.sub(r"[^a-z0-9]+", " ", item["title"].lower()).strip()
        age_hours = max(0.0, (current - stamp).total_seconds() / 3600)
        source_count = len(source_sets[title_key])
        score = round((max(0.0, 72.0 - age_hours) / 72.0) * 70 + min(source_count, 3) / 3 * 30, 2)
        ranked.append({**item, "age_hours": round(age_hours, 1), "independent_source_count": source_count,
                       "research_signal_score": score, "signal_label": "fresh_research_signal_not_verified_platform_trend"})
    return sorted(ranked, key=lambda x: (x["research_signal_score"], x["published_at"] or ""), reverse=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect attributed RSS/Atom research signals; not platform trend verification.")
    parser.add_argument("--feed", action="append", default=[], metavar="NAME=HTTPS_URL", help="Repeat for each approved public feed.")
    parser.add_argument("--output", default="output/trend-research/signals.json")
    parser.add_argument("--max-age-hours", type=int, default=72)
    args = parser.parse_args()
    if not args.feed:
        parser.error("provide at least one --feed NAME=HTTPS_URL")
    if args.max_age_hours <= 0:
        parser.error("--max-age-hours must be a positive integer")
    items = []
    failures = []
    for spec in args.feed:
        if "=" not in spec:
            failures.append(f"Invalid feed specification: {spec}")
            continue
        name, url = spec.split("=", 1)
        try:
            items.extend(fetch_feed(name.strip(), url.strip()))
        except (ValueError, RuntimeError) as exc:
            failures.append(str(exc))
    ranked = rank_signals(items, max_age_hours=args.max_age_hours)
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(),
               "status": "research_signals_only_not_verified_social_trends",
               "freshness_window_hours": args.max_age_hours,
               "items": ranked, "source_failures": failures}
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")
    print(f"Wrote {len(ranked)} fresh research signals to {output}; failed sources: {len(failures)}")
    return 0 if ranked else 2


if __name__ == "__main__":
    raise SystemExit(main())
