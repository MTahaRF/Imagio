from manim import *
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from manim_voiceover import VoiceoverScene
from services.piper_service import PiperTTSService

class ImagioScene(VoiceoverScene):
    def construct(self):
        self.camera.background_color = "#0f0f23"
        self.set_speech_service(PiperTTSService(voice='fr_FR-siwis-medium'))

        _footer = Text('Made by Imagio', font_size=15, color=WHITE)
        _footer.to_corner(DR, buff=0.25)
        self.add(_footer)

        self.wait(0.5)  # scene entry buffer

        import textwrap

        title = Text("Applications de la gravité dans la technologie et l'exploration", font_size=27, color=WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=0.8, rate_func=smooth)
        self.wait(0.3)

        col_h    = 5.6
        left_bg  = RoundedRectangle(corner_radius=0.15, width=6.5, height=col_h,
            fill_color='#16213e', fill_opacity=1, stroke_color='#3a5a8a', stroke_width=2)
        right_bg = RoundedRectangle(corner_radius=0.15, width=6.5, height=col_h,
            fill_color='#1e1630', fill_opacity=1, stroke_color='#8a3a5a', stroke_width=2)
        left_bg.next_to(title, DOWN, buff=0.25).to_edge(LEFT, buff=0.2)
        right_bg.next_to(title, DOWN, buff=0.25).to_edge(RIGHT, buff=0.2)
        self.play(
            AnimationGroup(FadeIn(left_bg, shift=RIGHT*0.1), FadeIn(right_bg, shift=LEFT*0.1), lag_ratio=0.1),
            run_time=0.6, rate_func=smooth,
        )

        l_hdr  = Text('Applications proches de la Terre', font_size=28, color=BLUE, weight=BOLD)
        r_hdr  = Text('Applications extrêmes', font_size=28, color='#ff6b9d', weight=BOLD)
        l_hdr.move_to(left_bg.get_top() + DOWN * 0.42)
        r_hdr.move_to(right_bg.get_top() + DOWN * 0.42)
        l_line = Line(left_bg.get_left()+RIGHT*0.3, left_bg.get_right()+LEFT*0.3,
            color=BLUE).next_to(l_hdr, DOWN, buff=0.12)
        r_line = Line(right_bg.get_left()+RIGHT*0.3, right_bg.get_right()+LEFT*0.3,
            color='#ff6b9d').next_to(r_hdr, DOWN, buff=0.12)
        self.play(
            AnimationGroup(Write(l_hdr), Write(r_hdr), Create(l_line), Create(r_line), lag_ratio=0.15),
            run_time=0.7,
        )
        self.wait(0.25)

        left_list       = ['GPS – corrections relativistes pour la localisation', "Satellites de communication – maintien d'orbite stable"]
        right_list      = ['Missions vers les trous noirs – navigation gravitationnelle', "Détecteurs d'ondes gravitationnelles – test de la relativité"]
        narrations_data = ["Le GPS doit ajuster son horloge grâce à la dilatation du temps, alors que les sondes vers les trous noirs utilisent la courbure de l'espace‑temps pour tracer leur trajectoire.", "Les satellites de communication restent en orbite grâce à l'équilibre gravité‑centrifuge, tandis que les détecteurs d'ondes gravitationnelles mesurent les minuscules déformations du champ gravitationnel lointain."]
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
                anims.append(FadeIn(l_item, shift=RIGHT * 0.18))
            if idx < len(right_list):
                wrapped  = '\n'.join(textwrap.wrap(right_list[idx], width=28))
                r_bullet = Text('-', font_size=21, color='#ff6b9d')
                r_label  = Paragraph(wrapped, font_size=21, color=WHITE)
                r_item   = VGroup(r_bullet, r_label).arrange(RIGHT, buff=0.2, aligned_edge=UP)
                r_item.next_to(r_line, DOWN, buff=0.3 + idx * 0.8)
                r_item.align_to(right_bg, LEFT).shift(RIGHT * 0.3)
                anims.append(FadeIn(r_item, shift=LEFT * 0.18))
            with self.voiceover(text=narration):
                self.play(
                    AnimationGroup(*anims, lag_ratio=0.2),
                    run_time=0.55, rate_func=smooth,
                )
                self.wait(0.2)

        self.wait(2)
        self.play(FadeOut(*self.mobjects), run_time=0.8)

        self.wait(0.5)  # scene exit buffer
