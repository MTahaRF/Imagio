from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.piper import PiperTTSService

class ImagioScene(VoiceoverScene, ThreeDScene):
    def construct(self):
        self.set_speech_service(PiperTTSService())
        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)

        grid = Surface(
            lambda u, v: np.array([u, v, 0]),
            u_range=[-5, 5],
            v_range=[-5, 5],
            resolution=(15, 15),
            fill_opacity=0,
            stroke_color=BLUE_D,
            stroke_width=1
        )

        with self.voiceover(text='Imagine the universe as a vast, flexible fabric stretched tight across the cosmos. In its empty state, this fabric is perfectly flat.'):
            self.play(Create(grid))
            self.wait(1)

        mass = Sphere(radius=0.6, color=YELLOW).move_to([0, 0, -2.0])

        with self.voiceover(text='But when we introduce a massive object, like a star, the fabric yields, curving downward. This distortion changes the very geometry of the environment.'):
            self.play(
                grid.animate.apply_function(lambda p: np.array([p[0], p[1], -3.0 / (1 + p[0]**2 + p[1]**2)])),
                FadeIn(mass, shift=IN),
                run_time=3
            )

        def orbit_func(t):
            r = 3 - 0.1 * t
            z = -3.0 / (1 + r**2) + 0.15
            return np.array([r * np.cos(2*t), r * np.sin(2*t), z])

        marble = Sphere(radius=0.15, color=RED)
        marble_path = ParametricFunction(orbit_func, t_range=[0, 10])

        with self.voiceover(text='A smaller marble nearby follows the natural contours of the warped surface, spiraling inward. Mass tells space how to curve, and curvature tells matter how to move.'):
            self.play(MoveAlongPath(marble, marble_path), run_time=6, rate_func=linear)

        _footer = Text('Made by Imagio', font_size=15, color=WHITE)
        _footer.to_corner(DR, buff=0.25)
        self.add(_footer)