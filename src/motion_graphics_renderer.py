"""Render a small original procedural magic-motion short; no AI or external media."""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT, FPS, DURATION = 720, 1280, 24, 10
FRAMES = FPS * DURATION


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    candidates = [
        Path("/usr/share/fonts/truetype/dejavu") / name,
        Path("/usr/share/fonts/dejavu") / name,
    ]
    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont,
          max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and draw.textbbox((0, 0), candidate, font=font)[2] > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


@lru_cache(maxsize=1)
def _background() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = image.load()
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        base = (int(5 + 12 * ratio), int(10 + 15 * ratio), int(30 + 40 * ratio))
        for x in range(WIDTH):
            glow = max(0.0, 1.0 - math.sqrt(((x-WIDTH/2)/(WIDTH*.75))**2 +
                                             ((y-HEIGHT*.48)/(HEIGHT*.62))**2))
            pixels[x, y] = (min(255, int(base[0] + 8*glow)),
                            min(255, int(base[1] + 24*glow)),
                            min(255, int(base[2] + 55*glow)))
    return image


def _draw_growth_tree(draw: ImageDraw.ImageDraw, cx: int, ground: int,
                      growth: float, t: float) -> None:
    """Draw a seed-to-sapling-to-golden-tree progression using vector strokes."""
    growth = max(0.0, min(1.0, growth))
    if growth < 0.10:
        # A small seed rests in a pool of warm light before it sprouts.
        r = 9 + int(5 * math.sin(t * 4) ** 2)
        draw.ellipse((cx-r, ground-r, cx+r, ground+r//2),
                     fill=(143, 91, 42, 255), outline=(255, 207, 105, 255), width=3)
        return

    trunk_height = int(300 * growth)
    top = ground - trunk_height
    bend = int(24 * math.sin(t * .8) * growth)
    points = []
    for step in range(13):
        p = step / 12
        y = ground - int(trunk_height * p)
        x = cx + int(bend * p * p)
        points.append((x, y))
    # Draw the trunk in short tapered sections.
    for i in range(len(points)-1):
        width = max(3, int((20 - 13 * (i / 12)) * growth))
        draw.line((points[i], points[i+1]), fill=(151, 91, 43, 255), width=width)
    draw.ellipse((cx-30, ground-5, cx+30, ground+8),
                 fill=(106, 72, 42, 180))

    branch_specs = [
        (-1, .28, .50), (1, .34, .57), (-1, .52, .72),
        (1, .62, .78), (-1, .77, .88), (1, .82, .94),
    ]
    leaf_tips = []
    for side, start_p, end_p in branch_specs:
        if growth < start_p:
            continue
        amount = min(1.0, (growth-start_p) / max(.01, end_p-start_p))
        y0 = ground - int(trunk_height * (start_p * .82))
        x0 = cx + int(bend * (start_p * .82) ** 2)
        length = int((72 + 18 * (start_p > .7)) * amount)
        x1 = x0 + side * length
        y1 = y0 - int(length * .52)
        draw.line((x0, y0, x1, y1), fill=(151, 91, 43, 255),
                  width=max(2, int(8 * growth)))
        leaf_tips.append((x1, y1, side))
    # Crown foliage unfolds in stages, with gently moving golden leaves.
    if growth > .38:
        leaf_count = int(8 + 34 * min(1.0, (growth-.38)/.62))
        for n in range(leaf_count):
            angle = n * 2.399 + t * .12
            radius = (18 + (n % 7) * 10) * min(1.0, growth)
            x = cx + int(math.cos(angle) * radius * 1.35 + bend)
            y = top + 25 + int(math.sin(angle) * radius * .82)
            size = 5 + (n % 3)
            color = (255, 205 + n % 35, 76 + n % 40, 235)
            draw.ellipse((x-size, y-size//2, x+size, y+size//2),
                         fill=color, outline=(255, 237, 165, 210), width=1)
    for x, y, side in leaf_tips:
        sway = int(4 * math.sin(t * 2 + x))
        draw.ellipse((x-8+sway, y-5, x+8+sway, y+5),
                     fill=(255, 211, 91, 245), outline=(255, 239, 174, 220))
    # Floating motes orbit the crown as the tree matures.
    if growth > .55:
        for n in range(18):
            angle = n * math.tau / 18 + t * .35
            radius = 155 + 10 * math.sin(t + n)
            x = cx + int(math.cos(angle) * radius)
            y = top + 95 + int(math.sin(angle) * radius * .48)
            draw.ellipse((x-2, y-2, x+2, y+2),
                         fill=(255, 226, 145, 190))


def render_frame(index: int, title: str, premise: str) -> Image.Image:
    t = index / FPS
    image = _background().copy()
    draw = ImageDraw.Draw(image, "RGBA")
    cx, cy = WIDTH // 2, int(HEIGHT * .55)
    growth = min(1.0, max(0.0, (t - .7) / 7.0))
    _draw_growth_tree(draw, cx, cy + 205, growth, t)
    # Warm halo grows with the tree; it is an original drawn effect, not footage.
    halo = int(85 + 100 * growth)
    draw.ellipse((cx-halo, cy-halo-35, cx+halo, cy+halo-35),
                 outline=(255, 196, 85, int(45 + 75*growth)), width=3)
    # Story-led caption: use the actual draft premise rather than a generic tagline.
    caption_font = _font(25)
    caption_lines = _wrap(draw, premise.strip(), caption_font, WIDTH - 112)[:3]
    caption_y = int(HEIGHT * .13)
    for line in caption_lines:
        box = draw.textbbox((0, 0), line, font=caption_font)
        draw.text(((WIDTH-(box[2]-box[0]))/2, caption_y), line,
                  font=caption_font, fill=(220, 237, 255, 245),
                  stroke_width=1, stroke_fill=(10, 25, 55, 220))
        caption_y += 38

    # Three-act progress cue makes the short feel paced, without pretending
    # that this procedural render contains generated footage.
    bar_left, bar_right = 90, WIDTH - 90
    bar_y = int(HEIGHT * .68)
    draw.rounded_rectangle((bar_left, bar_y, bar_right, bar_y + 5),
                           radius=3, fill=(85, 130, 175, 130))
    progress = min(1.0, max(0.0, t / DURATION))
    draw.rounded_rectangle((bar_left, bar_y,
                            bar_left + int((bar_right-bar_left)*progress), bar_y+5),
                           radius=3, fill=(170, 220, 255, 230))

    title_font = _font(48, True)
    lines = _wrap(draw, title.upper(), title_font, WIDTH - 80)[:2]
    y0 = int(HEIGHT * .76)
    for line in lines:
        box = draw.textbbox((0, 0), line, font=title_font)
        draw.text(((WIDTH-(box[2]-box[0]))/2, y0), line,
                  font=title_font, fill=(255, 255, 255, 255),
                  stroke_width=2, stroke_fill=(25, 55, 100, 255))
        y0 += 62
    small = _font(22)
    tagline = "A LITTLE DAILY MOMENT OF WONDER"
    box = draw.textbbox((0, 0), tagline, font=small)
    draw.text(((WIDTH-(box[2]-box[0]))/2, y0+8), tagline,
              font=small, fill=(155, 220, 255, 255))
    # Text-only brand mark; the channel's original logo asset is not in this repo.
    brand = "WONDERVEXA"
    brand_font = _font(21, True)
    box = draw.textbbox((0, 0), brand, font=brand_font)
    draw.text((WIDTH-(box[2]-box[0])-28, HEIGHT-58), brand,
              font=brand_font, fill=(235, 245, 255, 220))
    return image


def build_narration(title: str, premise: str, max_chars: int = 130) -> str:
    """Build a concise narration line that fits the ten-second proof video."""
    clean_title = " ".join(title.split()).strip(" .!?")
    clean_premise = " ".join(premise.split())
    if not clean_title:
        raise ValueError("Narration title must not be empty.")
    title_budget = max(1, max_chars - 3)
    if len(clean_title) > title_budget:
        clean_title = clean_title[:title_budget].rsplit(" ", 1)[0] or clean_title[:title_budget]
    remaining = max_chars - len(clean_title) - 2
    if remaining <= 0 or not clean_premise:
        return clean_title + "."
    if len(clean_premise) > remaining:
        clipped = clean_premise[:max(1, remaining - 1)].rsplit(" ", 1)[0]
        clean_premise = (clipped or clean_premise[:remaining - 1]).rstrip(" .,;:") + "…"
    return f"{clean_title}. {clean_premise}"



def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True, type=Path,
                        help="Validated offline draft package containing metadata.json")
    parser.add_argument("--output", required=True, type=Path,
                        help="Destination MP4 path")
    parser.add_argument("--thumbnail", required=True, type=Path,
                        help="Destination 1080x1920 PNG thumbnail path")
    args = parser.parse_args()

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        parser.error("ffmpeg is required; install FFmpeg before rendering.")
    tts = shutil.which("espeak-ng")
    if not tts:
        parser.error("espeak-ng is required for the offline narration track.")

    metadata_path = args.package / "metadata.json"
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(f"Could not read valid package metadata: {exc}")
    title = metadata.get("topic")
    premise = metadata.get("premise")
    if not isinstance(title, str) or not title.strip():
        parser.error("Package metadata must contain a non-empty topic.")
    if not isinstance(premise, str) or not premise.strip():
        parser.error("Package metadata must contain a non-empty premise.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.thumbnail.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix="wondervexa-audio-") as audio_dir:
            narration_path = Path(audio_dir) / "narration.wav"
            # eSpeak NG is an offline open-source synthesizer; no API, account,
            # paid quota, or network request is used. Keep narration concise.
            narration = build_narration(title, premise)
            subprocess.run(
                [tts, "-v", "en-us", "-s", "175", "-w", str(narration_path), narration],
                check=True, capture_output=True, text=True, timeout=60,
            )
            command = [
                ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                "-f", "rawvideo", "-pixel_format", "rgb24",
                "-video_size", f"{WIDTH}x{HEIGHT}", "-framerate", str(FPS),
                "-i", "-", "-i", str(narration_path),
                "-vf", "scale=1080:1920:flags=lanczos",
                "-map", "0:v:0", "-map", "1:a:0", "-t", str(DURATION),
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
                "-af", "apad", "-shortest", "-movflags", "+faststart",
                str(args.output),
            ]
            with tempfile.TemporaryFile() as error_log:
                process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=error_log)
                assert process.stdin is not None
                try:
                    for index in range(FRAMES):
                        frame = render_frame(index, title, premise)
                        process.stdin.write(frame.tobytes())
                    process.stdin.close()
                except (BrokenPipeError, OSError):
                    if process.stdin and not process.stdin.closed:
                        process.stdin.close()
                return_code = process.wait(timeout=600)
                if return_code != 0:
                    error_log.seek(0)
                    detail = error_log.read().decode("utf-8", errors="replace")[-2000:]
                    raise RuntimeError(f"FFmpeg render failed (exit {return_code}): {detail}")

        final_frame = render_frame(FRAMES - 1, title, premise)
        final_frame = final_frame.resize((1080, 1920), Image.Resampling.LANCZOS)
        final_frame.save(args.thumbnail, format="PNG", optimize=True)
    except (OSError, subprocess.SubprocessError, RuntimeError) as exc:
        print(f"RENDER FAILED: {exc}")
        return 1

    print(f"Rendered 10-second MP4 with offline synthetic narration: {args.output}")
    print(f"Rendered 1080x1920 PNG thumbnail: {args.thumbnail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
