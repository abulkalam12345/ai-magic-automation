import tempfile
import unittest
from pathlib import Path

from media_assembler import build_ffmpeg_command


class MediaAssemblerTests(unittest.TestCase):
    def test_command_has_vertical_format_and_watermark(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "input.mp4"
            source.write_bytes(b"placeholder")
            command = build_ffmpeg_command(source, root / "out.mp4", root / "thumb.png")
            joined = " ".join(command)
            self.assertIn("scale=1080:1920", joined)
            self.assertIn("WonderVexa", joined)
            self.assertIn("libx264", joined)
            self.assertIn("thumb.png", joined)

    def test_missing_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(FileNotFoundError):
                build_ffmpeg_command(root / "missing.mp4", root / "out.mp4", root / "thumb.png")


if __name__ == "__main__":
    unittest.main()
