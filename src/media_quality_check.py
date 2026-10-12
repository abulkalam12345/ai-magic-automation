"""Offline technical quality checks for finished WonderVexa short exports.

Uses ffprobe only; it does not upload, publish, or modify media.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


def validate_probe_data(data: dict[str, Any], min_duration: float = 8.0,
                        max_duration: float = 60.0,
                        require_audio: bool = False) -> list[str]:
    errors: list[str] = []
    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    if video is None:
        return ["No video stream found."]

    if video.get("codec_name") != "h264":
        errors.append("Video codec must be H.264.")
    if (video.get("width"), video.get("height")) != (1080, 1920):
        errors.append("Video dimensions must be exactly 1080x1920 (vertical 9:16).")
    if video.get("pix_fmt") != "yuv420p":
        errors.append("Pixel format must be yuv420p for broad platform compatibility.")

    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if require_audio and audio is None:
        errors.append("An audio stream is required but none was found.")
    elif require_audio and audio.get("codec_name") != "aac":
        errors.append("Audio codec must be AAC when audio is required.")

    try:
        duration = float(data.get("format", {}).get("duration"))
    except (TypeError, ValueError):
        duration = -1.0
    if duration < min_duration or duration > max_duration:
        errors.append(f"Duration must be between {min_duration:g} and {max_duration:g} seconds.")
    return errors


def check_files(video_path: Path, thumbnail_path: Path,
                probe_data: dict[str, Any], require_audio: bool = False) -> list[str]:
    errors = validate_probe_data(probe_data, require_audio=require_audio)
    if not video_path.is_file() or video_path.stat().st_size == 0:
        errors.append("Video file is missing or empty.")
    if not thumbnail_path.is_file() or thumbnail_path.stat().st_size == 0:
        errors.append("Thumbnail file is missing or empty.")
    elif thumbnail_path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
        errors.append("Thumbnail must be a valid PNG file.")
    return errors


def inspect(video_path: Path, thumbnail_path: Path, require_audio: bool = False) -> list[str]:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise RuntimeError("ffprobe is not installed. Install FFmpeg/ffprobe before checking media.")
    if not video_path.is_file():
        return ["Video file is missing or empty."]
    result = subprocess.run(
        [ffprobe, "-v", "error", "-show_streams", "-show_format",
         "-of", "json", str(video_path)],
        check=True, capture_output=True, text=True,
    )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("ffprobe returned invalid JSON.") from exc
    return check_files(video_path, thumbnail_path, data, require_audio=require_audio)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--thumbnail", required=True, type=Path)
    parser.add_argument("--require-audio", action="store_true",
                        help="Fail unless an AAC audio stream is present")
    args = parser.parse_args()
    errors = inspect(args.video, args.thumbnail, require_audio=args.require_audio)
    if errors:
        print("QUALITY CHECK FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("QUALITY CHECK PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
