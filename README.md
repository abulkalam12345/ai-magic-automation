# WonderVexa Video Automation

A zero-budget-first project for creating original 9:16 magical transformation and visual-story Shorts.

## Current status
A twice-daily **draft package** workflow has been added. It creates scripts, shot lists, title/description, long-tail keywords, hashtags and an SVG thumbnail draft. It does not yet generate an AI video, fetch live trends, or publish.

## Safety rules
- Free services only; never silently enable paid billing.
- No API secrets in source control.
- No automatic uploads; require explicit approval for each final video and its selected destinations.
- Keep the separate Nepal News automation project out of scope.
- Viral performance cannot be guaranteed.

## Daily drafts
GitHub Actions is scheduled for 06:15 and 18:15 Nepal time. Draft packages are saved as workflow artifacts for 14 days. Scheduled Actions are best-effort and may be delayed or skipped. The current generator uses a small offline idea bank, not live trend data or an AI text model.

## Media quality check

A local ffprobe-based gate checks final MP4 technical properties and PNG thumbnail integrity before human review. It does not generate footage or publish.

## Documentation
- [Daily content pipeline](docs/DAILY_CONTENT_PIPELINE.md)
- [Project plan](docs/PROJECT_PLAN.md)
- [Safety and operations](docs/SAFETY_AND_OPERATIONS.md)
- [Example settings](config/settings.example.yaml)

## First video proof
An 8–12 second vertical flower-restoration magic visual, subject to a verified zero-cost video provider and human quality review.
