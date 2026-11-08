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

        title = Text('Swirl & Float: Fluid Mechanics in\nAction', font_size=34, color=WHITE, weight=BOLD)
        _safe_fit(title, max_w=11.5, min_scale=0.85)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=0.8, rate_func=smooth)
        self.wait(0.3)

        # Generated image for: 'A cross‑section illustration showing water spiraling down a drain with arrows indicating velocity, beside a ship hull displacing water with pressure arrows, labeled, clean white background'
        _image_path = 'E:\\random\\Imagio\\Imagio\\workspace\\media\\generated\\pic_766c03c22e0b.png'
        image = ImageMobject(_image_path)
        image.set_height(4.0)
        image.move_to(LEFT * 2.8 + DOWN * 0.25)
        image.set_z_index(-1)
        with self.voiceover(text='Ever watched water spiral into a sink and wondered why it twirls, or marveled at a massive ship gliding effortlessly across the sea? The answer lies in the same invisible forces that govern every fluid. As water drains, pressure drops at the center, pulling surrounding fluid inward and converting that motion into rotation—an elegant dance of angular momentum. A ship, meanwhile, displaces a volume of water; the resulting pressure difference creates an upward buoyant force that balances its weight, letting it float. Both phenomena showcase how pressure and motion intertwine, the heart of fluid mechanics.'):
            self.play(FadeIn(image, shift=RIGHT * 0.15), run_time=0.8, rate_func=smooth)
        self.wait(0.3)

        caption_obj = Text('Both swirling drains and\nfloating ships illustrate\npressure‑driven fluid\nbehavior.', font_size=20,
            color='#a0a8d0', slant=ITALIC, line_spacing=1.1)
        _safe_fit(caption_obj, max_w=4.8, min_scale=0.82)
        caption_obj.next_to(image, DOWN, buff=0.18)
        self.play(FadeIn(caption_obj, shift=UP * 0.1), run_time=0.5)
        self.wait(0.25)

        points_data = [('Drains create a low‑pressure\ncore', 'When water exits a drain, the center pressure drops, pulling surrounding fluid inward and starting the spin.'), ('Conservation of angular\nmomentum drives the swirl', 'The inward flow converts linear speed into rotation, conserving angular momentum and forming the familiar vortex.'), ('Buoyancy balances weight for\nships', 'A ship pushes water aside, creating higher pressure below and lower pressure above, generating an upward buoyant force.')]
        point_rows = VGroup()
        for point_text, _point_narration in points_data:
            dot   = Text('•', font_size=24, color=YELLOW)
            label = Text(point_text, font_size=24, color=WHITE, line_spacing=1.15)
            _safe_fit(label, max_w=4.8, min_scale=0.85)
            row   = VGroup(dot, label).arrange(RIGHT, buff=0.2, aligned_edge=UP)
            point_rows.add(row)
        point_rows.arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        _safe_fit(point_rows, max_w=5.4, max_h=4.6, min_scale=0.82)
        point_rows.move_to(RIGHT * 3.2 + DOWN * 0.2)
        self.play(FadeOut(caption_obj), run_time=0.3)
        for i, (row, (_point_text, point_narration)) in enumerate(zip(point_rows, points_data)):
            with self.voiceover(text=point_narration):
                animations = [FadeIn(row, shift=LEFT * 0.15)]
                if i > 0:
                    animations.append(point_rows[i - 1].animate.set_opacity(0.45))
                self.play(*animations, run_time=0.8, rate_func=smooth)
                self.wait(0.2)

        self.wait(2)
        self.play(FadeOut(*self.mobjects), run_time=0.8)
        self.wait(0.25)  # scene exit buffer
