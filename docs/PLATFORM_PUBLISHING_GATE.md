# Official Platform Publishing Gate

Checked: 2026-10-18

## Decision

Publishing stays disabled. This document records verified API prerequisites; it does not enable uploads, create credentials, or authorize any account. Use official APIs and OAuth only. Never request passwords, cookies, or tokens in chat or commit secrets.

## YouTube Shorts

The YouTube Data API `videos.insert` endpoint supports uploading a video and setting title, description, tags, and privacy/scheduled-publish status. It requires OAuth authorization, including the `youtube.upload` scope. Google's current docs list a default 100 `videos.insert` calls/day upload quota bucket. This is API quota, not proof that this repository has an authorized OAuth client or that a particular channel has completed required setup.

Official docs:
- https://developers.google.com/youtube/data/reference/rest/v3/videos/insert
- https://developers.google.com/youtube/data/getting-started

Status: API capability confirmed; adapter and OAuth are not configured.

## TikTok

Direct Post requires a registered developer app, Content Posting API product, Direct Post configuration, approval for `video.publish`, and OAuth authorization by the target creator. TikTok says unaudited clients are restricted to private visibility; public visibility requires an audit. The Direct Post flow queries creator info and obtains explicit consent before sending the post. The API also requires honoring creator privacy options.

Official docs:
- https://developers.tiktok.com/docs/en/content-posting-api-get-started
- https://developers.tiktok.com/docs/en/content-posting-api-reference-direct-post

Status: public unattended posting is blocked pending app audit and compliant creator-consent UX. A hands-off unattended flow cannot bypass these requirements.

## Instagram Reels and Facebook Reels

Do not implement until current Meta official docs and the intended account's eligibility are checked. The account type, Page linkage, app review/access level, permissions, and OAuth token scopes must be confirmed. Do not assume personal profiles can be published to by API and do not use unofficial endpoints.

Status: unverified; disabled.

## Daily posting time

No universal best time is established. 06:15 Nepal time is only the current draft-generation schedule, not a proven publishing time. Choose posting windows using each account's audience analytics after the account is authorized, then evaluate performance over multiple weeks.

## Implementation gates

Before any platform is enabled:
1. Verify current account eligibility and official API requirements.
2. Complete developer-app setup, review/audit where required, and OAuth authorization.
3. Verify permissions, quotas, rate limits, media specs, and policies.
4. Store secrets only in GitHub Actions secrets or an approved secret manager.
5. Keep NPR 0 cost: no billing, paid fallback, card, or auto-recharge.
6. Implement upload polling, bounded retries, idempotency, and failure reporting.
7. Keep all switches off until the platform is genuinely ready and the user has authorized the publishing behavior.

## Current project state

- Draft package: implemented.
- AI footage generation: blocked until a genuinely free provider passes the existing evidence gate.
- FFmpeg assembly: implemented for provided/generated media, not proven with generated footage.
- YouTube, Meta, TikTok adapters: not implemented or authorized.
- Publishing remains disabled.
