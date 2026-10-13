import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timezone

MODULE = __import__("pathlib").Path(__file__).parents[1] / "src" / "trend_research.py"
SPEC = importlib.util.spec_from_file_location("trend_research", MODULE)
trend = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(trend)


class TrendResearchTests(unittest.TestCase):
    def test_parses_rss_with_attribution_and_timestamp(self):
        xml = b"""<rss version="2.0"><channel><item><title>Magic flowers</title><link>https://example.org/a</link><pubDate>Sun, 11 Oct 2026 08:00:00 GMT</pubDate><description>Blooming magic</description></item></channel></rss>"""
        result = trend.parse_feed(xml, "Example", "https://example.org/feed", datetime(2026, 10, 11, 9, tzinfo=timezone.utc))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["source_name"], "Example")
        self.assertEqual(result[0]["title"], "Magic flowers")
        self.assertTrue(result[0]["published_at"].endswith("+00:00"))

    def test_parses_atom(self):
        xml = b"""<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Crystal garden</title><link href="https://example.org/b"/><updated>2026-10-11T08:00:00Z</updated><summary>Shimmering</summary></entry></feed>"""
        result = trend.parse_feed(xml, "Atom source", "https://example.org/atom")
        self.assertEqual(result[0]["url"], "https://example.org/b")
        self.assertEqual(result[0]["source_name"], "Atom source")

    def test_rejects_unsafe_or_relative_article_links(self):
        xml = b"""<rss><channel>
        <item><title>Unsafe</title><link>javascript:alert(1)</link><pubDate>Sun, 11 Oct 2026 08:00:00 GMT</pubDate></item>
        <item><title>Relative</title><link>/story</link><pubDate>Sun, 11 Oct 2026 08:00:00 GMT</pubDate></item>
        <item><title>Safe</title><link>https://example.org/story</link><pubDate>Sun, 11 Oct 2026 08:00:00 GMT</pubDate></item>
        </channel></rss>"""
        result = trend.parse_feed(xml, "Example", "https://example.org/feed")
        self.assertEqual([item["title"] for item in result], ["Safe"])

    def test_rejects_nonpositive_freshness_window(self):
        with self.assertRaisesRegex(ValueError, "positive"):
            trend.rank_signals([], max_age_hours=0)

    def test_rejects_malformed_xml(self):
        with self.assertRaisesRegex(ValueError, "Invalid feed XML"):
            trend.parse_feed(b"<rss>", "Bad", "https://example.org")

    def test_rejects_dtd_and_entity_declarations(self):
        payloads = (
            b'<!DOCTYPE rss [<!ENTITY x "expanded">]><rss><channel/></rss>',
            b'<!ENTITY x "expanded"><rss><channel/></rss>',
        )
        for payload in payloads:
            with self.subTest(payload=payload), self.assertRaisesRegex(ValueError, "DTD and entity"):
                trend.parse_feed(payload, "Untrusted", "https://example.org/feed")

    def test_rejects_non_https_feed(self):
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            trend.fetch_feed("bad", "http://example.org/feed")

    def test_rejects_feed_urls_with_credentials_or_invalid_authority(self):
        for url in ("https://user:pass@example.org/feed", "https://[broken/feed"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                trend.fetch_feed("bad", url)

    def test_redirect_policy_rejects_cross_host_and_http_before_following(self):
        handler = trend._SameHostHTTPSRedirect("example.org")
        request = __import__("urllib.request", fromlist=["Request"]).Request("https://example.org/feed")
        with self.assertRaisesRegex(ValueError, "redirect"):
            handler.redirect_request(request, None, 302, "Found", {}, "https://evil.example/feed")
        with self.assertRaisesRegex(ValueError, "redirect"):
            handler.redirect_request(request, None, 302, "Found", {}, "http://example.org/feed")
        with self.assertRaisesRegex(ValueError, "redirect"):
            handler.redirect_request(request, None, 302, "Found", {}, "https://user:pass@example.org/feed")

    def test_rss_summary_whitespace_is_normalized(self):
        xml = b"""<rss><channel><item><title>Test</title><link>https://example.org/x</link><pubDate>Sun, 11 Oct 2026 08:00:00 GMT</pubDate><description>line one&#10;   line two</description></item></channel></rss>"""
        result = trend.parse_feed(xml, "Example", "https://example.org/feed")
        self.assertEqual(result[0]["summary"], "line one line two")

    def test_ranking_filters_stale_and_future_and_deduplicates_urls(self):
        now = datetime(2026, 10, 11, 12, tzinfo=timezone.utc)
        def item(title, url, published, source):
            return {"title": title, "url": url, "published_at": published,
                    "source_name": source, "source_url": "https://example.org/feed",
                    "summary": "", "fetched_at": now.isoformat()}
        records = [
            item("Magic flower", "https://example.org/1", "2026-10-11T11:00:00Z", "A"),
            item("Magic flower", "https://example.net/2", "2026-10-11T10:00:00Z", "B"),
            item("Old item", "https://example.org/old", "2026-10-01T10:00:00Z", "A"),
            item("Future item", "https://example.org/future", "2026-10-12T10:00:00Z", "A"),
            item("Duplicate URL", "https://example.org/1", "2026-10-11T11:30:00Z", "C"),
        ]
        ranked = trend.rank_signals(records, now=now, max_age_hours=72)
        self.assertEqual(len(ranked), 2)
        self.assertEqual(ranked[0]["independent_source_count"], 2)
        self.assertEqual(ranked[0]["signal_label"], "fresh_research_signal_not_verified_platform_trend")

    def test_cli_writes_parseable_json_file(self):
        now = datetime.now(timezone.utc)
        record = {"title": "Current signal", "url": "https://example.org/story",
                  "published_at": now.isoformat(), "source_name": "Example",
                  "source_url": "https://example.org/feed", "summary": "Summary",
                  "fetched_at": now.isoformat()}
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "signals.json"
            with patch.object(sys, "argv", ["trend_research.py", "--feed",
                                            "Example=https://example.org/feed",
                                            "--output", str(output)]), \
                 patch.object(trend, "fetch_feed", return_value=[record]):
                self.assertEqual(trend.main(), 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["items"][0]["title"], "Current signal")

    def test_rejects_invalid_timestamp_as_not_fresh(self):
        now = datetime(2026, 10, 11, 12, tzinfo=timezone.utc)
        record = {"title": "Unknown date", "url": "https://example.org/x", "published_at": None}
        self.assertEqual(trend.rank_signals([record], now=now), [])


if __name__ == "__main__":
    unittest.main()
