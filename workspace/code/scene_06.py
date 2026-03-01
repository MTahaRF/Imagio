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

        title   = Text('Escape Velocity and the Event Horizon', font_size=38, color=WHITE, weight=BOLD)
        divider = Line(UP * 2.8, DOWN * 3.0, color='#3a3a5c', stroke_width=2)
        title.to_edge(UP, buff=0.4)
        with self.voiceover(text='Now we focus on the escape‑velocity equation that links gravity to the speed needed to break free.'):
            self.play(Write(title), run_time=0.8, rate_func=smooth)
            self.wait(0.2)
            self.play(Create(divider), run_time=0.5)
            self.wait(0.2)

        l_header  = Text('Escape‑velocity formula', font_size=28, color=YELLOW)
        l_formula = MathTex('v_{esc}=\\sqrt{\\frac{2GM}{r}}', font_size=54, color=WHITE)
        l_header.move_to(LEFT * 3.2 + UP * 1.8)
        l_formula.move_to(LEFT * 3.2)
        with self.voiceover(text='The escape speed is given by v_{esc}=\\sqrt{\\frac{2GM}{r}}.'):
            self.play(FadeIn(l_header, shift=DOWN*0.1), run_time=0.4)
            self.wait(0.15)
            self.play(Write(l_formula), run_time=1.1, rate_func=smooth)
            self.wait(0.3)

        r_header = Text('What each term means', font_size=28, color=YELLOW)
        r_header.move_to(RIGHT * 3.0 + UP * 1.8)
        self.play(FadeIn(r_header, shift=DOWN*0.1), run_time=0.4)
        self.wait(0.2)

        raw_lines       = ['G – universal gravitational constant', 'M – mass creating the gravitational field', 'r – distance from the mass’s center', 'Setting v_{esc}=c defines the horizon radius']
        narrations_data = ['G is the gravitational constant, the strength of gravity in Newton’s law.', 'M represents the mass of the object whose pull we’re trying to overcome.', "r is the radial distance from the object's center to the point of escape.", 'If we set that escape speed equal to light’s speed c, we locate the radius where nothing can escape.']
        r_group = VGroup(*[
            Text(line, font_size=25, color=WHITE) for line in raw_lines
        ]).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        r_group.set_width(min(r_group.width, 5.2))
        r_group.move_to(RIGHT * 3.0)

        for line_obj, narration in zip(r_group, narrations_data):
            with self.voiceover(text=narration):
                self.play(
                    FadeIn(line_obj, shift=UP * 0.12),
                    run_time=0.5, rate_func=smooth,
                )
                self.wait(0.2)

        self.wait(2)
        self.play(FadeOut(*self.mobjects), run_time=0.8)

        self.wait(0.5)  # scene exit buffer
