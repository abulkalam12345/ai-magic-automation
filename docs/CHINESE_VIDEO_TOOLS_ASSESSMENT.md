# Chinese AI video tools assessment (2026-10-11)

## Decision

Chinese-origin tools are included as research candidates, but **none is approved for WonderVexa automation yet**. The project requirements remain:

- No payment method, paid credits, subscription, or paid fallback.
- Explicit, current permission for public/commercial social-media use.
- Clear handling/retention terms for prompts, reference images, and outputs.
- Stable API or repeatable manual export, with exact model/version documented.
- Portrait 9:16 output or reliable local reframing, with a human continuity/quality review.
- No account creation, API-key request, quota use, generation, or publishing without the required user approval.

## Candidate 1: Kling AI (Kuaishou) — not approved

**Official-terms recheck (2026-10-17):** Kling's current Terms of Service restrict use of the service for commercial purposes without written consent, require Kling branding/attribution for generated output absent written permission, and prohibit commercial use/modification of output without written permission. These binding terms conflict with promotional FAQ wording that suggests free-tier commercial use. The Terms therefore control this project's decision: free-tier Kling output is **not approved for WonderVexa commercial/social monetized use** unless Kling provides explicit written permission applicable to the account and output.


Official pages:
- Video generation / image-to-video overview: https://kling.ai/explore/open_video
- Kling AI assistance FAQ: https://kling.ai/explore/kling_ai_assistance
- Free background app FAQ: https://kling.ai/explore/free_background_app

What is established:
- Kling advertises video generation and image-to-video features.
- Its public pages describe a free entry tier / free generations with credits.
- The public pages are inconsistent about free-tier commercial rights: one page says free outputs may be used commercially, while another says commercial use depends on subscription and free use is typically personal. The public statements are not sufficient to establish a reliable right for WonderVexa's monetized/social-media use.
- Free outputs may carry a Kling watermark; watermark-free output is presented as a membership benefit on some pages.

Blockers:
1. Confirm the terms actually applicable to the user's account region and Basic/free tier.
2. Confirm free-tier commercial/social-media rights from the current binding Terms, not a promotional FAQ alone.
3. Confirm exact free credit allowance, reset rules, generation duration/resolution, watermark, and whether API access is free.
4. Confirm no payment method or paid fallback is required.
5. No official evidence reviewed here establishes a no-cost API suitable for scheduled GitHub Actions.

Decision: keep as a possible manually operated creative tool only after terms and free quota are verified. Do not integrate, call an API, or use its output commercially based on conflicting public FAQ claims.

## Candidate 2: Wan (Alibaba ecosystem / open model family) — research candidate

Official model repository: https://github.com/Wan-Video/Wan2.2

Wan is an open model family rather than a single hosted free service. Running it locally or on a hosted GPU requires compute. Open model weights do not make GPU time, storage, hosting, or API inference automatically free. The exact checkpoint's license and model requirements must be checked separately.

Blockers:
1. Select an exact checkpoint and inspect its license.
2. Verify GPU memory/runtime requirements against genuinely available no-cost hardware.
3. Confirm portrait framing and short-clip settings for the exact checkpoint.
4. Do not route through pay-as-you-go inference endpoints or paid GPU rentals.

Decision: retain as a self-hosted research option; no hosted endpoint or GPU runtime is approved.

## Candidate 3: Hailuo AI / MiniMax — not yet verified

Official site: https://hailuoai.video/

Hailuo is a relevant Chinese-origin video-generation candidate, but this assessment has not established a stable free quota, no-payment/no-billing behavior, commercial-use rights for free outputs, or a free API with predictable limits.

Decision: research lead only. Do not create an account, integrate, submit jobs, or use output commercially until current official pricing, terms, data handling, API, and export details are verified.

## Automation policy

- The scheduled WonderVexa workflow remains draft-only.
- Do not add any of these providers to GitHub Actions or request API credentials.
- Do not use unofficial wrappers, shared keys, account farming, or quota workarounds.
- Stop immediately if a billing prompt, token purchase, subscription, or paid fallback appears.
- Keep a provider disabled until the existing `src/provider_readiness.py` evidence gate can be completed from current official documents and a separate human approval is recorded.
- A human must approve each individual generated video and its publishing destinations. No video is published automatically.

## Current outcome

No Chinese provider has passed the zero-cost, rights, data-handling, technical, and operational checks. No accounts were created, no credentials requested, no API calls made, no credits consumed, and no videos generated.
