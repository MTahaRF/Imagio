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

        title   = Text('Gravitational Attraction Between Two Masses', font_size=40, color=WHITE, weight=BOLD)
        divider = Line(UP * 2.8, DOWN * 3, color='#3a3a5c', stroke_width=2)
        title.to_edge(UP, buff=0.4)
        with self.voiceover(text='Now we look at how two objects pull on each other through gravity.'):
            self.play(Write(title), run_time=0.8)
            self.play(Create(divider), run_time=0.5)

        l_header  = Text('Force Law', font_size=28, color=YELLOW)
        l_formula = MathTex('F = \\frac{G m_1 m_2}{r^2}', font_size=54, color=WHITE)
        l_header.move_to(LEFT * 3.2 + UP * 1.8)
        l_formula.move_to(LEFT * 3.2)
        with self.voiceover(text='The gravitational force follows Newton’s law: F equals G times the product of the masses divided by the square of their separation.'):
            self.play(FadeIn(l_header), run_time=0.5)
            self.play(Write(l_formula), run_time=1.2)

        r_header = Text('What It Means', font_size=28, color=YELLOW)
        r_header.move_to(RIGHT * 3.0 + UP * 1.8)
        self.play(FadeIn(r_header), run_time=0.4)

        raw_lines       = ['Each mass pulls on the other with a force.', 'The force grows stronger as the masses increase.', 'It weakens quickly as the distance between them grows.']
        narrations_data = ['Both bodies experience the same attractive pull toward one another.', 'If either mass gets larger, the pull strengthens proportionally.', 'Doubling the distance reduces the force by a factor of four.']
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

