# Video provider evidence gate

WonderVexa has no approved hosted video-generation backend. Do not submit generation jobs, add API credentials, consume a free quota, or configure billing while a provider is unapproved.

## Local evidence-manifest checker

Before considering any provider, prepare a JSON manifest from current **official** provider documentation and run:

```bash
python src/provider_readiness.py path/to/provider-evidence.json
```

The checker requires official HTTPS references for free-tier pricing/quota, exact model/API documentation, model/output licensing, and prompt/reference/output data handling. It also requires explicit evidence for no-payment-method access, disabled paid fallback, commercial-use permission, daily quota, per-request limit, exact model ID, exact 9:16 dimensions, and an 8–12 second duration range.

Example manifest shape (replace every placeholder with verified official facts; this example is deliberately not a real approval):

```json
{
  "schema_version": 1,
  "provider": "REPLACE_WITH_PROVIDER",
  "evidence": {
    "official_free_tier_terms_url": "https://provider.example/free-terms",
    "official_model_docs_url": "https://provider.example/model-docs",
    "official_license_terms_url": "https://provider.example/license",
    "official_data_handling_url": "https://provider.example/data",
    "free_without_payment_method": false,
    "paid_fallback_disabled": false,
    "commercial_use_permitted": false,
    "prompt_and_output_data_terms_clear": false,
    "quota_daily_units": 1,
    "quota_unit": "REPLACE_WITH_UNIT",
    "per_request_limit": 1,
    "model_id": "REPLACE_WITH_EXACT_MODEL_ID",
    "output_width": 1080,
    "output_height": 1920,
    "min_duration_seconds": 8,
    "max_duration_seconds": 12
  },
  "controls": {
    "generation_enabled": false,
    "automatic_publishing_enabled": false,
    "requires_per_video_human_approval": true
  }
}
```

The checker is a **structural evidence gate only**. It cannot verify the truth or currentness of cited terms, independently approve a provider, or call an API. A passing manifest does not enable generation. A human must inspect the official terms and approve a one-off proof separately. Stop if a payment method, credits, billing, or paid fallback is required.

## Current candidates

- **Agnes AI — not approved.** Its official homepage advertises a Free API and Agnes-Video 2.5, but the public material checked does not establish the exact free video quota, no-payment/no-billing behavior, current model/API identifier, commercial output rights, or prompt/output data terms. The official model catalog lists Agnes Video 2.0 and a throughput rate; that is not a daily free-seconds guarantee. Do not infer free video generation from the general Free API wording.
- **Hugging Face ZeroGPU — not approved.** The free quota is limited and does not guarantee a particular video job will complete. Inference Providers are pay-as-you-go and excluded.
- Community Spaces and third-party clients are leads only, not authoritative evidence of free access, runtime, or commercial rights.

## Permanent safety controls

- Never store API keys in source code or sample manifests.
- Never enable generation in the scheduled workflow.
- Never enable automatic publishing.
- Require human approval for each individual video and each destination.
- No paid fallback, credit purchase, or billing setup.
- No provider call is made by this checker.

## Leading candidate: Free.ai CogVideoX (not yet approved)

Official research found a potentially useful self-hosted CogVideoX path: advertised 30K free tokens/day, no credit card, commercial use for self-hosted outputs, and native 9:16 support. However, its API documentation conflicts: the API quick start says to purchase tokens and demonstrates a premium video model, while a later model table lists CogVideoX at 5,000 tokens/video and a 30K/day free pool. The web product page estimates 10K tokens for a 4-second clip. It is not yet clear whether a free account can create an API key and call the self-hosted CogVideoX route without buying tokens.

Privacy terms say prompts/outputs are stored as generation history, are not used to train without explicit consent, and self-hosted model data stays on Free.ai servers. The Terms permit commercial use of self-hosted model outputs. The product supports 2–6 second clips and advertises 9:16; our 8–12 second proof would require multiple clips and continuity review.

Full assessment: [VIDEO_PROVIDER_FREEAI_ASSESSMENT.md](VIDEO_PROVIDER_FREEAI_ASSESSMENT.md).

**Decision:** leading candidate for a controlled evaluation only. No account/API key created, no API request made, no tokens consumed, and no provider integration enabled. Resolve the API free-balance/model-routing mismatch from official support before any generation request.


## Free.ai quota clarification (2026-10-11)

A later review of the official [CogVideoX model page](https://free.ai/models/cogvideox-2b/) and [Pricing page](https://free.ai/pricing/) found additional limits that materially affect feasibility: the model page estimates about 10K tokens for a ~5-second clip (minimum 15K), while the API page lists 30K tokens/video; Pricing says Free accounts are capped at one video clip every two days. The [Developer API page](https://free.ai/developer/) says a free account can create an API key without a card, but this does not remove the video-frequency cap or settle the conflicting per-video cost. The API uses a shared wallet, so no paid balance, token pack, subscription, payment method, or premium fallback may be used.

**Updated decision:** Free.ai remains a possible one-off manually approved proof candidate only, not a scheduled backend. The one-video-every-two-days cap cannot support the target of two daily videos. Do not create an account, request a key, or generate until the user explicitly approves the single test and the current model cost/cap are verified. See [full assessment](VIDEO_PROVIDER_FREEAI_ASSESSMENT.md).


## Free.ai official-page quota conflict (2026-10-11)

The current main English [Pricing page](https://free.ai/pricing/) says Free accounts have a daily cap of one video. Other localized official Pricing pages say one clip every two days. The official [CogVideoX-2B model page](https://free.ai/models/cogvideox-2b/) estimates about 10K tokens per clip with a 15K minimum; the main Pricing page says 15K minimum, while the API model table previously reviewed showed 30K/video. Treat frequency and cost as unresolved until confirmed in the live account UI/support. Even the more generous daily cap is below WonderVexa's target of two videos/day. No account or API activity is authorized by this assessment.

Updated full assessment: [VIDEO_PROVIDER_FREEAI_ASSESSMENT.md](VIDEO_PROVIDER_FREEAI_ASSESSMENT.md).


## Official recheck (2026-10-17) — Free.ai rejected for schedule

The current official Free.ai homepage states **one video every two days** on a free account, despite a 30,000-token daily pool. The same page says a video clip costs 30,000 tokens; the official API pricing table also lists CogVideoX at 30,000 tokens/video. This is not a viable backend for WonderVexa's target of two videos every 24 hours. Older Free.ai pages still show conflicting lower clip costs/durations; the stricter current quota and API pricing are used for this decision.

References:
- https://free.ai/
- https://free.ai/api/
- https://free.ai/models/cogvideox-2b/
- https://free.ai/video/text-to-video/

**Decision: Free.ai is not approved and is removed from the candidate shortlist for scheduled automation.** Do not create an account, request an API key, submit generation jobs, consume tokens, or integrate it. Generation remains disabled; no paid fallback is allowed. See [the updated detailed assessment](VIDEO_PROVIDER_FREEAI_ASSESSMENT.md).
