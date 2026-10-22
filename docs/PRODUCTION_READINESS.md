# WonderVexa Production Readiness

Last reviewed: 2026-10-22

This tracker separates working draft automation from the unfinished real-video and publishing pipeline.

## Verified working

- Morning draft workflow is scheduled for 06:15 Nepal time (00:30 UTC).
- Evening draft workflow is scheduled for 18:15 Nepal time (12:30 UTC).
- Both workflows build draft metadata and procedural preview renders.
- Evening workflow builds the six-scene Episode 01 editorial package.
- Draft validation and technical preview checks run in GitHub Actions.
- GitHub Actions artifacts are retained for 14 days.
- The project validation workflow passed after the Episode 01 production pack was committed.

## Not yet delivered

- No verified photorealistic AI magician footage has been generated.
- Procedural preview renders are not the intended live-action magician videos.
- Hindi voice performance and recurring-character identity consistency have not been validated on generated footage.
- No AI video provider has passed the project's zero-cost and commercial-rights approval gate.
- No social platform publishing integration is approved or enabled.
- No video has been published by this workflow.

## Provider approval checklist

A candidate provider must be checked against its current official terms and actual selected model/engine:

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

## Next action

Generate one manual five-second test clip using a candidate zero-cost provider. Review the actual exported file and the selected engine's terms before integrating anything into scheduled automation.

## Non-goals

- Do not modify the separate Nepal News project.
- Do not purchase credits, subscriptions, API usage, or cloud compute.
- Do not enable unattended public posting without explicit user approval.
