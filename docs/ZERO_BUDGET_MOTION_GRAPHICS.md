# Zero-budget procedural motion-graphics proof

## Why this path
The repository is public. GitHub documents standard GitHub-hosted runners as free and unlimited for public repositories. That makes a short CPU-rendered animation on an Ubuntu runner a plausible NPR 0 path without a paid video-generation API or a local computer.

## What the experimental workflow does
The manually triggered workflow `.github/workflows/experimental-motion-graphics.yml`:
1. Creates a normal offline WonderVexa draft package.
2. Uses Pillow to draw original animated blue magic rings, particles, title text and a small text-only WonderVexa mark.
3. Uses FFmpeg to encode a silent 10-second, 1080x1920 H.264 MP4 and a PNG thumbnail.
4. Runs the existing technical media checker and uploads a short-lived artifact.

It makes no external AI/API calls, downloads no stock footage, needs no credentials, does not publish, and does not alter the existing daily draft workflow.

## Important limitations
- This is **procedural motion graphics**, not generative AI footage, cinematic scenes, or a verified viral/trend-based video.
- The current repository does not contain the user's original blue energy-ring logo asset; this proof uses text branding only. Do not claim the actual logo is embedded.
- The first proof is silent. Add only properly licensed audio in a later separately tested step.
- Technical QA cannot judge whether the animation looks attractive, tells a good story, or meets every platform's content rules. Human review remains required.
- The workflow is manual-only until its output, runtime, and artifact size are inspected. It is not connected to the scheduled daily workflow.
- Publishing remains disabled.

## Run only after reviewing
Open the repository's Actions tab, choose **WonderVexa experimental motion-graphics proof**, and use **Run workflow**. No payment method or secret should be requested. Stop if GitHub displays any billing or payment prompt; do not enable paid usage.

## Success criteria
A successful proof must contain a playable MP4 and 1080x1920 PNG thumbnail, pass `media_quality_check.py`, complete within the 20-minute job limit, and remain unpublished. Only after human visual review should integration into the daily schedule be considered.
