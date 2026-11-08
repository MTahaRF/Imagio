"""Focused test for Piper speech synthesis and MP3 conversion."""

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from imageio_ffmpeg import get_ffmpeg_exe
from manim_voiceover.modify_audio import get_duration
from services.piper_service import PiperTTSService
from src.config import Config


class PiperAudioGenerationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.service = PiperTTSService(
            voice="en_US-lessac-medium",
            cache_dir=cls.temp_dir.name,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp_dir.cleanup()

    def test_generates_decodable_audible_mp3(self) -> None:
        with tempfile.TemporaryDirectory() as output_dir:
            with patch.object(Config, "OUTPUT_DIR", output_dir):
                result = self.service.generate_from_text(
                    "This is a short test of Piper voice generation.",
                    cache_dir=self.temp_dir.name,
                )

            original_audio = result.get("original_audio")
            final_audio = result.get("final_audio")
            self.assertIsInstance(original_audio, str)
            self.assertIsInstance(final_audio, str)
            assert isinstance(original_audio, str)
            assert isinstance(final_audio, str)

            wav_path = Path(output_dir, "audio", f"{Path(original_audio).stem}.wav")
            mp3_path = Path(self.temp_dir.name, final_audio)
            self.assertTrue(wav_path.is_file(), f"WAV file was not created: {wav_path}")
            self.assertTrue(mp3_path.is_file(), f"Voiceover MP3 was not created: {mp3_path}")
            self.assertGreater(wav_path.stat().st_size, 0)
            self.assertGreater(mp3_path.stat().st_size, 0)
            self.assertGreater(get_duration(wav_path), 0, "Generated WAV has no duration")

            probe = subprocess.run(
                [
                    get_ffmpeg_exe(), "-hide_banner", "-i", str(wav_path),
                    "-af", "volumedetect", "-f", "null", "NUL",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            match = re.search(r"mean_volume:\s*(-?[\d.]+)\s*dB", probe.stderr)
            self.assertIsNotNone(match, "FFmpeg did not report the generated WAV audio level")
            assert match is not None
            self.assertGreater(float(match.group(1)), -50, "Generated WAV is silent or too quiet")


if __name__ == "__main__":
    unittest.main()
