import importlib.util
import unittest
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

    def test_rejects_malformed_xml(self):
        with self.assertRaisesRegex(ValueError, "Invalid feed XML"):
            trend.parse_feed(b"<rss>", "Bad", "https://example.org")

    def test_rejects_non_https_feed(self):
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            trend.fetch_feed("bad", "http://example.org/feed")

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

    def test_rejects_invalid_timestamp_as_not_fresh(self):
        now = datetime(2026, 10, 11, 12, tzinfo=timezone.utc)
        record = {"title": "Unknown date", "url": "https://example.org/x", "published_at": None}
        self.assertEqual(trend.rank_signals([record], now=now), [])


if __name__ == "__main__":
    unittest.main()
