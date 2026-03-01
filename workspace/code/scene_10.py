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

        term_text = Text('Gravity', font_size=52, color=YELLOW, weight=BOLD)
        term_text.to_edge(UP, buff=0.5)
        box = SurroundingRectangle(term_text, color=YELLOW, buff=0.18,
            corner_radius=0.12, stroke_width=2)
        with self.voiceover(text='Let’s talk about gravity, the universal pull that shapes our world.'):
            self.play(Write(term_text), Create(box), run_time=1.0)

        defn_label   = Text('Definition:', font_size=22, color='#a0a8d0')
        wrapped_defn = '\n'.join(textwrap.wrap('Gravity is the force (or spacetime curvature) that pulls masses together, governing everything from falling apples to planetary motion.', width=60))
        defn_text    = Paragraph(wrapped_defn, font_size=27, color=WHITE,
            line_spacing=1.2, alignment='left')
        defn_group   = VGroup(defn_label, defn_text).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        defn_group.next_to(box, DOWN, buff=0.4).to_edge(LEFT, buff=0.8)
        with self.voiceover(text='Gravity is the force—or, in Einstein’s view, the curvature of spacetime—that draws any two masses toward each other.'):
            self.play(FadeIn(defn_group, shift=UP * 0.2), run_time=0.8)

        y_ref = defn_group
        if 'F = G \\\\frac{m_1 m_2}{r^2}':
            formula_obj = MathTex('F = G \\\\frac{m_1 m_2}{r^2}', font_size=52, color=BLUE)
            formula_obj.next_to(defn_group, DOWN, buff=0.5).to_edge(LEFT, buff=1.5)
            with self.voiceover(text='Mathematically, the attraction between two masses follows Newton’s law: F equals G times the product of the masses divided by the square of their separation.'):
                self.play(Write(formula_obj), run_time=1.0)
            y_ref = formula_obj

        if 'A dropped apple accelerates toward Earth at about 9.8\u202fm/s², illustrating gravity’s pull on everyday objects.':
            ex_label   = Text('Example:', font_size=22, color='#a0a8d0')
            wrapped_ex = '\n'.join(textwrap.wrap('A dropped apple accelerates toward Earth at about 9.8\u202fm/s², illustrating gravity’s pull on everyday objects.', width=65))
            ex_text    = Paragraph(wrapped_ex, font_size=27,
                color='#c8d0f0', line_spacing=1.2, alignment='left')
            ex_group   = VGroup(ex_label, ex_text).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
            ex_group.next_to(y_ref, DOWN, buff=0.5).to_edge(LEFT, buff=0.8)
            with self.voiceover(text='Think of an apple falling from a tree; it speeds up at roughly nine point eight meters per second squared because of Earth’s gravity.'):
                self.play(FadeIn(ex_group, shift=UP * 0.15), run_time=0.6)

        self.wait(1)
        self.play(FadeOut(*self.mobjects))
        self.wait(0.3)

