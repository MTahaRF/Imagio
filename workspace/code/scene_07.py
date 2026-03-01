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

        title   = Text('L’équation de champ d’Einstein', font_size=44, color=WHITE, weight=BOLD)
        divider = Line(UP * 2.8, DOWN * 3.0, color='#3a3a5c', stroke_width=2)
        title.to_edge(UP, buff=0.4)
        with self.voiceover(text='Voici l’équation de champ d’Einstein, le cœur de la relativité générale.'):
            self.play(Write(title), run_time=0.8, rate_func=smooth)
            self.wait(0.2)
            self.play(Create(divider), run_time=0.5)
            self.wait(0.2)

        l_header  = Text('Formule', font_size=28, color=YELLOW)
        l_formula = MathTex('$G_{\\mu\\nu}+\\Lambda g_{\\mu\\nu}=\\frac{8\\pi G}{c^{4}} T_{\\mu\\nu}$', font_size=54, color=WHITE)
        l_header.move_to(LEFT * 3.2 + UP * 1.8)
        l_formula.move_to(LEFT * 3.2)
        with self.voiceover(text='L’équation s’écrit\u202f: $G_{\\mu\\nu}+ \\Lambda g_{\\mu\\nu}= \\frac{8\\pi G}{c^{4}} T_{\\mu\\nu}$.'):
            self.play(FadeIn(l_header, shift=DOWN*0.1), run_time=0.4)
            self.wait(0.15)
            self.play(Write(l_formula), run_time=1.1, rate_func=smooth)
            self.wait(0.3)

        r_header = Text('Signification des termes', font_size=28, color=YELLOW)
        r_header.move_to(RIGHT * 3.0 + UP * 1.8)
        self.play(FadeIn(r_header, shift=DOWN*0.1), run_time=0.4)
        self.wait(0.2)

        raw_lines       = ['$G_{\\mu\\nu}$\u202f: courbure de l’espace‑temps due à la matière.', '$\\Lambda g_{\\mu\\nu}$\u202f: énergie du vide, responsable de l’accélération cosmique.', '$\\frac{8\\pi G}{c^{4}}$\u202f: facteur de conversion entre géométrie et énergie.', '$T_{\\mu\\nu}$\u202f: distribution de masse‑énergie et de flux de moment.']
        narrations_data = ['Le terme $G_{\\mu\\nu}$ représente le tenseur d’Einstein, qui encode comment l’espace‑temps se courbe sous l’influence de la matière.', 'Le produit $\\Lambda g_{\\mu\\nu}$ introduit la constante cosmologique, une énergie du vide qui pousse l’expansion de l’univers.', 'Le facteur $\\frac{8\\pi G}{c^{4}}$ convertit la densité d’énergie en courbure, reliant gravitation et relativité.', 'Enfin $T_{\\mu\\nu}$ est le tenseur énergie‑impulsion, décrivant la distribution de masse, d’énergie et de flux de moment.']
        r_group = VGroup(*[
            Text(line, font_size=25, color=WHITE) for line in raw_lines
        ]).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        r_group.set_width(min(r_group.width, 5.2))
        r_group.move_to(RIGHT * 3.0)

        for line_obj, narration in zip(r_group, narrations_data):
            with self.voiceover(text=narration):
                self.play(
                    FadeIn(line_obj, shift=UP * 0.12),
                    run_time=0.5, rate_func=smooth,
                )
                self.wait(0.2)

        self.wait(2)
        self.play(FadeOut(*self.mobjects), run_time=0.8)

        self.wait(0.5)  # scene exit buffer
