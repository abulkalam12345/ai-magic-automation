"""Assemble WonderVexa shorts from already-generated, licensed source footage.

Requires FFmpeg installed locally. This module never generates footage, downloads
assets, contacts a provider, or publishes. Source media must be owned/licensed.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def _video_filter(include_watermark: bool = True) -> str:
    filters = [
        "scale=1080:1920:force_original_aspect_ratio=increase",
        "crop=1080:1920",
    ]
    if include_watermark:
        filters.append(
            "drawtext=text='WonderVexa':fontcolor=white@0.82:fontsize=34:"
            "box=1:boxcolor=black@0.22:boxborderw=12:"
            "x=w-tw-64:y=h-th-100"
        )
    return ",".join(filters)


def build_ffmpeg_command(source: Path, output: Path, thumbnail: Path, ffmpeg: str = "ffmpeg") -> list[str]:
    if not source.is_file():
        raise FileNotFoundError(f"Source video not found: {source}")
    output.parent.mkdir(parents=True, exist_ok=True)
    thumbnail.parent.mkdir(parents=True, exist_ok=True)
    return [
        ffmpeg, "-y", "-i", str(source),
        "-vf", _video_filter(), "-t", "60",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-an", str(output),
        "-ss", "1", "-i", str(source), "-frames:v", "1",
        "-vf", _video_filter(include_watermark=False), str(thumbnail),
    ]


def build_sequence_ffmpeg_command(
    sources: list[Path], output: Path, target_duration: int = 10, ffmpeg: str = "ffmpeg"
) -> list[str]:
    """Concatenate 2+ silent clips into an 8–12 second vertical short."""
    if len(sources) < 2:
        raise ValueError("A clip sequence requires at least two source videos")
    if not 8 <= target_duration <= 12:
        raise ValueError("Target duration must be between 8 and 12 seconds")
    for source in sources:
        if not source.is_file():
            raise FileNotFoundError(f"Source video not found: {source}")

    output.parent.mkdir(parents=True, exist_ok=True)
    inputs = [part for source in sources for part in ("-i", str(source))]
    chains = []
    labels = []
    for index in range(len(sources)):
        label = f"clip{index}"
        chains.append(
            f"[{index}:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,setsar=1,setpts=PTS-STARTPTS[{label}]"
        )
        labels.append(f"[{label}]")
    concat = "".join(labels) + f"concat=n={len(sources)}:v=1:a=0, {_video_filter()}[final]"
    filter_complex = ";".join(chains + [concat])
    return [
        ffmpeg, "-y", *inputs, "-filter_complex", filter_complex,
        "-map", "[final]", "-t", str(target_duration),
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-an", str(output),
    ]


def build_sequence_thumbnail_command(video: Path, thumbnail: Path, ffmpeg: str = "ffmpeg") -> list[str]:
    if not video.is_file():
        raise FileNotFoundError(f"Assembled video not found: {video}")
    thumbnail.parent.mkdir(parents=True, exist_ok=True)
    return [
        ffmpeg, "-y", "-ss", "1", "-i", str(video), "-frames:v", "1",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        str(thumbnail),
    ]


def assemble_sequence(
    sources: list[Path], output: Path, thumbnail: Path, target_duration: int = 10
) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is not installed. Install FFmpeg before assembling.")
    subprocess.run(
        build_sequence_ffmpeg_command(sources, output, target_duration, ffmpeg),
        check=True,
    )
    subprocess.run(build_sequence_thumbnail_command(output, thumbnail, ffmpeg), check=True)


def assemble(source: Path, output: Path, thumbnail: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is not installed. Install FFmpeg before assembling.")
    subprocess.run(build_ffmpeg_command(source, output, thumbnail, ffmpeg), check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, nargs="+", type=Path,
                        help="One source clip, or 2+ clips to concatenate in the supplied order")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--thumbnail", required=True, type=Path)
    parser.add_argument("--target-duration", type=int, default=10,
                        help="Sequence target in seconds (8–12; default 10)")
    args = parser.parse_args()
    if len(args.input) == 1:
        assemble(args.input[0], args.output, args.thumbnail)
    else:
        assemble_sequence(args.input, args.output, args.thumbnail, args.target_duration)
    print(f"Created video: {args.output}")
    print(f"Created thumbnail: {args.thumbnail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
