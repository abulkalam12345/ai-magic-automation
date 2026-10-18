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
    ("Moonlit Seed", "A tiny seed grows into a glowing moonflower when kindness is shown", "magical flower transformation", "A forgotten seed glows under moonlight and blooms into a tiny galaxy flower."),
    ("Crystal Rain", "A raindrop becomes a crystal garden above a dry village", "fantasy crystal garden", "One sparkling raindrop turns an empty garden into a crystal wonderland."),
    ("Clockwork Butterfly", "A broken mechanical butterfly receives a magical repair", "magical butterfly restoration", "A little brass butterfly gets one last spark and comes alive."),
    ("Lantern of Hope", "A dark lantern lights up when someone shares a small act of kindness", "hope magic short story", "A single act of kindness awakens a lantern that lights an entire forest."),
    ("Starfish Wish", "A stranded starfish is returned to the sea by a wave of stardust", "ocean magic transformation", "Stardust brings a stranded starfish safely back to a glowing ocean."),
    ("Frozen Rose", "A frozen rose blooms when a warm golden light touches it", "ice to flower magic", "A frozen rose transforms into a radiant flower in a swirl of blue and gold."),
    ("Paper Dragon", "A child's paper dragon becomes a tiny luminous guardian", "paper dragon comes alive", "An ordinary paper dragon receives a magical spark and spreads its wings."),
    ("Aurora Waterfall", "A hidden waterfall turns into flowing northern lights", "aurora waterfall fantasy", "A secret waterfall transforms into a river of colorful aurora light."),
    ("Lost Firefly", "A dim firefly regains its light and guides others home", "firefly magical rescue", "One tiny firefly finds its glow and lights the way home for the whole forest."),
    ("Wish Glass", "A cracked glass marble reveals a miniature enchanted world", "miniature fantasy world", "A cracked marble opens a tiny portal to a world of wonder."),

    ("Glasswing Moth", "A pale moth gains luminous glass-like wings and escapes a rainy window", "magical moth transformation", "A tiny moth discovers wings made of moonlit glass."),
    ("The Silent Bell", "A silent village bell rings again when a lost note returns", "enchanted bell fantasy", "One forgotten note awakens the bell that protects the village."),
    ("Pocket Galaxy", "A dark pocket watch opens to reveal a swirling miniature galaxy", "miniature galaxy magic", "A stopped watch hides an entire galaxy waiting to shine."),
    ("Coral Crown", "A dull coral crown restores color to a bleached underwater reef", "underwater coral restoration", "A forgotten crown sends color flowing through the reef."),
    ("Cloud Whale", "A small cloud becomes a glowing whale floating above a sleeping town", "cloud whale fantasy", "A lonely cloud transforms into a gentle sky whale."),
    ("Golden Acorn", "A tiny acorn grows into a protective tree of golden leaves", "magical acorn growth", "One golden acorn grows into a shelter for the forest."),
    ("Starlight Key", "An old key unlocks a doorway made of constellations", "starlight portal fantasy", "A rusty key turns and unlocks a sky full of stars."),
    ("Snowdrop Promise", "A frozen snowdrop flower blooms beneath a warm blue spark", "snowdrop flower magic", "A single blue spark wakes a flower beneath the snow."),
    ("Origami Crane", "A paper crane unfolds into a living bird of soft light", "origami crane comes alive", "A folded paper crane takes flight in a shower of light."),
    ("Pebble Planet", "An ordinary pebble reveals tiny oceans and mountains when illuminated", "tiny planet reveal", "A little pebble holds a whole world inside."),
    ("Rainbow Shell", "A faded seashell releases a ribbon of color across the shore", "rainbow shell transformation", "A forgotten shell paints the beach with a living rainbow."),
    ("Midnight Orchard", "Bare branches grow glowing fruit after a firefly visits", "magical glowing orchard", "One firefly brings a sleeping orchard back to life."),
    ("The Kindness Thread", "A loose blue thread repairs a torn star-shaped kite", "magical thread repair", "A tiny thread stitches a broken kite back to the sky."),
    ("Frost Phoenix", "A small ice sculpture becomes a gentle bird of shimmering frost", "ice phoenix fantasy", "A frozen bird spreads its wings without melting away."),
    ("Singing Pebble", "A dull river stone glows and sends musical ripples through water", "enchanted river stone", "A silent stone finds its song beneath the river."),
    ("Dandelion Comet", "A dandelion seed becomes a tiny comet crossing a twilight garden", "dandelion seed magic", "One drifting seed becomes a comet of golden light."),
    ("Mossy Doorway", "A moss-covered stone opens into a bright hidden garden", "hidden garden portal", "A small door in an old stone reveals a secret garden."),
    ("Blue Ember", "A fading ember becomes a floating blue lantern for a traveler", "blue ember transformation", "A dying ember finds a new purpose as a guiding light."),
    ("Pearl of Tides", "A dull pearl restores a moonlit path through the ocean", "ocean pearl magic", "A little pearl lights a path beneath the waves."),
    ("Feather Compass", "A fallen feather turns into a compass pointing toward home", "magical feather compass", "A lost feather becomes a guide home."),
    ("Enchanted Hourglass", "Golden sand reverses a wilted leaf into a fresh green sprout", "hourglass time magic", "A few golden grains give a tiny leaf a second chance."),
    ("Lighthouse Sprite", "A tiny sprite relights a lighthouse with a swirl of blue energy", "magical lighthouse story", "A little sprite restores the light that guides ships home."),
    ("Jade Tadpole", "A tiny tadpole grows a shimmering tail and becomes a pond guardian", "fantasy pond transformation", "A small pond creature discovers its magical glow."),
    ("Wishing Acorn Lantern", "An acorn shell becomes a lantern for woodland creatures", "woodland acorn lantern", "A hollow acorn shines bright enough to guide the forest."),
    ("Moonstone Bridge", "Floating moonstones form a glowing bridge over a quiet stream", "moonstone bridge fantasy", "One by one, moonstones create a path across the water."),
    ("Dewdrop Castle", "A single dewdrop reveals a tiny castle at sunrise", "dewdrop miniature castle", "A drop of morning dew hides a castle made of light."),
    ("The Last Snowflake", "A melting snowflake becomes a crystal flower before it disappears", "snowflake crystal flower", "The last snowflake leaves behind a flower of crystal."),
    ("Comet Seedling", "A weak seedling grows luminous leaves beneath a passing comet", "comet garden magic", "A passing comet gives one little seedling a brilliant glow."),
    ("Whispering Shell", "A seashell releases glowing musical notes that guide a turtle to the sea", "magical seashell rescue", "A shell whispers a song that leads a little turtle home."),
    ("Aurora Feather", "A grey feather transforms into a ribbon of northern lights", "aurora feather transformation", "A forgotten feather unfolds into the colors of the sky."),
    ("Crystal Acorn Door", "A crystal acorn opens to reveal a miniature forest home", "crystal acorn miniature world", "A tiny crystal acorn holds a home for the smallest forest friend."),
    ("Starlit Teacup", "A chipped teacup fills with a swirling night sky and tiny stars", "starlit teacup fantasy", "A chipped cup becomes a little universe under moonlight."),
    ("Emerald Raindrop", "A raindrop turns a grey leaf into a bright emerald canopy", "emerald leaf transformation", "One emerald raindrop awakens the colors of a tree."),
    ("Butterfly Lantern", "A paper lantern unfolds into a glowing butterfly that lights a path", "butterfly lantern magic", "A quiet lantern opens its wings and lights the way."),
    ("Tiny Tidepool", "A dry tidepool fills with miniature glowing sea life", "magical tidepool transformation", "A little pool becomes a whole ocean of wonder."),
    ("Sunrise Music Box", "An old music box releases a miniature sunrise over a dark room", "magical music box sunrise", "One gentle tune brings sunrise into a dark room."),
    ("Silver Willow", "A bare willow grows silver leaves that shimmer in the night breeze", "silver willow tree magic", "A quiet spark gives a bare willow a crown of silver."),
    ("Star Map Parchment", "A blank parchment reveals a glowing map to a hidden constellation", "magical star map", "A blank page becomes a map written in stars."),
    ("Candlefly Rescue", "A tiny insect trapped in darkness becomes a beacon for its friends", "glowing insect rescue", "One small light helps every lost friend find the way."),
    ("Ruby Raindrop", "A red raindrop transforms a grey stone into a blooming miniature garden", "ruby raindrop garden", "A single ruby drop turns stone into a secret garden."),
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
    hashtags = ["#WonderVexa", "#MagicShorts", "#FantasyShorts", "#AIMagic", "#Shorts"]
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
Use the exact same central subject, silhouette, colors, proportions, and environment in every scene. Keep the camera vertical and the subject centered. Preserve realistic, readable movement and a consistent cinematic fantasy 3D look. Generate clean footage without text, logos, captions, or watermark; add branding only during editing.

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
