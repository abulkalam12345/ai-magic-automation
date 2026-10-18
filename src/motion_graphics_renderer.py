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

