# WonderVexa first proof: two-clip generation plan

**Status:** prompt pack only; no provider selected, no generation authorized.  
**Final target:** 8–12 seconds, vertical 9:16.  
**Story:** one wilted bluebell-like flower is restored by a restrained blue-and-gold magical ring.

This plan is designed for a provider that can make short 2–6 second clips. It does not assume a provider is free or approved. Check current provider cost, license, duration, aspect ratio, and quota before any generation. Do not generate until the user approves the specific test.

## Continuity anchor

Create or select one still reference frame showing:
- one single bluebell-like flower in a small patch of dark garden soil;
- bent green stem and folded blue-violet petals;
- moonlit garden bokeh, dark uncluttered background;
- camera at macro flower height, vertical composition;
- no people, hands, text, logos, or watermark.

Use the exact same reference image, aspect ratio (9:16), style preset, and camera framing for both clips when the provider supports reference input. If it cannot reuse the same reference or otherwise preserve the scene, expect continuity drift and reject mismatched clips rather than hiding it with fast cuts.

## Clip A — wilted flower and first magic cue

**Target duration:** 4–5 seconds.

**Prompt**

Create a vertical 9:16 cinematic macro video of exactly one delicate wilted bluebell-like flower growing from a small patch of dark garden soil at night. Its green stem is slightly bent and its blue-violet petals are folded and dry. A thin, restrained ribbon of blue-and-gold magical light begins to form beside the flower and makes one gentle partial orbit. Only a few tiny luminous particles drift toward the flower; do not restore it yet. Keep the same single flower, stem, petal count, camera angle, scale, and moonlit garden background throughout. Static macro camera, shallow depth of field, elegant fantasy realism, subtle motion, readable silhouette, natural temporal consistency.

**Negative prompt**

Multiple flowers, extra stems, duplicated petals, changing species, hands, people, faces, fast camera movement, jump cuts, flower opening, sudden color change, chaotic particles, explosions, fire, excessive glow, flicker, text, logos, signatures, baked-in watermark, borders, landscape framing, malformed plant anatomy.

**Expected end frame:** same wilted flower, with a faint blue-gold glow near its stem.

## Clip B — continuous restoration and final reveal

**Target duration:** 4–6 seconds.

**Prompt**

Continue the exact same macro flower scene from the supplied reference frame: one single bluebell-like flower in the same dark moonlit garden, same bent green stem, same folded blue-violet petals, same camera angle, scale, lighting, and background. The existing thin blue-and-gold magical ribbon completes a gentle orbit. A few particles travel from the stem into the petals. In one smooth, physically readable transformation, the stem straightens, the petals regain rich blue-violet color, and the flower slowly opens into one healthy elegant bloom. End with the fully opened flower held clearly in frame. Keep the plant's identity and position stable. Static macro camera, shallow depth of field, polished fantasy realism, restrained glow, natural motion, no scene transition.

**Negative prompt**

Different flower, additional flowers, new stems, changing camera angle, scene/location change, duplicated petals, sudden morph jump, instant pop-open, human hands, people, faces, excessive particles, explosions, fire, flicker, strobing, text, logos, signatures, baked-in watermark, borders, landscape framing, deformed botanical anatomy.

**Expected first frame:** match Clip A's final composition as closely as the provider allows.  
**Expected end frame:** one fully restored blue-violet flower.

## Assembly and review

If both clips pass continuity review and contain at least 8 seconds of usable combined footage, assemble in the intended order:

```bash
python src/media_assembler.py \
  --input output/clip-a.mp4 output/clip-b.mp4 \
  --output output/final.mp4 \
  --thumbnail output/thumbnail.png \
  --target-duration 10

python src/media_quality_check.py \
  --video output/final.mp4 \
  --thumbnail output/thumbnail.png
```

The assembler trims to the selected target duration; it cannot extend clips or invent missing frames. The technical check does not assess visual quality. Human review must confirm:
- [ ] Both clips depict the same single flower, species, stem, petal arrangement, camera and lighting.
- [ ] Clip B begins plausibly from Clip A's ending state.
- [ ] No morphing glitches, flicker, jumps, or malformed petals.
- [ ] Combined usable footage is at least 8 seconds and the final reveal is not cut off.
- [ ] 9:16 framing and watermark safe area are clear.
- [ ] Source/model license and actual cost are verified; no payment method or paid fallback was used.
- [ ] Final video is explicitly approved before any platform-specific publishing decision.

If continuity fails, do not publish. Revise the prompt/reference or abandon the multi-clip approach; never imply that the clips are one continuous generation.
