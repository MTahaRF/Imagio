import os
import wave
import hashlib
from pathlib import Path
from piper.voice import PiperVoice
from pydub import AudioSegment
from manim_voiceover.services.base import SpeechService

class PiperTTSService(SpeechService):
    def __init__(self, model_path="voices/en_US-lessac-medium.onnx", **kwargs):
        self.voice = PiperVoice.load(model_path)
        super().__init__(**kwargs)

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        if path is None:
            hash_ = hashlib.md5(text.encode()).hexdigest()
            cache_dir = cache_dir or self.cache_dir
            Path(cache_dir).mkdir(parents=True, exist_ok=True)
            path = str(Path(cache_dir) / f"{hash_}.mp3")

        wav_path = path.replace(".mp3", ".wav")

        # Pass wave object — synthesize_wav sets format params itself
        wav_file = wave.open(wav_path, "wb")
        self.voice.synthesize_wav(text, wav_file)
        wav_file.close()

        AudioSegment.from_wav(wav_path).export(path, format="mp3")
        os.remove(wav_path)

        return {
            "original_audio": os.path.basename(path),
            "final_audio": os.path.basename(path),
        }
