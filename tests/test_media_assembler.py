import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).parents[1] / "src" / "media_assembler.py"
SPEC = importlib.util.spec_from_file_location("media_assembler", MODULE)
media_assembler = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(media_assembler)


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

    def test_optional_srt_is_burned_into_video_and_thumbnail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, captions = root / "input.mp4", root / "captions.srt"
            source.write_bytes(b"placeholder")
            captions.write_text("caption sample", encoding="utf-8")
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
            captions.write_text("caption sample", encoding="utf-8")
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


if __name__ == "__main__":
    unittest.main()
