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

        import os, textwrap

        title = Text('The Double Slit Experiment', font_size=40, color=WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=0.8)

        # ── Image (with fallback placeholder) ─────────────────────
        image_path = ''
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
        with self.voiceover(text='Let us look at the famous double slit experiment setup.'):
            self.play(FadeIn(image), run_time=0.8)

        # ── Caption ───────────────────────────────────────────────
        if 'Light behaves as both a wave and a particle':
            wrapped_cap = '\n'.join(textwrap.wrap('Light behaves as both a wave and a particle', width=30))
            caption_obj = Paragraph(wrapped_cap, font_size=18,
                color='#a0a8d0', alignment='center')
            caption_obj.next_to(image, DOWN, buff=0.2)
            with self.voiceover(text='Light and matter behave simultaneously as both waves and particles.'):
                self.play(FadeIn(caption_obj), run_time=0.5)

        # ── Body text ─────────────────────────────────────────────
        if 'When electrons pass through two narrow slits, they create an interference pattern on the detector, even when fired one at a time. This demonstrates wave-particle duality.':
            wrapped_body = '\n'.join(textwrap.wrap('When electrons pass through two narrow slits, they create an interference pattern on the detector, even when fired one at a time. This demonstrates wave-particle duality.', width=35))
            body = Paragraph(wrapped_body, font_size=24, color=WHITE,
                line_spacing=1.2, alignment='left')
            body.move_to(RIGHT * 3.2 + DOWN * 0.3)
            if body.height > 5:
                body.scale(5 / body.height)
            with self.voiceover(text='Electrons fired one at a time still produce an interference pattern, revealing their wave nature.'):
                self.play(FadeIn(body, shift=LEFT * 0.2), run_time=0.9)

        self.wait(1)
        self.play(FadeOut(*self.mobjects))
        self.wait(0.3)

