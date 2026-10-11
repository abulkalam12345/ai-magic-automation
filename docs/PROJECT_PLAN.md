# AI Magic Video Automation — Project Plan

## Goal
Create original vertical 9:16 short videos with one consistent fictional adult woman character, magical transformations, and educational storytelling. Prepare one approved master video and platform-specific variants for YouTube Shorts, Facebook Reels, TikTok, and Instagram Reels. Keep generation and publishing user-controlled until tested.

## Constraints
- Zero paid services, no credit card, Android-only project management.
- Nepal News automation is out of scope and must never be changed.
- Never store API keys, OAuth tokens, passwords, or personal credentials in Git.
- Never publish to any platform without the user's explicit approval for that individual video.
- No promise of unlimited or daily cinematic generation on free tiers.
- Use official platform APIs and follow each platform's account eligibility, app review, media, and disclosure rules. If a platform requires unavailable approval or paid capability, leave that connector disabled.

## Staged delivery
1. **Repository foundation:** document architecture, safety, configuration, and automated validation.
2. **Provider feasibility:** verify a genuinely free image/video inference route and its current quota, queue, license, and account requirements.
3. **Quality proof:** generate one 8–12 second 9:16 test (a wilted flower restored by magic), then inspect character consistency, motion, hands, transformation continuity, audio, render time, and actual cost.
4. **Video pipeline:** only after a passing proof, implement generation, FFmpeg assembly, subtitles, metadata, and technical/visual quality gates.
5. **Platform preparation:** define separate official publishing adapters and validation for YouTube Shorts, Facebook Reels, TikTok, and Instagram Reels. Keep every adapter disabled until its official API access, account eligibility, scopes, review status, and zero-cost operation are verified.
6. **Approval and publishing:** show the finished video and platform-specific captions to the user. Require a fresh explicit approval for each video before any upload. Publish only to the platforms selected in that approval and report each result independently.

## First proof acceptance criteria
- Complete playable MP4, 1080x1920 preferred (lower resolution acceptable for feasibility proof).
- One clearly adult fictional woman, visually consistent across shots.
- Coherent flower-restoration transformation.
- No severe face, hand, prop, or motion defects.
- No unlicensed music or copied story assets.
- Record runtime, queue time, quota consumed, and cost (must be zero).

## Proposed architecture (subject to provider test)
- Android: user reviews generated videos and gives per-video approval.
- GitHub: source control, tests, and manually triggered orchestration only; do not assume hosted runners have a GPU.
- Inference provider: optional free hosted GPU/API, selected only after verifying current free quota and terms.
- Media assembly: FFmpeg for vertical crop/scale, audio mix, subtitles, and MP4 export.
- Quality gate: technical checks plus human review; automated checks cannot guarantee visual quality.
- Publishing: separate official API/OAuth adapter per platform; no browser automation or credential scraping. One approval record per video, with selected destinations recorded before upload.

## Known blockers
- Free GPU availability and quotas can change and may require an account or queue.
- A free model does not imply free compute.
- Stable character identity across generated clips is not guaranteed; the proof must measure it.
- YouTube, Meta, and TikTok publishing access can require account eligibility, app review, permissions, or manual setup. These are not assumed available.
- Platform upload support and media requirements can change; verify each adapter against current official documentation before implementation.

## Status
Repository inspected on 2026-10-11. The blueprint and safety preflight are in place on a feature branch. No video-generation provider has yet been proven. No video has been generated or uploaded. All four publishing destinations are configured disabled by default.
