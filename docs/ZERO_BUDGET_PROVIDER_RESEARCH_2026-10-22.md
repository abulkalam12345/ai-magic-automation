# Zero-budget video provider research

Reviewed: 2026-10-22
Project target: one original WonderVexa video per 24 hours, Android-only operation, NPR 0 budget.

## Decision summary

No candidate is approved for unattended generation or monetized publishing yet. The strongest immediate path is a **manual one-clip proof**, followed by review of the exact engine and its terms. Do not connect a provider to GitHub Actions until the proof and rights checks pass.

## Candidate findings

### Hedra App — manual test candidate, not approved

- Official FAQ says no account/sign-up, free ad-supported access, Android support, and a few minutes of shared GPU time per visitor per day: https://app.hedra.pro/faq
- Its Terms say generators are operated by third-party providers; engine availability and results are not guaranteed. Output rights are subject to the selected engine's terms: https://app.hedra.pro/terms
- Its Privacy Policy says prompts and uploaded media go directly to the embedded AI provider; that provider's privacy terms govern processing: https://app.hedra.pro/privacy
- Conclusion: promising for a manual test, but commercial rights, provider identity, retention, and exact engine quota must be checked per selected engine. A daily one-video target is not guaranteed by a "few minutes" shared quota.

### nokeep — manual one-clip candidate only

- Its product page advertises one free five-second text-to-video clip per day, no account, and generated sound: https://nokeep.ai/video
- Longer clips and image-to-video require credits according to the page.
- Conclusion: the free daily clip length aligns with a proof-of-concept, but this is not enough evidence for an unattended automation integration. Re-check current terms and engine/license conditions before commercial use. Do not automate browser interactions or bypass limits.

### Adobe Firefly — promising rights position, quota uncertain

- Adobe says free users receive limited daily generations and the available models/features can change: https://helpx.adobe.com/creative-cloud/apps/generative-ai/generative-credits-faq.html
- Adobe says non-beta Firefly outputs can be used commercially; partner models may have different terms: https://www.adobe.com/products/firefly/features/ai-video-generator.html
- Conclusion: the Firefly Video Model is a better documented commercial-rights candidate, but the free daily allowance is limited and Adobe requires an account. The exact video feature availability and remaining free generation count must be checked in the user's account before choosing it. Do not use partner models without separate rights review.

### Wan2.Video and LTX AI web frontends — unapproved third-party demos

- Wan2.Video advertises public GPU queues, no sign-up, and Wan/LTX models: https://wan2.video/
- LTX AI frontend advertises free public GPU queues and no account: https://www.ltx-ai.net/
- Conclusion: public demo claims do not establish guaranteed daily quota, commercial output rights, data retention, or service continuity. Treat as experimental only; do not upload private assets or rely on them for a scheduled pipeline.

## Required proof protocol

1. Use a non-sensitive original prompt and no real person's likeness.
2. Generate one five-second vertical sample manually, only if the selected engine is available without payment details.
3. Record the exact engine/model name, duration, dimensions, watermark, quota message, and export behavior.
4. Open the selected engine's own terms and privacy policy. Confirm commercial/social-media rights and data handling.
5. Review face, hands, motion, sound, vertical framing, and character consistency.
6. Keep generation disabled in GitHub Actions until the user explicitly approves the exact provider/model and all checks pass.

## Non-negotiable constraints

- NPR 0: no paid credits, subscriptions, API usage, payment card, auto top-up, or paid fallback.
- One finished video target per 24 hours; this is a goal, not a guaranteed provider quota.
- User approval before every public upload and each destination.
- Never commit secrets or tokens.
- Do not modify the separate Nepal News automation project.

## Research limitation

Public product pages can change and may not disclose the actual embedded engine. A website's "free" claim is not proof of commercial rights, daily availability, or permission for automation. Verify the exact engine at the time of the manual test.
