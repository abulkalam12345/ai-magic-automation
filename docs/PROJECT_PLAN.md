# AI Magic Video Automation — Project Plan

## Goal
Create original, vertical 9:16 short videos with a consistent fictional adult woman character, magical transformations, and educational storytelling. Keep all generation and publishing user-controlled until tested.

## Constraints
- Zero paid services, no credit card, Android-only project management.
- Nepal News automation is out of scope and must never be changed.
- Never store API keys, OAuth tokens, passwords, or personal credentials in Git.
- No YouTube upload without explicit approval for each video.
- No promise of unlimited or daily cinematic generation on free tiers.

## Staged delivery
1. **Repository foundation:** document architecture, safety, configuration, and local validation.
2. **Provider feasibility:** verify a genuinely free image/video inference route and its current quota, queue, license, and account requirements.
3. **Quality proof:** generate one 8–12 second 9:16 test (a wilted flower restored by magic), then inspect character consistency, motion, hands, transformation continuity, audio, render time, and actual cost.
4. **Pipeline:** only after a passing proof, implement generation, FFmpeg assembly, metadata, and quality checks.
5. **Publishing:** optional YouTube OAuth and upload only after the user's explicit per-video approval.

## First proof acceptance criteria
- Complete playable MP4, 1080x1920 preferred (lower resolution acceptable for feasibility proof).
- One clearly adult fictional woman, visually consistent across shots.
- Coherent flower-restoration transformation.
- No severe face, hand, prop, or motion defects.
- No unlicensed music or copied story assets.
- Record runtime, queue time, quota consumed, and cost (must be zero).

## Proposed architecture (subject to provider test)
- Android: user reviews status and approves videos through GitHub/YouTube interfaces.
- GitHub: source control and manually triggered orchestration only; do not assume hosted runners have a GPU.
- Inference provider: optional free hosted GPU/API, selected only after verifying current free quota and terms.
- Media assembly: FFmpeg for vertical crop/scale, audio mix, subtitles, and MP4 export.
- Quality gate: technical checks plus human review; automated checks cannot guarantee visual quality.
- YouTube: official API/OAuth only, with per-video approval.

## Known blockers
- Free GPU availability and quotas can change and may require an account or queue.
- A free model does not imply free compute.
- Stable character identity across generated clips is not guaranteed; the proof must measure it.
- YouTube OAuth setup and API quota may require user action.

## Status
Repository inspected on 2026-10-11. Initial repository contained only README.md. No video-generation provider has yet been proven. No video has been generated or uploaded.
