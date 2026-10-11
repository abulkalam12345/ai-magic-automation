# Free.ai CogVideoX candidate assessment (2026-10-11)

## Status: promising manual-proof candidate; not approved for automation

Official pages inspected:
- Video product: https://free.ai/video/text-to-video/
- CogVideoX model page: https://free.ai/models/cogvideox-2b/
- API documentation: https://free.ai/api/
- Developer API overview: https://free.ai/developer/
- Pricing: https://free.ai/pricing/
- Terms: https://free.ai/terms/
- Privacy: https://free.ai/privacy/

### Current official evidence

The product and model pages describe a self-hosted CogVideoX path:
- 2–6 second single clips; native 9:16 portrait is listed as supported.
- The signed-in free account pool is advertised as 30,000 tokens/day, with no credit card required to start.
- The model page says a typical ~5-second clip uses about 10,000 tokens, with a minimum 15,000 tokens.
- The API documentation's model table instead lists CogVideoX at 30,000 tokens/video and the free plan at 30,000 tokens/day.
- The API documents `POST https://api.free.ai/v1/video/generate/`, Bearer API-key authentication, and `GET /v1/status/{job_id}/` for asynchronous status.
- The Developer API overview says a free user can sign up, confirm email, create an API key under the account API page, and use the free daily pool without a card.
- The API says exhausted balance returns HTTP 402. The API's token wallet is shared between website and API.
- The product page advertises clean output without a watermark and supports 9:16.
- Free.ai's pricing page currently says free accounts are limited to **one video clip every two days**, even though the general free pool is 30K/day. The home page also repeats a video cap. This cap is important and makes two daily WonderVexa videos impossible on the free tier.
- The Terms describe daily free tokens as subject to change/best-effort. Self-hosted model outputs are described as available for commercial use; CogVideoX is identified as a self-hosted model.
- The Privacy Policy says prompts and outputs are processed/stored as generation history and not used to train without explicit consent; self-hosted model data stays on Free.ai servers. Check current terms again before any public use.

### Important inconsistencies / operational risks

1. **Video token price differs by page.** Model page says ~10,000 tokens for ~5 seconds (minimum 15,000); API page lists 30,000 tokens/video. Do not assume a clip will fit the daily pool or use the lower estimate.
2. **Free video frequency cap.** Pricing says one clip every two days on Free. That is below WonderVexa's target of two posts per 24 hours and may constrain even a single proof.
3. **Shared wallet / paid balance risk.** The API uses a shared token balance. A 402 on exhausted balance is documented, but the behavior when an account has purchased tokens is irrelevant to this zero-paid project. Never add purchased tokens, subscribe, enter a payment method, or enable any paid model/fallback.
4. **Output length.** A single render is 2–6 seconds, not the 8–12 second proof. Multi-clip assembly is now supported locally, but continuity and total duration must be reviewed; two separate clips can visibly change subject identity or scene.
5. **Best-effort capacity.** Daily pool and GPU capacity are not a production SLA or guaranteed generation allocation.

### Fit for WonderVexa

- Native 9:16 is advertised.
- Commercial use is advertised for self-hosted outputs, subject to current Terms and applicable law.
- A 10-second proof can be assembled from multiple short clips if their combined usable duration is sufficient. The local FFmpeg sequence utility can concatenate two or more clips, crop to 1080x1920, add the WonderVexa watermark, and export a thumbnail. It does not generate footage or guarantee character continuity.
- The current free-tier one-video-every-two-days cap is incompatible with the desired twice-daily production target.
- The discrepancy in token cost and clip caps means quota must be confirmed in the account UI before any manual test.

### Decision

**Keep Free.ai as a candidate for a single, manually approved proof only; do not integrate it into scheduled automation.** This is not approval to create an account or spend quota.

Before a one-off test, the user must explicitly authorize account creation / key handling and a single generation attempt. First verify in official account UI/support:
1. Exact current CogVideoX model ID and API model selection.
2. Exact cost and minimum charge for one clip, and whether free account video caps apply equally to API.
3. The free account can create an API key without purchase (Developer page currently says yes).
4. Exhausted requests hard-stop and no purchased balance/payment method is attached.
5. No model routing to premium/external services.
6. Exact prompt/reference/output data retention terms.

No account was created, no email was submitted, no API key was requested, no API request was made, no tokens were consumed, and no video was generated. No payment method or paid fallback was enabled.
