# Free video provider gate — Free.ai (checked 2026-10-21)

## Decision

Status: **manual trial candidate only; not approved for automation**.

Do not connect an API key, spend tokens, start a paid plan, enable auto top-up, or run generation automatically. The WonderVexa project must remain at NPR 0 with no paid fallback.

## What the provider currently claims

Official Free.ai pages describe self-hosted CogVideoX video generation, MP4 output, no watermark, 9:16 output, and commercial use. The general video page currently describes free CogVideoX clips up to 3 seconds at 480p, with 6,000 daily tokens anonymously and 30,000 daily tokens for signed-in accounts. The CogVideoX-2B model page separately describes about 10,000 tokens per ~5-second clip, a minimum of 15,000 tokens, and paid top-ups after the daily pool is exhausted. These claims are inconsistent across the provider's own pages.

Official pricing/token pages are not fully consistent about video allowances:
- The general video page describes free clips up to 3 seconds, with 6,000 anonymous / 30,000 signed-in daily tokens; it estimates 2 seconds at ~5,000 tokens and 3 seconds at ~7,500 tokens.
- The CogVideoX-2B model page describes ~2,500 tokens per second, a 15,000-token minimum, and ~10,000 tokens per ~5-second clip elsewhere on the same page.
- A localized video page describes one free account clip every other day and a different 2-second/3-second token schedule.
- The separate Movie Generator says a 3-scene movie costs ~15,500 tokens, so it is not guaranteed to fit a free daily pool.

Therefore, even though the public pages advertise a free daily token pool, the actual eligible model, available clip quota, duration, and token cost are not reliably established by the public documentation. Confirm the exact selected model and live token cost in the signed-in account UI immediately before any manual test. Never assume that a daily token balance guarantees a free clip.

## Quality and workflow risks

- CogVideoX model guidance warns that intricate hand interaction and fine text are weaker. Episode 01 depends on a lemon vanish, independent mirror movement, and a mirror-crossing double; these are high-risk shots.
- A short sample cannot establish consistent character identity across six shots.
- Free.ai's published privacy description says prompts are retained for a limited share window; do not upload the user's channel logo, personal images, or sensitive material without reviewing the current privacy controls.
- API availability does not establish free API access, a stable quota, or suitability for unattended scheduled use.
- Provider terms and quotas can change. Re-check before every test or integration.

## Safe manual evaluation checklist

1. Open https://free.ai/video/text-to-video/ in the Android browser.
2. Confirm the selected model is the self-hosted CogVideoX option, not a paid premium model.
3. Read the current displayed clip duration, token cost, free quota, and remaining balance.
4. Confirm no card, paid plan, free trial, or auto top-up is required or enabled.
5. If the UI does not clearly show a free clip without payment risk, stop. Do not press Generate.
6. If it clearly shows an included free clip and the user explicitly authorizes a one-time test, use a simple low-risk 3-second mirror shot first. Do not attempt the full episode in one generation.
7. Review identity consistency, face quality, hands, mirror geometry, resolution, audio absence, watermark, commercial-use terms, and output download.
8. Only after a successful user-reviewed test may automation feasibility be reconsidered.

## Project integration gate

No Free.ai API credentials or generation calls are added to the repository. No scheduled generation is enabled. The existing evening workflow only creates the editorial package and technical draft artifacts. Publishing remains disabled and requires explicit approval for each finished video and destination.
