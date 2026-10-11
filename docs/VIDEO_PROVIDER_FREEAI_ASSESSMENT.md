# Free.ai CogVideoX candidate assessment (2026-10-11)

## Status: promising free-tier candidate; API activation blocked pending one documentation clarification

Official pages inspected:
- Video product: https://free.ai/video/text-to-video/
- API documentation: https://free.ai/api/
- Terms: https://free.ai/terms/
- Privacy: https://free.ai/privacy/

### Evidence that looks promising

The official video page describes a self-hosted CogVideoX path on Free.ai GPUs:
- 2–6 second single clips.
- Native 9:16 portrait is listed as a supported aspect ratio.
- The page advertises 30,000 free tokens/day for signed-in users and says no credit card is required.
- A 4-second clip is estimated at about 10,000 tokens on the web page.
- The page says the CogVideoX self-hosted route is free within the daily token pool, with no watermark.

The official API page independently lists CogVideoX video generation at **5,000 tokens/video**, a Free allowance of **30K/day (pool)**, and 10 API requests/minute. It documents `POST https://api.free.ai/v1/video/generate/`, Bearer API-key authentication, and `GET /v1/status/{job_id}/` for asynchronous status. It says a 402 response is returned when the balance is exhausted; paid token packs and subscriptions are available but must never be used by WonderVexa.

The official Terms say free tokens replenish daily at midnight UTC on a best-effort basis and may change. They say users retain ownership of inputs and outputs to the extent permitted by law, and that outputs from self-hosted models are available for commercial use. The Terms list CogVideoX among self-hosted models and say those models use commercial licenses. The video product page specifically names CogVideoX as the default self-hosted video model.

The Privacy Policy says prompts and outputs are processed and stored as generation history; inputs/outputs are not used to train models without explicit consent. It says self-hosted model data stays on Free.ai servers and is not sent to third parties. Generation history can be deleted from account settings; after account deletion it is purged within 30 days. Account data may be processed in the United States.

### Critical unresolved documentation mismatch

The API documentation is internally inconsistent:
- Its opening says users "Purchase tokens" before generating an API key.
- Its sample video call uses a `premium/kling-video/...` model.
- Later on the same API page, the model table lists CogVideoX at 5,000 tokens/video, the Free plan as 30K/day, and the endpoint as text/image-to-video (CogVideoX).
- The product page says CogVideoX is free within the daily token pool, but does not clearly demonstrate whether a free account can create an API key and call the self-hosted CogVideoX endpoint without first buying tokens.
- The web page says a 4-second clip costs about 10,000 tokens, while the API model table says 5,000 tokens/video. The units/pricing difference needs clarification.

Therefore do not assume that the website's free UI quota is available to API calls, or that an API key is available without purchase. Do not attempt a generation request to discover this: it could spend tokens or encounter a paid route.

### Fit for WonderVexa

- Native 9:16 is advertised, which is a strong fit.
- Single clips are only 2–6 seconds, shorter than the 8–12 second proof target. A proof would need at least two clips stitched together, or an officially documented extension workflow; consistency across separate clips would need visual review.
- The 30K/day pool appears to cover only a small number of short clips and is best-effort, not a guaranteed daily production allocation.
- API rate limit is 10 requests/minute; that is throughput, not quota.
- No watermark is advertised by the product page.
- Commercial use is supported by the provider's Terms for self-hosted models, but output uniqueness is not guaranteed. User remains responsible for rights in prompts/reference inputs.

### Decision

**Do not integrate or call the API yet. Keep Free.ai as the leading candidate for a manually controlled proof, not an approved automation backend.**

Before a one-off test:
1. Confirm from official support/docs that a Free account can create an API key without buying tokens.
2. Confirm the CogVideoX API request selects the self-hosted model and cannot silently route to a premium/external model.
3. Confirm the applicable video API token cost and that a free balance is actually available to the API.
4. Verify a failed/exhausted request returns a hard stop (e.g. 402) and cannot auto-charge; configure no paid tokens, no subscription, no payment method.
5. Use only a single, human-approved short proof if all above are clear. Do not use real-person likenesses or unlicensed reference media.
6. Inspect actual duration, 9:16 dimensions, watermark, character consistency, and quality manually before deciding whether to build an adapter.

No account was created, no email was submitted, no API key was requested, no API request was made, no tokens were consumed, and no video was generated.
