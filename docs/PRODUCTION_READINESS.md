# WonderVexa Production Readiness

Last reviewed: 2026-10-28

Current target: one finished video per 24 hours. Zero budget remains mandatory. The separate Nepal News project is out of scope.

This tracker distinguishes working draft automation from the unfinished real-video and publishing pipeline.

## Verified working

- The morning draft workflow is scheduled for 06:15 Nepal time (00:30 UTC), once per day.
- The optional evening draft workflow is manual-only (`workflow_dispatch`); it has no schedule and must not be treated as a second daily posting slot.
- The daily workflow builds draft metadata and a procedural motion-graphics preview.
- The optional evening workflow also builds the six-scene Episode 01 editorial package.
- Draft-package validation and technical preview checks run in GitHub Actions.
- GitHub Actions artifacts are retained for 14 days.
- Latest observed project validation: successful run [40699235341](https://github.com/abulkalam12345/ai-magic-automation/actions/runs/40699235341), commit `5e22a44a143626b81bf40ee0c061d98de8fb5709`.

## Not yet delivered

- No verified photorealistic AI magician footage has been generated.
- Procedural preview renders are not the intended live-action magician videos.
- Hindi voice performance and recurring-character identity consistency have not been validated on generated footage.
- No AI video provider has passed the project's zero-cost and commercial-rights approval gate.
- RSS trend research remains disabled pending source approval; current draft topics must not be described as verified live trends.
- No social platform publishing integration is approved or enabled.
- No video has been published by this workflow.

## Provider approval checklist

A candidate provider must be checked against its current official terms and the actual selected model/engine:

- [ ] A genuinely free, usable allowance is documented; no card, trial conversion, paid fallback, or auto top-up.
- [ ] The selected model supports the required vertical video format and practical clip length.
- [ ] Commercial/social-media rights are explicitly compatible with the intended use.
- [ ] Data handling and retention are understood.
- [ ] Daily quota is sufficient or the user accepts a lower manual cadence.
- [ ] Any aggregator's underlying engine and its terms are identified.
- [ ] A real sample is reviewed for face, hands, motion, audio, and character continuity.

Passing a website marketing claim alone does not satisfy this checklist.

## Publishing approval gate

- [ ] User reviews the complete final video.
- [ ] User explicitly approves each destination before upload.
- [ ] The platform's current API and account requirements are met.
- [ ] Credentials remain in GitHub encrypted secrets or the platform's secure OAuth flow; never commit tokens.
- [ ] Publishing remains disabled until all checks pass.

## Provider research

See [Zero-budget provider research (2026-10-22)](ZERO_BUDGET_PROVIDER_RESEARCH_2026-10-22.md) and [video provider evidence gate](VIDEO_PROVIDER_GATE.md). Current decision: no provider is approved for scheduled generation. Google Flow's public help currently describes 50 daily credits for non-subscribers, but account-specific access, regional availability at the time of use, generation reliability, model terms, and commercial-use suitability have not been independently confirmed for this project. Treat it as a manual evaluation lead only; do not integrate or automate it yet. Third-party browser generators are also manual-evaluation leads only until their exact engine terms, data handling, output rights, and quota are verified.

## Next action

Evaluate one manual, free sample only after confirming the exact engine, current terms, no-payment behavior, and the user's available quota. Do not consume a quota or submit a generation job without the user's explicit approval for that test. Review the exported file before any provider integration.

## Non-goals and safety controls

- Do not modify the separate Nepal News project.
- Do not purchase credits, subscriptions, API usage, or cloud compute.
- Do not enable unattended public posting.
- Require explicit user approval for every final video and each destination.
