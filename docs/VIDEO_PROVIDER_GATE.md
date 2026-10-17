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



## Additional hosted-provider screening (2026-10-17)

- **Hugging Face Inference Providers — rejected for zero-budget production.** Official pricing says Free users receive only $0.10 monthly credit, subject to change, and extra usage is pay-as-you-go. The official text-to-video API docs show the video task and provider routing, but do not promise enough free video-generation quota for two finished videos every day. Do not route requests through a paid provider or allow extra usage. References: https://huggingface.co/docs/inference-providers/pricing and https://huggingface.co/docs/inference-providers/main/en/tasks/text-to-video
- **FXI Studio — rejected for the daily schedule.** Its official page advertises 65 initial credits, about three short video clips, then 25 credits weekly. It says stitched-film export requires Creator plan or above. This is not enough for two finished 8–12 second videos every day. No account created and no credits consumed. Reference: https://www.fxi.studio/free-ai-film-maker
- **Synthesia — not suitable for this pipeline.** Its official page advertises up to 10 minutes/month on a free plan, but states free videos include Synthesia branding and that downloads require a paid plan. This does not meet the WonderVexa output/export and branding requirements. Reference: https://www.synthesia.io/features/text-to-video

**Screening result:** none of these providers qualifies for integration. Keep `generation_enabled=false`, do not add credentials, and do not enable any billing or paid fallback. These are desktop/cloud service assessments only; no account creation, API key request, generation job, or quota use occurred.


## Free.ai reassessment for a one-video-per-day target (2026-10-17)

The target has been reduced from two daily videos to one. This makes Free.ai's **website free tier** worth considering for a manual trial, but does not qualify its API for automation.

Current official pages reviewed:
- Pricing: https://free.ai/pricing/ — advertises 30,000 free tokens/day and a free-account cap of one video clip/day, with no credit card. It also lists video at 15,000 tokens minimum plus 2,500 tokens/second beyond 6 seconds.
- Tools directory: https://free.ai/tools/ — says video needs a free account, a video costs 30,000 tokens, and hosted self-hosted-model outputs are commercially usable.
- Text-to-video: https://free.ai/video/text-to-video/ — describes CogVideoX output as a 2–6 second MP4 clip and advertises commercial use.
- API pricing: https://free.ai/api/ — lists CogVideoX at 30,000 tokens/video and 30,000 free tokens/day, but the current Docs FAQ says the daily free pool applies to web requests, not API calls; the API page also says "Purchase tokens" in its API-key flow.
- Docs: https://free.ai/docs/ — says the free daily pool applies to web requests, not API calls, and the API request cap is 1,000/month on Free.

**Decision:** Free.ai may be tried manually on its website for at most one short clip/day, subject to the account UI confirming the free quota and no payment requirement. It is **not approved for unattended API automation**. The clip is only 2–6 seconds, so it does not alone meet WonderVexa's intended 8–12 second finished video. Do not assume stitching, multiple clips, exact 9:16 output, or commercial permission beyond the terms shown in the actual free account.

No account has been created, no API key requested, no generation submitted, and no tokens consumed. Keep generation disabled in GitHub Actions and publishing disabled. A manual trial requires the user to sign up/confirm the free account on the official site and verify the displayed cost before pressing Generate; stop if a payment method, token purchase, or paid upgrade is requested.


## Watermark policy update (2026-10-17)

The user accepts a provider's own visible watermark on free-tier output. A provider watermark is **not a disqualifier**. The final WonderVexa edit may add the WonderVexa channel logo as a separate overlay, preferably in a clear corner that does not obscure the provider watermark, captions, or important scene content.

Do not remove, crop out, blur, cover, or otherwise defeat a provider watermark or attribution. Before use, verify that the provider's free-tier terms permit downloading, editing/overlaying a channel logo, and publishing the resulting video on the intended social platforms, including commercial/monetized use if applicable. A watermark acceptance does not waive licensing, quota, account, privacy, or billing checks.

Keep the same zero-budget controls: no payment method, no paid fallback, no token purchases, and no automatic publishing. A provider may only be integrated after its current free quota, output rights, duration/aspect-ratio, and API access are verified. Generation stays disabled until a separately approved test succeeds.


## Free.ai official page conflict recheck (2026-10-17)

The latest official pages still conflict, so Free.ai is **not approved for automation**:

- Homepage says the free account gets 30,000 tokens/day but only **one video every two days**, and its FAQ says a clip costs 30,000 tokens.
- Pricing page says Free has 30,000 tokens/day and **one video clip/day**, while its pricing explanation gives an approximate 15,000-token minimum / 2,500 tokens per second.
- CogVideoX model page says approximately 10,000 tokens per 5-second clip, with a maximum of 6 seconds and 9:16 supported.
- Text-to-video page says a 4-second clip is about 10,000 tokens, supports 2–6 seconds and 9:16, and claims commercial use is permitted.
- API page's key-creation flow says **purchase tokens**, despite listing a Free plan with 30,000 tokens/day and 1,000 API requests/month. This does not establish that the free web allowance is actually usable through API.

Official pages checked:
- https://free.ai/
- https://free.ai/pricing/
- https://free.ai/models/cogvideox-2b/
- https://free.ai/video/text-to-video/
- https://free.ai/api/

**Decision:** Keep Free.ai as a possible *manual, user-controlled web trial only*, not an unattended provider. The contradictory free video cap and token cost are unresolved. Its 2–6 second clips would need stitching to reach the 8–12 second target; do not assume multiple clips fit the free quota. The current one-video-per-day target does not resolve these contradictions. The user accepts a provider watermark, but that does not waive rights, quota, or billing checks.

No account was created, no API key requested, no generation run, and no tokens consumed. Do not enable generation, add credentials, configure billing, or use paid fallback. A manual trial requires the user to inspect the live account balance/quota and confirm the exact free cost before pressing Generate. Publishing remains disabled pending explicit user approval.


## PixVerse screening (2026-10-17)

**Decision: not approved for WonderVexa free commercial production.**

Official PixVerse app FAQ states that free members receive 60 daily credits (non-members 30), refreshed at UTC midnight; generation cost varies by model, resolution, duration, and settings and is shown before generation. This does not by itself establish enough credits for a finished 8–12 second video each day.

More importantly, the official PixVerse Terms of Service state that output use is limited to **non-commercial purposes** unless separate authorization or a commercial-use license is obtained. A later download clause says certain information may be used commercially if unaltered, creating an ambiguity with the explicit output restriction. For a monetized/social brand workflow, do not rely on that ambiguous clause. The official API platform terms separately require written authorization for certain commercial-profit uses of API-generated videos and preserve source/generation identifiers.

Official sources:
- https://docs.pixverse.ai/FAQ-PixVerse-App-1533e99bf35080888cb5effee85f8289
- https://pixverse.ai/en/terms-of-service
- https://pixverse.ai/en/pixverse-platform-terms-of-service

No PixVerse account was created, no credits consumed, no API key requested, and no generation submitted. Do not integrate or use free outputs for WonderVexa commercial/monetized publishing unless PixVerse provides clear written commercial authorization applicable to the exact plan and workflow. A visible provider watermark would be acceptable under the user's preference, but does not resolve the licensing restriction. Keep generation and publishing disabled.
