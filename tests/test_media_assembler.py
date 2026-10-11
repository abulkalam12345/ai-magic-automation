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

    def test_sequence_command_concatenates_in_order_and_adds_watermark(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first, second = root / "first.mp4", root / "second.mp4"
            first.write_bytes(b"placeholder")
            second.write_bytes(b"placeholder")
            command = media_assembler.build_sequence_ffmpeg_command(
                [first, second], root / "out.mp4", target_duration=10
            )
            joined = " ".join(command)
            self.assertEqual(command.count("-i"), 2)
            self.assertIn("concat=n=2:v=1:a=0", joined)
            self.assertIn("scale=1080:1920", joined)
            self.assertIn("WonderVexa", joined)
            self.assertIn("-t 10", joined)
            self.assertIn("-an", joined)

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
