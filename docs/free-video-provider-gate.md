# Free video provider gate — Free.ai (checked 2026-10-21)

## Decision

Status: **manual trial candidate only; not approved for automation**.

Do not connect an API key, spend tokens, start a paid plan, enable auto top-up, or run generation automatically. The WonderVexa project must remain at NPR 0 with no paid fallback.

## What the provider currently claims

Official Free.ai pages describe self-hosted CogVideoX video generation, MP4 output, no watermark, mobile-browser support, 9:16 output, and commercial use. The text-to-video page describes 2–6 second clips and says signed-in accounts receive 30,000 daily tokens. The CogVideoX model page says a 4-second clip uses roughly 10,000 tokens.

Official pricing/token pages are not fully consistent about video allowances:
- The pricing page describes a free account with 30,000 daily tokens and a daily cap of one video clip.
- The video page describes free clips up to 3 seconds and 6,000 anonymous / 30,000 signed-in daily tokens.
- Another localized video page describes one free clip every other day.
- The token page gives differing per-clip figures in different sections (5,000 vs 15,000 tokens).

Therefore, the actual available free clip quota, clip duration, and token cost must be confirmed in the signed-in account UI immediately before any manual test. Never assume that the advertised daily pool means a clip is available today.

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
