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

        title = Text('Déduction de la loi de gravitation universelle', font_size=32, color=YELLOW, weight=BOLD)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=0.8, rate_func=smooth)
        self.wait(0.3)

        steps_latex     = ['F \\propto \\frac{m_1 m_2}{r^2}', 'F = G\\,\\frac{m_1 m_2}{r^2}', '\\boxed{F = G\\frac{m_1 m_2}{r^2}}']
        annotations     = ['Force proportionnelle au produit des masses et inverse du carré de la distance', 'On introduit la constante gravitationnelle G', 'Forme finale, prête à l’usage']
        narrations_data = ['La force augmente avec les masses et décroît avec le carré de la distance.', 'On ajoute la constante G pour convertir la proportion en égalité exacte.', 'On obtient la formule finale qui relie force, masses et distance.']

        current_eq   = MathTex(steps_latex[0], font_size=54, color=WHITE)
        current_eq.move_to(ORIGIN + UP * 0.5)
        current_note = Text(annotations[0], font_size=26, color='#a0a8d0')
        current_note.next_to(current_eq, DOWN, buff=0.4)

        with self.voiceover(text=narrations_data[0]):
            self.play(Write(current_eq), run_time=1.0, rate_func=smooth)
            if annotations[0]:
                self.play(FadeIn(current_note, shift=UP * 0.1), run_time=0.5)
            self.wait(0.3)

        for i in range(1, len(steps_latex)):
            next_eq   = MathTex(steps_latex[i], font_size=54, color=WHITE)
            next_eq.move_to(ORIGIN + UP * 0.5)
            next_note = Text(annotations[i], font_size=26, color='#a0a8d0')
            next_note.next_to(next_eq, DOWN, buff=0.4)

            with self.voiceover(text=narrations_data[i]):
                self.play(
                    TransformMatchingShapes(current_eq, next_eq),
                    run_time=1.1, rate_func=smooth,
                )
                self.wait(0.2)
                if annotations[i - 1]:
                    self.play(FadeOut(current_note), run_time=0.3)
                if annotations[i]:
                    self.play(FadeIn(next_note, shift=UP * 0.1), run_time=0.45)
                self.wait(0.25)

            current_eq   = next_eq
            current_note = next_note

        self.wait(2)
        self.play(FadeOut(*self.mobjects), run_time=0.8)

        self.wait(0.5)  # scene exit buffer
