"""Assemble a vertical WonderVexa short from already-generated source footage.

Requires FFmpeg installed locally. This module never generates footage, downloads
assets, contacts a provider, or publishes. Source media must be owned/licensed.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def build_ffmpeg_command(source: Path, output: Path, thumbnail: Path, ffmpeg: str = "ffmpeg") -> list[str]:
    if not source.is_file():
        raise FileNotFoundError(f"Source video not found: {source}")
    output.parent.mkdir(parents=True, exist_ok=True)
    thumbnail.parent.mkdir(parents=True, exist_ok=True)
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "drawtext=text='WonderVexa':fontcolor=white@0.82:fontsize=34:"
        "box=1:boxcolor=black@0.22:boxborderw=12:"
        "x=w-tw-64:y=h-th-100"
    )
    return [
        ffmpeg, "-y", "-i", str(source),
        "-vf", vf, "-t", "60",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-an", str(output),
        "-ss", "1", "-i", str(source), "-frames:v", "1",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        str(thumbnail),
    ]


def assemble(source: Path, output: Path, thumbnail: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is not installed. Install FFmpeg before assembling.")
    command = build_ffmpeg_command(source, output, thumbnail, ffmpeg)
    subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--thumbnail", required=True, type=Path)
    args = parser.parse_args()
    assemble(args.input, args.output, args.thumbnail)
    print(f"Created video: {args.output}")
    print(f"Created thumbnail: {args.thumbnail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
