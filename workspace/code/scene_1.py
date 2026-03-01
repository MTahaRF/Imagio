from manim import *

class ImagioScene(Scene):
    def construct(self):
        self.camera.background_color = "#0f0f23"

        # ── Imagio Footer ──────────────────────────────────────
        _footer = Text('Made by Imagio', font_size=15, color=WHITE)
        _footer.to_corner(DR, buff=0.25)
        self.add(_footer)
        # ───────────────────────────────────────────────────────

        # ── Title ─────────────────────────────────────────────────
        title = Text(
            'Unlocking Right Triangles: How the Pythagorean Theorem Works',
            font_size=72,
            color=WHITE,
            weight=BOLD,
        )
        title.move_to(ORIGIN + UP * 0.6)

        # ── Subtitle ───────────────────────────────────────────────
        subtitle = Text(
            'Discover the fundamental relationship between the sides of a right triangle',
            font_size=36,
            color="#a0a8d0",
        )
        subtitle.next_to(title, DOWN, buff=0.5)

        # ── Accent line ────────────────────────────────────────────
        line = Line(LEFT * 3, RIGHT * 3, color=YELLOW, stroke_width=3)
        line.next_to(title, DOWN, buff=0.25)

        # ── Animations ────────────────────────────────────────────
        self.play(Write(title), run_time=1.2)
        self.play(Create(line), run_time=0.6)
        self.play(FadeIn(subtitle, shift=UP * 0.2), run_time=0.8)
        self.wait(2)
        self.play(FadeOut(*self.mobjects))
        self.wait(0.3)
