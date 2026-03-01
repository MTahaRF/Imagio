from manim import *
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from manim_voiceover import VoiceoverScene
from services.piper_service import PiperTTSService

class ImagioScene(VoiceoverScene):
    def construct(self):
        self.camera.background_color = "#0f0f23"
        self.set_speech_service(PiperTTSService(voice='fr_FR-siwis-medium'))

        _footer = Text('Made by Imagio', font_size=15, color=WHITE)
        _footer.to_corner(DR, buff=0.25)
        self.add(_footer)

        self.wait(0.5)  # scene entry buffer

        import numpy as np

        title = Text('Potential gravitationnelle V(r) = -GM/r', font_size=38, color=WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=0.8, rate_func=smooth)
        self.wait(0.3)

        axes = Axes(
            x_range=[0.1, 10.0, (10.0-(0.1))/8],
            y_range=[-10.0, 0.0, (0.0-(-10.0))/6],
            x_length=10, y_length=5.0,
            axis_config={'color': '#666688', 'stroke_width': 2},
            tips=True,
        )
        axes.next_to(title, DOWN, buff=0.25)
        x_lbl = axes.get_x_axis_label(
            Text('Distance r (m)', font_size=22, color='#a0a8d0'), edge=RIGHT, direction=RIGHT)
        y_lbl = axes.get_y_axis_label(
            Text('Potentiel V(r) (J·kg⁻¹)', font_size=22, color='#a0a8d0'), edge=UP, direction=UP)

        with self.voiceover(text='Les axes apparaissent, l’axe horizontal représente la distance r, l’axe vertical le potentiel V(r).'):
            self.play(
                AnimationGroup(Create(axes), Write(x_lbl), Write(y_lbl), lag_ratio=0.2),
                run_time=1.1, rate_func=smooth,
            )
            self.wait(0.3)

        graph = axes.plot(lambda x: -G*M/ x, color=BLUE, stroke_width=3)
        with self.voiceover(text='La courbe se trace, montrant V(r) qui augmente vers zéro quand r grandit.'):
            self.play(Create(graph), run_time=2.0, rate_func=smooth)
            self.wait(0.3)

        if 'Le potentiel devient moins négatif quand la distance augmente':
            caption_obj = Text('Le potentiel devient moins négatif quand la distance augmente', font_size=22, color='#a0a8d0')
            caption_obj.to_edge(DOWN, buff=0.3)
            with self.voiceover(text='Cette légende explique la décroissance du potentiel avec la distance.'):
                self.play(FadeIn(caption_obj, shift=UP * 0.12), run_time=0.6, rate_func=smooth)
                self.wait(0.3)

        self.wait(2)
        self.play(FadeOut(*self.mobjects), run_time=0.8)

        self.wait(0.5)  # scene exit buffer
