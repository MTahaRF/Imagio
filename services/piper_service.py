# src/services/piper_service.py
import os
import wave
import hashlib
from pathlib import Path

from piper.voice import PiperVoice
from pydub import AudioSegment
from manim_voiceover.services.base import SpeechService

from src.config import Config


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
        text:      str,
        cache_dir: str | None = None,
        path:      str | None = None,
        **kwargs,
    ) -> dict:

        # Use stable MD5 hash for caching — same text = same file, no re-synthesis
        hash_     = hashlib.md5(text.encode()).hexdigest()
        cache_dir = cache_dir or self.cache_dir
        Path(cache_dir).mkdir(parents=True, exist_ok=True)

        if path is None:
            path = str(Path(cache_dir) / f"{hash_}.mp3")

        wav_path = path.replace(".mp3", ".wav")

        # Synthesize WAV (piper sets sample rate / channels itself)
        wav_file = wave.open(wav_path, "wb")
        self._voice.synthesize_wav(text, wav_file)
        wav_file.close()

        # Convert to MP3 — Manim-Voiceover's get_duration() requires MP3
        AudioSegment.from_wav(wav_path).export(path, format="mp3")
        os.remove(wav_path)

        # Return basename only — Manim-Voiceover prepends cache_dir itself
        return {
            "original_audio": os.path.basename(path),
            "final_audio":    os.path.basename(path),
        }
