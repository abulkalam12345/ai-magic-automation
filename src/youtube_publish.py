"""Fail-closed YouTube Data API uploader for approved WonderVexa MP4s.

Default behavior is a local dry-run. Uploading requires explicit runtime gates,
a valid OAuth token JSON secret, and an existing MP4. This module is not called
by the daily draft workflow.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
MAX_TITLE_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 5000
MAX_TAGS = 500


class PublishingBlocked(RuntimeError):
    """Raised when a publishing safety gate is not satisfied."""


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def require_upload_gates(*, public: bool = False) -> None:
    """Require separate opt-ins for any upload and for public visibility."""
    if not _truthy("PUBLISHING_ENABLED"):
        raise PublishingBlocked("PUBLISHING_ENABLED is not true.")
    if not _truthy("YOUTUBE_AUTOMATION_AUTHORIZED"):
        raise PublishingBlocked("YOUTUBE_AUTOMATION_AUTHORIZED is not true.")
    if public and not _truthy("YOUTUBE_PUBLIC_PUBLISHING_APPROVED"):
        raise PublishingBlocked(
            "Public upload is blocked; YOUTUBE_PUBLIC_PUBLISHING_APPROVED is not true."
        )


def load_metadata(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read valid metadata JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Metadata must be a JSON object.")
    if data.get("channel") != "WonderVexa":
        raise ValueError("Only WonderVexa metadata is accepted.")
    if data.get("status") != "draft":
        raise ValueError("Only a draft package can be considered by this adapter.")
    publishing = data.get("publishing")
    if not isinstance(publishing, dict) or publishing.get("enabled") is not False:
        raise ValueError("Draft metadata must keep publishing disabled.")
    for key in ("title", "description"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError(f"Metadata field {key!r} must be non-empty text.")
    if len(data["title"]) > MAX_TITLE_LENGTH:
        raise ValueError("YouTube title exceeds 100 characters.")
    if len(data["description"]) > MAX_DESCRIPTION_LENGTH:
        raise ValueError("YouTube description exceeds 5000 characters.")
    keywords = data.get("long_tail_keywords", [])
    hashtags = data.get("hashtags", [])
    if not isinstance(keywords, list) or not isinstance(hashtags, list):
        raise ValueError("Keywords and hashtags must be arrays.")
    tags = []
    for value in [*keywords, *hashtags]:
        if isinstance(value, str):
            tag = value.strip().lstrip("#")
            if tag and tag not in tags:
                tags.append(tag)
    if len(tags) > MAX_TAGS:
        raise ValueError("Combined tag count exceeds the configured safety limit.")
    data["_youtube_tags"] = tags
    return data


def validate_video(path: Path) -> None:
    if not path.is_file():
        raise ValueError(f"Video file does not exist: {path}")
    if path.suffix.lower() != ".mp4":
        raise ValueError("Only MP4 files are accepted.")
    if path.stat().st_size <= 0:
        raise ValueError("Video file is empty.")


def build_request_body(metadata: dict[str, Any], *, public: bool = False) -> dict[str, Any]:
    """Build YouTube API request body; privacy is private unless explicitly gated."""
    return {
        "snippet": {
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata.get("_youtube_tags", []),
            "categoryId": "22",
        },
        "status": {
            "privacyStatus": "public" if public else "private",
            "selfDeclaredMadeForKids": False,
        },
    }


def validate_upload_metadata(metadata: dict[str, Any]) -> None:
    """Re-check critical draft invariants at the upload boundary."""
    if not isinstance(metadata, dict):
        raise ValueError("Upload metadata must be an object.")
    if metadata.get("channel") != "WonderVexa":
        raise ValueError("Only WonderVexa metadata is accepted.")
    if metadata.get("status") != "draft":
        raise ValueError("Only draft metadata is accepted.")
    publishing = metadata.get("publishing")
    if not isinstance(publishing, dict) or publishing.get("enabled") is not False:
        raise ValueError("Draft metadata must keep publishing disabled.")
    title = metadata.get("title")
    description = metadata.get("description")
    if not isinstance(title, str) or not title.strip() or len(title) > MAX_TITLE_LENGTH:
        raise ValueError("Upload title must be non-empty and at most 100 characters.")
    if (not isinstance(description, str) or not description.strip()
            or len(description) > MAX_DESCRIPTION_LENGTH):
        raise ValueError("Upload description must be non-empty and at most 5000 characters.")
    tags = metadata.get("_youtube_tags", [])
    if (not isinstance(tags, list) or len(tags) > MAX_TAGS
            or any(not isinstance(tag, str) or not tag.strip() for tag in tags)):
        raise ValueError("Prepared YouTube tags must be a valid array of at most 500 strings.")


def upload_video(video_path: Path, metadata: dict[str, Any], *, public: bool = False) -> str:
    """Upload one MP4 using an OAuth authorized-user token supplied as a secret."""
    validate_video(video_path)
    validate_upload_metadata(metadata)
    require_upload_gates(public=public)
    token_json = os.environ.get("YOUTUBE_OAUTH_TOKEN_JSON", "")
    if not token_json:
        raise PublishingBlocked("YOUTUBE_OAUTH_TOKEN_JSON secret is missing.")

    try:
        token_info = json.loads(token_json)
    except json.JSONDecodeError as exc:
        raise PublishingBlocked("YOUTUBE_OAUTH_TOKEN_JSON is not valid JSON.") from exc
    if not isinstance(token_info, dict):
        raise PublishingBlocked("YOUTUBE_OAUTH_TOKEN_JSON must contain an object.")

    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError as exc:
        raise PublishingBlocked(
            "Install requirements-youtube.txt before using the YouTube adapter."
        ) from exc

    credentials = Credentials.from_authorized_user_info(token_info, scopes=SCOPES)
    service = build("youtube", "v3", credentials=credentials, cache_discovery=False)
    request = service.videos().insert(
        part="snippet,status",
        body=build_request_body(metadata, public=public),
        media_body=MediaFileUpload(str(video_path), mimetype="video/mp4",
                                   chunksize=8 * 1024 * 1024, resumable=True),
    )
    response = None
    while response is None:
        _, response = request.next_chunk()
    video_id = response.get("id") if isinstance(response, dict) else None
    if not video_id:
        raise RuntimeError("YouTube API returned no video ID.")
    return str(video_id)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", type=Path, required=True, help="Rendered MP4 path")
    parser.add_argument("--metadata", type=Path, required=True, help="Draft metadata.json")
    parser.add_argument("--upload", action="store_true",
                        help="Perform upload; without this flag only validate and dry-run.")
    parser.add_argument("--public", action="store_true",
                        help="Request public visibility; requires a separate public approval gate.")
    args = parser.parse_args()

    try:
        validate_video(args.video)
        metadata = load_metadata(args.metadata)
        if args.upload:
            require_upload_gates(public=args.public)
            video_id = upload_video(args.video, metadata, public=args.public)
            print(f"YouTube upload completed. Video ID: {video_id}")
            return 0

        print("DRY RUN ONLY — no upload attempted.")
        print(f"Video: {args.video} ({args.video.stat().st_size} bytes)")
        print(f"Title: {metadata['title']}")
        print(f"Tags prepared: {len(metadata['_youtube_tags'])}")
        print("Visibility on upload: " + ("public (separate gate required)" if args.public else "private"))
        return 0
    except (ValueError, PublishingBlocked, RuntimeError) as exc:
        print(f"YOUTUBE PUBLISH BLOCKED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
