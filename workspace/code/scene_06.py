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

        term_text = Text('Relativité générale', font_size=44, color=YELLOW, weight=BOLD)
        term_text.to_edge(UP, buff=0.45)
        box = SurroundingRectangle(term_text, color=YELLOW, buff=0.18,
            corner_radius=0.12, stroke_width=2)
        with self.voiceover(text='Le concept que nous définissons maintenant est la relativité générale.'):
            self.play(
                AnimationGroup(Write(term_text), Create(box), lag_ratio=0.35),
                run_time=0.9, rate_func=smooth,
            )
            self.wait(0.3)

        defn_label   = Text('Definition:', font_size=22, color='#a0a8d0')
        wrapped_defn = '\n'.join(textwrap.wrap("Théorie d'Einstein qui décrit la gravité comme la courbure de l'espace‑temps provoquée par la présence de masse‑énergie.", width=60))
        defn_text    = Paragraph(wrapped_defn, font_size=27, color=WHITE,
            line_spacing=1.2, alignment='left')
        defn_group   = VGroup(defn_label, defn_text).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        defn_group.next_to(box, DOWN, buff=0.35).to_edge(LEFT, buff=0.8)
        with self.voiceover(text='C’est la description d’Einstein où la gravité résulte de la courbure de l’espace‑temps par la masse‑énergie.'):
            self.play(FadeIn(defn_group, shift=UP * 0.15), run_time=0.7, rate_func=smooth)
            self.wait(0.3)

        y_ref = defn_group
        if '$G_{\\\\mu\\\\nu}+\\\\Lambda g_{\\\\mu\\\\nu}=\\\\frac{8\\\\pi G}{c^4} T_{\\\\mu\\\\nu}$':
            formula_obj = MathTex('$G_{\\\\mu\\\\nu}+\\\\Lambda g_{\\\\mu\\\\nu}=\\\\frac{8\\\\pi G}{c^4} T_{\\\\mu\\\\nu}$', font_size=52, color=BLUE)
            formula_obj.next_to(defn_group, DOWN, buff=0.45).to_edge(LEFT, buff=1.5)
            with self.voiceover(text='L’équation de champ relie la géométrie de l’espace‑temps à la distribution de matière et d’énergie.'):
                self.play(Write(formula_obj), run_time=0.9, rate_func=smooth)
                self.wait(0.3)
            y_ref = formula_obj

        if "La Terre déforme l'espace‑temps autour d'elle, faisant suivre à la Lune une trajectoire courbée qui apparaît comme une orbite.":
            ex_label   = Text('Example:', font_size=22, color='#a0a8d0')
            wrapped_ex = '\n'.join(textwrap.wrap("La Terre déforme l'espace‑temps autour d'elle, faisant suivre à la Lune une trajectoire courbée qui apparaît comme une orbite.", width=65))
            ex_text    = Paragraph(wrapped_ex, font_size=27,
                color='#c8d0f0', line_spacing=1.2, alignment='left')
            ex_group   = VGroup(ex_label, ex_text).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
            ex_group.next_to(y_ref, DOWN, buff=0.45).to_edge(LEFT, buff=0.8)
            with self.voiceover(text='Par exemple, la Terre crée une déformation qui guide la Lune le long d’une géodésique.'):
                self.play(FadeIn(ex_group, shift=UP * 0.12), run_time=0.6, rate_func=smooth)
                self.wait(0.3)

        self.wait(2)
        self.play(FadeOut(*self.mobjects), run_time=0.8)

        self.wait(0.5)  # scene exit buffer
