# src/languages.py
"""
Central language configuration for Imagio.
All per-language settings live here — TTS model, Manim font, LLM instruction.
"""

LANGUAGES: dict[str, dict] = {
    "en": {
        "name":            "English",
        "piper_model":     "en_US-lessac-medium",
        "manim_font":      "",               # empty = Manim default
        "llm_instruction": (
            "Generate ALL content in English."
        ),
    },
    "es": {
        "name":            "Español (Spanish)",
        "piper_model":     "es_ES-davefx-medium",
        "manim_font":      "",
        "llm_instruction": (
            "Generate ALL content in Spanish (Español). "
            "Every title, bullet point, narration, explanation, and annotation "
            "must be written in Spanish. Do NOT mix in English."
        ),
    },
    "fr": {
        "name":            "Français (French)",
        "piper_model":     "fr_FR-siwis-medium",
        "manim_font":      "",
        "llm_instruction": (
            "Generate ALL content in French (Français). "
            "Every title, bullet point, narration, explanation, and annotation "
            "must be written in French. Do NOT mix in English."
        ),
    },
    "hi": {
        "name":            "हिन्दी (Hindi)",
        "piper_model":     "hi_IN-priyamvada-medium",
        "manim_font":      "Nirmala UI",
        "llm_instruction": (
            "Generate ALL content in Hindi (हिन्दी) using Devanagari script. "
            "Every title, bullet point, narration, explanation, and annotation "
            "must be written in Hindi. Do NOT mix in English or use Roman transliteration."
        ),
    },
}

DEFAULT_LANG = "en"


def get_language(code: str) -> dict:
    """Returns config for the given language code; falls back to English."""
    return LANGUAGES.get(code, LANGUAGES[DEFAULT_LANG])


def list_languages() -> list[dict]:
    return [{"code": k, **v} for k, v in LANGUAGES.items()]
