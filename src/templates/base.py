from abc import ABC, abstractmethod

class BaseTemplate(ABC):

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
        )
        if not safe_script:
            safe_script = "This scene demonstrates the concept visually."

        body = self._scene_body(data, safe_script)

        return (
            "from manim import *\n"
            "import sys, os\n"
            "sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))\n"
            "from manim_voiceover import VoiceoverScene\n"
            "from services.piper_service import PiperTTSService\n"
            "\n"
            "class ImagioScene(VoiceoverScene):\n"
            "    def construct(self):\n"
            f'        self.camera.background_color = "{self._bg_color()}"\n'
            "        self.set_speech_service(PiperTTSService())\n"
            "\n"
            f"{self._footer_code()}\n"
            "\n"
            "        self.wait(1)  # scene entry buffer\n"
            "\n"
            f"{body}\n"
            "        self.wait(1)  # scene exit buffer\n"
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

