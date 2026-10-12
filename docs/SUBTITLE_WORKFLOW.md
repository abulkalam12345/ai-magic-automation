# WonderVexa subtitle workflow

## Goal

Burn readable captions into the final short while keeping the editable SRT sidecar as the source for later corrections.

## Caption requirements

- Supply an editable UTF-8 SubRip file (`.srt`) with the script and metadata.
- Keep each cue short: ideally one phrase and no more than two lines on a 1080x1920 canvas.
- Use high-contrast text with a subtle outline or shadow; keep captions inside the central safe area and away from platform controls.
- Avoid covering the subject's face, key transformation, or the WonderVexa watermark.
- Use sentence case and natural punctuation. Do not fill the screen with hashtags.
- Do not claim that a voiceover exists unless an actual voice track has been recorded or generated under approved terms.

## Rendering

The assembler accepts optional `--captions captions.srt` for both single-clip and multi-clip assembly. It uses FFmpeg's `subtitles` filter (libass) with a bottom-center style and a 260-pixel lower margin; the watermark is composited after captions. The thumbnail also receives the captions. If FFmpeg lacks the subtitles/libass filter, rendering fails rather than silently dropping captions.

Example:

```bash
python src/media_assembler.py --input clip-a.mp4 clip-b.mp4 --output output/final.mp4 --thumbnail output/thumbnail.png --captions captions.srt --target-duration 10
```

Before invoking FFmpeg, the assembler resolves output paths and rejects any output/thumbnail collision with source video, captions, or audio, as well as output and thumbnail paths that point to the same file. This protects inputs from FFmpeg's overwrite flag, including equivalent relative paths. The assembler validates UTF-8 SRT structure before rendering: cue numbers must be sequential, timestamps must be valid (minutes and seconds are 00–59), each cue must contain text, end times must follow start times, and cues must be chronological and non-overlapping. The SRT is copied into a temporary directory under a safe fixed filename, avoiding filter-path parsing problems. The temporary copy is removed after rendering; retain the original editable SRT separately.

## Optional audio

You may supply a locally available audio file with `--audio music.mp3` for either single-clip or multi-clip assembly. Only use audio you created or have a license/permission to use on the intended social platforms. The assembler loops the supplied track as needed, mixes it at 20% volume, trims it to the output duration, and fades the final second. No music is downloaded or generated, and no audio provider is contacted. Without `--audio`, the output remains silent as before. Check the final mix and platform music rights manually; this option does not grant a license.

When you include audio, verify the rendered MP4 contains an AAC audio stream:

```bash
python src/media_quality_check.py --video output/final.mp4 --thumbnail output/thumbnail.png --require-audio
```

Without `--require-audio`, the quality checker preserves its previous video-only acceptance behavior. The audio check confirms stream presence and AAC codec only; it does not judge loudness, music rights, clipping, synchronization, or subjective sound quality.

## Thumbnail integrity checks

The media quality checker validates the PNG signature, 1080x1920 dimensions, IHDR bit-depth/color-type compatibility, compression/filter/interlace fields, chunk framing and order, reserved chunk-type bit, CRCs, required indexed-color palette, IEND placement, and absence of trailing bytes. It reads chunk payloads in bounded blocks rather than loading the complete PNG into memory. This is a structural integrity check; it does not decompress IDAT image pixels or assess visual thumbnail quality. A human must still open and inspect the thumbnail before approval.

## Timing and quality review

The suggested 10-second structure is:
- 0–2 seconds: opening hook.
- 2–5 seconds: introduce the magical problem.
- 5–8 seconds: transformation.
- 8–10 seconds: final reveal / channel identity.

These are editorial placeholders, not verified synchronization. A human editor must adjust cue start/end times to the actual footage and any approved voice track. Remove any caption that describes an action not visible in the final cut.

Before a video can be considered ready:
- [ ] Every caption matches the visible action and any spoken words.
- [ ] No spelling, punctuation, or UTF-8 character corruption.
- [ ] Reading speed is comfortable on a phone.
- [ ] Captions remain inside platform-safe margins.
- [ ] Captions do not obscure the subject, transformation, or watermark.
- [ ] Timing has been checked from the rendered video, not inferred from the storyboard alone.
- [ ] Final video remains draft until explicitly approved by the user.

## Safety

No speech recognition, text-to-speech service, external API, paid service, or publishing integration is enabled. This feature only renders a user-supplied SRT; it does not generate or synchronize captions automatically.
