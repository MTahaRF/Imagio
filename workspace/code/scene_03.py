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

        term_text = Text('gravité', font_size=52, color=YELLOW, weight=BOLD)
        term_text.to_edge(UP, buff=0.45)
        box = SurroundingRectangle(term_text, color=YELLOW, buff=0.18,
            corner_radius=0.12, stroke_width=2)
        with self.voiceover(text='Voici le concept de gravité, la force qui attire les masses les unes vers les autres.'):
            self.play(
                AnimationGroup(Write(term_text), Create(box), lag_ratio=0.35),
                run_time=0.9, rate_func=smooth,
            )
            self.wait(0.3)

        defn_label   = Text('Definition:', font_size=22, color='#a0a8d0')
        wrapped_defn = '\n'.join(textwrap.wrap('Force d’attraction mutuelle entre toutes les masses, qui les fait se rapprocher.', width=60))
        defn_text    = Paragraph(wrapped_defn, font_size=30, color=WHITE,
            line_spacing=1.2, alignment='left')
        defn_group   = VGroup(defn_label, defn_text).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        defn_group.next_to(box, DOWN, buff=0.35).to_edge(LEFT, buff=0.8)
        with self.voiceover(text='La gravité est la force d’attraction mutuelle entre toutes les masses, les poussant à se rapprocher.'):
            self.play(FadeIn(defn_group, shift=UP * 0.15), run_time=0.7, rate_func=smooth)
            self.wait(0.3)

        y_ref = defn_group
        if 'F = G \\frac{m_1 m_2}{r^2}':
            formula_obj = MathTex('F = G \\frac{m_1 m_2}{r^2}', font_size=52, color=BLUE)
            formula_obj.next_to(defn_group, DOWN, buff=0.45).to_edge(LEFT, buff=1.5)
            with self.voiceover(text='La loi de Newton donne F égal à G fois le produit des masses divisé par le carré de la distance.'):
                self.play(Write(formula_obj), run_time=0.9, rate_func=smooth)
                self.wait(0.3)
            y_ref = formula_obj

        if 'Une balle lâchée tombe vers le sol parce que la Terre l’attire.':
            ex_label   = Text('Example:', font_size=22, color='#a0a8d0')
            wrapped_ex = '\n'.join(textwrap.wrap('Une balle lâchée tombe vers le sol parce que la Terre l’attire.', width=65))
            ex_text    = Paragraph(wrapped_ex, font_size=30,
                color='#c8d0f0', line_spacing=1.2, alignment='left')
            ex_group   = VGroup(ex_label, ex_text).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
            ex_group.next_to(y_ref, DOWN, buff=0.45).to_edge(LEFT, buff=0.8)
            with self.voiceover(text='Quand on laisse tomber une balle, elle tombe parce que la Terre exerce sur elle une force gravitationnelle.'):
                self.play(FadeIn(ex_group, shift=UP * 0.12), run_time=0.6, rate_func=smooth)
                self.wait(0.3)

        self.wait(2)
        self.play(FadeOut(*self.mobjects), run_time=0.8)

        self.wait(0.5)  # scene exit buffer
