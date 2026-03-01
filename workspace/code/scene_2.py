from manim import *
import os
import textwrap

class ImagioScene(Scene):
    def construct(self):
        self.camera.background_color = "#0f0f23"

        # ── Title ─────────────────────────────────────────────────
        title = Text('The Ladder Problem', font_size=40, color=WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=0.8)

        # ── Image (with fallback placeholder) ─────────────────────
        image_path = 'ladder_wall_window.jpg'
        if image_path and os.path.exists(image_path):
            image = ImageMobject(image_path)
            image.set_height(4.0)
        else:
            image = Rectangle(
                width=5.0, height=3.6,
                fill_color="#2a2a4a", fill_opacity=1,
                stroke_color="#666688", stroke_width=2,
            )
            placeholder_label = Text("[ Image ]", font_size=26, color="#666688")
            placeholder_label.move_to(image.get_center())
            image = VGroup(image, placeholder_label)

        image.move_to(LEFT * 3.0 + DOWN * 0.3)
        self.play(FadeIn(image), run_time=0.8)

        # ── Caption ───────────────────────────────────────────────
        if 'A ladder leaning against a wall with a window':
            # Wrap caption if it's too long for the image width
            wrapped_cap = "\n".join(textwrap.wrap('A ladder leaning against a wall with a window', width=30))
            caption_obj = Paragraph(
                wrapped_cap,
                font_size=18,
                color="#a0a8d0",
                alignment="center"
            )
            caption_obj.next_to(image, DOWN, buff=0.2)
            self.play(FadeIn(caption_obj), run_time=0.5)

        # ── Body text (right side) ────────────────────────────────
        if 'What is the minimum length of ladder needed to reach the window? This classic optimization problem involves finding the shortest distance while avoiding the corner where the wall meets the ground.':
            # textwrap.wrap converts the long string into a list of lines
            # we join them with \n so Paragraph can render them as lines
            wrapped_body = "\n".join(textwrap.wrap('What is the minimum length of ladder needed to reach the window? This classic optimization problem involves finding the shortest distance while avoiding the corner where the wall meets the ground.', width=35))
            
            body = Paragraph(
                wrapped_body,
                font_size=24,
                color=WHITE,
                line_spacing=1.2,
                alignment="left"
            )
            
            # Position the paragraph relative to the right side
            body.move_to(RIGHT * 3.2 + DOWN * 0.3)
            
            # Safety check: If paragraph is still too tall, scale it slightly
            if body.height > 5:
                body.scale(5 / body.height)
                
            self.play(FadeIn(body, shift=LEFT * 0.2), run_time=0.9)

        self.wait(2)
        self.play(FadeOut(*self.mobjects))
        self.wait(0.3)
