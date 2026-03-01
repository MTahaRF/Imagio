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

        title    = Text('The Fourier Transform', font_size=72, color=WHITE, weight=BOLD)
        subtitle = Text('Decomposing Signals Into Frequencies', font_size=36, color='#a0a8d0')
        line     = Line(LEFT * 3, RIGHT * 3, color=YELLOW, stroke_width=3)
        title.move_to(ORIGIN + UP * 0.6)
        line.next_to(title, DOWN, buff=0.25)
        subtitle.next_to(title, DOWN, buff=0.5)

        with self.voiceover(text='Welcome to this exploration of the Fourier Transform, one of the most powerful tools in all of mathematics.'):
            self.play(Write(title), run_time=1.2)
            self.play(Create(line), run_time=0.6)
            self.play(FadeIn(subtitle, shift=UP * 0.2), run_time=0.8)

        self.wait(1)
        self.play(FadeOut(*self.mobjects))
        self.wait(0.3)

