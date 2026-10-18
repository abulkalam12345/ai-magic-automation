"""Safety and metadata tests for the YouTube publishing adapter."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.youtube_publish import (
    PublishingBlocked,
    build_request_body,
    load_metadata,
    require_upload_gates,
    upload_video,
    validate_video,
)


class YouTubePublishTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.metadata_path = self.root / "metadata.json"
        self.metadata = {
            "channel": "WonderVexa",
            "status": "draft",
            "title": "Moonlit Seed ✨ | WonderVexa #Shorts",
            "description": "An original magical story.",
            "long_tail_keywords": ["magical flower short", "fantasy story"],
            "hashtags": ["#WonderVexa", "#Shorts"],
            "publishing": {"enabled": False},
        }
        self.metadata_path.write_text(json.dumps(self.metadata), encoding="utf-8")
        self.video_path = self.root / "sample.mp4"
        self.video_path.write_bytes(b"test-mp4-placeholder")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_metadata_loads_and_combines_tags(self) -> None:
        loaded = load_metadata(self.metadata_path)
        self.assertEqual(
            loaded["_youtube_tags"],
            ["magical flower short", "fantasy story", "WonderVexa", "Shorts"],
        )

    def test_rejects_non_wondervexa_package(self) -> None:
        bad = dict(self.metadata, channel="OtherChannel")
        self.metadata_path.write_text(json.dumps(bad), encoding="utf-8")
        with self.assertRaises(ValueError):
            load_metadata(self.metadata_path)

    def test_rejects_enabled_draft_metadata(self) -> None:
        bad = dict(self.metadata, publishing={"enabled": True})
        self.metadata_path.write_text(json.dumps(bad), encoding="utf-8")
        with self.assertRaises(ValueError):
            load_metadata(self.metadata_path)

    def test_rejects_malformed_publishing_metadata(self) -> None:
        for value in (None, [], "disabled", True):
            with self.subTest(value=value):
                bad = dict(self.metadata, publishing=value)
                self.metadata_path.write_text(json.dumps(bad), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_metadata(self.metadata_path)

    def test_rejects_long_title(self) -> None:
        bad = dict(self.metadata, title="x" * 101)
        self.metadata_path.write_text(json.dumps(bad), encoding="utf-8")
        with self.assertRaises(ValueError):
            load_metadata(self.metadata_path)

    def test_video_must_be_nonempty_mp4(self) -> None:
        validate_video(self.video_path)
        wrong = self.root / "video.mov"
        wrong.write_bytes(b"x")
        with self.assertRaises(ValueError):
            validate_video(wrong)

    def test_upload_blocked_by_default(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(PublishingBlocked):
                require_upload_gates()

    def test_public_upload_needs_separate_gate(self) -> None:
        env = {
            "PUBLISHING_ENABLED": "true",
            "YOUTUBE_AUTOMATION_AUTHORIZED": "true",
        }
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(PublishingBlocked):
                require_upload_gates(public=True)

    def test_upload_boundary_rejects_non_draft_even_when_called_directly(self) -> None:
        env = {
            "PUBLISHING_ENABLED": "true",
            "YOUTUBE_AUTOMATION_AUTHORIZED": "true",
        }
        bad = dict(self.metadata, status="ready")
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ValueError):
                upload_video(self.video_path, bad)

    def test_upload_boundary_validates_mp4_before_authentication(self) -> None:
        env = {
            "PUBLISHING_ENABLED": "true",
            "YOUTUBE_AUTOMATION_AUTHORIZED": "true",
        }
        missing = self.root / "missing.mp4"
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ValueError):
                upload_video(missing, self.metadata)

    def test_private_is_default(self) -> None:
        loaded = load_metadata(self.metadata_path)
        self.assertEqual(build_request_body(loaded)["status"]["privacyStatus"], "private")

    def test_public_request_is_explicit(self) -> None:
        loaded = load_metadata(self.metadata_path)
        self.assertEqual(build_request_body(loaded, public=True)["status"]["privacyStatus"], "public")


if __name__ == "__main__":
    unittest.main()
