# WonderVexa daily content pipeline

## What the scheduled workflow does
Twice per day (06:15 and 18:15 Asia/Kathmandu), GitHub Actions runs the offline content factory and stores a downloadable artifact containing:
- a short-form script and shot list;
- a suggested title and description;
- long-tail keyword phrases and hashtags;
- a generated SVG thumbnail draft;
- JSON metadata marking the package as draft-only.

The workflow uses a small curated idea bank and a history file within that run. It does not currently have persistent cross-run topic history, live trend research, an AI language model, image/video generation, or FFmpeg rendering. Therefore it must not label its suggestions as live trends or guarantee uniqueness across all future runs. A future persistent history store and verified trend source are needed.

## Safety and cost
- No external AI or video-generation API is called.
- No payment method, secret, or credential is needed.
- No video is rendered or uploaded.
- Publishing remains disabled and every final video requires explicit user approval.
- GitHub scheduled workflows are best-effort; GitHub may delay or skip scheduled runs, and public-repository schedules can be disabled after inactivity.

## Next integrations (blocked until verified)
1. A genuinely free trend feed / official public source with rate-limit and attribution handling.
2. A genuinely free text-generation provider, with model license and quota verified.
3. A video/image provider with suitable 9:16 duration, queue, and zero-cost quota.
4. FFmpeg rendering, subtitle and thumbnail export, and technical QA.
5. Separate official publishing adapters, each left disabled until account/API eligibility and approval are verified.

## FFmpeg assembly utility
`src/media_assembler.py` can take an already-generated, licensed source MP4 and:
- crop/scale to 1080x1920;
- overlay a subtle WonderVexa watermark near the lower-right safe area;
- export H.264 MP4 and a PNG thumbnail frame.

It requires FFmpeg installed and is not part of the scheduled draft-only workflow. It does not create source footage, add music, or publish. Run locally only after a video provider has produced an input clip and the user has reviewed the intended output.
