# WonderVexa daily content pipeline

## What the scheduled workflow does
Once per day (06:15 Asia/Kathmandu, best-effort), GitHub Actions:
1. Restores best-effort cross-run topic history and records an execution audit.
2. Creates an offline draft package from the curated evergreen idea bank.
3. Validates the script, SEO metadata, SVG draft, topic consistency, trend disclaimer, and disabled publishing state.
4. Renders a 10-second original procedural motion-graphics MP4 with offline eSpeak NG synthetic English narration.
5. Exports a 1080x1920 PNG thumbnail and technically validates the H.264/AAC MP4 and thumbnail.
6. Stores draft packages and rendered files in a downloadable GitHub Actions artifact for 14 days.

The renderer creates original vector-style animation (currently a golden-tree growth scene), not AI-generated cinematic footage, live footage, or generated photographic scenes. The voice is synthetic eSpeak NG, not a human voice. No music is added. The channel logo asset is not yet included; the video currently uses a text-only WONDERVEXA mark. Human review is still required for visual quality, story accuracy, accessibility, rights, and platform suitability.

The content factory uses a small curated idea bank. It does not verify live trends, and metadata explicitly labels topics as unverified evergreen seeds. It does not call a language model or video-generation provider.

## Safety and cost
- No external AI, image, voice, or video-generation API is called.
- FFmpeg, Pillow, DejaVu fonts, and eSpeak NG are installed from public Ubuntu/Python packages on the GitHub-hosted runner; no paid quota, payment method, secret, or credential is required by this workflow.
- The scheduled job has a 20-minute execution limit.
- GitHub Actions workflow uses read-only contents permission and checkout does not persist its token credentials.
- The workflow renders and stores drafts only. It does not publish, upload to social platforms, or enable YouTube publishing.
- Publishing remains disabled; every final video requires explicit user approval.
- GitHub scheduled workflows are best-effort; GitHub may delay or skip scheduled runs, and public-repository schedules can be disabled after inactivity.
- Topic-history cache retention and eviction are controlled by GitHub, so duplicate avoidance is best-effort, not a permanent ledger or a guarantee of uniqueness.

## Remaining integrations (blocked until verified)
1. A genuinely free trend feed / official public source with rate-limit and attribution handling.
2. A genuinely free text-generation provider, with model license and quota verified.
3. A suitable zero-cost source of licensed footage or richer generated scenes, if available.
4. Human review and application of the original WonderVexa logo asset.
5. Separate official publishing adapters, each left disabled until account/API eligibility and per-video approval are verified.

## Separate FFmpeg assembly utility
`src/media_assembler.py` can take already-generated, licensed source MP4 clips and:
- process one clip, or concatenate 2+ clips in the supplied order to reach an 8–12 second target;
- crop/scale to 1080x1920 and overlay a subtle WonderVexa watermark near the lower-right safe area;
- export H.264 MP4 and a PNG thumbnail frame.

For a sequence, use `python src/media_assembler.py --input shot1.mp4 shot2.mp4 --output output/final.mp4 --thumbnail output/thumbnail.png --target-duration 10`. The source clips must contain enough combined usable footage; the command trims to the selected target duration and does not synthesize missing frames. Audio is intentionally omitted, and clip-to-clip character/scene continuity still requires human review. This utility is separate from the scheduled procedural renderer.

## Finished-video technical quality gate
`src/media_quality_check.py` uses `ffprobe` to check a rendered MP4 and PNG thumbnail. The scheduled workflow requires H.264 video, exact 1080x1920 dimensions, yuv420p pixel format, 24–60 fps, an 8–12 second duration, AAC audio, and a structurally valid 1080x1920 PNG. This is technical QA only; it does not judge visual quality, rights, story consistency, audio intelligibility, or platform policy.

## Draft package integrity check
The scheduled workflow runs `src/draft_package_check.py` automatically for every package. To check one locally:

```bash
python src/draft_package_check.py output/drafts/2026-10-13-morning-lantern-of-hope
```
