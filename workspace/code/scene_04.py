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

        title = Text('From Continuous Fourier Integral to Discrete Fourier Transform', font_size=27, color=YELLOW, weight=BOLD)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=0.8, rate_func=smooth)
        self.wait(0.3)

        steps_latex     = ['f(t)=\\sum_{k=-\\infty}^{\\infty} c_k e^{i 2\\pi k t /T},\\quad c_k=\\frac{1}{T}\\int_{0}^{T} f(t) e^{-i 2\\pi k t /T}\\,dt', 'f(t)=\\int_{-\\infty}^{\\infty} \\hat{f}(\\omega) e^{i\\omega t}\\,d\\omega,\\quad \\hat{f}(\\omega)=\\frac{1}{2\\pi}\\int_{-\\infty}^{\\infty} f(t) e^{-i\\omega t}\\,dt', 'X_k=\\sum_{n=0}^{N-1} x_n e^{-i 2\\pi k n /N},\\quad x_n=\\frac{1}{N}\\sum_{k=0}^{N-1} X_k e^{i 2\\pi k n /N}']
        annotations     = ['Fourier series expresses a periodic function as a sum of complex exponentials.', 'Letting the period go to infinity replaces the sum with an integral, defining the continuous Fourier transform.', 'Sampling the integral at N points yields the DFT, a finite sum used in digital signal processing.']
        narrations_data = ['We write a periodic signal as a sum of exponentials with coefficients given by an integral over one period.', 'As the period grows, the frequency spacing shrinks, turning the sum into an integral—the continuous Fourier transform pair.', 'With only N samples, the integral becomes a finite sum, giving the Discrete Fourier Transform and its inverse.']

        current_eq   = MathTex(steps_latex[0], font_size=54, color=WHITE)
        current_eq.move_to(ORIGIN + UP * 0.5)
        current_note = Text(annotations[0], font_size=26, color='#a0a8d0')
        current_note.next_to(current_eq, DOWN, buff=0.4)

        with self.voiceover(text=narrations_data[0]):
            self.play(Write(current_eq), run_time=1.0, rate_func=smooth)
            if annotations[0]:
                self.play(FadeIn(current_note, shift=UP * 0.1), run_time=0.5)
            self.wait(0.3)

        for i in range(1, len(steps_latex)):
            next_eq   = MathTex(steps_latex[i], font_size=54, color=WHITE)
            next_eq.move_to(ORIGIN + UP * 0.5)
            next_note = Text(annotations[i], font_size=26, color='#a0a8d0')
            next_note.next_to(next_eq, DOWN, buff=0.4)

            with self.voiceover(text=narrations_data[i]):
                self.play(
                    TransformMatchingShapes(current_eq, next_eq),
                    run_time=1.1, rate_func=smooth,
                )
                self.wait(0.2)
                if annotations[i - 1]:
                    self.play(FadeOut(current_note), run_time=0.3)
                if annotations[i]:
                    self.play(FadeIn(next_note, shift=UP * 0.1), run_time=0.45)
                self.wait(0.25)

            current_eq   = next_eq
            current_note = next_note

        self.wait(2)
        self.play(FadeOut(*self.mobjects), run_time=0.8)

        self.wait(0.5)  # scene exit buffer
