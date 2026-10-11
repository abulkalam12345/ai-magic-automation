# Safety and Operations

## Scope boundary
This repository is only for AI Magic Video Automation. Do not inspect, modify, import, or connect the separate Nepal News project.

## Secrets
- Never commit tokens, API keys, OAuth client secrets, cookies, or passwords.
- Use GitHub Actions Secrets only if a later workflow genuinely needs them.
- Do not ask the user to paste credentials into chat.
- Use least-privilege repository and provider permissions.

## Publishing
- Generation and rendering are separate from publishing.
- Never upload automatically.
- Require the user's explicit approval for each final video.
- Use the official YouTube API and OAuth flow.
- Respect music, image, model, and dataset licenses.
- Disclose realistic synthetic/altered content when YouTube policy requires it.

## Cost controls
- Free-only by default. Do not enable paid billing or paid APIs.
- Check current quotas and terms before choosing a provider.
- Stop rather than silently fall back to a paid service.
- Record estimated and actual usage for each proof run.

## Human quality review
Review character identity, adult appearance, face and hands, motion, scene continuity, text legibility, audio levels, vertical framing, and factual claims before approval.
