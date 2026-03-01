from abc import ABC, abstractmethod
from src.languages import get_language, DEFAULT_LANG

class BaseTemplate(ABC):
    def __init__(self):
        self._lang_code:   str  = DEFAULT_LANG
        self._lang_config: dict = get_language(DEFAULT_LANG)

    # ── Language API ──────────────────────────────────────────────

    def set_language(self, lang_code: str) -> None:
        """Call before code() to set target language."""
        self._lang_code   = lang_code
        self._lang_config = get_language(lang_code)

    def _piper_model(self) -> str:
        return self._lang_config.get("piper_model", "en_US-lessac-medium")

    def _manim_font(self) -> str:
        return self._lang_config.get("manim_font", "")
    
    # ── Abstract interface ────────────────────────────────────────

    @abstractmethod
    def description(self) -> str:
        """Tells the planner WHEN to use this template."""

    @abstractmethod
    def schema(self) -> dict:
        """JSON schema the LLM must fill for template_data."""

    @abstractmethod
    def prompt(self) -> str:
        """One-line instruction to the SceneDirector."""

    @abstractmethod
    def _scene_body(self, data: dict, script: str) -> str:
        """
        Returns ONLY the indented animation lines inside construct().
        No imports, no class def, no voiceover setup — base handles all that.
        Use: with self.voiceover(text="{script}") as tracker:
        """

    @staticmethod
    def _title_font_size(title: str) -> int:
        n = len(title)
        if n <= 18:   return 52
        elif n <= 30: return 44
        elif n <= 42: return 38
        elif n <= 55: return 32
        else:         return 27

    @staticmethod
    def _auto_font_size(text: str) -> int:
        n = len(text)
        if n <= 30:   return 30
        elif n <= 50: return 26
        elif n <= 70: return 22
        elif n <= 90: return 19
        else:         return 16
    # ── Final assembler — templates never override this ───────────
    def code(self, data: dict, script: str = "") -> str:
        safe_script = (
            script
            .replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", " ")
            .strip()
        ) or "This scene demonstrates the concept visually."

        body       = self._scene_body(data, safe_script)
        manim_font = self._manim_font()
        piper_model = self._piper_model()

        # Font override block — only emitted for non-default fonts (e.g. Hindi)
        font_override = ""
        if manim_font:
            font_override = (
                f"\n"
                f"# ── Language font override ({self._lang_code}) ──────────────────────\n"
                f"_LANG_FONT = {manim_font!r}\n"
                f"_OrigText = Text\n"
                f"class Text(_OrigText):\n"
                f"    def __init__(self, text, **kwargs):\n"
                f"        kwargs.setdefault('font', _LANG_FONT)\n"
                f"        super().__init__(text, **kwargs)\n"
            )

        return (
            "from manim import *\n"
            "import sys, os\n"
            "sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))\n"
            "from manim_voiceover import VoiceoverScene\n"
            "from services.piper_service import PiperTTSService\n"
            f"{font_override}"
            "\n"
            "class ImagioScene(VoiceoverScene):\n"
            "    def construct(self):\n"
            f'        self.camera.background_color = "{self._bg_color()}"\n'
            f'        self.set_speech_service(PiperTTSService(voice={piper_model!r}))\n'
            "\n"
            f"{self._footer_code()}\n"
            "\n"
            "        self.wait(0.5)  # scene entry buffer\n"
            "\n"
            f"{body}\n"
            "        self.wait(0.5)  # scene exit buffer\n"
        )

    # ── Shared helpers ────────────────────────────────────────────

    def _footer_code(self) -> str:
        return (
            "        _footer = Text('Made by Imagio', font_size=15, color=WHITE)\n"
            "        _footer.to_corner(DR, buff=0.25)\n"
            "        self.add(_footer)"
        )

    def _bg_color(self) -> str:
        return "#0f0f23"
    
    def _header(self, scene_class: str = "VoiceoverScene", service_class: str = "PiperTTSService") -> str:
        return (
            "from manim import *\n"
            "import sys, os\n"
            "sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))\n"
            f"from manim_voiceover import {scene_class}\n"
            f"from services.piper_service import {service_class}\n"
        )

