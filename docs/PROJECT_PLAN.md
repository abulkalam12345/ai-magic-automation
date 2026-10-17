# WonderVexa Video Automation — Project Plan

## Channel identity
- Channel name: **WonderVexa**.
- Video watermark: subtle **“WonderVexa”**, lower-right safe area.
- Format target: 9:16 vertical magical transformation and visual-story Shorts.

## Goal and non-negotiable constraints
Build an Android-friendly, zero-budget workflow that prepares one daily content draft at 06:15 Asia/Kathmandu. The evening slot is intentionally disabled; the schedule is a draft target, not a promise of a finished video. Budget target is NPR 0: no paid API, subscription, payment card, auto-recharge or paid fallback. Never store secrets in source control. Do not modify the separate Nepal News project.

No automatic publishing. Every final video and every destination require explicit human approval. A viral result is not guaranteed.

## Implemented on main
1. GitHub Actions scheduled draft workflow once daily at 06:15 Nepal time, plus manual workflow-dispatch inputs restricted to the morning slot.
2. Offline deterministic content factory with 50 curated evergreen story seeds, scripts, shot lists, SEO metadata, hashtags and subject-matched SVG thumbnail drafts.
3. Four-scene visual prompt packs with continuity locks, negative prompts and assembly notes.
4. Draft package integrity validation and tests, including publishing-disabled checks.
5. Topic history avoids repeats until the idea bank is exhausted, then recycles the least-recently-used topic. GitHub Actions cache makes cross-run history best-effort, not permanent.
6. Provider-neutral RSS/Atom research adapter and research-only story brief generator, integrated into the workflow but disabled until reviewed feed sources are configured.
7. Local FFmpeg assembly, subtitle workflow and MP4/PNG technical quality checks for already-generated source media.
8. Fail-closed video-provider evidence manifest validator.

## Not complete / blocked
- No reviewed RSS/Atom sources are enabled; research automation therefore produces no live-feed signals by default. The offline idea bank is evergreen content, not live trend detection.
- No suitable hosted video provider has passed the NPR 0, quota, 9:16 duration, license and data-handling evidence gate.
- No AI video has been generated; the Flower Magic proof remains a storyboard and two-clip prompt plan.
- Local media assembly is implemented but has not been proven end-to-end with real licensed source clips in this project.
- No platform publishing adapters or account eligibility checks are complete. Publishing remains disabled.

## First video proof
The planned proof is a 10-second vertical restoration of one wilted bluebell-like flower by a restrained blue-and-gold magical ring. See:
- [Storyboard](FIRST_PROOF_STORYBOARD.md)
- [Two-clip generation plan](FIRST_PROOF_CLIP_PLAN.md)

Do not submit a generation request until an exact provider/model is verified against official free-tier, quota, commercial-license, data-handling and output-spec evidence, paid fallback is disabled, and the user approves that specific test. If no provider qualifies, keep the video step blocked rather than incur cost or misrepresent a draft as footage.

## Operational checks
- CI must pass on the latest main commit.
- Inspect actual scheduled run artifacts; a successful CI test is not proof that a real video was generated.
- Scheduled GitHub Actions are best-effort and may be delayed or skipped.
- Each draft artifact is retained for 14 days.
- Human review must approve visual quality, rights, platform compliance, exact video and destination before any upload.
