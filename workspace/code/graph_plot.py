from manim import *
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from manim_voiceover import VoiceoverScene
from services.piper_service import PiperTTSService

class ImagioScene(VoiceoverScene):
    def construct(self):
        self.camera.background_color = "#0f0f23"
        self.set_speech_service(PiperTTSService())

        _footer = Text('Made by Imagio', font_size=15, color=WHITE)
        _footer.to_corner(DR, buff=0.25)
        self.add(_footer)

        import numpy as np
        title = Text('A Simple Sine Wave', font_size=38, color=WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=0.8)

        axes = Axes(
            x_range=[-2.0, 2.0, (2.0-(-2.0))/8],
            y_range=[-1.5, 1.5, (1.5-(-1.5))/6],
            x_length=10, y_length=5.2,
            axis_config={'color': '#666688', 'stroke_width': 2},
            tips=True,
        )
        axes.next_to(title, DOWN, buff=0.3)
        x_lbl = axes.get_x_axis_label(Text('Time (s)', font_size=22, color='#a0a8d0'), edge=RIGHT, direction=RIGHT)
        y_lbl = axes.get_y_axis_label(Text('Amplitude', font_size=22, color='#a0a8d0'), edge=UP, direction=UP)
        with self.voiceover(text='Let us set up the time and amplitude axes for our sine wave.'):
            self.play(Create(axes), Write(x_lbl), Write(y_lbl), run_time=1.0)

        graph = axes.plot(lambda x: np.sin(2 * np.pi * x), color=BLUE, stroke_width=3)
        with self.voiceover(text='Here is the sine wave completing exactly one full cycle per second.'):
            self.play(Create(graph), run_time=1.8)

        if 'sin(2πt) — one complete cycle per second':
            caption_obj = Text('sin(2πt) — one complete cycle per second', font_size=24, color='#a0a8d0')
            caption_obj.to_edge(DOWN, buff=0.35)
            with self.voiceover(text='This is sin of 2 pi t, oscillating between negative one and positive one.'):
                self.play(FadeIn(caption_obj, shift=UP * 0.15), run_time=0.6)

        self.wait(1)
        self.play(FadeOut(*self.mobjects))
        self.wait(0.3)

