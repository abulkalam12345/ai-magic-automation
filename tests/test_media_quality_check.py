import importlib.util
import struct
import tempfile
import unittest
import zlib
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


def valid_png_header(width=1080, height=1920):
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    chunk_type_and_data = b"IHDR" + ihdr_data
    crc = zlib.crc32(chunk_type_and_data) & 0xFFFFFFFF
    return (b"\\x89PNG\\r\\n\\x1a\\n" + struct.pack(">I", 13)
            + chunk_type_and_data + struct.pack(">I", crc))


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

    def test_non_finite_duration_fails_closed(self):
        for duration in ("nan", "inf", "-inf"):
            with self.subTest(duration=duration):
                data = valid_probe()
                data["format"]["duration"] = duration
                errors = qc.validate_probe_data(data)
                self.assertTrue(any("finite value" in error for error in errors))

    def test_missing_video_stream_fails(self):
        self.assertTrue(qc.validate_probe_data({"streams": [], "format": {}}))

    def test_audio_is_optional_by_default(self):
        self.assertEqual(qc.validate_probe_data(valid_probe()), [])

    def test_required_audio_missing_fails(self):
        errors = qc.validate_probe_data(valid_probe(), require_audio=True)
        self.assertTrue(any("audio stream is required" in e for e in errors))

    def test_required_aac_audio_passes(self):
        data = valid_probe()
        data["streams"].append({"codec_type": "audio", "codec_name": "aac"})
        self.assertEqual(qc.validate_probe_data(data, require_audio=True), [])

    def test_required_non_aac_audio_fails(self):
        data = valid_probe()
        data["streams"].append({"codec_type": "audio", "codec_name": "mp3"})
        errors = qc.validate_probe_data(data, require_audio=True)
        self.assertTrue(any("AAC" in e for e in errors))

    def test_valid_png_ihdr_and_dimensions_pass(self):
        self.assertEqual(qc.validate_png_header(valid_png_header()), [])

    def test_png_wrong_dimensions_fail(self):
        errors = qc.validate_png_header(valid_png_header(width=720, height=1280))
        self.assertTrue(any("dimensions" in error for error in errors))

    def test_png_bad_ihdr_crc_fails(self):
        header = bytearray(valid_png_header())
        header[-1] ^= 0x01
        self.assertTrue(any("checksum" in error for error in qc.validate_png_header(bytes(header))))

    def test_png_truncated_ihdr_fails(self):
        self.assertTrue(any("truncated" in error for error in qc.validate_png_header(b"\\x89PNG")))

    def test_png_signature_only_is_rejected(self):
        header = b"\\x89PNG\\r\\n\\x1a\\n" + b"rest"
        self.assertTrue(qc.validate_png_header(header))

    def test_files_validate_png_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            video = root / "video.mp4"
            thumb = root / "thumb.png"
            video.write_bytes(b"video")
            thumb.write_bytes(b"not a png")
            errors = qc.check_files(video, thumb, valid_probe())
            self.assertTrue(any("PNG" in e for e in errors))
            thumb.write_bytes(valid_png_header() + b"rest")
            self.assertEqual(qc.check_files(video, thumb, valid_probe()), [])


if __name__ == "__main__":
    unittest.main()
