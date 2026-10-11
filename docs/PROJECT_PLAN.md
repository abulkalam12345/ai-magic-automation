# WonderVexa Video Automation — Project Plan

## Channel identity
- Channel name: **WonderVexa**.
- Logo reference: user-provided blue magical energy-ring image.
- Video watermark: subtle **“WonderVexa”**, lower-right safe area.

## Goal
Build an Android-friendly, zero-budget-first pipeline for original vertical 9:16 magical transformation and educational Shorts. Prepare two daily content drafts (morning and evening, Asia/Kathmandu), including scripts, storyboards, SEO metadata and thumbnail artwork. Video rendering and publishing remain gated on verified free providers and human approval.

## Daily content workflow
- Scheduled GitHub Actions runs at 06:15 and 18:15 Nepal time to create draft packages.
- Each package includes an original short script, shot list, suggested title, description, long-tail keyword phrases, hashtags, metadata JSON and SVG thumbnail.
- Current draft generator uses an offline curated idea bank. It is not live trend research and does not use a generative AI model. Trend-aware selection and durable duplicate history are future integrations.
- Workflow output is saved as a downloadable GitHub Actions artifact; scheduled runs are best-effort and may be delayed or skipped.
- Never claim a topic is trending unless a reliable trend source has actually verified it.

## Publishing and safety
- Intended destinations: YouTube Shorts, Facebook Reels, TikTok, Instagram Reels.
- Every final video requires explicit user approval and a destination selection before upload.
- Automatic publishing is disabled. No upload happens from the daily draft workflow.
- Keep a clean master export and separate watermarked copies where practical.
- No paid service, credit card, paid fallback, or hidden billing.

## Staged delivery
1. Repository foundation, safe configuration and validation.
2. Daily offline content-draft generation (implemented; needs CI verification).
3. Live trend research and AI script generation, only after a suitable zero-cost source/model is verified.
4. Video/image provider feasibility: verify license, runtime, 9:16 support, quota, queue and actual zero cost.
5. FFmpeg rendering, subtitle composition, thumbnail export, WonderVexa watermark and technical QA.
6. Human review, then separate official publishing adapters with per-video approval.

## First video proof
A 8–12 second vertical flower-restoration magic visual. Check character continuity, hands, motion, transformation, framing, watermark, render time, quota and actual cost before further automation.

## Known blockers
- The daily draft factory is template-based, not AI-generated.
- It does not currently fetch live trends or persist topic history between scheduled workflow runs.
- No video-generation provider has been validated; no video rendering or upload is implemented.
- Platform API eligibility and review requirements are not assumed.
- A viral result cannot be guaranteed.

## Current status
Daily draft package code and scheduled workflow have been added to the feature branch. Verify CI before relying on it. No video has been generated or published. All publishing destinations remain disabled.
