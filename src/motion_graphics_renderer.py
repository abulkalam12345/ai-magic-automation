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


def render_frame(index: int, title: str, premise: str) -> Image.Image:
    t = index / FPS
    image = _background().copy()
    draw = ImageDraw.Draw(image, "RGBA")
    cx, cy = WIDTH // 2, int(HEIGHT * .48)
    pulse = 1 + .035 * math.sin(t * math.tau / 2.5)
    for ring in range(5):
        radius = int((115 + ring * 39) * pulse + 9 * math.sin(t * 2 + ring))
        alpha = 150 - ring * 18
        draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius),
                     outline=(95, 190, 255, alpha), width=3 if ring else 7)
    draw.ellipse((cx-86, cy-86, cx+86, cy+86), fill=(60, 150, 255, 28),
                 outline=(175, 225, 255, 190), width=4)
    for n in range(32):
        angle = n * math.tau / 32 + t * (.25 if n % 2 else -.18)
        radius = 245 + 18 * math.sin(t * 1.7 + n)
        x = int(cx + math.cos(angle) * radius)
        y = int(cy + math.sin(angle) * radius)
        r = 3 + (n % 3)
        draw.ellipse((x-r, y-r, x+r, y+r), fill=(170, 220, 255, 190))
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
    tagline = "A LITTLE MOMENT OF WONDER"
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
    command = [
        ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pixel_format", "rgb24",
        "-video_size", f"{WIDTH}x{HEIGHT}", "-framerate", str(FPS),
        "-i", "-", "-an", "-vf", "scale=1080:1920:flags=lanczos",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(args.output),
    ]

    try:
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

    print(f"Rendered silent 10-second MP4: {args.output}")
    print(f"Rendered 1080x1920 PNG thumbnail: {args.thumbnail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
