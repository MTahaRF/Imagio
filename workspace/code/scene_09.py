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
        title = Text('Gravity in Everyday Life', font_size=48, color=YELLOW, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        underline = Line(title.get_left(), title.get_right(), color=YELLOW, stroke_width=2)
        underline.next_to(title, DOWN, buff=0.1)
        self.play(Write(title), Create(underline), run_time=1.0)

        # ── Bullet points ─────────────────────────────────────────
        raw_points      = ['Satellite orbits and space travel rely on gravity to stay bound.', 'Ocean tides and why we stay on Earth arise from the Moon’s pull.', 'GPS timing corrections need relativistic adjustments due to gravity.']
        narrations_data = ['Gravity provides the centripetal force that keeps satellites in stable paths and propels spacecraft on their interplanetary journeys.', 'The Moon’s gravitational tug raises bulges in Earth’s oceans, creating tides and anchoring us to the planet’s surface.', 'GPS satellites must account for gravitational time dilation, otherwise their clocks drift and navigation errors would quickly accumulate.']
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

