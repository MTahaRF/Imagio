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
    def _wrap_text(text: str, width: int = 42) -> str:
        """Wraps text cleanly preserving existing newlines."""
        import textwrap
        if not text:
            return ""
        lines = str(text).split("\n")
        wrapped = [textwrap.fill(line, width=width) if line.strip() else "" for line in lines]
        return "\n".join(wrapped)

    @staticmethod
    def _title_font_size(title: str) -> int:
        n = len(title)
        if n <= 20:   return 48
        elif n <= 35: return 40
        elif n <= 50: return 34
        elif n <= 70: return 28
        else:         return 24

    @staticmethod
    def _auto_font_size(text: str) -> int:
        n = len(text)
        if n <= 30:   return 28
        elif n <= 60: return 25
        elif n <= 90: return 22
        else:         return 20

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
            "import sys, os, textwrap, re\n"
            "from contextlib import contextmanager\n"
            "sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))\n"
            "from manim_voiceover import VoiceoverScene\n"
            "from services.piper_service import PiperTTSService\n"
            f"{font_override}"
            "\n"
            "_OrigMathTex = MathTex\n"
            "\n"
            "class MathTex(VMobject):\n"
            "    def __new__(cls, *args, **kwargs):\n"
            "        try:\n"
            "            return _OrigMathTex(*args, **kwargs)\n"
            "        except Exception:\n"
            "            tex_str = args[0] if args else kwargs.get('tex_strings', [''])[0]\n"
            "            font_size = kwargs.get('font_size', 46)\n"
            "            color = kwargs.get('color', WHITE)\n"
            "            clean = (\n"
            "                str(tex_str)\n"
            "                .replace(r'\\hat', '')\n"
            "                .replace(r'\\int', '∫')\n"
            "                .replace(r'\\infty', '∞')\n"
            "                .replace(r'\\omega', 'ω')\n"
            "                .replace(r'\\pi', 'π')\n"
            "                .replace(r'\\sigma', 'σ')\n"
            "                .replace(r'\\theta', 'θ')\n"
            "                .replace(r'\\alpha', 'α')\n"
            "                .replace(r'\\beta', 'β')\n"
            "                .replace(r'\\gamma', 'γ')\n"
            "                .replace(r'\\delta', 'δ')\n"
            "                .replace(r'\\lambda', 'λ')\n"
            "                .replace(r'\\mu', 'μ')\n"
            "                .replace(r'\\frac', '')\n"
            "                .replace(r'\\cdot', '·')\n"
            "                .replace(r'\\times', '×')\n"
            "                .replace(r'\\sqrt', '√')\n"
            "                .replace(r'\\sum', '∑')\n"
            "                .replace(r'\\left', '')\n"
            "                .replace(r'\\right', '')\n"
            "                .replace(r'\\_', '_')\n"
            "                .replace(r'\\text', '')\n"
            "                .replace('{', '')\n"
            "                .replace('}', '')\n"
            "                .replace(r'\\\\', '')\n"
            "                .replace('\\\\', '')\n"
            "                .strip()\n"
            "            )\n"
            "            return Text(clean, font_size=int(font_size * 0.85), color=color)\n"
            "\n"
            "def _safe_fit(mob, max_w=11.5, max_h=5.2, min_scale=0.82):\n"
            "    if mob is None:\n"
            "        return mob\n"
            "    s_w = max_w / mob.width if max_w and mob.width > max_w else 1.0\n"
            "    s_h = max_h / mob.height if max_h and mob.height > max_h else 1.0\n"
            "    factor = max(min(s_w, s_h), min_scale)\n"
            "    if factor < 0.999:\n"
            "        mob.scale(factor)\n"
            "    return mob\n"
            "\n"
            "class ImagioScene(VoiceoverScene):\n"
            "    @contextmanager\n"
            "    def voiceover(self, text=None, **kwargs):\n"
            "        if not text:\n"
            "            with super().voiceover(text=text, **kwargs) as tracker:\n"
            "                yield tracker\n"
            "            return\n"
            "\n"
            "        cap_group = None\n"
            "        updater_fn = None\n"
            "        try:\n"
            "            with super().voiceover(text=text, **kwargs) as tracker:\n"
            "                start_time = self.time\n"
            "                duration = tracker.duration\n"
            "                clean = ' '.join(str(text).split())\n"
            "                sentences = [s.strip() for s in re.split(r'(?<=[.!?])\\s+', clean) if s.strip()]\n"
            "                if len(clean) > 140 and len(sentences) > 1:\n"
            "                    raw_chunks = sentences\n"
            "                else:\n"
            "                    raw_chunks = [clean]\n"
            "\n"
            "                mobs = []\n"
            "                for c in raw_chunks:\n"
            "                    wrapped = textwrap.fill(c, width=52)\n"
            "                    t = Text(wrapped, font_size=19, color='#f8fafc', line_spacing=1.15)\n"
            "                    _safe_fit(t, max_w=11.2, min_scale=0.82)\n"
            "                    box = SurroundingRectangle(\n"
            "                        t,\n"
            "                        color='#3b82f6',\n"
            "                        fill_color='#030712',\n"
            "                        fill_opacity=0.88,\n"
            "                        buff=0.18,\n"
            "                        corner_radius=0.12,\n"
            "                        stroke_width=1.2,\n"
            "                        stroke_opacity=0.5,\n"
            "                    )\n"
            "                    grp = VGroup(box, t).to_edge(DOWN, buff=0.32)\n"
            "                    mobs.append(grp)\n"
            "\n"
            "                if len(mobs) == 1:\n"
            "                    cap_group = mobs[0]\n"
            "                else:\n"
            "                    weights = [len(c) for c in raw_chunks]\n"
            "                    total_w = sum(weights) or 1\n"
            "                    cum_times = []\n"
            "                    c_t = 0.0\n"
            "                    for w in weights:\n"
            "                        c_t += duration * (w / total_w)\n"
            "                        cum_times.append(c_t)\n"
            "                    cap_group = VGroup(mobs[0])\n"
            "\n"
            "                    def _u(mob, dt):\n"
            "                        elapsed = self.time - start_time\n"
            "                        idx = 0\n"
            "                        for i, ct in enumerate(cum_times):\n"
            "                            if elapsed < ct:\n"
            "                                idx = i\n"
            "                                break\n"
            "                            idx = len(mobs) - 1\n"
            "                        target = mobs[idx]\n"
            "                        if mob.submobjects[0] is not target:\n"
            "                            mob.submobjects = [target]\n"
            "                    updater_fn = _u\n"
            "                    cap_group.add_updater(updater_fn)\n"
            "\n"
            "                self.add(cap_group)\n"
            "                try:\n"
            "                    yield tracker\n"
            "                finally:\n"
            "                    pass\n"
            "        finally:\n"
            "            if cap_group is not None:\n"
            "                if updater_fn is not None:\n"
            "                    cap_group.remove_updater(updater_fn)\n"
            "                self.remove(cap_group)\n"
            "\n"
            "    def construct(self):\n"
            f'        self.camera.background_color = "{self._bg_color()}"\n'
            f'        self.set_speech_service(PiperTTSService(voice={piper_model!r}))\n'
            "\n"
            f"{self._footer_code()}\n"
            "\n"
            "        self.wait(0.25)  # scene entry buffer\n"
            "\n"
            f"{body}\n"
            "        self.wait(0.25)  # scene exit buffer\n"
        )

    # ── Shared helpers ────────────────────────────────────────────

    def _footer_code(self) -> str:
        return (
            "        _footer = Text('Made by Imagio', font_size=11, color='#475569')\n"
            "        _footer.to_corner(DR, buff=0.18)\n"
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

