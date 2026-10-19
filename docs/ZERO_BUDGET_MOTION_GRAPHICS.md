# Zero-budget procedural motion-graphics proof

## Why this path
The repository is public. GitHub documents standard GitHub-hosted runners as free and unlimited for public repositories. That makes a short CPU-rendered animation on an Ubuntu runner a plausible NPR 0 path without a paid video-generation API or a local computer.

## What the experimental workflow does
The manually triggered workflow `.github/workflows/experimental-motion-graphics.yml`:
1. Creates a normal offline WonderVexa draft package.
2. Uses Pillow to draw an original seed-to-sapling-to-golden-tree progression, warm halo, floating motes, story premise captions, title text and a small text-only WonderVexa mark. eSpeak NG adds a short offline English narration track.
3. Uses FFmpeg to encode a 10-second, 1080x1920 H.264 MP4 with AAC narration and a PNG thumbnail.
4. Runs the technical media checker with the AAC-audio requirement enabled and uploads a short-lived artifact.

It makes no external AI/API calls, downloads no stock footage, needs no credentials, does not publish, and does not alter the existing daily draft workflow.

## Important limitations
- This is **procedural motion graphics**, not generative AI footage, cinematic scenes, or a verified viral/trend-based video.
- The current repository does not contain the user's original blue energy-ring logo asset; this proof uses text branding only. Do not claim the actual logo is embedded.
- The current proof includes a short synthetic English narration generated locally by eSpeak NG. It does not include background music. The voice is computer-synthesized, not a human recording. Add only properly licensed audio in a later separately tested step.
- Technical QA cannot judge whether the animation looks attractive, tells a good story, or meets every platform's content rules. Human review remains required.
- The proof workflow can be started manually from Actions and also runs automatically when `src/motion_graphics_renderer.py` changes on `main`. It is still not connected to the scheduled daily draft workflow; automatic proof renders are not daily publishing.
- Publishing remains disabled.

## Run only after reviewing
For a manual test, open the repository's Actions tab, choose **WonderVexa experimental motion-graphics proof**, select `main`, and use **Run workflow**. Renderer changes on `main` also trigger a proof render. No payment method or secret should be requested. Stop if GitHub displays any billing or payment prompt; do not enable paid usage.

## Success criteria
A successful proof must contain a playable MP4 and 1080x1920 PNG thumbnail, pass `media_quality_check.py`, complete within the 20-minute job limit, and remain unpublished. Only after human visual review should integration into the daily schedule be considered.
