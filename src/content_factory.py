"""Create an offline, zero-cost WonderVexa short-video draft package.

This creates scripts, shot lists, SEO metadata and a thumbnail SVG. It does not
call an AI provider, download media, render a video, or publish anything.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
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
]


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def choose_idea(day: date, slot: str, history: list[str]) -> tuple[str, str, str, str]:
    offset = int(hashlib.sha256(f"{day.isoformat()}:{slot}".encode()).hexdigest()[:8], 16)
    for step in range(len(IDEAS)):
        idea = IDEAS[(offset + step) % len(IDEAS)]
        if idea[0] not in history:
            return idea
    raise RuntimeError("All built-in ideas have been used. Add fresh reviewed ideas to IDEAS.")


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
- 2–5s — Show the magical problem and build anticipation.
- 5–8s — Reveal the transformation with a clear visual action.
- 8–10s — Hold on the beautiful result; show the WonderVexa brand.

## Shot list
1. Vertical close-up establishing the subject and its problem.
2. A hand-free magical energy swirl approaches; keep the subject consistent.
3. The transformation happens in one readable continuous action.
4. Final hero shot with clean space for the WonderVexa watermark.

## Generation / editing notes
- Original fictional visuals only; do not imitate a living artist or existing franchise.
- Keep motion simple, coherent, and physically readable.
- No copyrighted music; use silence or properly licensed audio.
- Add subtle WonderVexa watermark in the lower-right safe area.
- Export 1080x1920 MP4 when a verified zero-cost renderer is available.
"""
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
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">
<defs><radialGradient id="bg"><stop offset="0" stop-color="#183d78"/><stop offset="1" stop-color="#050916"/></radialGradient>
<linearGradient id="ring"><stop stop-color="#6ffcff"/><stop offset=".5" stop-color="#7c8dff"/><stop offset="1" stop-color="#f1aaff"/></linearGradient></defs>
<rect width="1080" height="1920" fill="url(#bg)"/>
<circle cx="540" cy="760" r="300" fill="none" stroke="url(#ring)" stroke-width="18" opacity=".9"/>
<circle cx="540" cy="760" r="250" fill="none" stroke="#8feeff" stroke-width="4" opacity=".55"/>
<text x="540" y="1320" text-anchor="middle" fill="#ffffff" font-size="76" font-family="Arial,sans-serif" font-weight="bold">{safe_title}</text>
<text x="540" y="1440" text-anchor="middle" fill="#aeeeff" font-size="44" font-family="Arial,sans-serif">A WonderVexa Magical Short</text>
<text x="540" y="1790" text-anchor="middle" fill="#d9eaff" font-size="38" font-family="Arial,sans-serif">WONDERVEXA</text>
</svg>'''
    (out / "thumbnail.svg").write_text(svg, encoding="utf-8")
    history.append(title)
    history_file.parent.mkdir(parents=True, exist_ok=True)
    history_file.write_text(json.dumps(history, indent=2), encoding="utf-8")
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
