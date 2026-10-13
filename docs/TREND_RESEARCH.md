# WonderVexa trend research adapter

## What is implemented

`src/trend_research.py` is a provider-neutral RSS 2.0 / Atom adapter. It accepts explicitly supplied public HTTPS feed URLs, fetches each with a timeout and a 1 MB response limit, blocks redirects to another host or to HTTP, rejects unsafe or relative article links, and preserves source name, source URL and fetch time.

It drops entries with missing/unparseable dates, entries older than the configured freshness window (72 hours by default), and entries more than two hours in the future. It deduplicates identical URLs and ranks remaining items using recency and repeated title coverage across feeds. The score is a triage heuristic, not a measure of platform popularity.

## Scheduled workflow integration

The scheduled draft workflow now calls `src/scheduled_research.py` after the normal evergreen draft package is built and validated. The integration is deliberately **disabled by default** in `config/trend_feeds.json`:

- `enabled` must be explicitly changed to `true`.
- Only reviewed public HTTPS RSS/Atom feed URLs may be added.
- No feed is approved or enabled in this change; the default configuration makes no external feed requests.
- When enabled with valid sources, the workflow collects attributed signals, writes research-only story briefs for the morning and evening slots, and validates each package.
- If no fresh signal is available, the ordinary evergreen drafts remain the only drafts for that run.
- Feed failures fail the research stage closed; no feed text is treated as trusted instructions.

The scheduled workflow uploads evergreen drafts plus any research signal/story artifacts for human review. It does not render video or publish content.

## Research story brief generator

`src/story_generator.py` converts a reviewed signal JSON file into an original fictional story brief. It:
- accepts only the research-only status emitted by the trend adapter;
- requires a non-empty headline, summary, source name and absolute HTTP(S) source/article URLs;
- escapes untrusted feed text before placing it in Markdown, bounds input lengths, and rejects non-finite ranking scores;
- rejects unsafe URLs and any signal label other than `fresh_research_signal_not_verified_platform_trend`;
- preserves source attribution in the generated brief and metadata;
- creates a 10-second story structure and visual-generation prompt without copying article wording or making factual claims;
- keeps every output as a draft and publishing disabled with explicit per-video approval required.

This is deterministic template generation, not an AI language model. It does not fetch feeds itself or claim that a signal is a verified platform trend.

## Run trend research manually

```bash
python src/trend_research.py \
  --feed "Source One=https://example.org/feed.xml" \
  --feed "Source Two=https://example.net/rss" \
  --output output/trend-research/signals.json
```

Only add sources whose public feed use is permitted and whose attribution requirements can be met. The example domains above are placeholders, not approved production sources.

## Efficient and polite feed polling

The collector currently performs one fetch per scheduled run. Future repeated polling should honor publisher cache directives and conditional request validators (ETag / If-None-Match and Last-Modified / If-Modified-Since), handle 304 responses without parsing an empty body, and back off on 429 responses. See the [Open RSS developer guide](https://openrss.org/guides/developers-guide-to-open-rss-feeds) and [feedparser conditional request documentation](https://feedparser.readthedocs.io/en/stable/http-etag.html).

## Important limits

- RSS/Atom mentions are **research signals**, not verified YouTube, TikTok, Instagram or Facebook trends.
- Repeated titles across feeds do not prove independent reporting or audience demand.
- No scraping, login, cookies, platform private APIs, AI calls or paid services are used.
- Human review remains required before a topic becomes a WonderVexa video or any video is approved for publication.
