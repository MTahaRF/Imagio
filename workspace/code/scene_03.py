from manim import *
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from manim_voiceover import VoiceoverScene
from services.piper_service import PiperTTSService

class ImagioScene(VoiceoverScene):
    def construct(self):
        self.set_speech_service(PiperTTSService())
        self.camera.background_color = "#0f0f23"

        title = Text("Flow Field Visualization", font_size=48, color=WHITE)
        title.to_edge(UP)

        # Pressure scalar field (radial gradient)
        def pressure_func(p):
            r = np.linalg.norm(p[:2])
            return 1 - np.exp(-r**2 / 2)

        pressure_plane = Plane(
            x_range=[-4, 4, 0.5],
            y_range=[-3, 3, 0.5],
            background_line_style=dict(stroke_opacity=0)
        )
        pressure_plane.set_fill_by_value(
            lambda p: pressure_func(p),
            colors=[BLUE_D, BLUE, GREEN, YELLOW, ORANGE, RED],
            opacity=0.8
        )

        # Velocity field – a vortex
        vortex_field = ArrowVectorField(
            lambda p: np.array([-p[1], p[0], 0]),
            x_range=[-4, 4, 0.5],
            y_range=[-3, 3, 0.5],
            colors=[WHITE],
            length_func=lambda norm: 0.3
        )

        # Streamlines following the same vortex field
        stream = StreamLines(
            lambda p: np.array([-p[1], p[0], 0]),
            x_range=[-4, 4, 0.5],
            y_range=[-3, 3, 0.5],
            line_color=WHITE,
            max_anchors_per_line=30,
            stroke_width=2
        )
        stream.start_animation()

        # Vortex core highlight
        core = Circle(radius=0.5, color=YELLOW)
        core.set_fill(opacity=0.2)

        # Footer
        _footer = Text("Made by Imagio", font_size=15, color=WHITE)
        _footer.to_corner(DR, buff=0.25)
        self.add(_footer)

        # Animation sequence with voiceovers
        with self.voiceover(text="Here we see a colorful map of pressure, cooler near the center and warmer outward."):
            self.play(FadeIn(title), FadeIn(pressure_plane), run_time=3)

        with self.voiceover(text="Next, arrows illustrate the velocity field, circling around the low‑pressure core."):
            self.play(FadeIn(vortex_field), run_time=3)

        with self.voiceover(text="Streamlines trace the exact paths a particle would follow in this rotating flow."):
            self.play(FadeIn(stream), run_time=3)

        with self.voiceover(text="At the heart lies a vortex, where rotation is strongest."):
            self.play(FadeIn(core), run_time=2)

        self.wait(2)
        self.play(FadeOut(*self.mobjects))