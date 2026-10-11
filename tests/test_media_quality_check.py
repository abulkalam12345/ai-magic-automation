import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).parents[1] / "src" / "media_quality_check.py"
SPEC = importlib.util.spec_from_file_location("media_quality_check", MODULE)
qc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(qc)


def valid_probe():
    return {
        "streams": [{
            "codec_type": "video", "codec_name": "h264",
            "width": 1080, "height": 1920, "pix_fmt": "yuv420p",
        }],
        "format": {"duration": "10.0"},
    }


class MediaQualityTests(unittest.TestCase):
    def test_valid_vertical_export_passes(self):
        self.assertEqual(qc.validate_probe_data(valid_probe()), [])

    def test_wrong_dimensions_and_codec_fail(self):
        data = valid_probe()
        data["streams"][0]["width"] = 1920
        data["streams"][0]["codec_name"] = "vp9"
        errors = qc.validate_probe_data(data)
        self.assertTrue(any("dimensions" in e for e in errors))
        self.assertTrue(any("H.264" in e for e in errors))

    def test_duration_out_of_range_fails(self):
        data = valid_probe()
        data["format"]["duration"] = "4.2"
        self.assertTrue(any("Duration" in e for e in qc.validate_probe_data(data)))

    def test_missing_video_stream_fails(self):
        self.assertTrue(qc.validate_probe_data({"streams": [], "format": {}}))

    def test_files_and_png_signature_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            video = root / "video.mp4"
            thumb = root / "thumb.png"
            video.write_bytes(b"video")
            thumb.write_bytes(b"not a png")
            errors = qc.check_files(video, thumb, valid_probe())
            self.assertTrue(any("valid PNG" in e for e in errors))
            thumb.write_bytes(b"\x89PNG\r\n\x1a\nrest")
            self.assertEqual(qc.check_files(video, thumb, valid_probe()), [])


if __name__ == "__main__":
    unittest.main()
