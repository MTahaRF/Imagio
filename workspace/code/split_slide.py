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

        title   = Text('The Fourier Transform Formula', font_size=40, color=WHITE, weight=BOLD)
        divider = Line(UP * 2.8, DOWN * 3, color='#3a3a5c', stroke_width=2)
        title.to_edge(UP, buff=0.4)
        with self.voiceover(text='Let us break down the Fourier Transform formula piece by piece.'):
            self.play(Write(title), run_time=0.8)
            self.play(Create(divider), run_time=0.5)

        l_header  = Text('Formula', font_size=28, color=YELLOW)
        l_formula = MathTex('\\hat{f}(\\omega) = \\int_{-\\infty}^{\\infty} f(t)\\, e^{-i\\omega t}\\, dt', font_size=54, color=WHITE)
        l_header.move_to(LEFT * 3.2 + UP * 1.8)
        l_formula.move_to(LEFT * 3.2)
        with self.voiceover(text='This integral transforms a time-domain signal into the frequency domain.'):
            self.play(FadeIn(l_header), run_time=0.5)
            self.play(Write(l_formula), run_time=1.2)

        r_header = Text('What it means', font_size=28, color=YELLOW)
        r_header.move_to(RIGHT * 3.0 + UP * 1.8)
        self.play(FadeIn(r_header), run_time=0.4)

        raw_lines       = ['f(t) is the original signal in time', 'e^(-iwt) is a rotating complex sinusoid', 'The integral sums contributions at each frequency w', 'The result F(w) is the amplitude at each frequency']
        narrations_data = ['f of t is the original signal measured over time.', 'The exponential term is a rotating complex sinusoid at frequency omega.', 'The integral accumulates all contributions across every frequency.', 'The result gives us the amplitude present at each individual frequency.']
        r_group = VGroup(*[
            Text(line, font_size=25, color=WHITE) for line in raw_lines
        ]).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        r_group.set_width(min(r_group.width, 5.2))
        r_group.move_to(RIGHT * 3.0)

        for line_obj, narration in zip(r_group, narrations_data):
            with self.voiceover(text=narration):
                self.play(FadeIn(line_obj, shift=UP * 0.15), run_time=0.45)

        self.wait(1)
        self.play(FadeOut(*self.mobjects))
        self.wait(0.3)

