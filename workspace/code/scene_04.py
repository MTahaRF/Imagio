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

        import os, textwrap

        title = Text("Courbure de l'espace‑temps autour d'une masse", font_size=32, color=WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=0.8, rate_func=smooth)
        self.wait(0.3)

        image_path = 'images/spacetime_curvature.png'
        if image_path and os.path.exists(image_path):
            image = ImageMobject(image_path)
            image.set_height(4.0)
        else:
            placeholder = Rectangle(width=5.0, height=3.6,
                fill_color='#2a2a4a', fill_opacity=1,
                stroke_color='#666688', stroke_width=2)
            label = Text('[ Image ]', font_size=26, color='#666688')
            label.move_to(placeholder.get_center())
            image = VGroup(placeholder, label)
        image.move_to(LEFT * 3.0 + DOWN * 0.3)
        with self.voiceover(text="Voici la visualisation de la courbure de l'espace‑temps autour d'une masse, comme un drap qui s'enfonce sous un poids."):
            self.play(FadeIn(image, shift=RIGHT * 0.15), run_time=0.8, rate_func=smooth)
            self.wait(0.3)

        if "Déformation du tissu d'espace‑temps provoquée par une masse":
            wrapped_cap = '\n'.join(textwrap.wrap("Déformation du tissu d'espace‑temps provoquée par une masse", width=30))
            caption_obj = Paragraph(wrapped_cap, font_size=18,
                color='#a0a8d0', alignment='center')
            caption_obj.next_to(image, DOWN, buff=0.18)
            with self.voiceover(text='Cette image montre le creux créé par la masse.'):
                self.play(FadeIn(caption_obj, shift=UP*0.1), run_time=0.5)
                self.wait(0.25)

        if "Selon la relativité générale, la présence d'une masse modifie la géométrie du continuum espace‑temps. Cette déformation se représente comme un creux dans un drap élastique. Tout objet qui se déplace à proximité suit la trajectoire la plus courte – une géodésique – dans ce paysage courbé, ce qui apparaît comme une attraction gravitationnelle. Ainsi, la Terre tourne autour du Soleil non pas parce qu'une force invisible l'attire, mais parce que le Soleil crée une courbure qui guide le chemin de la Terre.":
            wrapped_body = '\n'.join(textwrap.wrap("Selon la relativité générale, la présence d'une masse modifie la géométrie du continuum espace‑temps. Cette déformation se représente comme un creux dans un drap élastique. Tout objet qui se déplace à proximité suit la trajectoire la plus courte – une géodésique – dans ce paysage courbé, ce qui apparaît comme une attraction gravitationnelle. Ainsi, la Terre tourne autour du Soleil non pas parce qu'une force invisible l'attire, mais parce que le Soleil crée une courbure qui guide le chemin de la Terre.", width=35))
            body = Paragraph(wrapped_body, font_size=16, color=WHITE,
                line_spacing=1.2, alignment='left')
            body.move_to(RIGHT * 3.2 + DOWN * 0.3)
            if body.height > 5:
                body.scale(5 / body.height)
            with self.voiceover(text="La masse déforme l'espace‑temps, et les corps suivent les géodésiques de ce tissu courbé, ce qui se manifeste comme la gravité que nous ressentons."):
                self.play(FadeIn(body, shift=LEFT * 0.15), run_time=0.9, rate_func=smooth)
                self.wait(0.3)

        self.wait(2)
        self.play(FadeOut(*self.mobjects), run_time=0.8)

        self.wait(0.5)  # scene exit buffer
