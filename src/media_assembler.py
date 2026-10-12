"""Assemble WonderVexa shorts from already-generated, licensed source footage.

Requires FFmpeg with the subtitles/libass filter when --captions is supplied.
This module never generates footage, downloads assets, contacts a provider, or
publishes. Source media and caption text must be owned/licensed and reviewed.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


_CAPTION_FILTER = (
    "subtitles=filename='captions.srt':"
    "force_style='FontName=Arial,FontSize=22,Alignment=2,MarginV=260,Outline=2,Shadow=1'"
)


def _video_filter(include_watermark: bool = True, include_captions: bool = False) -> str:
    filters = [
        "scale=1080:1920:force_original_aspect_ratio=increase",
        "crop=1080:1920",
    ]
    if include_captions:
        filters.append(_CAPTION_FILTER)
    if include_watermark:
        filters.append(
            "drawtext=text='WonderVexa':fontcolor=white@0.82:fontsize=34:"
            "box=1:boxcolor=black@0.22:boxborderw=12:"
            "x=w-tw-64:y=h-th-100"
        )
    return ",".join(filters)


_SRT_CUE = re.compile(
    r"(?P<index>\d+)\s*\n"
    r"(?P<start>\d{2,}:\d{2}:\d{2},\d{3})\s+-->\s+"
    r"(?P<end>\d{2,}:\d{2}:\d{2},\d{3})\s*\n"
    r"(?P<text>.*?)(?=\n\s*\n|\Z)",
    re.DOTALL,
)


def _srt_milliseconds(timestamp: str) -> int:
    hours, minutes, remainder = timestamp.split(":")
    seconds, millis = remainder.split(",")
    hours_value, minutes_value = int(hours), int(minutes)
    seconds_value, millis_value = int(seconds), int(millis)
    if minutes_value > 59 or seconds_value > 59:
        raise ValueError("SRT minutes and seconds must be between 00 and 59")
    return (((hours_value * 60 + minutes_value) * 60) + seconds_value) * 1000 + millis_value


def _validate_captions(captions: Path | None) -> None:
    if captions is None:
        return
    if not captions.is_file():
        raise FileNotFoundError(f"Caption file not found: {captions}")
    try:
        content = captions.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("Caption file must be valid UTF-8") from exc
    content = content.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not content:
        raise ValueError("Caption file is empty")

    cues = []
    position = 0
    for match in _SRT_CUE.finditer(content):
        if content[position:match.start()].strip():
            raise ValueError("Invalid SRT structure before a caption cue")
        index = int(match.group("index"))
        start = _srt_milliseconds(match.group("start"))
        end = _srt_milliseconds(match.group("end"))
        cue_text = match.group("text").strip()
        if index < 1 or not cue_text:
            raise ValueError("Each SRT cue needs a positive index and non-empty text")
        if end <= start:
            raise ValueError("SRT cue end time must be later than its start time")
        cues.append((index, start, end))
        position = match.end()
    if not cues or content[position:].strip():
        raise ValueError("Invalid SRT file: expected numbered cues and timestamp lines")
    indexes = [cue[0] for cue in cues]
    if indexes != list(range(1, len(cues) + 1)):
        raise ValueError("SRT cue numbers must be sequential starting at 1")
    previous_end = -1
    for _, start, end in cues:
        if start < previous_end:
            raise ValueError("SRT cues must be chronological and must not overlap")
        previous_end = end


def build_ffmpeg_command(
    source: Path, output: Path, thumbnail: Path, ffmpeg: str = "ffmpeg",
    captions: Path | None = None, audio: Path | None = None,
) -> list[str]:
    if not source.is_file():
        raise FileNotFoundError(f"Source video not found: {source}")
    _validate_captions(captions)
    if audio is not None and not audio.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio}")
    output.parent.mkdir(parents=True, exist_ok=True)
    thumbnail.parent.mkdir(parents=True, exist_ok=True)
    command = [ffmpeg, "-y", "-i", str(source)]
    if audio is not None:
        command += ["-stream_loop", "-1", "-i", str(audio)]
    command += [
        "-vf", _video_filter(include_captions=captions is not None), "-t", "60",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
    ]
    if audio is None:
        command += ["-an"]
    else:
        command += [
            "-map", "0:v:0", "-map", "1:a:0",
            "-af", "volume=0.20,afade=t=out:st=59:d=1",
            "-c:a", "aac", "-b:a", "192k", "-shortest",
        ]
    command += [
        str(output),
        "-ss", "1", "-i", str(source), "-frames:v", "1",
        "-vf", _video_filter(include_watermark=False, include_captions=captions is not None),
        str(thumbnail),
    ]
    return command


def build_sequence_ffmpeg_command(
    sources: list[Path], output: Path, target_duration: int = 10, ffmpeg: str = "ffmpeg",
    captions: Path | None = None, audio: Path | None = None,
) -> list[str]:
    """Concatenate 2+ silent clips into an 8–12 second vertical short."""
    if len(sources) < 2:
        raise ValueError("A clip sequence requires at least two source videos")
    if not 8 <= target_duration <= 12:
        raise ValueError("Target duration must be between 8 and 12 seconds")
    for source in sources:
        if not source.is_file():
            raise FileNotFoundError(f"Source video not found: {source}")
    _validate_captions(captions)
    if audio is not None and not audio.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio}")

    output.parent.mkdir(parents=True, exist_ok=True)
    inputs = [part for source in sources for part in ("-i", str(source))]
    if audio is not None:
        inputs += ["-stream_loop", "-1", "-i", str(audio)]
    chains = []
    labels = []
    for index in range(len(sources)):
        label = f"clip{index}"
        chains.append(
            f"[{index}:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,fps=30,format=yuv420p,setsar=1,setpts=PTS-STARTPTS[{label}]"
        )
        labels.append(f"[{label}]")
    concat = "".join(labels) + f"concat=n={len(sources)}:v=1:a=0,{_video_filter(include_captions=captions is not None)}[final]"
    filter_parts = chains + [concat]
    if audio is not None:
        audio_index = len(sources)
        filter_parts.append(
            f"[{audio_index}:a]atrim=duration={target_duration},asetpts=PTS-STARTPTS,"
            f"volume=0.20,afade=t=out:st={target_duration - 1}:d=1[audio]"
        )
    filter_complex = ";".join(filter_parts)
    command = [
        ffmpeg, "-y", *inputs, "-filter_complex", filter_complex,
        "-map", "[final]", "-t", str(target_duration),
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
    ]
    if audio is None:
        command += ["-an"]
    else:
        command += ["-map", "[audio]", "-c:a", "aac", "-b:a", "192k", "-shortest"]
    command += [str(output)]
    return command


def build_sequence_thumbnail_command(
    video: Path, thumbnail: Path, ffmpeg: str = "ffmpeg",
    captions: Path | None = None,
) -> list[str]:
    if not video.is_file():
        raise FileNotFoundError(f"Assembled video not found: {video}")
    _validate_captions(captions)
    thumbnail.parent.mkdir(parents=True, exist_ok=True)
    filters = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
    if captions is not None:
        filters += "," + _CAPTION_FILTER
    return [
        ffmpeg, "-y", "-ss", "1", "-i", str(video), "-frames:v", "1",
        "-vf", filters, str(thumbnail),
    ]


def _execute_ffmpeg(command: list[str], cwd: str | None, outputs: list[Path]) -> None:
    """Run FFmpeg with a hard timeout and remove incomplete deliverables on failure."""
    try:
        subprocess.run(command, check=True, cwd=cwd, timeout=600)
    except subprocess.TimeoutExpired as exc:
        for path in outputs:
            path.unlink(missing_ok=True)
        raise RuntimeError("FFmpeg exceeded the 10-minute processing limit.") from exc
    except subprocess.CalledProcessError as exc:
        for path in outputs:
            path.unlink(missing_ok=True)
        detail = (exc.stderr or "").strip() if isinstance(exc.stderr, str) else ""
        if len(detail) > 500:
            detail = detail[:500] + "..."
        message = "FFmpeg failed to assemble the media."
        if detail:
            message += f" Details: {detail}"
        raise RuntimeError(message) from exc
    except OSError as exc:
        for path in outputs:
            path.unlink(missing_ok=True)
        raise RuntimeError("FFmpeg could not be started; check the FFmpeg installation.") from exc


def _run_with_captions(captions: Path | None, output: Path, run) -> None:
    """Run FFmpeg in a temporary safe-named caption directory (no shell parsing)."""
    if captions is None:
        run(None, output.resolve())
        return
    _validate_captions(captions)
    with tempfile.TemporaryDirectory(prefix="wondervexa-captions-") as temp:
        workdir = Path(temp)
        shutil.copyfile(captions, workdir / "captions.srt")
        run(workdir, output.resolve())


def assemble_sequence(
    sources: list[Path], output: Path, thumbnail: Path, target_duration: int = 10,
    captions: Path | None = None, audio: Path | None = None,
) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is not installed. Install FFmpeg before assembling.")

    def run(workdir: Path | None, resolved_output: Path) -> None:
        resolved_sources = [source.resolve() for source in sources]
        resolved_thumbnail = thumbnail.resolve()
        command = build_sequence_ffmpeg_command(
            resolved_sources, resolved_output, target_duration, ffmpeg,
            (workdir / "captions.srt") if workdir else None, audio.resolve() if audio else None,
        )
        _execute_ffmpeg(command, str(workdir) if workdir else None, [resolved_output, resolved_thumbnail])
        thumb_command = build_sequence_thumbnail_command(
            resolved_output, resolved_thumbnail, ffmpeg,
            (workdir / "captions.srt") if workdir else None,
        )
        _execute_ffmpeg(thumb_command, str(workdir) if workdir else None, [resolved_thumbnail])

    _run_with_captions(captions, output, run)


def assemble(
    source: Path, output: Path, thumbnail: Path, captions: Path | None = None,
    audio: Path | None = None,
) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is not installed. Install FFmpeg before assembling.")

    def run(workdir: Path | None, resolved_output: Path) -> None:
        resolved_source = source.resolve()
        resolved_thumbnail = thumbnail.resolve()
        command = build_ffmpeg_command(
            resolved_source, resolved_output, resolved_thumbnail, ffmpeg,
            (workdir / "captions.srt") if workdir else None, audio.resolve() if audio else None,
        )
        _execute_ffmpeg(command, str(workdir) if workdir else None, [resolved_output, resolved_thumbnail])

    _run_with_captions(captions, output, run)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, nargs="+", type=Path,
                        help="One source clip, or 2+ clips to concatenate in the supplied order")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--thumbnail", required=True, type=Path)
    parser.add_argument("--captions", type=Path,
                        help="Optional UTF-8 SRT file to burn into the video and thumbnail")
    parser.add_argument("--audio", type=Path,
                        help="Optional user-supplied, licensed music/audio file; looped and mixed at 20%")
    parser.add_argument("--target-duration", type=int, default=10,
                        help="Sequence target in seconds (8–12; default 10)")
    args = parser.parse_args()
    if len(args.input) == 1:
        assemble(args.input[0], args.output, args.thumbnail, args.captions, args.audio)
    else:
        assemble_sequence(args.input, args.output, args.thumbnail, args.target_duration, args.captions, args.audio)
    print(f"Created video: {args.output}")
    print(f"Created thumbnail: {args.thumbnail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
