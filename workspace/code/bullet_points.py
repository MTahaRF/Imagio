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

        # ── Title ─────────────────────────────────────────────────
        title = Text('Why the Fourier Transform Matters', font_size=48, color=YELLOW, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        underline = Line(title.get_left(), title.get_right(), color=YELLOW, stroke_width=2)
        underline.next_to(title, DOWN, buff=0.1)
        self.play(Write(title), Create(underline), run_time=1.0)

        # ── Bullet points ─────────────────────────────────────────
        raw_points      = ['Converts a signal from the time domain to the frequency domain', 'Reveals the hidden frequencies inside any waveform', 'Powers MP3 compression, JPEG images, and noise cancellation', 'Used in quantum mechanics and solving differential equations', 'One of the most widely applied tools in all of mathematics']
        narrations_data = ['The Fourier Transform moves a signal from the time domain into the frequency domain.', 'It reveals hidden frequencies that are invisible in the original waveform.', 'This powers everyday technology like MP3 audio and JPEG image compression.', 'It also appears in quantum mechanics and differential equation solutions.', 'Making it one of the most broadly applied tools across all of mathematics.']
        bullet_group = VGroup()
        for text in raw_points:
            dot   = Text('*', font_size=25, color=YELLOW)
            label = Text(text, font_size=25, color=WHITE)
            label.set_width(min(label.width, 10.0))
            row = VGroup(dot, label).arrange(RIGHT, buff=0.28, aligned_edge=UP)
            bullet_group.add(row)
        bullet_group.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        bullet_group.next_to(underline, DOWN, buff=0.45)
        bullet_group.to_edge(LEFT, buff=0.75)

        for row, narration in zip(bullet_group, narrations_data):
            with self.voiceover(text=narration):
                self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.5)

        self.wait(1)
        self.play(FadeOut(*self.mobjects))
        self.wait(0.3)

