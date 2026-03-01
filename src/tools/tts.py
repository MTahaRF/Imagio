# src/tools/tts.py
import os
import wave
from src.config import Config
from src.languages import get_language

try:
    from piper import PiperVoice
    _PIPER_AVAILABLE = True
except ImportError:
    _PIPER_AVAILABLE = False


class TTSGenerator:
    """
    Standalone TTS used by the pipeline for pre-rendering audio.
    Pass lang_code to auto-select the correct Piper voice model.
    """

    def __init__(self, lang_code: str = "en", model_name: str | None = None):
        if not _PIPER_AVAILABLE:
            raise ImportError("piper-tts not installed.")

        lang_cfg   = get_language(lang_code)
        model_name = model_name or lang_cfg["piper_model"]
        model_path = os.path.join(Config.PIPER_MODELS_DIR, f"{model_name}.onnx")

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Piper model not found: {model_path}\n"
                f"Download with: python -m piper.download_voices {model_name}"
            )

        try:
            self._voice = PiperVoice.load(model_path, use_cuda=True)
            print(f"[TTSGenerator] Loaded '{model_name}' on GPU")
        except Exception:
            self._voice = PiperVoice.load(model_path, use_cuda=False)
            print(f"[TTSGenerator] Loaded '{model_name}' on CPU")

        self._audio_dir = os.path.join(Config.OUTPUT_DIR, "audio")
        os.makedirs(self._audio_dir, exist_ok=True)

    def generate(self, text: str, filename_id: str) -> str | None:
        if not text:
            print(f"⚠️  Empty text for {filename_id}")
            return None

        output_path = os.path.join(self._audio_dir, f"{filename_id}.wav")
        try:
            with wave.open(output_path, "wb") as wf:
                self._voice.synthesize_wav(text, wf)
            return output_path
        except Exception as e:
            print(f"❌ TTS error for {filename_id}: {e}")
            return None
