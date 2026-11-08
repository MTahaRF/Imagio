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

        title = Text('The Flow of Forces', font_size=48, color=WHITE, weight=BOLD)
        _safe_fit(title, max_w=11.5, max_h=3.0, min_scale=0.85)

        line_w = max(min(title.width * 0.85, 7.5), 3.0)
        line   = Line(LEFT * (line_w / 2), RIGHT * (line_w / 2), color=YELLOW, stroke_width=3)

        subtitle = Text('Mastering Fluid Mechanics and Its Core Equations', font_size=25, color='#a0a8d0')
        _safe_fit(subtitle, max_w=11.0, max_h=2.0, min_scale=0.82)

        content = VGroup(title, line, subtitle).arrange(DOWN, buff=0.28).move_to(ORIGIN)
        _safe_fit(content, max_w=11.5, max_h=5.5, min_scale=0.85)

        with self.voiceover(text='In this video we explore how fluids move and the equations that describe their behavior.') as tracker:
            t_title = max(min(tracker.duration * 0.35, 1.6), 0.9)
            t_sub   = max(min(tracker.duration * 0.35, 1.4), 0.7)
            self.play(Write(title), run_time=t_title, rate_func=smooth)
            self.wait(0.15)
            self.play(Create(line), run_time=0.4)
            self.play(FadeIn(subtitle, shift=UP * 0.15), run_time=t_sub, rate_func=smooth)
            self.wait(0.3)

        self.wait(1.0)
        self.play(FadeOut(*self.mobjects), run_time=0.6)

        self.wait(0.25)  # scene exit buffer
