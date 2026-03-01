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
        title = Text('Ladder Problem Constraints', font_size=48, color=YELLOW, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        underline = Line(
            title.get_left(), title.get_right(),
            color=YELLOW, stroke_width=2,
        )
        underline.next_to(title, DOWN, buff=0.1)
        self.play(Write(title), Create(underline), run_time=1.0)

        # ── Bullet points ─────────────────────────────────────────
        # Font size pre-computed: 28pt  row spacing: 0.36
        raw_points = ['Wall is vertical, floor is horizontal', 'Ladder touches the window at height h', 'Base of ladder is distance x from the wall', 'Find the minimal ladder length L']
        bullet_group = VGroup()

        for text in raw_points:
            dot = Text("*", font_size=28, color=YELLOW)
            label = Text(text, font_size=28, color=WHITE)
            # Wrap long lines inside the available width (10 units)
            label.set_width(min(label.width, 10.0))
            row = VGroup(dot, label).arrange(RIGHT, buff=0.28, aligned_edge=UP)
            bullet_group.add(row)

        bullet_group.arrange(DOWN, buff=0.36, aligned_edge=LEFT)
        bullet_group.next_to(underline, DOWN, buff=0.45)
        bullet_group.to_edge(LEFT, buff=0.75)

        for row in bullet_group:
            self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.5)

        self.wait(2)
        self.play(FadeOut(*self.mobjects))
        self.wait(0.3)
