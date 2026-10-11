# Safety and Operations

## Scope boundary
This repository is only for AI Magic Video Automation. Do not inspect, modify, import, or connect the separate Nepal News project.

## Secrets
- Never commit tokens, API keys, OAuth client secrets, cookies, or passwords.
- Use GitHub Actions Secrets only if a later workflow genuinely needs them.
- Do not ask the user to paste credentials into chat.
- Use least-privilege repository and provider permissions.

## Publishing
- Target two Reels per rolling 24 hours: one morning and one evening in Asia/Kathmandu time.
- Intended destinations are YouTube Shorts, Facebook Reels, TikTok, and Instagram Reels, each through its own verified official publishing path.
- The cadence is a planning target only; no scheduled or automatic publishing is enabled.
- Never upload automatically. Require explicit approval for each individual final video and the destinations selected for it.
- Do not publish an unreviewed, failed, or unavailable render merely to meet a schedule.
- Use official platform APIs and OAuth flows; never use browser automation or credential scraping.
- Respect music, image, model, and dataset licenses.
- Disclose realistic synthetic/altered content when the relevant platform policy requires it.

## Watermark
- Apply a consistent, subtle “AI Magic” watermark to exported videos.
- Keep it inside vertical safe margins, preferably in a lower corner, without covering faces, key action, subtitles, or platform controls.
- Preserve a clean master export where practical; create watermarked platform-ready copies.

## Cost controls
- Free-only by default. Do not enable paid billing or paid APIs.
- Check current quotas and terms before choosing a provider.
- Stop rather than silently fall back to a paid service.
- Record estimated and actual usage for each proof run.

## Human quality review
Review character identity, adult appearance, face and hands, motion, scene continuity, text legibility, audio levels, vertical framing, watermark placement, and factual claims before approval.
