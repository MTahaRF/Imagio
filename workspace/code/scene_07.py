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

        import textwrap
        title = Text('Newtonian vs Einsteinian Gravity', font_size=42, color=WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=0.8)

        col_h    = 5.8
        left_bg  = RoundedRectangle(corner_radius=0.15, width=6.5, height=col_h,
            fill_color='#16213e', fill_opacity=1, stroke_color='#3a5a8a', stroke_width=2)
        right_bg = RoundedRectangle(corner_radius=0.15, width=6.5, height=col_h,
            fill_color='#1e1630', fill_opacity=1, stroke_color='#8a3a5a', stroke_width=2)
        left_bg.next_to(title, DOWN, buff=0.3).to_edge(LEFT, buff=0.2)
        right_bg.next_to(title, DOWN, buff=0.3).to_edge(RIGHT, buff=0.2)
        self.play(FadeIn(left_bg), FadeIn(right_bg), run_time=0.5)

        l_hdr  = Text('Newtonian (Force View)', font_size=28, color=BLUE, weight=BOLD)
        r_hdr  = Text('Einsteinian (Spacetime Curvature)', font_size=28, color='#ff6b9d', weight=BOLD)
        l_hdr.move_to(left_bg.get_top() + DOWN * 0.42)
        r_hdr.move_to(right_bg.get_top() + DOWN * 0.42)
        l_line = Line(left_bg.get_left()+RIGHT*0.3, left_bg.get_right()+LEFT*0.3,
            color=BLUE).next_to(l_hdr, DOWN, buff=0.12)
        r_line = Line(right_bg.get_left()+RIGHT*0.3, right_bg.get_right()+LEFT*0.3,
            color='#ff6b9d').next_to(r_hdr, DOWN, buff=0.12)
        self.play(Write(l_hdr), Write(r_hdr), Create(l_line), Create(r_line), run_time=0.7)

        left_list       = ['Gravity is a force acting at a distance', 'Objects follow trajectories given by the inverse‑square law']
        right_list      = ['Gravity is the geometry of spacetime', 'Objects follow geodesics, the straightest possible paths']
        narrations_data = ['Newton describes gravity as an invisible pull between masses, while Einstein describes it as the bending of spacetime itself.', 'In Newton’s picture planets accelerate toward the Sun, whereas in Einstein’s picture they glide along curved spacetime, feeling no force.']
        max_rows = max(len(left_list), len(right_list))

        for idx in range(max_rows):
            anims    = []
            narration = narrations_data[idx] if idx < len(narrations_data) else ''
            if idx < len(left_list):
                wrapped  = '\n'.join(textwrap.wrap(left_list[idx], width=28))
                l_bullet = Text('-', font_size=21, color=BLUE)
                l_label  = Paragraph(wrapped, font_size=21, color=WHITE)
                l_item   = VGroup(l_bullet, l_label).arrange(RIGHT, buff=0.2, aligned_edge=UP)
                l_item.next_to(l_line, DOWN, buff=0.3 + idx * 0.8)
                l_item.align_to(left_bg, LEFT).shift(RIGHT * 0.3)
                anims.append(FadeIn(l_item, shift=RIGHT * 0.2))
            if idx < len(right_list):
                wrapped  = '\n'.join(textwrap.wrap(right_list[idx], width=28))
                r_bullet = Text('-', font_size=21, color='#ff6b9d')
                r_label  = Paragraph(wrapped, font_size=21, color=WHITE)
                r_item   = VGroup(r_bullet, r_label).arrange(RIGHT, buff=0.2, aligned_edge=UP)
                r_item.next_to(r_line, DOWN, buff=0.3 + idx * 0.8)
                r_item.align_to(right_bg, LEFT).shift(RIGHT * 0.3)
                anims.append(FadeIn(r_item, shift=RIGHT * 0.2))
            with self.voiceover(text=narration):
                self.play(*anims, run_time=0.5)

        self.wait(1)
        self.play(FadeOut(*self.mobjects))
        self.wait(0.3)

