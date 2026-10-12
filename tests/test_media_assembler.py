import importlib.util
import tempfile
import unittest
import subprocess
from unittest import mock
from pathlib import Path

MODULE = Path(__file__).parents[1] / "src" / "media_assembler.py"
SPEC = importlib.util.spec_from_file_location("media_assembler", MODULE)
media_assembler = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(media_assembler)

VALID_SRT = "1\n00:00:00,000 --> 00:00:02,000\nHello world\n"


class MediaAssemblerTests(unittest.TestCase):
    def test_command_has_vertical_format_and_watermark(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "input.mp4"
            source.write_bytes(b"placeholder")
            command = media_assembler.build_ffmpeg_command(source, root / "out.mp4", root / "thumb.png")
            joined = " ".join(command)
            self.assertIn("scale=1080:1920", joined)
            self.assertIn("WonderVexa", joined)
            self.assertIn("libx264", joined)
            self.assertIn("thumb.png", joined)
            self.assertNotIn("subtitles=", joined)

    def test_optional_audio_is_looped_mixed_quietly_and_faded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, audio = root / "input.mp4", root / "licensed-music.mp3"
            source.write_bytes(b"placeholder")
            audio.write_bytes(b"placeholder")
            command = media_assembler.build_ffmpeg_command(
                source, root / "out.mp4", root / "thumb.png", audio=audio
            )
            joined = " ".join(command)
            self.assertIn("-stream_loop -1 -i", joined)
            self.assertIn("volume=0.20,afade=t=out:st=59:d=1", joined)
            self.assertIn("-c:a aac", joined)
            self.assertNotIn("-an", command)

    def test_sequence_audio_is_trimmed_and_faded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = [root / "a.mp4", root / "b.mp4"]
            for source in sources:
                source.write_bytes(b"placeholder")
            audio = root / "licensed-music.mp3"
            audio.write_bytes(b"placeholder")
            command = media_assembler.build_sequence_ffmpeg_command(
                sources, root / "out.mp4", target_duration=10, audio=audio
            )
            graph = command[command.index("-filter_complex") + 1]
            self.assertIn("[2:a]atrim=duration=10", graph)
            self.assertIn("volume=0.20,afade=t=out:st=9:d=1[audio]", graph)
            self.assertIn("-map [audio]", " ".join(command))
            self.assertNotIn("-an", command)

    def test_missing_audio_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "input.mp4"
            source.write_bytes(b"placeholder")
            with self.assertRaises(FileNotFoundError):
                media_assembler.build_ffmpeg_command(
                    source, root / "out.mp4", root / "thumb.png", audio=root / "missing.mp3"
                )

    def test_optional_valid_srt_is_burned_into_video_and_thumbnail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, captions = root / "input.mp4", root / "captions.srt"
            source.write_bytes(b"placeholder")
            captions.write_text(VALID_SRT, encoding="utf-8")
            command = media_assembler.build_ffmpeg_command(
                source, root / "out.mp4", root / "thumb.png", captions=captions
            )
            joined = " ".join(command)
            self.assertEqual(joined.count("subtitles=filename='captions.srt'"), 2)
            self.assertIn("MarginV=260", joined)
            self.assertLess(joined.index("subtitles="), joined.index("drawtext="))

    def test_sequence_captions_are_applied_after_concat_and_before_watermark(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = [root / "a.mp4", root / "b.mp4"]
            for source in sources:
                source.write_bytes(b"placeholder")
            captions = root / "captions.srt"
            captions.write_text(VALID_SRT, encoding="utf-8")
            command = media_assembler.build_sequence_ffmpeg_command(
                sources, root / "out.mp4", captions=captions
            )
            graph = command[command.index("-filter_complex") + 1]
            self.assertIn("concat=n=2:v=1:a=0", graph)
            self.assertIn("subtitles=filename='captions.srt'", graph)
            self.assertLess(graph.index("subtitles="), graph.index("drawtext="))

    def test_missing_and_empty_captions_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "input.mp4"
            source.write_bytes(b"placeholder")
            with self.assertRaises(FileNotFoundError):
                media_assembler.build_ffmpeg_command(
                    source, root / "out.mp4", root / "thumb.png",
                    captions=root / "missing.srt",
                )
            empty = root / "empty.srt"
            empty.write_text("  ", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "empty"):
                media_assembler.build_ffmpeg_command(
                    source, root / "out.mp4", root / "thumb.png", captions=empty
                )

    def test_invalid_srt_timestamp_or_cue_text_rejected(self):
        invalid_examples = [
            "1\nnot-a-time --> 00:00:02,000\nHello",
            "1\n00:60:00,000 --> 00:01:02,000\nInvalid minutes",
            "1\n00:00:00,000 --> 00:00:99,000\nInvalid seconds",
            "1\n00:00:02,000 --> 00:00:01,000\nHello",
            "1\n00:00:00,000 --> 00:00:02,000\n   ",
            "1\n00:00:00,000 --> 00:00:02,000\nHello\n\n3\n00:00:03,000 --> 00:00:04,000\nWorld",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for number, content in enumerate(invalid_examples):
                captions = root / f"bad-{number}.srt"
                captions.write_text(content, encoding="utf-8")
                with self.subTest(content=content), self.assertRaises(ValueError):
                    media_assembler._validate_captions(captions)

    def test_valid_multiple_srt_cues_are_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            captions = Path(tmp) / "valid.srt"
            captions.write_text(
                "1\n00:00:00,000 --> 00:00:01,000\nFirst line\n\n"
                "2\n00:00:01,200 --> 00:00:02,000\nSecond line\n",
                encoding="utf-8",
            )
            media_assembler._validate_captions(captions)

    def test_overlapping_or_out_of_order_srt_cues_rejected(self):
        samples = [
            "1\n00:00:00,000 --> 00:00:02,000\nFirst\n\n"
            "2\n00:00:01,500 --> 00:00:03,000\nSecond",
            "2\n00:00:00,000 --> 00:00:01,000\nFirst",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for number, content in enumerate(samples):
                captions = root / f"bad-order-{number}.srt"
                captions.write_text(content, encoding="utf-8")
                with self.subTest(number=number), self.assertRaises(ValueError):
                    media_assembler._validate_captions(captions)

    def test_sequence_requires_multiple_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "one.mp4"
            source.write_bytes(b"placeholder")
            with self.assertRaisesRegex(ValueError, "at least two"):
                media_assembler.build_sequence_ffmpeg_command([source], Path("out.mp4"))

    def test_sequence_target_must_be_8_to_12_seconds(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = [root / "a.mp4", root / "b.mp4"]
            for source in sources:
                source.write_bytes(b"placeholder")
            for duration in (7, 13):
                with self.subTest(duration=duration):
                    with self.assertRaisesRegex(ValueError, "8 and 12"):
                        media_assembler.build_sequence_ffmpeg_command(
                            sources, root / "out.mp4", target_duration=duration
                        )

    def test_missing_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(FileNotFoundError):
                media_assembler.build_ffmpeg_command(
                    root / "missing.mp4", root / "out.mp4", root / "thumb.png"
                )


    def test_ffmpeg_timeout_removes_partial_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output, thumb = root / "out.mp4", root / "thumb.png"
            output.write_bytes(b"partial")
            thumb.write_bytes(b"partial")
            with mock.patch.object(media_assembler.subprocess, "run",
                                   side_effect=subprocess.TimeoutExpired("ffmpeg", 600)) as run:
                with self.assertRaisesRegex(RuntimeError, "10-minute"):
                    media_assembler._execute_ffmpeg(["ffmpeg"], None, [output, thumb])
            self.assertEqual(run.call_args.kwargs["timeout"], 600)
            self.assertFalse(output.exists())
            self.assertFalse(thumb.exists())

    def test_ffmpeg_failure_removes_partial_outputs_and_limits_error_detail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "out.mp4"
            output.write_bytes(b"partial")
            failure = subprocess.CalledProcessError(1, "ffmpeg", stderr="bad media")
            with mock.patch.object(media_assembler.subprocess, "run", side_effect=failure):
                with self.assertRaisesRegex(RuntimeError, "bad media"):
                    media_assembler._execute_ffmpeg(["ffmpeg"], None, [output])
            self.assertFalse(output.exists())

    def test_ffmpeg_start_error_is_reported_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out.mp4"
            output.write_bytes(b"partial")
            with mock.patch.object(media_assembler.subprocess, "run",
                                   side_effect=FileNotFoundError("ffmpeg")):
                with self.assertRaisesRegex(RuntimeError, "could not be started"):
                    media_assembler._execute_ffmpeg(["ffmpeg"], None, [output])
            self.assertFalse(output.exists())


    def test_single_clip_rejects_output_collisions_with_inputs_and_each_other(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, audio, captions = root / "input.mp4", root / "music.mp3", root / "captions.srt"
            source.write_bytes(b"placeholder")
            audio.write_bytes(b"placeholder")
            captions.write_text(VALID_SRT, encoding="utf-8")
            cases = [
                (source, root / "thumb.png", None, None),
                (root / "out.mp4", source, None, None),
                (captions, root / "thumb.png", captions, None),
                (root / "out.mp4", audio, None, audio),
                (root / "same.mp4", root / "same.mp4", None, None),
            ]
            for output, thumbnail, caption_input, audio_input in cases:
                with self.subTest(output=output, thumbnail=thumbnail), self.assertRaises(ValueError):
                    media_assembler.build_ffmpeg_command(
                        source, output, thumbnail, captions=caption_input, audio=audio_input
                    )

    def test_sequence_rejects_output_collision_with_source_and_thumbnail_collision_with_video(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = [root / "a.mp4", root / "b.mp4"]
            for source in sources:
                source.write_bytes(b"placeholder")
            with self.assertRaisesRegex(ValueError, "overwrite"):
                media_assembler.build_sequence_ffmpeg_command(sources, sources[0])
            with self.assertRaisesRegex(ValueError, "overwrite"):
                media_assembler.build_sequence_thumbnail_command(sources[0], sources[0])

    def test_sequence_rejects_output_equal_to_thumbnail_before_assembly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = [root / "a.mp4", root / "b.mp4"]
            for source in sources:
                source.write_bytes(b"placeholder")
            with self.assertRaisesRegex(ValueError, "different files"):
                media_assembler.assemble_sequence(sources, root / "same", root / "same")


if __name__ == "__main__":
    unittest.main()
