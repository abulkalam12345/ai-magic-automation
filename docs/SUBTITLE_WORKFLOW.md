# WonderVexa subtitle workflow

## Goal

Prepare readable captions for every short without inventing speech or claiming that draft captions are synchronized to generated footage.

## Caption requirements

- Deliver an editable UTF-8 SubRip file (`.srt`) alongside the script and metadata.
- Keep each cue short: ideally one phrase and no more than two lines on a 1080x1920 canvas.
- Use high-contrast text with a subtle outline or shadow; keep captions inside the central safe area and away from platform controls.
- Avoid covering the subject's face, key transformation, or the WonderVexa watermark.
- Use sentence case and natural punctuation. Do not fill the screen with hashtags.
- Do not claim that a voiceover exists unless an actual voice track has been recorded or generated under approved terms.

## Timing and synchronization

The content package's suggested 10-second structure is:
- 0–2 seconds: opening hook.
- 2–5 seconds: introduce the magical problem.
- 5–8 seconds: transformation.
- 8–10 seconds: final reveal / channel identity.

These are editorial placeholders, not verified synchronization. A human editor must adjust cue start/end times to the actual footage and any approved voice track. Remove any caption that describes an action not visible in the final cut.

## Rendering

The current `src/media_assembler.py` adds the vertical crop and WonderVexa watermark but does not burn subtitles into the MP4. Keep the SRT as a sidecar until subtitle overlay support has been implemented and tested. Do not manually rename a sidecar file to imply it is embedded.

## Quality review

Before a video can be considered ready:
- [ ] Every caption matches the visible action and any spoken words.
- [ ] No spelling, punctuation, or UTF-8 character corruption.
- [ ] Reading speed is comfortable on a phone.
- [ ] Captions remain inside platform-safe margins.
- [ ] Captions do not obscure the subject, transformation, or watermark.
- [ ] Timing has been checked from the rendered video, not inferred from the storyboard alone.
- [ ] Final video remains draft until explicitly approved by the user.

## Safety

No speech recognition, text-to-speech service, external API, paid service, or publishing integration is enabled by this document. Any future provider must pass the existing zero-cost, license, privacy, and human-approval gates first.
