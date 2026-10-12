"""Optional real-FFmpeg smoke tests for single and sequence assembly.

These tests skip when FFmpeg/ffprobe are unavailable. They generate only tiny
synthetic test media in temporary directories; no external assets or services.
"""
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
MODULE = ROOT / "src" / "media_assembler.py"
SPEC = importlib.util.spec_from_file_location("media_assembler_integration", MODULE)
assembler = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(assembler)

FFMPEG = shutil.which("ffmpeg")
FFPROBE = shutil.which("ffprobe")


@unittest.skipUnless(FFMPEG and FFPROBE, "FFmpeg and ffprobe are required for media smoke tests")
class MediaAssemblerIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.audio = self.root / "tone.wav"
        subprocess.run([
            FFMPEG, "-v", "error", "-y", "-f", "lavfi",
            "-i", "sine=frequency=440:duration=1", str(self.audio),
        ], check=True)

    def tearDown(self):
        self.temp.cleanup()

    def make_video(self, path: Path, duration: int):
        subprocess.run([
            FFMPEG, "-v", "error", "-y", "-f", "lavfi",
            "-i", f"color=c=blue:s=320x240:r=30:d={duration}",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path),
        ], check=True)

    def probe(self, path: Path):
        result = subprocess.run([
            FFPROBE, "-v", "error", "-show_streams", "-show_format",
            "-of", "json", str(path),
        ], check=True, capture_output=True, text=True)
        return json.loads(result.stdout)

    def assert_vertical_aac_export(self, video: Path):
        data = self.probe(video)
        streams = data["streams"]
        picture = next(s for s in streams if s["codec_type"] == "video")
        sound = next(s for s in streams if s["codec_type"] == "audio")
        self.assertEqual(picture["codec_name"], "h264")
        self.assertEqual((picture["width"], picture["height"]), (1080, 1920))
        self.assertEqual(picture["pix_fmt"], "yuv420p")
        self.assertEqual(sound["codec_name"], "aac")
        self.assertGreater(float(data["format"]["duration"]), 7.5)

    def test_single_clip_audio_render_and_thumbnail(self):
        source = self.root / "source.mp4"
        output = self.root / "single.mp4"
        thumbnail = self.root / "single.png"
        self.make_video(source, 8)
        assembler.assemble(source, output, thumbnail, audio=self.audio)
        self.assert_vertical_aac_export(output)
        self.assertEqual(thumbnail.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

    def test_sequence_audio_render_and_thumbnail(self):
        first = self.root / "first.mp4"
        second = self.root / "second.mp4"
        output = self.root / "sequence.mp4"
        thumbnail = self.root / "sequence.png"
        self.make_video(first, 4)
        self.make_video(second, 4)
        assembler.assemble_sequence(
            [first, second], output, thumbnail, target_duration=8, audio=self.audio,
        )
        self.assert_vertical_aac_export(output)
        self.assertEqual(thumbnail.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")


if __name__ == "__main__":
    unittest.main()
