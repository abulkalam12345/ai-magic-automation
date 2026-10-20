"""Validate SubRip subtitle structure and cue timing without external services."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

TIMESTAMP = re.compile(
    r"^(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> "
    r"(\d{2}):(\d{2}):(\d{2}),(\d{3})$"
)


def to_milliseconds(parts: tuple[str, ...]) -> int:
    hours, minutes, seconds, millis = map(int, parts)
    if minutes > 59 or seconds > 59:
        raise ValueError("minutes and seconds must be between 00 and 59")
    return ((hours * 60 + minutes) * 60 + seconds) * 1000 + millis


def validate_srt(source: Path | str) -> list[str]:
    """Accept a Path, a filename, or literal SRT text."""
    if isinstance(source, Path):
        try:
            content = source.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            return [f"cannot read UTF-8 subtitle file: {exc}"]
    elif "\n" in source or "\r" in source:
        content = source
    else:
        try:
            content = Path(source).read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            return [f"cannot read UTF-8 subtitle file: {exc}"]

    if not content.strip():
        return ["subtitle file is empty"]

    blocks = re.split(r"\r?\n\s*\r?\n", content.strip())
    errors: list[str] = []
    previous_end = -1
    for block_number, block in enumerate(blocks, start=1):
        lines = block.splitlines()
        if len(lines) < 2:
            errors.append(f"cue {block_number}: expected index and timestamp")
            continue
        if lines[0].strip() != str(block_number):
            errors.append(f"cue {block_number}: cue index must be {block_number}")
        match = TIMESTAMP.fullmatch(lines[1].strip())
        if not match:
            errors.append(f"cue {block_number}: invalid timestamp line")
            continue
        try:
            start = to_milliseconds(match.groups()[:4])
            end = to_milliseconds(match.groups()[4:])
        except ValueError as exc:
            errors.append(f"cue {block_number}: {exc}")
            continue
        if end <= start:
            errors.append(f"cue {block_number}: end time must be after start time")
        if start < previous_end:
            errors.append(f"cue {block_number}: overlaps or precedes the previous cue")
        if not any(line.strip() for line in lines[2:]):
            errors.append(f"cue {block_number}: subtitle text is empty")
        previous_end = max(previous_end, end)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("srt", type=Path)
    args = parser.parse_args()
    errors = validate_srt(args.srt)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"SRT structure and timing checks passed: {args.srt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
