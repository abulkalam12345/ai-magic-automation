# WonderVexa trend research adapter

## What is implemented

`src/trend_research.py` is a provider-neutral RSS 2.0 / Atom adapter. It accepts explicitly supplied public HTTPS feed URLs, fetches each with a timeout and a 1 MB response limit, blocks redirects to another host or to HTTP, parses titles/links/summaries/publication timestamps, and preserves source name, source URL and fetch time.

It drops entries with missing/unparseable dates, entries older than the configured freshness window (72 hours by default), and entries more than two hours in the future. It deduplicates identical URLs and ranks the remaining items using recency and repeated title coverage across feeds. The score is a triage heuristic, not a measure of platform popularity.

## Run manually

```bash
python src/trend_research.py \
  --feed "Source One=https://example.org/feed.xml" \
  --feed "Source Two=https://example.net/rss" \
  --output output/trend-research/signals.json
```

Only add sources whose public feed use is permitted and whose attribution requirements can be met. The example domains above are placeholders, not approved production sources. A feed returning no usable fresh entries exits with status 2. Individual feed failures are recorded in the output.

## Important limits

- RSS/Atom mentions are **research signals**, not verified YouTube, TikTok, Instagram or Facebook trends.
- Repeated titles across feeds do not prove independent reporting or audience demand.
- No scraping, login, cookies, platform private APIs, AI calls or paid services are used.
- No default sources are enabled until their ownership, terms, stability, update frequency and attribution requirements are reviewed.
- This module is not yet connected to the scheduled draft workflow. That integration should happen only after a reviewed source list is selected.
- Human review remains required before a topic becomes a WonderVexa script or any video is approved for publication.
