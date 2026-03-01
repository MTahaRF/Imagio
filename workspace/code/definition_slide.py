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

        term_text = Text('Eigenvalue', font_size=52, color=YELLOW, weight=BOLD)
        term_text.to_edge(UP, buff=0.5)
        box = SurroundingRectangle(term_text, color=YELLOW, buff=0.18,
            corner_radius=0.12, stroke_width=2)
        with self.voiceover(text='Let us define the concept of an eigenvalue in linear algebra.'):
            self.play(Write(term_text), Create(box), run_time=1.0)

        defn_label   = Text('Definition:', font_size=22, color='#a0a8d0')
        wrapped_defn = '\n'.join(textwrap.wrap('A scalar lambda is an eigenvalue of a matrix A if there exists a non-zero vector v such that Av equals lambda times v.', width=60))
        defn_text    = Paragraph(wrapped_defn, font_size=27, color=WHITE,
            line_spacing=1.2, alignment='left')
        defn_group   = VGroup(defn_label, defn_text).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        defn_group.next_to(box, DOWN, buff=0.4).to_edge(LEFT, buff=0.8)
        with self.voiceover(text='An eigenvalue is a scalar that scales a vector without rotating it under a matrix transformation.'):
            self.play(FadeIn(defn_group, shift=UP * 0.2), run_time=0.8)

        y_ref = defn_group
        if 'A\\mathbf{v} = \\lambda\\mathbf{v}':
            formula_obj = MathTex('A\\mathbf{v} = \\lambda\\mathbf{v}', font_size=52, color=BLUE)
            formula_obj.next_to(defn_group, DOWN, buff=0.5).to_edge(LEFT, buff=1.5)
            with self.voiceover(text='This is expressed as A times v equals lambda times v.'):
                self.play(Write(formula_obj), run_time=1.0)
            y_ref = formula_obj

        if 'Stretching a vector without changing its direction':
            ex_label   = Text('Example:', font_size=22, color='#a0a8d0')
            wrapped_ex = '\n'.join(textwrap.wrap('Stretching a vector without changing its direction', width=65))
            ex_text    = Paragraph(wrapped_ex, font_size=30,
                color='#c8d0f0', line_spacing=1.2, alignment='left')
            ex_group   = VGroup(ex_label, ex_text).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
            ex_group.next_to(y_ref, DOWN, buff=0.5).to_edge(LEFT, buff=0.8)
            with self.voiceover(text='A simple example is stretching a vector along its own direction.'):
                self.play(FadeIn(ex_group, shift=UP * 0.15), run_time=0.6)

        self.wait(1)
        self.play(FadeOut(*self.mobjects))
        self.wait(0.3)

