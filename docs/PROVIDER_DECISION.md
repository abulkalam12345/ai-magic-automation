# Free inference provider decision (2026-10-11)

## Candidate: Hugging Face Spaces ZeroGPU

Official documentation: https://huggingface.co/docs/hub/en/spaces-zerogpu

Current official docs say public ZeroGPU Spaces can be used free, with a daily quota of 5 GPU minutes for a free account and medium queue priority. The quota resets 24 hours after first use. This is a quota, not a promise that a video job will fit within it. Hugging Face documents Gradio Spaces as callable APIs, but the API interface alone does not guarantee a usable or affordable generation job.

## Candidate checks

### Rejected for this project's first proof: OpenKing/wan2-video-generation
- Space page showed Running and its code identifies model `Wan-AI/Wan2.2-TI2V-5B-Diffusers`.
- Its code uses `@spaces.GPU(duration=180)`, describes generation as approximately 2–3 minutes, and defaults to 73 frames (about 3 seconds) at 1280x704 (landscape).
- This does not meet our 8–12 second vertical proof target as configured, and the 180-second GPU reservation is not safe to assume compatible with a free account. We have not called it.
- The model license and the Space's real-world free-tier completion behavior still need independent confirmation before any use.

### Rejected: HITMAN6178/text-to-video-gradio-demo
- The Space page showed Sleeping due to inactivity when checked. Not a dependable provider.

Other Wan2.2 ZeroGPU Spaces appeared in the directory, including image-to-video demos, but a directory listing is not enough to verify API parameters, free-tier runtime, model license, output dimensions, or character consistency. No provider has passed those checks.

## Re-check (2026-10-11)

- Re-read the current official ZeroGPU documentation. It explicitly lists 5 minutes of daily GPU quota for free accounts, medium queue priority, and automatic paid-credit billing only for PRO/Team/Enterprise tiers after their included quota. Free accounts do not have that paid-credit extension described for them. The quota resets 24 hours after first GPU use.
- The current Spaces video-generation directory lists several entries marked Running on ZeroGPU, including Wan2.2 14B Fast, Wan2.2 14B Preview, Stable Video Diffusion 1.1, Wan2.1 Fast, and LTX Video Fast. Directory status alone does not prove a working API, the exact model license, compatible output length/aspect ratio, or completion within the free account's 5-minute daily quota.
- Current Inference Providers documentation explicitly describes the service as pay-as-you-go. It is therefore excluded from this zero-cost project unless a genuinely free, no-billing route is separately documented and verified.
- No candidate was invoked: even a seemingly free ZeroGPU call consumes the account's limited daily quota, and no candidate has yet passed the full technical/license/runtime checks. No credentials or billing settings were touched.

## Decision
**No production provider approved yet. Do not integrate or call a generator until a candidate passes all checks below.**

1. Confirm the exact Space is running and exposes a usable Gradio API.
2. Confirm its model and output license permit the intended use.
3. Confirm a free account can complete a short test within its free per-call and daily quota, with no payment method, credits, or paid fallback.
4. Verify the output can be cropped/produced as 9:16 and record actual duration, resolution, queue time, GPU seconds, and cost.
5. Generate only a small proof clip first. Stop on any billing prompt or unexpected charge.

## Proof test
Target an original 8–12 second 9:16 flower-restoration magic story. Inspect stable fictional adult character identity, face/hands, motion, scene continuity, and render integrity. A human must approve visual quality. If no free provider can satisfy this, report the blocker rather than silently switching to a paid service.

## Sources checked
- Hugging Face ZeroGPU docs (current free tier: 5 GPU minutes/day): https://huggingface.co/docs/hub/en/spaces-zerogpu
- Hugging Face video-generation Spaces directory: https://huggingface.co/spaces?category=video-generation&includeNonRunning=true&p=0&sort=likes
- Hugging Face Inference Providers docs (pay-as-you-go): https://huggingface.co/docs/inference-providers/index?python-clients=requests
- Hugging Face Spaces API docs: https://huggingface.co/docs/hub/en/spaces-api-endpoints
- OpenKing Wan2 video generation Space and app source: https://huggingface.co/spaces/OpenKing/wan2-video-generation
- Sleeping text-to-video demo: https://huggingface.co/spaces/HITMAN6178/text-to-video-gradio-demo

No provider API has been called and no video has been generated.
