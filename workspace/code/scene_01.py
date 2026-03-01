from manim import *
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from manim_voiceover import VoiceoverScene
from services.piper_service import PiperTTSService

class ImagioScene(VoiceoverScene):
    def construct(self):
        self.camera.background_color = "#0f0f23"
        self.set_speech_service(PiperTTSService(voice='en_US-lessac-medium'))

        _footer = Text('Made by Imagio', font_size=15, color=WHITE)
        _footer.to_corner(DR, buff=0.25)
        self.add(_footer)

        self.wait(0.5)  # scene entry buffer

        title    = Text('Unveiling the Secrets of the Fourier Transform', font_size=32, color=WHITE, weight=BOLD)
        subtitle = Text('From Waves to Data – A Visual Journey', font_size=26, color='#a0a8d0')
        line     = Line(LEFT * 3.5, RIGHT * 3.5, color=YELLOW, stroke_width=3)
        title.move_to(ORIGIN + UP * 0.7)
        line.next_to(title, DOWN, buff=0.22)
        subtitle.next_to(line, DOWN, buff=0.3)

        with self.voiceover(text='In this video we’ll explore how the Fourier transform turns complex signals into simple frequencies, revealing hidden patterns in waves and data.'):
            self.play(Write(title), run_time=1.0, rate_func=smooth)
            self.wait(0.2)
            self.play(Create(line), run_time=0.5)
            self.play(FadeIn(subtitle, shift=UP * 0.15), run_time=0.7, rate_func=smooth)
            self.wait(0.4)

        self.wait(2)
        self.play(FadeOut(*self.mobjects), run_time=0.8)

        self.wait(0.5)  # scene exit buffer
