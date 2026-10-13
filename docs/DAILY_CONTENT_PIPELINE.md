# WonderVexa daily content pipeline

## What the scheduled workflow does
Twice per day (06:15 and 18:15 Asia/Kathmandu), GitHub Actions runs the offline content factory and stores a downloadable artifact containing:
- a short-form script and shot list;
- a suggested title and description;
- long-tail keyword phrases and hashtags;
- a generated SVG thumbnail draft;
- JSON metadata marking the package as draft-only.

Before artifact upload, `src/draft_package_check.py` checks that each package has its required files, parseable metadata and SVG, matching topic/script, valid hashtags, an explicit evergreen/unverified trend label, no claimed rendered video, and publishing disabled with per-video approval required. This is an integrity and safety gate, not a visual review.

The workflow uses a small curated idea bank and attempts to restore/save a cross-run topic-history cache using GitHub Actions cache. Cache retention and eviction are controlled by GitHub, so this is best-effort duplicate avoidance, not a permanent ledger or a guarantee of uniqueness. It does not have live trend research, an AI language model, image/video generation, or FFmpeg rendering. Suggestions are explicitly labeled as unverified evergreen seeds, never live trends.

## Safety and cost
- No external AI or video-generation API is called.
- No payment method, secret, or credential is needed.
- No video is rendered or uploaded.
- Publishing remains disabled and every final video requires explicit user approval.
- GitHub Actions workflow uses read-only contents permission and checkout does not persist its token credentials.
- The scheduled draft job has a 10-minute execution limit to bound runner usage if a step stalls.
- GitHub scheduled workflows are best-effort; GitHub may delay or skip scheduled runs, and public-repository schedules can be disabled after inactivity.

## Next integrations (blocked until verified)
1. A genuinely free trend feed / official public source with rate-limit and attribution handling.
2. A genuinely free text-generation provider, with model license and quota verified.
3. A video/image provider with suitable 9:16 duration, queue, and zero-cost quota.
4. FFmpeg rendering, subtitle and thumbnail export, and technical QA.
5. Separate official publishing adapters, each left disabled until account/API eligibility and approval are verified.

## FFmpeg assembly utility
`src/media_assembler.py` can take already-generated, licensed source MP4 clips and:
- process one clip, or concatenate 2+ clips in the supplied order to reach an 8–12 second target;
- crop/scale to 1080x1920 and overlay a subtle WonderVexa watermark near the lower-right safe area;
- export H.264 MP4 and a PNG thumbnail frame.

For a sequence, use `python src/media_assembler.py --input shot1.mp4 shot2.mp4 --output output/final.mp4 --thumbnail output/thumbnail.png --target-duration 10`. The source clips must contain enough combined usable footage; the command trims to the selected target duration and does not synthesize missing frames. Audio is intentionally omitted, and clip-to-clip character/scene continuity still requires human review. It requires FFmpeg installed locally and is not part of the scheduled draft-only workflow. It does not create source footage, add music, contact a provider, or publish.

## Finished-video technical quality gate
`src/media_quality_check.py` uses `ffprobe` to check a rendered MP4 and PNG thumbnail before human review. It verifies an H.264 video stream, exact 1080x1920 dimensions, yuv420p pixel format, an 8–60 second duration, non-empty files, and the PNG file signature. It does not judge visual quality, rights, story consistency, audio quality, or platform policy; those still need human review. Run it with:

```bash
python src/media_quality_check.py --video output/final.mp4 --thumbnail output/thumbnail.png
```

## Draft package integrity check
The scheduled workflow runs this automatically for every generated package. To check one locally:

```bash
python src/draft_package_check.py output/drafts/2026-10-13-morning-moonlit-seed
```
