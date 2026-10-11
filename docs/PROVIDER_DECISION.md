# Free inference provider decision (2026-10-11)

## Candidate: Hugging Face Spaces ZeroGPU

Official documentation: https://huggingface.co/docs/hub/en/spaces-zerogpu

The current documentation says existing ZeroGPU Spaces are free to use, with a daily quota of 5 GPU minutes for free accounts, medium queue priority, and shared on-demand hardware. Quota resets 24 hours after first GPU use. Actual wait time and a specific Space's model, availability, license, and output quality vary.

Important distinction: free access to an existing Space is not a guarantee that a suitable text-to-video model is available or that a complete short can be generated within the quota. Hugging Face Inference Providers separately list $0.10 monthly credits for free users in current pricing docs; this is not treated as a dependable free video-generation backend.

## Decision
Candidate only — **not yet approved as production provider**. Before integration:
1. Select a specific existing Space with a suitable video model.
2. Confirm its model and output license allow intended use.
3. Check that it is currently running and exposes a usable Gradio/API interface.
4. Generate one short sample within free quota, recording queue time, GPU seconds, output dimensions, and actual cost.
5. Do not provide a payment method or enable paid credits. Stop if any payment or paid fallback is requested.

## Proof test
Use an original 8–12 second 9:16 flower-restoration magic story. Inspect stable adult fictional character identity, face/hands, motion, scene continuity, and render integrity. A human must approve visual quality.

## Sources checked
- Hugging Face ZeroGPU docs: https://huggingface.co/docs/hub/en/spaces-zerogpu
- Hugging Face Inference Providers pricing: https://huggingface.co/docs/inference-providers/pricing

No provider call or video generation has been performed yet.
