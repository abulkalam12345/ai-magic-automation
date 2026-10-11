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

## Reassessment (2026-10-11, official documentation rechecked)

The current ZeroGPU documentation still lists a Free account allowance of **5 GPU minutes per 24-hour window**, with medium queue priority. The window resets 24 hours after first GPU usage. PRO/Team/Enterprise can extend usage with prepaid credits; this project must not use those plans or credits. ZeroGPU currently documents shared RTX Pro 6000 Blackwell hardware and Gradio-only compatibility for ZeroGPU Spaces. These platform facts do not establish that a particular video-generation Space will finish within the free quota.

Official current references:
- ZeroGPU quota, queue, hardware, compatibility and billing: https://huggingface.co/docs/hub/en/spaces-zerogpu
- Hugging Face text-to-video API examples route through Inference Providers such as fal.ai; the Inference Providers docs describe provider billing, so this route is not approved as a zero-cost backend: https://huggingface.co/docs/inference-providers/main/en/tasks/text-to-video
- Hugging Face inference guide says routed provider calls are billed to the user's Hugging Face account and direct provider calls use the provider's own billing: https://huggingface.co/docs/huggingface_hub/v1.3.2/en/guides/inference

### Decision after reassessment

**No hosted provider is approved for automated production generation yet.** Do not wire Hugging Face Inference Providers, fal.ai, Replicate, or another pay-as-you-go endpoint into the workflow. A free ZeroGPU Space remains a possible one-off manual experiment only after its exact Space API, model license, output settings, per-call duration, and free-tier behavior are checked. Do not spend the daily quota merely to discover whether an unverified demo works.

An open-source notebook (for example, CogVideoX's published Colab notebooks) is a possible manual research path, not a dependable GitHub Actions backend: free notebook GPU availability and session limits are not a guaranteed always-on service. It is not selected as the production provider.

### Next safe proof route

1. Keep provider integration disabled and retain the existing offline draft + FFmpeg assembly + media-QC path.
2. Continue looking for an exact, publicly callable ZeroGPU Space with a documented model license and compatible short vertical output.
3. Before any generation call, record the expected GPU reservation and verify it is within the remaining free quota; never allow paid fallback or billing.
4. If no candidate passes, tell the user honestly that a dependable automated zero-cost video-generation backend is not currently verified. Do not claim daily video generation is ready.


## Exact Space API/runtime candidate check (2026-10-11)

### OpenKing/wan2-video-generation — rejected for the WonderVexa proof

The currently indexed Space deployment guide describes a Gradio Space using Wan2.2-TI2V-5B, with an example 73-frame output at 24 fps (about 3 seconds), landscape 1280x704 defaults, and a GPU reservation of 180 seconds. The same guide says Free-tier GPU duration is typically limited to 60 seconds and that the 2–3 minute generation profile is optimized for Pro. This is incompatible with a safe assumption of Free-tier completion and does not meet the 8–12 second vertical target. The Space's Running label and Gradio interface do not prove successful free-tier inference. No API call was made.

Sources:
- Space deployment guide: https://huggingface.co/spaces/OpenKing/wan2-video-generation/blob/main/DEPLOYMENT.md
- Space source/status snapshot: https://huggingface.co/spaces/OpenKing/wan2-video-generation

### Other candidates

- Fhwang/wan2-video-generation is a community deployment based on the same template and explicitly documents Free GPU duration as 60 seconds, 3-second default clips, and timeouts for longer outputs. It is not a better candidate for our 8–12 second proof: https://huggingface.co/spaces/Fhwang/wan2-video-generation
- IdlecloudX/wan-i2v-1 documents an asynchronous job API, but requires a configured JOB_API_KEY and does not establish free anonymous generation, zero-cost usage, or the needed text-to-video pipeline. It is not approved: https://huggingface.co/spaces/IdlecloudX/wan-i2v-1
- A separate Wan2.2 Remix Space declares its fine-tune license as `other` without providing terms; output rights are unresolved, so it is excluded from commercial use: https://huggingface.co/spaces/mastaP/wan22-remix-sfw-t2v

**Result:** No candidate passed the project's full free-tier, license, API, duration, vertical-output, and operational checks. Keep provider integration disabled. No GPU quota was consumed and no credentials were requested.
