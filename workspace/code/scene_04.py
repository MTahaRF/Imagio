from manim import *
import sys, os, textwrap, re
from contextlib import contextmanager
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from manim_voiceover import VoiceoverScene
from services.piper_service import PiperTTSService

_OrigMathTex = MathTex

class MathTex(VMobject):
    def __new__(cls, *args, **kwargs):
        try:
            return _OrigMathTex(*args, **kwargs)
        except Exception:
            tex_str = args[0] if args else kwargs.get('tex_strings', [''])[0]
            font_size = kwargs.get('font_size', 46)
            color = kwargs.get('color', WHITE)
            clean = (
                str(tex_str)
                .replace(r'\hat', '')
                .replace(r'\int', '∫')
                .replace(r'\infty', '∞')
                .replace(r'\omega', 'ω')
                .replace(r'\pi', 'π')
                .replace(r'\sigma', 'σ')
                .replace(r'\theta', 'θ')
                .replace(r'\alpha', 'α')
                .replace(r'\beta', 'β')
                .replace(r'\gamma', 'γ')
                .replace(r'\delta', 'δ')
                .replace(r'\lambda', 'λ')
                .replace(r'\mu', 'μ')
                .replace(r'\frac', '')
                .replace(r'\cdot', '·')
                .replace(r'\times', '×')
                .replace(r'\sqrt', '√')
                .replace(r'\sum', '∑')
                .replace(r'\left', '')
                .replace(r'\right', '')
                .replace(r'\_', '_')
                .replace(r'\text', '')
                .replace('{', '')
                .replace('}', '')
                .replace(r'\\', '')
                .replace('\\', '')
                .strip()
            )
            return Text(clean, font_size=int(font_size * 0.85), color=color)

def _safe_fit(mob, max_w=11.5, max_h=5.2, min_scale=0.82):
    if mob is None:
        return mob
    s_w = max_w / mob.width if max_w and mob.width > max_w else 1.0
    s_h = max_h / mob.height if max_h and mob.height > max_h else 1.0
    factor = max(min(s_w, s_h), min_scale)
    if factor < 0.999:
        mob.scale(factor)
    return mob

class ImagioScene(VoiceoverScene):
    @contextmanager
    def voiceover(self, text: str | None = None, ssml: str | None = None, **kwargs: object):
        if not text:
            with super().voiceover(text=text, ssml=ssml, **kwargs) as tracker:
                yield tracker
            return

        cap_group = None
        updater_fn = None
        try:
            with super().voiceover(text=text, ssml=ssml, **kwargs) as tracker:
                start_time = self.time
                duration = tracker.duration
                clean = ' '.join(str(text).split())
                sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean) if s.strip()]
                if len(clean) > 140 and len(sentences) > 1:
                    raw_chunks = sentences
                else:
                    raw_chunks = [clean]

                mobs = []
                for c in raw_chunks:
                    wrapped = textwrap.fill(c, width=52)
                    t = Text(wrapped, font_size=19, color='#f8fafc', line_spacing=1.15)
                    _safe_fit(t, max_w=11.2, min_scale=0.82)
                    box = SurroundingRectangle(
                        t,
                        color='#3b82f6',
                        fill_color='#030712',
                        fill_opacity=0.88,
                        buff=0.18,
                        corner_radius=0.12,
                        stroke_width=1.2,
                        stroke_opacity=0.5,
                    )
                    grp = VGroup(box, t).to_edge(DOWN, buff=0.32)
                    mobs.append(grp)

                if len(mobs) == 1:
                    cap_group = mobs[0]
                else:
                    weights = [len(c) for c in raw_chunks]
                    total_w = sum(weights) or 1
                    cum_times = []
                    c_t = 0.0
                    for w in weights:
                        c_t += duration * (w / total_w)
                        cum_times.append(c_t)
                    cap_group = VGroup(*mobs)
                    for i, mob in enumerate(mobs):
                        mob.set_opacity(1 if i == 0 else 0)

                    def _u(mob, dt):
                        elapsed = self.time - start_time
                        idx = 0
                        for i, ct in enumerate(cum_times):
                            if elapsed < ct:
                                idx = i
                                break
                            idx = len(mobs) - 1
                        for i, caption in enumerate(mobs):
                            caption.set_opacity(1 if i == idx else 0)
                    updater_fn = _u
                    cap_group.add_updater(updater_fn)

                cap_group.set_z_index(100)
                self.add(cap_group)
                try:
                    yield tracker
                finally:
                    pass
        finally:
            if cap_group is not None:
                if updater_fn is not None:
                    cap_group.remove_updater(updater_fn)
                self.remove(cap_group)

    def construct(self):
        self.camera.background_color = "#0f0f23"
        self.set_speech_service(PiperTTSService(voice='en_US-lessac-medium'))

        _footer = Text('Made by Imagio', font_size=11, color='#475569')
        _footer.to_corner(DR, buff=0.18)
        self.add(_footer)

        self.wait(0.25)  # scene entry buffer

        title = Text('Deriving Fluid Foundations', font_size=40, color=YELLOW, weight=BOLD)
        _safe_fit(title, max_w=11.5, min_scale=0.85)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=0.8, rate_func=smooth)
        self.wait(0.3)

        steps_latex     = ['\\\\frac{\\\\partial \\\\rho}{\\\\partial t} + \\\\nabla \\\\cdot (\\\\rho \\\\mathbf{v}) = 0', 'p + \\\\frac{1}{2}\\\\rho \\\\|\\\\mathbf{v}\\\\|^{2} + \\\\rho g h = \\\\text{constant}', '\\\\rho\\\\left(\\\\frac{\\\\partial \\\\mathbf{v}}{\\\\partial t} + (\\\\mathbf{v}\\\\cdot\\\\nabla)\\\\mathbf{v}\\\\right) = -\\\\nabla p + \\\\mu \\\\nabla^{2}\\\\mathbf{v} + \\\\rho \\\\mathbf{g}']
        annotations     = ['Mass conservation in a fluid element', 'Energy balance along a streamline', 'Momentum balance with viscosity and gravity']
        narrations_data = ["We start by insisting mass can't disappear, which gives the continuity equation linking density changes to the flow divergence.", 'Assuming steady, incompressible, frictionless flow, energy stays constant along a streamline, leading to Bernoulli’s pressure‑velocity relation.', 'Finally we balance inertia, pressure gradients, viscous diffusion, and gravity, arriving at the core Navier–Stokes momentum equation.']

        current_eq   = MathTex(steps_latex[0], font_size=54, color=WHITE)
        _safe_fit(current_eq, max_w=11.0, max_h=2.0, min_scale=0.75)
        current_eq.move_to(ORIGIN + UP * 0.5)
        current_note = Text(annotations[0], font_size=26, color='#a0a8d0')
        _safe_fit(current_note, max_w=10.5, min_scale=0.82)
        current_note.next_to(current_eq, DOWN, buff=0.4)

        with self.voiceover(text=narrations_data[0]):
            self.play(Write(current_eq), run_time=1.0, rate_func=smooth)
            if annotations[0]:
                self.play(FadeIn(current_note, shift=UP * 0.1), run_time=0.5)
            self.wait(0.3)

        for i in range(1, len(steps_latex)):
            next_eq   = MathTex(steps_latex[i], font_size=54, color=WHITE)
            _safe_fit(next_eq, max_w=11.0, max_h=2.0, min_scale=0.75)
            next_eq.move_to(ORIGIN + UP * 0.5)
            next_note = Text(annotations[i], font_size=26, color='#a0a8d0')
            _safe_fit(next_note, max_w=10.5, min_scale=0.82)
            next_note.next_to(next_eq, DOWN, buff=0.4)

            with self.voiceover(text=narrations_data[i]):
                self.play(
                    TransformMatchingShapes(current_eq, next_eq),
                    run_time=1.1, rate_func=smooth,
                )
                self.wait(0.2)
                if annotations[i - 1]:
                    self.play(FadeOut(current_note), run_time=0.3)
                if annotations[i]:
                    self.play(FadeIn(next_note, shift=UP * 0.1), run_time=0.45)
                self.wait(0.25)

            current_eq   = next_eq
            current_note = next_note

        self.wait(2)
        self.play(FadeOut(*self.mobjects), run_time=0.8)

        self.wait(0.25)  # scene exit buffer
