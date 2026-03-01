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

        title   = Text('Gravity as Geometry', font_size=40, color=WHITE, weight=BOLD)
        divider = Line(UP * 2.8, DOWN * 3, color='#3a3a5c', stroke_width=2)
        title.to_edge(UP, buff=0.4)
        with self.voiceover(text='Now we shift from forces to geometry, seeing gravity as the shape of space itself.'):
            self.play(Write(title), run_time=0.8)
            self.play(Create(divider), run_time=0.5)

        l_header  = Text('Einstein’s Field Equation', font_size=28, color=YELLOW)
        l_formula = MathTex('R_{\\\\mu\\\\nu} - \\\\frac{1}{2} R g_{\\\\mu\\\\nu} = \\\\frac{8\\\\pi G}{c^{4}} T_{\\\\mu\\\\nu}', font_size=54, color=WHITE)
        l_header.move_to(LEFT * 3.2 + UP * 1.8)
        l_formula.move_to(LEFT * 3.2)
        with self.voiceover(text='Einstein’s field equation relates the curvature of spacetime to the energy and momentum of matter.'):
            self.play(FadeIn(l_header), run_time=0.5)
            self.play(Write(l_formula), run_time=1.2)

        r_header = Text('What It Means', font_size=28, color=YELLOW)
        r_header.move_to(RIGHT * 3.0 + UP * 1.8)
        self.play(FadeIn(r_header), run_time=0.4)

        raw_lines       = ['Mass tells spacetime how to curve.', 'Curved spacetime tells mass how to move.', 'Planets follow the straightest possible paths—geodesics—on this curved sheet.']
        narrations_data = ['Mass creates a depression in spacetime, just as a weight bends a rubber sheet.', 'Objects then move along the curved surface, following the natural straightest routes dictated by that geometry.', 'Thus planetary orbits are simply geodesics—paths that appear curved only because the underlying spacetime is curved.']
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

