"""Create a WonderVexa magician-led illusion episode pack without generating media.

This is an editorial package builder only. It makes no network/API calls, spends
no credits, and never publishes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

EPISODE = {
    "id": "wondervexa-episode-01",
    "title": "THE FORBIDDEN MAGICIAN — THE VANISHING WOMAN",
    "duration_seconds": 30,
    "format": "9:16",
    "status": "editorial_draft_only",
    "character_lock": (
        "One photorealistic adult South Asian woman magician: warm brown skin, "
        "almond brown eyes, long jet-black hair, tiny beauty mark, fitted black "
        "and deep-plum costume with violet-blue embroidery, restrained silver "
        "jewelry. Preserve the same face, hair, costume, age, body proportions, "
        "and voice in every shot. No face substitution or extra performer."
    ),
    "scenes": [
        {
            "time": "0-3s",
            "visual": "Extreme close-up of the magician's eyes; she looks directly into camera.",
            "hindi_vo": "रुको… अपनी आँखें मत झपकाना।",
            "english_subtitle": "Wait… don't blink.",
            "hook": "SHE VANISHED. HER REFLECTION DIDN'T.",
            "sound": "Near-silence, intimate breath, low mysterious pulse."
        },
        {
            "time": "3-7s",
            "visual": "Medium close-up. She clearly displays one lemon, closes her hand, then opens an empty palm. Keep both hands visible and anatomically correct.",
            "hindi_vo": "ये सिर्फ़ एक नींबू नहीं… मेरा पहला जादू है।",
            "english_subtitle": "This isn't just a lemon… it's my first trick.",
            "sound": "Playful shimmer, sharp vanish whoosh exactly as the palm opens."
        },
        {
            "time": "7-12s",
            "visual": "Over-shoulder mirror shot. The real magician stays still while her reflection smiles a fraction too late.",
            "hindi_vo": "लेकिन… आईने में कुछ गड़बड़ है।",
            "english_subtitle": "But… something is wrong with the mirror.",
            "sound": "Reverse glass shimmer; pulse becomes tense."
        },
        {
            "time": "12-18s",
            "visual": "Locked camera. The reflection slowly raises one hand independently; the real magician does not move.",
            "hindi_vo": "मेरी परछाईं… मेरी नकल करना बंद कर चुकी है!",
            "english_subtitle": "My reflection… has stopped copying me!",
            "sound": "Sub-bass rise and subtle mirror ripple."
        },
        {
            "time": "18-24s",
            "visual": "The reflection steps forward through the mirror plane; the real magician disappears in one continuous, readable VFX transition.",
            "hindi_vo": "नहीं! ये क्या… मेरी जगह कौन आ रहा है?!",
            "english_subtitle": "No! What's happening… who's taking my place?!",
            "sound": "Glass impact, reverse suction, sudden drop."
        },
        {
            "time": "24-30s",
            "visual": "The double now occupies the real side of the mirror, faces camera, and gives a chilling restrained smile.",
            "hindi_vo": "अब… इस दुनिया में मेरी बारी है।",
            "english_subtitle": "Now… it's my turn in this world.",
            "end_card": "WHO REALLY ESCAPED THE MIRROR?",
            "sound": "Almost silent final whisper; cut to black."
        }
    ],
    "global_visual_prompt": (
        "Photorealistic live-action cinematic supernatural illusion, vertical 9:16. "
        "Use the exact same adult South Asian woman magician described in the "
        "character lock in every shot. Real human skin texture, believable eyes, "
        "natural hand anatomy, physically coherent object handling, practical "
        "mirror reflections, controlled in-camera perspective, restrained "
        "violet-blue magical light, dark elegant room, premium suspense-film "
        "cinematography. Keep the lemon and both hands visible during the vanish. "
        "The mirror double must be the same woman and costume. No cartoon, no "
        "illustration, no generic stock footage, no extra fingers, no fused "
        "hands, no face drift, no costume changes, no random text, no fake logos."
    ),
    "publishing": {
        "enabled": False,
        "requires_user_approval_per_video_and_destination": True
    }
}


def build(output: Path) -> Path:
    output.mkdir(parents=True, exist_ok=True)
    (output / "episode.json").write_text(
        json.dumps(EPISODE, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    lines = [
        "# " + EPISODE["title"], "",
        "**Channel:** WonderVexa  ",
        "**Format:** 9:16 vertical  ",
        "**Duration:** 30 seconds  ",
        "**Status:** Editorial package only — no footage or audio generated.", "",
        "## Character continuity lock", "", EPISODE["character_lock"], "",
        "## Global visual prompt", "", EPISODE["global_visual_prompt"], "",
        "## Six-shot storyboard", ""
    ]
    for scene in EPISODE["scenes"]:
        lines.extend([
            "### " + scene["time"], "",
            "**Visual:** " + scene["visual"], "",
            "**Hindi voice-over:** " + scene["hindi_vo"], "",
            "**English subtitle:** " + scene["english_subtitle"], "",
            "**Sound:** " + scene["sound"], ""
        ])
        if "hook" in scene:
            lines.extend(["**On-screen hook:** " + scene["hook"], ""])
        if "end_card" in scene:
            lines.extend(["**End card:** " + scene["end_card"], ""])
    lines.extend([
        "## Production and approval gates", "",
        "- Generate only if an officially documented zero-cost provider and quota are verified.",
        "- Do not start a free trial, add a card, buy credits, or permit paid fallback.",
        "- Confirm commercial/social usage rights and reference-image data handling first.",
        "- Review face identity, hands, mirror geometry, lemon continuity, Hindi voice, subtitles, and watermark.",
        "- Keep every provider watermark visible; add the WonderVexa logo only in a separate edit layer.",
        "- No upload or publication without explicit approval for the finished video and each destination.",
        ""
    ])
    (output / "production.md").write_text("\n".join(lines), encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("output/magician-episode-01"))
    args = parser.parse_args()
    result = build(args.output)
    print(f"Created editorial package: {result}")


if __name__ == "__main__":
    main()
