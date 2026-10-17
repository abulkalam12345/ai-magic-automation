# Free.ai CogVideoX candidate assessment (2026-10-11)

## Status: candidate for a manually approved proof only; not approved for automation

Official pages reviewed:
- Video product: https://free.ai/video/text-to-video/
- CogVideoX model page: https://free.ai/models/cogvideox-2b/
- API documentation: https://free.ai/api/
- Pricing: https://free.ai/pricing/
- Terms: https://free.ai/terms/
- Privacy: https://free.ai/privacy/

### Positive evidence

The official product and model pages describe a self-hosted CogVideoX route:
- Short clips, with the product page describing 2–6 seconds and native 9:16 portrait.
- The product page advertises 30,000 free tokens/day for confirmed accounts, no credit card, and a free self-hosted CogVideoX route.
- The CogVideoX model page describes API use with model slug `cogvideox-2b`, bearer key auth, and a typical cost of about 10,000 tokens per clip, with a 15,000-token minimum.
- The API documentation describes `POST https://api.free.ai/v1/video/generate/`, Bearer API-key authentication, and asynchronous status polling.
- The Developer/API information indicates free-account API access; this is not evidence that every video request is free or that free caps can be bypassed.
- The Terms describe commercial use for self-hosted model outputs. The model page identifies CogVideoX-2B as Apache 2.0; verify the actual model/version and provider terms at time of use.
- The product/model pages advertise clean output without a watermark.

### Material conflicts in official pages

Do not treat the public documentation as a single consistent quota contract:

1. **Free video frequency differs by page.** The main English Pricing page says free accounts have a daily cap of 1 video. Other localized official Pricing pages say one clip every two days. The one-per-day statement nominally matches the target but leaves no retry capacity; the every-two-days statement does not meet it. This discrepancy must be resolved in the live account UI/support before any test or automation decision.
2. **Per-video token cost differs by page.** The CogVideoX model page says about 10,000 tokens typical and 15,000 minimum. The main English Pricing page says video costs 15,000 minimum per clip. API model documentation previously reviewed listed 30,000 tokens/video. Do not budget against the lowest number; confirm the exact selected model and displayed cost before any action.
3. **API model routing must be explicit.** The general API quick start has shown premium-model examples. A request must explicitly select the self-hosted CogVideoX-2B model. Never use a generic default that could route to a paid/external provider.
4. **Free pool and per-tool caps are separate.** 30,000 tokens/day does not mean 30,000 tokens worth of video can be generated every day; the per-video cap applies separately.
5. **Output duration.** Single clips are limited to short duration (product page says 2–6 seconds). The 8–12 second proof would require multiple clips or a documented extension workflow. The local sequence assembler can join clips, but it cannot invent missing footage or preserve identity between separate generations.
6. **Privacy and retention.** The Privacy Policy says prompts/outputs may be stored as generation history and gives account controls for deletion. Re-check the current policy and exact self-hosted handling before uploading any reference image or personal data.

### Fit for WonderVexa

- 9:16 portrait is advertised.
- Commercial use is described for self-hosted outputs, subject to current Terms, model license and applicable law.
- Multi-clip assembly is technically supported locally, but continuity needs a human review.
- The published frequency cap is inconsistent: one English page nominally permits one video daily, while localized pages say one every two days. Neither provides a dependable, consistently documented daily production allowance.
- Free pool, token cost, frequency caps and API model selection are not yet sufficiently consistent for unattended automation.

### Decision

**Keep Free.ai as a candidate for one manually approved proof only; do not integrate it into scheduled automation.** This is not approval to create an account, request a key, or consume quota.

Before any one-off test, obtain explicit user approval and verify in the live official account UI/support:
1. Current free video frequency cap for the account's region/locale.
2. Exact CogVideoX-2B API model ID and that the request cannot route to a premium/external model.
3. Exact token cost and minimum charge for the selected clip duration.
4. Free-account API key creation without buying tokens.
5. Exhausted quota hard-stops without any charge; no purchased balance, subscription, payment method, or paid fallback.
6. Current commercial license and prompt/reference/output retention terms.

No account was created, no email was submitted, no API key was requested, no API request was made, no tokens were consumed, and no video was generated.


## Official-page recheck (2026-10-17)

The current official Free.ai homepage and API pricing information reviewed on 2026-10-17 indicate a 30,000-token daily free pool and a 30,000-token CogVideoX clip cost. However, the frequency statement is not consistent across the official pages: the homepage/other localized pages indicate one video every two days, while the main English Pricing page says a daily cap of one video. Treat the frequency cap as unresolved until confirmed in the actual account UI or by official support. At 30,000 tokens per clip, one generation would also consume the entire stated daily pool, leaving no retry headroom.

Current official references checked:
- https://free.ai/ — free account quota and one-video-every-two-days cap.
- https://free.ai/api/ — API token pricing table, including 30,000 tokens/video.
- https://free.ai/models/cogvideox-2b/ — CogVideoX model details, 9:16 support, and API model slug.
- https://free.ai/video/text-to-video/ — product interface and duration information.

**Updated decision: do not approve Free.ai for WonderVexa's scheduled generation.** Its official quota/frequency statements conflict, and one clip consumes the entire stated daily token pool, leaving no retry headroom. The two-day limit shown on some official pages would also fail the target. Do not create an account, request an API key, generate a test clip, or integrate it into GitHub Actions unless the user explicitly approves a test after the quota and terms are reconciled. No account/API activity has been performed.

Older quota/cost statements elsewhere in this document are historical snapshots and are superseded by this dated recheck. The generation gate remains disabled.
