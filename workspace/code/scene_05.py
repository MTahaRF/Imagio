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

        title = Text('Gravity: The Cosmic Architect', font_size=44, color=YELLOW, weight=BOLD)
        title.to_edge(UP, buff=0.45)
        underline = Line(title.get_left(), title.get_right(), color=YELLOW, stroke_width=2)
        underline.next_to(title, DOWN, buff=0.1)
        self.play(
            AnimationGroup(Write(title), Create(underline), lag_ratio=0.4),
            run_time=0.9, rate_func=smooth,
        )
        self.wait(0.35)

        raw_points       = ['Star Formation: The Birth of Light', 'Galactic Structure: The Cosmic Glue', 'Black Holes: Extreme Spacetime Curvature']
        narrations_data  = ['Gravity compresses vast gas clouds, triggering nuclear fusion and giving birth to the stars that light up our universe.', 'On a larger scale, gravity binds billions of stars together, maintaining the intricate structures of rotating galaxies.', 'In its most intense form, gravity creates black holes, where spacetime is so warped that even light is trapped forever.']
        bullet_group = VGroup()
        for text in raw_points:
            dot   = Text('*', font_size=32, color=YELLOW)
            label = Text(text, font_size=32, color=WHITE)
            label.set_width(min(label.width, 10.0))
            row = VGroup(dot, label).arrange(RIGHT, buff=0.28, aligned_edge=UP)
            bullet_group.add(row)
        bullet_group.arrange(DOWN, buff=0.42, aligned_edge=LEFT)
        bullet_group.next_to(underline, DOWN, buff=0.4)
        bullet_group.to_edge(LEFT, buff=0.75)

        for row, narration in zip(bullet_group, narrations_data):
            with self.voiceover(text=narration):
                self.play(
                    FadeIn(row, shift=RIGHT * 0.25),
                    run_time=0.55, rate_func=smooth,
                )
                self.wait(0.2)

        self.wait(2)
        self.play(FadeOut(*self.mobjects), run_time=0.8)

        self.wait(0.5)  # scene exit buffer
