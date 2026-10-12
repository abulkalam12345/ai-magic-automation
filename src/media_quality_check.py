"""Offline technical quality checks for finished WonderVexa short exports.

Uses ffprobe only; it does not upload, publish, or modify media.
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import struct
import subprocess
import zlib
from pathlib import Path
from typing import Any


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_IHDR_HEADER_SIZE = 33
THUMBNAIL_WIDTH = 1080
THUMBNAIL_HEIGHT = 1920


def validate_png_header(header: bytes) -> list[str]:
    """Validate the PNG signature and complete IHDR chunk for a 1080x1920 thumbnail."""
    if len(header) < PNG_IHDR_HEADER_SIZE:
        return ["Thumbnail PNG header is truncated."]
    if header[:8] != PNG_SIGNATURE:
        return ["Thumbnail must be a PNG file."]
    if struct.unpack(">I", header[8:12])[0] != 13 or header[12:16] != b"IHDR":
        return ["Thumbnail must begin with a valid 13-byte IHDR chunk."]

    width, height = struct.unpack(">II", header[16:24])
    if (width, height) != (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT):
        return ["Thumbnail dimensions must be exactly 1080x1920."]
    expected_crc = zlib.crc32(header[12:29]) & 0xFFFFFFFF
    actual_crc = struct.unpack(">I", header[29:33])[0]
    if actual_crc != expected_crc:
        return ["Thumbnail PNG IHDR checksum is invalid."]
    return []



def validate_png_file(path: Path) -> list[str]:
    """Check PNG chunk framing, ordering, dimensions, and CRCs without loading the image."""
    try:
        with path.open("rb") as stream:
            if stream.read(8) != PNG_SIGNATURE:
                return ["Thumbnail must be a PNG file."]
            seen_ihdr = False
            seen_plte = False
            seen_idat = False
            idat_ended = False
            seen_iend = False
            png_color_type = None
            png_bit_depth = None
            png_decompressor = None
            png_decoded_bytes = 0
            png_expected_bytes = None

            while not seen_iend:
                chunk_header = stream.read(8)
                if len(chunk_header) != 8:
                    return ["Thumbnail PNG is truncated before IEND."]
                length, chunk_type = struct.unpack(">I4s", chunk_header)
                if length > 0x7FFFFFFF:
                    return ["Thumbnail PNG chunk length exceeds the PNG limit."]
                if not all(65 <= byte <= 90 or 97 <= byte <= 122 for byte in chunk_type):
                    return ["Thumbnail PNG contains an invalid chunk type."]
                if not seen_ihdr and chunk_type != b"IHDR":
                    return ["Thumbnail PNG must begin with IHDR."]
                if chunk_type == b"IHDR":
                    if seen_ihdr or length != 13:
                        return ["Thumbnail PNG must contain exactly one 13-byte IHDR first."]
                elif chunk_type == b"PLTE":
                    if (seen_plte or seen_idat or length == 0 or length % 3 or length > 768
                            or png_color_type in (0, 4)):
                        return ["Thumbnail PNG contains an invalid PLTE chunk."]
                    if png_color_type == 3 and png_bit_depth is not None and length // 3 > 2 ** png_bit_depth:
                        return ["Thumbnail PNG palette has more entries than its bit depth allows."]
                    seen_plte = True
                elif chunk_type == b"IDAT":
                    if idat_ended:
                        return ["Thumbnail PNG IDAT chunks must be consecutive."]
                    seen_idat = True
                    if png_decompressor is None:
                        png_decompressor = zlib.decompressobj()
                elif chunk_type == b"IEND":
                    if length != 0 or not seen_idat:
                        return ["Thumbnail PNG IEND is invalid or appears before IDAT."]
                elif (chunk_type[0] & 0x20) == 0:
                    return ["Thumbnail PNG contains an unsupported critical chunk."]

                crc = zlib.crc32(chunk_type)
                remaining = length
                ihdr_data = bytearray() if chunk_type == b"IHDR" else None
                while remaining:
                    block = stream.read(min(65536, remaining))
                    if not block:
                        return ["Thumbnail PNG chunk data is truncated."]
                    crc = zlib.crc32(block, crc)
                    if ihdr_data is not None:
                        ihdr_data.extend(block)
                    remaining -= len(block)
                crc_bytes = stream.read(4)
                if len(crc_bytes) != 4:
                    return ["Thumbnail PNG chunk checksum is truncated."]
                if struct.unpack(">I", crc_bytes)[0] != (crc & 0xFFFFFFFF):
                    return ["Thumbnail PNG chunk checksum is invalid."]

                if chunk_type == b"IHDR":
                    seen_ihdr = True
                    width, height = struct.unpack(">II", ihdr_data[:8])
                    if (width, height) != (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT):
                        return ["Thumbnail dimensions must be exactly 1080x1920."]
                    png_bit_depth = ihdr_data[8]
                    png_color_type = ihdr_data[9]
                    valid_depths = {
                        0: (1, 2, 4, 8, 16),
                        2: (8, 16),
                        3: (1, 2, 4, 8),
                        4: (8, 16),
                        6: (8, 16),
                    }
                    if png_color_type not in valid_depths or png_bit_depth not in valid_depths[png_color_type]:
                        return ["Thumbnail PNG has an invalid bit-depth and color-type combination."]
                    if ihdr_data[10] != 0 or ihdr_data[11] != 0 or ihdr_data[12] not in (0, 1):
                        return ["Thumbnail PNG has unsupported compression, filter, or interlace settings."]
                elif chunk_type == b"IDAT":
                    seen_idat = True
                elif seen_idat and chunk_type not in (b"IDAT", b"IEND"):
                    idat_ended = True
                if chunk_type == b"IEND":
                    seen_iend = True

            if png_color_type == 3 and not seen_plte:
                return ["Thumbnail PNG indexed-color images must contain a PLTE chunk."]
            if stream.read(1):
                return ["Thumbnail PNG has trailing data after IEND."]
    except OSError:
        return ["Thumbnail PNG could not be read."]
    return []

def validate_probe_data(data: dict[str, Any], min_duration: float = 8.0,
                        max_duration: float = 60.0,
                        require_audio: bool = False) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["ffprobe JSON must contain a top-level object."]

    streams = data.get("streams")
    if not isinstance(streams, list):
        errors.append("ffprobe streams must be a list.")
        streams = []
    elif any(not isinstance(stream, dict) for stream in streams):
        errors.append("Every ffprobe stream entry must be an object.")
        streams = [stream for stream in streams if isinstance(stream, dict)]

    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    if video is None:
        errors.append("No video stream found.")
    else:
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

    media_format = data.get("format")
    if not isinstance(media_format, dict):
        errors.append("ffprobe format must be an object.")
        media_format = {}
    try:
        duration = float(media_format.get("duration"))
    except (TypeError, ValueError):
        duration = -1.0
    if not math.isfinite(duration) or duration < min_duration or duration > max_duration:
        errors.append(f"Duration must be a finite value between {min_duration:g} and {max_duration:g} seconds.")
    return errors


def check_files(video_path: Path, thumbnail_path: Path,
                probe_data: dict[str, Any], require_audio: bool = False) -> list[str]:
    errors = validate_probe_data(probe_data, require_audio=require_audio)
    if not video_path.is_file() or video_path.stat().st_size == 0:
        errors.append("Video file is missing or empty.")
    if not thumbnail_path.is_file() or thumbnail_path.stat().st_size == 0:
        errors.append("Thumbnail file is missing or empty.")
    else:
        errors.extend(validate_png_file(thumbnail_path))
    return errors


def inspect(video_path: Path, thumbnail_path: Path, require_audio: bool = False) -> list[str]:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return ["ffprobe is not installed. Install FFmpeg/ffprobe before checking media."]
    if not video_path.is_file():
        return ["Video file is missing or empty."]
    try:
        result = subprocess.run(
            [ffprobe, "-v", "error", "-show_streams", "-show_format",
             "-of", "json", str(video_path)],
            check=True, capture_output=True, text=True, timeout=30,
        )
    except subprocess.TimeoutExpired:
        return ["ffprobe timed out while inspecting the video (30-second limit)."]
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "").strip()
        if len(detail) > 500:
            detail = detail[:500] + "..."
        return ["ffprobe could not inspect the video." + (f" Details: {detail}" if detail else "")]
    except OSError:
        return ["ffprobe could not be started. Check the FFmpeg installation."]
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return ["ffprobe returned invalid JSON."]
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
