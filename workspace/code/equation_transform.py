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

        title = Text("Deriving Euler's Identity", font_size=38, color=YELLOW, weight=BOLD)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=0.8)

        steps_latex     = ['e^{i\\theta} = \\cos\\theta + i\\sin\\theta', 'e^{i\\pi} = \\cos\\pi + i\\sin\\pi', 'e^{i\\pi} = -1 + i \\cdot 0', 'e^{i\\pi} + 1 = 0']
        annotations     = ["Start with Euler's formula", 'Substitute theta = pi', 'Evaluate: cos(pi) = -1, sin(pi) = 0', 'Rearrange to get the famous identity']
        narrations_data = ["We start with Euler's formula relating the exponential to sine and cosine.", 'Substituting theta equals pi into both sides of the equation.', 'Evaluating cosine of pi gives negative one, and sine of pi gives zero.', "Rearranging gives us Euler's famous identity, considered the most beautiful equation in mathematics."]

        current_eq   = MathTex(steps_latex[0], font_size=54, color=WHITE)
        current_eq.move_to(ORIGIN + UP * 0.4)
        current_note = Text(annotations[0], font_size=26, color='#a0a8d0')
        current_note.next_to(current_eq, DOWN, buff=0.45)

        with self.voiceover(text=narrations_data[0]):
            self.play(Write(current_eq), run_time=1.0)
            if annotations[0]:
                self.play(FadeIn(current_note, shift=UP * 0.1), run_time=0.5)

        for i in range(1, len(steps_latex)):
            next_eq   = MathTex(steps_latex[i], font_size=54, color=WHITE)
            next_eq.move_to(ORIGIN + UP * 0.4)
            next_note = Text(annotations[i], font_size=26, color='#a0a8d0')
            next_note.next_to(next_eq, DOWN, buff=0.45)
            with self.voiceover(text=narrations_data[i]):
                self.play(TransformMatchingShapes(current_eq, next_eq), run_time=1.0)
                if annotations[i - 1]:
                    self.play(FadeOut(current_note), run_time=0.3)
                if annotations[i]:
                    self.play(FadeIn(next_note, shift=UP * 0.1), run_time=0.4)
            current_eq   = next_eq
            current_note = next_note

        self.wait(1.5)
        self.play(FadeOut(*self.mobjects))
        self.wait(0.3)

