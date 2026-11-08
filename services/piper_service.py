# src/services/piper_service.py
import os
import subprocess
import wave
import hashlib
from pathlib import Path

import imageio_ffmpeg

from piper.voice import PiperVoice
from manim_voiceover._typing import VoiceoverData
from manim_voiceover.services.base import SpeechService

from src.config import Config

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()


class PiperTTSService(SpeechService):

    def __init__(self, voice: str = "en_US-lessac-medium", **kwargs):
        super().__init__(**kwargs)

        model_path = os.path.join(Config.PIPER_MODELS_DIR, f"{voice}.onnx")

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Piper model '{voice}' not found at: {model_path}\n"
                f"Download with:\n"
                f"  python download_models.py --lang <code>"
            )

        # Try GPU, fall back to CPU silently
        try:
            self._voice = PiperVoice.load(model_path, use_cuda=True)
            print(f"[PiperTTS] '{voice}' loaded on GPU")
        except Exception:
            self._voice = PiperVoice.load(model_path, use_cuda=False)
            print(f"[PiperTTS] '{voice}' loaded on CPU")

        self._voice_name = voice

    def generate_from_text(
        self,
        text: str,
        cache_dir: str | os.PathLike[str] | None = None,
        path: str | os.PathLike[str] | None = None,
        **kwargs: object,
    ) -> VoiceoverData:

        # Use stable MD5 hash for caching — same text = same file, no re-synthesis
        hash_     = hashlib.md5(text.encode()).hexdigest()
        cache_dir = cache_dir or self.cache_dir
        Path(cache_dir).mkdir(parents=True, exist_ok=True)

        path = os.fspath(path) if path is not None else str(Path(cache_dir) / f"{hash_}.mp3")

        wav_path = Path(Config.OUTPUT_DIR) / "audio" / f"{hash_}.wav"
        wav_path.parent.mkdir(parents=True, exist_ok=True)

        with wave.open(str(wav_path), "wb") as wav_file:
            self._voice.synthesize_wav(text, wav_file)

        subprocess.run(
            [
                FFMPEG_EXE, "-y", "-i", str(wav_path),
                "-codec:a", "libmp3lame", "-q:a", "4", path,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Return basename only — Manim-Voiceover prepends cache_dir itself
        return {
            "original_audio": os.path.basename(path),
            "final_audio":    os.path.basename(path),
        }
