import importlib.util
import struct
import tempfile
import unittest
from unittest import mock
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
    return (b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13)
            + chunk_type_and_data + struct.pack(">I", crc))


def png_chunk(kind, data):
    crc = zlib.crc32(kind + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", crc)


def valid_png_file():
    ihdr_data = struct.pack(">IIBBBBB", 1080, 1920, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", ihdr_data)
            + png_chunk(b"IDAT", b"placeholder") + png_chunk(b"IEND", b""))


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

    def test_malformed_top_level_probe_data_fails_cleanly(self):
        self.assertTrue(any("top-level object" in error
                            for error in qc.validate_probe_data(["not", "an", "object"])))

    def test_missing_or_wrong_stream_list_fails_cleanly(self):
        for streams in (None, {}, "video", 3):
            with self.subTest(streams=streams):
                errors = qc.validate_probe_data({"streams": streams, "format": {"duration": "10"}})
                self.assertTrue(any("streams must be a list" in error for error in errors))

    def test_non_object_stream_entry_fails_cleanly(self):
        errors = qc.validate_probe_data({
            "streams": [None, {"codec_type": "video", "codec_name": "h264",
                               "width": 1080, "height": 1920, "pix_fmt": "yuv420p"}],
            "format": {"duration": "10"},
        })
        self.assertTrue(any("stream entry must be an object" in error for error in errors))

    def test_missing_or_wrong_format_object_fails_cleanly(self):
        for media_format in (None, [], "format"):
            with self.subTest(media_format=media_format):
                errors = qc.validate_probe_data({"streams": [], "format": media_format})
                self.assertTrue(any("format must be an object" in error for error in errors))
                self.assertTrue(any("finite value" in error for error in errors))

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
        self.assertTrue(any("truncated" in error for error in qc.validate_png_header(b"\x89PNG")))

    def test_png_signature_only_is_rejected(self):
        header = b"\x89PNG\r\n\x1a\n" + b"rest"
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
            thumb.write_bytes(valid_png_file())
            self.assertEqual(qc.check_files(video, thumb, valid_probe()), [])
            thumb.write_bytes(valid_png_file() + b"trailing")
            self.assertTrue(any("trailing data" in e
                                for e in qc.check_files(video, thumb, valid_probe())))


    def test_png_file_requires_iend(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "thumb.png"
            path.write_bytes(valid_png_file()[:-12])
            self.assertTrue(any("IEND" in error for error in qc.validate_png_file(path)))

    def test_png_file_checks_idat_crc(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "thumb.png"
            broken = bytearray(valid_png_file())
            broken[-13] ^= 0x01
            path.write_bytes(broken)
            self.assertTrue(any("checksum" in error for error in qc.validate_png_file(path)))

    def test_png_file_rejects_missing_idat(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "thumb.png"
            ihdr_data = struct.pack(">IIBBBBB", 1080, 1920, 8, 6, 0, 0, 0)
            path.write_bytes(b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", ihdr_data)
                             + png_chunk(b"IEND", b""))
            self.assertTrue(qc.validate_png_file(path))


    def test_inspect_reports_missing_ffprobe_without_raising(self):
        with mock.patch.object(qc.shutil, "which", return_value=None):
            errors = qc.inspect(Path("video.mp4"), Path("thumb.png"))
        self.assertTrue(any("ffprobe is not installed" in error for error in errors))

    def test_inspect_reports_ffprobe_timeout(self):
        with tempfile.TemporaryDirectory() as tmp:
            video = Path(tmp) / "video.mp4"
            video.write_bytes(b"video")
            with mock.patch.object(qc.shutil, "which", return_value="/usr/bin/ffprobe"), \
                 mock.patch.object(qc.subprocess, "run", side_effect=__import__("subprocess").TimeoutExpired("ffprobe", 30)) as run:
                errors = qc.inspect(video, Path(tmp) / "thumb.png")
        self.assertTrue(any("timed out" in error for error in errors))
        self.assertEqual(run.call_args.kwargs["timeout"], 30)

    def test_inspect_reports_ffprobe_nonzero_exit(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            video = Path(tmp) / "video.mp4"
            video.write_bytes(b"video")
            failure = subprocess.CalledProcessError(1, "ffprobe", stderr="invalid container")
            with mock.patch.object(qc.shutil, "which", return_value="/usr/bin/ffprobe"), \
                 mock.patch.object(qc.subprocess, "run", side_effect=failure):
                errors = qc.inspect(video, Path(tmp) / "thumb.png")
        self.assertTrue(any("invalid container" in error for error in errors))

    def test_inspect_reports_invalid_ffprobe_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            video = Path(tmp) / "video.mp4"
            video.write_bytes(b"video")
            completed = __import__("subprocess").CompletedProcess([], 0, stdout="{", stderr="")
            with mock.patch.object(qc.shutil, "which", return_value="/usr/bin/ffprobe"), \
                 mock.patch.object(qc.subprocess, "run", return_value=completed):
                errors = qc.inspect(video, Path(tmp) / "thumb.png")
        self.assertTrue(any("invalid JSON" in error for error in errors))


    def test_png_rejects_invalid_ihdr_encoding_fields(self):
        cases = [
            (8, 1, 0, 0, 0),
            (8, 6, 1, 0, 0),
            (8, 6, 0, 1, 0),
            (8, 6, 0, 0, 2),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "thumb.png"
            for bit_depth, color_type, compression, filtering, interlace in cases:
                with self.subTest(case=(bit_depth, color_type, compression, filtering, interlace)):
                    ihdr = struct.pack(">IIBBBBB", 1080, 1920, bit_depth, color_type,
                                       compression, filtering, interlace)
                    path.write_bytes(b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", ihdr)
                                     + png_chunk(b"IDAT", b"x") + png_chunk(b"IEND", b""))
                    self.assertTrue(any("bit-depth" in error or "compression" in error
                                        for error in qc.validate_png_file(path)))

    def test_png_indexed_color_requires_palette(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "thumb.png"
            ihdr = struct.pack(">IIBBBBB", 1080, 1920, 8, 3, 0, 0, 0)
            path.write_bytes(b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", ihdr)
                             + png_chunk(b"IDAT", b"x") + png_chunk(b"IEND", b""))
            self.assertTrue(any("PLTE" in error for error in qc.validate_png_file(path)))

    def test_png_rejects_palette_for_grayscale_and_oversized_indexed_palette(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "thumb.png"
            gray = struct.pack(">IIBBBBB", 1080, 1920, 8, 0, 0, 0, 0)
            path.write_bytes(b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", gray)
                             + png_chunk(b"PLTE", b"\x00\x00\x00")
                             + png_chunk(b"IDAT", b"x") + png_chunk(b"IEND", b""))
            self.assertTrue(any("PLTE" in error for error in qc.validate_png_file(path)))

            indexed = struct.pack(">IIBBBBB", 1080, 1920, 1, 3, 0, 0, 0)
            path.write_bytes(b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", indexed)
                             + png_chunk(b"PLTE", b"\x00\x00\x00" * 3)
                             + png_chunk(b"IDAT", b"x") + png_chunk(b"IEND", b""))
            self.assertTrue(any("palette" in error for error in qc.validate_png_file(path)))



    def test_reserved_chunk_type_bit(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "thumb.png"
            ihdr = struct.pack(">IIBBBBB", 1080, 1920, 8, 6, 0, 0, 0)
            signature = bytes([137, 80, 78, 71, 13, 10, 26, 10])
            path.write_bytes(signature + png_chunk(b"IHDR", ihdr)
                             + png_chunk(b"IDAt", b"x") + png_chunk(b"IEND", b""))
            self.assertEqual(qc.validate_png_file(path), ["Thumbnail PNG chunk type uses the reserved lowercase bit."])


if __name__ == "__main__":
    unittest.main()
