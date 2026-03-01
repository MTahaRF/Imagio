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

        title = Text('Récapitulatif et perspectives futures', font_size=38, color=YELLOW, weight=BOLD)
        title.to_edge(UP, buff=0.45)
        underline = Line(title.get_left(), title.get_right(), color=YELLOW, stroke_width=2)
        underline.next_to(title, DOWN, buff=0.1)
        self.play(
            AnimationGroup(Write(title), Create(underline), lag_ratio=0.4),
            run_time=0.9, rate_func=smooth,
        )
        self.wait(0.35)

        raw_points       = ['Gravité au cœur de nos technologies quotidiennes (GPS, satellites)', 'Exploitation des phénomènes extrêmes (trous noirs, ondes gravitationnelles)', 'Avenir : colonies lunaires, propulsion gravitationnelle, détection d’ondes gravitationnelles plus sensible']
        narrations_data  = ['Le GPS et les satellites utilisent les corrections relativistes pour maintenir une précision de quelques mètres, montrant l’impact quotidien de la gravité.', 'Près des trous noirs, la courbure de l’espace‑temps permet des manœuvres de freinage gravitationnel, ouvrant des possibilités inédites pour les sondes.', 'Les futurs projets visent l’exploration interstellaire, la détection plus sensible d’ondes gravitationnelles et la propulsion basée sur la gravité.']
        bullet_group = VGroup()
        for text in raw_points:
            dot   = Text('*', font_size=25, color=YELLOW)
            label = Text(text, font_size=25, color=WHITE)
            label.set_width(min(label.width, 10.0))
            row = VGroup(dot, label).arrange(RIGHT, buff=0.28, aligned_edge=UP)
            bullet_group.add(row)
        bullet_group.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        bullet_group.next_to(underline, DOWN, buff=0.4)
        bullet_group.to_edge(LEFT, buff=0.75)

        for row, narration in zip(bullet_group, narrations_data):
            with self.voiceover(text=narration):
                self.play(
                    FadeIn(row, shift=RIGHT * 0.25),
                    run_time=0.55, rate_func=smooth,
                )
                self.wait(0.2)

        self.wait(2)
        self.play(FadeOut(*self.mobjects), run_time=0.8)

        self.wait(0.5)  # scene exit buffer
