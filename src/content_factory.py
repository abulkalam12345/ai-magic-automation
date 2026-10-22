"""Create an offline, zero-cost WonderVexa short-video draft package.

This creates scripts, shot lists, SEO metadata and a thumbnail SVG. It does not
call an AI provider, download media, render a video, or publish anything.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDEAS = [
    ("Vanishing Lemon", "A magician closes her hand around a lemon; it vanishes, but appears inside the mirror", "lemon vanish magic trick", "She opened her hand. The lemon was gone. The mirror still held it."),
    ("The Delayed Reflection", "A magician moves, but her mirror reflection reacts one second too late", "mirror reflection illusion", "Watch the mirror. It moves after she stops."),
    ("The Escaping Reflection", "The magician's reflection steps out of the mirror while she remains still", "reflection escape illusion", "Her reflection just walked out of the mirror."),
    ("The Floating Ring", "A silver ring rises from the magician's palm and circles her wrist", "levitating ring magic trick", "She never touched it. So why is it floating?"),
    ("The Borrowed Shadow", "The magician's shadow turns and waves while she faces forward", "living shadow illusion", "Her shadow is waving. She isn't."),
    ("The Empty Hat", "A magician shows an empty hat; a white dove's shadow appears inside it", "magic hat illusion", "The hat was empty. Then something moved inside."),
    ("The Impossible Key", "A key melts through a locked glass box without breaking the glass", "impossible key magic illusion", "The glass is still locked. The key is now inside."),
    ("The Mirror Double", "A second version of the magician appears behind her in the mirror", "mirror double illusion", "There is someone behind her. Look again."),
    ("The Floating Playing Card", "A single playing card hovers and turns between the magician's fingers", "levitating playing card trick", "One card. No strings. Don't blink."),
    ("The Disappearing Rose", "A red rose vanishes from the magician's fingers and blooms in a sealed glass", "rose vanish magic trick", "The rose vanished from her hand. It bloomed inside the glass."),
    ("The Time-Stopped Watch", "A watch stops ticking while everything around it keeps moving", "time stop magic illusion", "Only the watch stopped. Everything else kept moving."),
    ("The Portal in the Mirror", "A violet portal opens inside an ordinary standing mirror", "mirror portal fantasy illusion", "That mirror is no longer reflecting the room."),
    ("The Vanishing Woman", "The magician disappears, leaving only her reflection staring at camera", "woman disappearance magic illusion", "She vanished. Her reflection didn't."),
    ("The Endless Coin", "A coin passes through the magician's closed fist and returns from behind her ear", "coin through hand magic trick", "She closed her fist. The coin came out somewhere impossible."),
    ("The Glass Without Walls", "A silk scarf passes through a sealed transparent glass cylinder", "penetration magic illusion", "The glass never opened. The scarf passed straight through."),
    ("The Shadow Doppelganger", "The magician's shadow separates from her feet and stands upright", "shadow double magic illusion", "Her shadow has stopped following her."),
    ("The Floating Candle", "A candle rises and circles the magician in a dark room", "levitating candle magic illusion", "No wire. No hands. Just a floating flame."),
    ("The Split Reflection", "The mirror shows two different versions of the magician at once", "split mirror illusion", "One mirror. Two different reflections."),
    ("The Locked Box Escape", "A silk ribbon tied around a small box appears outside while the box remains sealed", "impossible box magic trick", "The ribbon escaped. The box never opened."),
    ("The Black Rose", "A white rose turns black between two finger snaps", "instant rose color change trick", "One snap changed every petal."),
    ("The Vanishing Deck", "A full deck of cards disappears between the magician's hands", "disappearing playing cards trick", "A full deck. One second. Nothing left."),
    ("The Mirror Hand", "A hand reaches out from the mirror and touches the glass from the outside", "hand through mirror illusion", "Something inside the mirror just touched the glass."),
    ("The Floating Silk", "A violet silk cloth rises and folds itself into a rose", "self folding silk magic illusion", "The silk is folding itself. Watch what it becomes."),
    ("The Impossible Water", "Water pours upward from a glass into a hovering bottle", "reverse gravity water magic", "The water is flowing in the wrong direction."),
    ("The Vanishing Ring Box", "A ring box disappears, leaving the ring floating in place", "ring box vanish magic trick", "The box disappeared. The ring stayed in mid-air."),
    ("The Living Portrait", "A portrait of the magician blinks while she stands motionless", "moving portrait magic illusion", "The portrait just blinked. She didn't."),
    ("The Paper Butterfly", "A paper butterfly unfolds, flaps its wings, then lands on her finger", "paper butterfly comes alive magic", "It was paper a second ago."),
    ("The Impossible Knot", "A rope tied in a tight knot becomes perfectly straight in her closed fist", "instant rope restoration magic", "One squeeze. The knot is gone."),
    ("The Candle Through Glass", "A candle flame passes through a glass pane without cracking it", "flame through glass illusion", "The flame crossed the glass. The glass is untouched."),
    ("The Second Moon", "A tiny glowing moon appears between the magician's palms", "miniature moon magic illusion", "She is holding something that shouldn't fit in her hands."),
    ("The Vanishing Chair", "An empty chair disappears, but its shadow remains on the floor", "vanishing object shadow illusion", "The chair is gone. Its shadow is still there."),
    ("The Reverse Footsteps", "Footprints appear in dust ahead of the magician before she takes a step", "reverse footsteps magic illusion", "The footprints are appearing before she walks."),
    ("The Floating Hourglass", "An hourglass turns upside down in mid-air and its sand rises", "reverse sand hourglass illusion", "The sand is falling upward."),
    ("The Duplicate Coin", "One coin splits into three identical coins across her fingertips", "coin multiplication magic trick", "One coin became three. Count them."),
    ("The Vanishing Door", "A doorway appears in a blank wall and closes behind the magician", "secret portal door illusion", "There was no door there a moment ago."),
    ("The Unblinking Twin", "A mirror double keeps eye contact while the magician turns away", "mirror twin magic illusion", "She looked away. Her reflection kept staring."),
    ("The Floating Water Drop", "A single water droplet hovers and circles a glass sphere", "levitating water drop illusion", "A drop of water is orbiting the glass."),
    ("The Impossible Match", "A burning match extinguishes, then relights inside a sealed jar", "impossible match magic trick", "The flame went out. Now it is burning inside the jar."),
    ("The Shadow Portal", "A dark doorway opens inside the magician's shadow", "shadow portal magic illusion", "Her shadow just became a doorway."),
    ("The Final Switch", "The magician and her reflection exchange places in a single flash", "magician mirror switch illusion", "Which one came out of the mirror?")
]


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _atomic_write_text(path: Path, content: str) -> None:
    """Replace a text file atomically so interruption cannot truncate its prior contents."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n",
            dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def thumbnail_style(title: str, premise: str, keyword: str) -> tuple[str, str, str]:
    """Return a deterministic subject glyph and palette for a story thumbnail."""
    text = f"{title} {premise} {keyword}".lower()
    themes = (
        (("flower", "rose", "seed", "orchard", "willow", "leaf", "acorn", "garden", "sprout"), "✿", "#ffbd68", "#173b48"),
        (("butterfly", "moth", "feather", "crane", "phoenix", "bird", "wing"), "❋", "#a9e8ff", "#182c62"),
        (("ocean", "sea", "shell", "coral", "starfish", "tide", "pearl", "turtle"), "≋", "#5ce6d0", "#103d5c"),
        (("crystal", "ice", "frost", "snow", "frozen", "snowflake"), "❄", "#a8eaff", "#263c78"),
        (("star", "galaxy", "comet", "moon", "aurora", "planet", "constellation"), "✦", "#e3b4ff", "#251b59"),
        (("lantern", "firefly", "candle", "ember", "lighthouse", "light"), "☼", "#ffd66b", "#49301c"),
        (("bell", "music", "singing", "note", "teacup"), "♫", "#ffc0df", "#48254c"),
        (("key", "doorway", "bridge", "castle", "portal", "compass", "hourglass", "watch"), "◇", "#b9a8ff", "#292653"),
        (("dragon", "whale", "cloud"), "♧", "#9de5ff", "#17405d"),
    )
    for words, symbol, accent, background in themes:
        if any(word in text for word in words):
            return symbol, accent, background
    return "✧", "#8feeff", "#183d78"


def choose_idea(day: date, slot: str, history: list[str]) -> tuple[str, str, str, str]:
    """Prefer unused ideas, then recycle the least-recently-used curated idea."""
    offset = int(hashlib.sha256(f"{day.isoformat()}:{slot}".encode()).hexdigest()[:8], 16)
    used = set(history)
    for step in range(len(IDEAS)):
        idea = IDEAS[(offset + step) % len(IDEAS)]
        if idea[0] not in used:
            return idea

    # The finite catalogue is exhausted. Reuse the topic whose latest use is
    # oldest; stable IDEAS order breaks ties for deterministic output.
    last_used = {title: index for index, title in enumerate(history)}
    return min(IDEAS, key=lambda idea: last_used.get(idea[0], -1))


def build_package(day: date, slot: str, out_dir: Path, history_file: Path) -> Path:
    if slot not in {"morning", "evening"}:
        raise ValueError("slot must be morning or evening")
    history = json.loads(history_file.read_text(encoding="utf-8")) if history_file.exists() else []
    if not isinstance(history, list) or any(not isinstance(item, str) for item in history):
        raise ValueError("Topic history must be a JSON array of topic-name strings.")
    title, premise, keyword, hook = choose_idea(day, slot, history)
    video_id = f"{day.isoformat()}-{slot}-{slug(title)}"
    out = out_dir / video_id
    out.mkdir(parents=True, exist_ok=True)

    short_title = f"{title} ✨ | WonderVexa #Shorts"
    description = (
        f"{hook}\n\n"
        "A tiny original fantasy moment from WonderVexa. Watch till the final magical reveal! "
        "Follow for more original magic transformations and short fantasy stories.\n\n"
        "This is an AI-assisted fictional visual story."
    )
    keywords = [
        f"{keyword} short video", f"{keyword} story", f"how {keyword} happens",
        f"beautiful {keyword} animation", "AI magic transformation short",
        "original fantasy short story", "WonderVexa magical shorts",
    ]
    hashtags = ["#WonderVexa", "#MagicShorts", "#IllusionShorts", "#AIMagic", "#Shorts"]
    script = f"""# {title}

**Channel:** WonderVexa  
**Date / slot:** {day.isoformat()} / {slot}  
**Concept:** {premise}  
**Target:** 10 seconds, vertical 9:16  
**Status:** DRAFT — human review required

## Voiceover / on-screen story
- 0–2s — Hook: {hook}
- 2–5s — Build: Show the obstacle or unfinished state described in the concept; introduce one clear magical trigger.
- 5–8s — Change: Show the named subject visibly changing into the result promised by the concept.
- 8–10s — Payoff: Hold on the completed result long enough to understand it; show the WonderVexa brand.

## Shot list
1. Establish the exact subject and its starting state from the concept.
2. Show one simple, story-relevant magical trigger; avoid unrelated props.
3. Show one continuous, readable before-to-after transformation while preserving subject identity.
4. Hold the finished result in a clean hero frame with safe space for the WonderVexa watermark.

## Generation / editing notes
- Original fictional visuals only; do not imitate a living artist or existing franchise.
- Keep motion simple, coherent, and physically readable.
- No copyrighted music; use silence or properly licensed audio.
- Add subtle WonderVexa watermark in the lower-right safe area.
- Export 1080x1920 MP4 when a verified zero-cost renderer is available.
"""
    visual_prompts = f"""# Visual generation prompts — {title}

**Project:** WonderVexa  
**Story concept:** {premise}  
**Target canvas:** 9:16 portrait, 1080x1920  
**Target duration:** 10 seconds  
**Status:** Prompt pack only — no media has been generated.

## Continuity lock
Character continuity lock: the same photorealistic adult South Asian female magician in every scene, with long jet-black hair, warm brown skin, almond-shaped brown eyes, high cheekbones, and a tiny beauty mark. Keep her face, age, hair, body proportions, and identity unchanged. She wears the same fitted black/deep-plum magician costume with violet-blue embroidery and restrained silver jewelry. Live-action cinematic VFX realism, believable skin texture, practical lighting, physically coherent hands and props; avoid cartoon, illustration, or generic fantasy animation. Keep the camera vertical and subject centered. Generate clean footage without text, logos, captions, or watermark; add WonderVexa branding only during editing.

## Scene 1 — Establish the problem (0–2 seconds)
Create a vertical 9:16 cinematic macro establishing shot for this story: {premise}. Show the subject clearly in its initial state, with the problem immediately understandable. Use a simple uncluttered background, gentle camera movement, soft depth of field, and restrained moonlit blue lighting. Keep the subject centered and fully inside frame.

## Scene 2 — Magic arrives (2–5 seconds)
Continue with the identical subject and environment from Scene 1. Introduce one restrained magical trigger that fits this specific story (for example, a small spark, soft ripple, or gentle glow). Let it interact with the central subject without obscuring it. Keep the original problem or starting state visible so the viewer understands what is about to change. Use a subtle slow push-in; do not change species, shape, scale, or camera orientation.

## Scene 3 — Transformation reveal (5–8 seconds)
Continue seamlessly with the same subject, framing, and lighting. Show the exact subject from the premise changing in one continuous, physically coherent action into the specific result described there. Make the before-and-after difference unmistakable; do not add a second unrelated transformation. No jump cuts, sudden replacement, duplicated subjects, or abrupt camera movement.

## Scene 4 — Final hero shot (8–10 seconds)
Hold on the completed magical result of this story: {hook} Keep the same subject identity and environment. Show the full result clearly with lighting and colors that complement this story, a few restrained fading particles, and clean negative space in the lower-right safe area for a separately added WonderVexa watermark. Stable composition; no baked-in text or logo.

## Negative prompt
Low resolution, landscape framing, cropped subject, inconsistent subject identity, extra subjects, duplicate limbs or parts, deformed anatomy, flicker, jitter, rapid camera spins, jump cuts, abrupt morphing, chaotic particles, excessive bloom, strobing, unreadable text, subtitles, logos, signatures, watermarks, borders, copyrighted characters, imitation of a living artist.

## Assembly notes
- Treat the four scenes as a visual plan, not proof that a provider can preserve continuity.
- If separate clips are generated, compare the subject silhouette and colors at every cut.
- Use only footage and audio with verified usage rights.
- Keep the final master vertical at 1080x1920 and 8–12 seconds.
- Human review is required before any final video or publication.
"""
    (out / "visual_prompts.md").write_text(visual_prompts, encoding="utf-8")
    (out / "script.md").write_text(script, encoding="utf-8")
    metadata = {
        "id": video_id, "channel": "WonderVexa", "date": day.isoformat(),
        "slot": slot, "status": "draft", "topic": title, "premise": premise,
        "title": short_title, "description": description,
        "long_tail_keywords": keywords, "hashtags": hashtags,
        "thumbnail": "thumbnail.svg", "video": None,
        "trend_status": "evergreen_seed_not_live_trend_verified",
        "publishing": {"enabled": False, "requires_explicit_video_approval": True},
    }
    (out / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    safe_title = html.escape(title, quote=False)
    symbol, accent, background = thumbnail_style(title, premise, keyword)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">
<defs>
<radialGradient id="bg"><stop offset="0" stop-color="{background}"/><stop offset="1" stop-color="#050916"/></radialGradient>
<linearGradient id="halo"><stop stop-color="{accent}"/><stop offset=".55" stop-color="#7c8dff"/><stop offset="1" stop-color="#f1aaff"/></linearGradient>
</defs>
<rect width="1080" height="1920" fill="url(#bg)"/>
<circle cx="540" cy="720" r="340" fill="none" stroke="url(#halo)" stroke-width="16" opacity=".82"/>
<circle cx="540" cy="720" r="275" fill="none" stroke="{accent}" stroke-width="3" opacity=".55"/>
<circle cx="540" cy="720" r="205" fill="{accent}" opacity=".10"/>
<text x="540" y="845" text-anchor="middle" fill="{accent}" font-size="390" font-family="Arial,sans-serif">{symbol}</text>
<text x="540" y="1270" text-anchor="middle" fill="#ffffff" font-size="76" font-family="Arial,sans-serif" font-weight="bold">{safe_title}</text>
<text x="540" y="1400" text-anchor="middle" fill="{accent}" font-size="42" font-family="Arial,sans-serif">A MAGICAL TRANSFORMATION</text>
<text x="540" y="1790" text-anchor="middle" fill="#d9eaff" font-size="38" font-family="Arial,sans-serif">WONDERVEXA</text>
</svg>'''
    (out / "thumbnail.svg").write_text(svg, encoding="utf-8")
    history.append(title)
    _atomic_write_text(history_file, json.dumps(history, indent=2) + "\n")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot", choices=("morning", "evening"), required=True)
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--output", default="output/drafts")
    parser.add_argument("--history", default="output/used_topics.json")
    args = parser.parse_args()
    path = build_package(date.fromisoformat(args.date), args.slot, ROOT / args.output, ROOT / args.history)
    print(f"Draft package created: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
