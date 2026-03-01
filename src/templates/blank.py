from .base import BaseTemplate

class BlankTemplate(BaseTemplate):

    def description(self) -> str:
        return (
            "FALLBACK ONLY — use as a last resort when no other template fits. "
            "The coder model generates raw Manim Python code directly. "
            "Use for highly custom animations: particle systems, 3D scenes, complex "
            "geometric constructions, or anything the other nine templates cannot express."
        )

    def schema(self) -> dict:
        return {
            "raw_code": (
                "Complete Manim Python source code as a single string. "
                "Must define 'class ImagioScene(VoiceoverScene)' with a construct() method. "
                "Must include all imports including manim_voiceover and PiperTTSService. "
                "Must call self.set_speech_service(PiperTTSService()) inside construct(). "
                "Must wrap each animation in: with self.voiceover(text='...'):  "
                "Must include footer: _footer = Text('Made by Imagio', font_size=15, color=WHITE); "
                "_footer.to_corner(DR, buff=0.25); self.add(_footer)."
            ),
        }

    def prompt(self) -> str:
        return (
            "You are writing a complete Manim scene from scratch.\n"
            "Return ONLY a JSON object with one key 'raw_code' whose value is the full Python source.\n\n"
            "Schema:\n"
            "{\n"
            '  "raw_code": "from manim import *\\nimport sys, os\\n..."\n'
            "}\n\n"
            "Requirements for raw_code:\n"
            "- First lines must be:\n"
            "    from manim import *\n"
            "    import sys, os\n"
            "    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))\n"
            "    from manim_voiceover import VoiceoverScene\n"
            "    from services.piper_service import PiperTTSService\n"
            "- Class must be: class ImagioScene(VoiceoverScene)\n"
            "- Inside construct(): self.set_speech_service(PiperTTSService())\n"
            "- Background: self.camera.background_color = '#0f0f23'\n"
            "- Every animation must be wrapped in: with self.voiceover(text='...'):\n"
            "- Must include Imagio footer inside construct().\n"
            "- End with: self.play(FadeOut(*self.mobjects))\n"
            "- Use only Manim Community Edition APIs. No placeholders.\n"
        )

    def _scene_body(self, data: dict, script: str) -> str:
        # blank.py is special — raw_code is the full file, not just the body.
        # _scene_body is not used; we override code() instead.
        return ""

    def code(self, data: dict, script: str = "") -> str:
        raw = data.get("raw_code", "").strip()

        if raw:
            return raw

        # Safe fallback if raw_code is empty
        safe_script = script.replace('"', '\\"').replace("\n", " ").strip()
        if not safe_script:
            safe_script = "This scene could not be generated."

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
            "        notice = Text(\n"
            f'            "{safe_script}",\n'
            "            font_size=32, color='#ff6b6b'\n"
            "        )\n"
            "        notice.move_to(ORIGIN)\n"
            f'        with self.voiceover(text="{safe_script}"):\n'
            "            self.play(Write(notice))\n"
            "        self.wait(2)\n"
        )
