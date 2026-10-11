# WonderVexa trend research adapter

## What is implemented

`src/trend_research.py` is a provider-neutral RSS 2.0 / Atom adapter. It accepts explicitly supplied public HTTPS feed URLs, fetches each with a timeout and a 1 MB response limit, blocks redirects to another host or to HTTP, rejects unsafe or relative article links, validates the freshness window, and parses titles/links/summaries/publication timestamps, and preserves source name, source URL and fetch time.

It drops entries with missing/unparseable dates, entries older than the configured freshness window (72 hours by default), and entries more than two hours in the future. It deduplicates identical URLs and ranks the remaining items using recency and repeated title coverage across feeds. The score is a triage heuristic, not a measure of platform popularity.

## Research story brief generator

`src/story_generator.py` converts a reviewed signal JSON file into an original fictional story brief. It:
- accepts only the research-only status emitted by the trend adapter;
- requires a non-empty headline, summary, source name and absolute HTTP(S) source/article URLs;
- escapes untrusted feed text before placing it in Markdown, bounds input lengths, and rejects non-finite ranking scores;
- rejects unsafe URLs and any signal label other than `fresh_research_signal_not_verified_platform_trend`;
- selects the highest-ranked signal and preserves source attribution in the generated brief and metadata;
- creates a 10-second story structure and visual-generation prompt without copying article wording or making factual claims;
- keeps every output as a draft and publishing disabled with explicit per-video approval required.

This is deterministic template generation, not an AI language model. It does not fetch feeds itself or claim that a signal is a verified platform trend.

Example after producing a non-empty signal file:

```bash
python src/story_generator.py --signals output/trend-research/signals.json --slot morning
```

The output is written under `output/research-stories/`. Validate a generated package before review with `python src/story_package_check.py output/research-stories/<story-id>/`; the checker enforces attribution, required sections, draft-only status and explicit approval gates.

## Run trend research manually

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
- The research adapter and story brief generator are not connected to the scheduled draft workflow. That integration should happen only after a reviewed source list is selected and the output is reviewed.
- Human review remains required before a topic becomes a WonderVexa video or any video is approved for publication.
