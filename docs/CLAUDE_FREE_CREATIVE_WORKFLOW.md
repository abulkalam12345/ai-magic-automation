# Claude Free Creative Workflow (Zero-Budget)

## Decision

Claude is an optional, manual creative assistant for WonderVexa. It is **not** a video-generation provider and is **not** connected to the scheduled GitHub Actions workflow.

Use Claude Free in its official Android app or mobile website to improve scripts and creative direction. Do not purchase a plan, API credits, or usage credits for this project.

## Why this is the safest fit

- Claude Free can be used for writing, brainstorming, research, and creating files, subject to its changing usage limits.
- Claude Code is not included in the Free plan.
- Claude API calls are billed separately. Never add an Anthropic API key or paid billing path to this repository under the NPR 0 requirement.
- Do not automate Claude Free by browser scraping, unofficial endpoints, shared cookies, or account-session extraction.
- Claude plans and limits can change. Recheck the official pricing page before relying on a feature.

Official references:
- https://claude.com/pricing
- https://support.claude.com/en/articles/8977456-how-do-i-pay-for-my-claude-api-usage

## Recommended workflow

1. Let the existing GitHub Actions workflow create the daily draft package.
2. Open the package's script.md and visual_prompts.md artifact on the Android phone.
3. If desired, paste the prompt below into Claude Free with the draft content.
4. Review Claude's suggestions. Keep only factual, original, brand-safe improvements.
5. Put approved edits into the draft package manually. Do not paste secrets, OAuth tokens, private URLs, or personal data into Claude.
6. Actual footage generation remains blocked until a video provider passes docs/VIDEO_PROVIDER_GATE.md.
7. Rendering and publishing remain disabled unless their separate quality, rights, cost, and platform gates pass.

This manual step is optional. If Claude Free is unavailable or its usage limit is reached, continue with the existing offline draft workflow.

## Copy-ready WonderVexa prompt

You are the creative script editor for WonderVexa, a short-form visual storytelling channel.

Improve the supplied draft for one original vertical 9:16 short video. The target length is 8–12 seconds unless the brief specifies otherwise.

Requirements:
- Create a strong visual hook in the first second.
- Use a clear beginning, transformation/action, and satisfying final reveal.
- Keep the story understandable without audio.
- Write concise voiceover only if it genuinely improves the story.
- Provide 4 visually coherent scenes with camera framing, movement, lighting, subject details, and continuity notes.
- Avoid claims that a visual event is real if it is fictional or AI-generated.
- Do not imitate a living artist or copy a copyrighted character, franchise, script, or existing video.
- Suggest a short title, a truthful description, relevant long-tail search phrases, and a small set of relevant hashtags.
- Suggest a thumbnail concept that remains readable on a phone.
- Preserve the WonderVexa brand. Leave room for the channel logo watermark; do not cover or remove any provider watermark.
- Do not claim that a topic is trending unless the supplied research contains current evidence and a source.
- Do not invent facts, sources, statistics, or performance guarantees.
- Return a revised script and scene prompts, followed by a short change log and any factual/rights concerns.

Zero-budget and safety rules:
- Recommend only workflows that can be used at NPR 0.
- Do not request or recommend paid APIs, paid subscriptions, paid credits, credit cards, auto-recharge, or paid fallback.
- Do not say that you generated an MP4 or actual footage. You are preparing text and creative direction only.
- If the supplied draft cannot be improved reliably, explain why rather than inventing details.

Draft package:
[PASTE script.md AND visual_prompts.md HERE]

Research notes and sources, if any:
[PASTE APPROVED RESEARCH NOTES HERE]
