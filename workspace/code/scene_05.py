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

        term_text = Text("Newton's law of universal gravitation", font_size=52, color=YELLOW, weight=BOLD)
        term_text.to_edge(UP, buff=0.5)
        box = SurroundingRectangle(term_text, color=YELLOW, buff=0.18,
            corner_radius=0.12, stroke_width=2)
        with self.voiceover(text='The principle we’re about to define is Newton’s law of universal gravitation.'):
            self.play(Write(term_text), Create(box), run_time=1.0)

        defn_label   = Text('Definition:', font_size=22, color='#a0a8d0')
        wrapped_defn = '\n'.join(textwrap.wrap("Newton's law of universal gravitation states that every pair of masses attracts each other with a force proportional to the product of their masses and inversely proportional to the square of the distance between their centers.", width=60))
        defn_text    = Paragraph(wrapped_defn, font_size=21, color=WHITE,
            line_spacing=1.2, alignment='left')
        defn_group   = VGroup(defn_label, defn_text).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        defn_group.next_to(box, DOWN, buff=0.4).to_edge(LEFT, buff=0.8)
        with self.voiceover(text='It says any two masses pull on each other with a force proportional to their product and inversely to the square of their separation.'):
            self.play(FadeIn(defn_group, shift=UP * 0.2), run_time=0.8)

        y_ref = defn_group
        if 'F = G \\frac{m_1 m_2}{r^2}':
            formula_obj = MathTex('F = G \\frac{m_1 m_2}{r^2}', font_size=52, color=BLUE)
            formula_obj.next_to(defn_group, DOWN, buff=0.5).to_edge(LEFT, buff=1.5)
            with self.voiceover(text='Mathematically, the force F equals G times the product of the masses divided by the distance squared.'):
                self.play(Write(formula_obj), run_time=1.0)
            y_ref = formula_obj

        if 'The gravitational force between Earth (mass 5.97×10^24 kg) and the Moon (mass 7.35×10^22 kg) separated by 3.84×10^8 m is about 1.98×10^20 newtons.':
            ex_label   = Text('Example:', font_size=22, color='#a0a8d0')
            wrapped_ex = '\n'.join(textwrap.wrap('The gravitational force between Earth (mass 5.97×10^24 kg) and the Moon (mass 7.35×10^22 kg) separated by 3.84×10^8 m is about 1.98×10^20 newtons.', width=65))
            ex_text    = Paragraph(wrapped_ex, font_size=27,
                color='#c8d0f0', line_spacing=1.2, alignment='left')
            ex_group   = VGroup(ex_label, ex_text).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
            ex_group.next_to(y_ref, DOWN, buff=0.5).to_edge(LEFT, buff=0.8)
            with self.voiceover(text='For Earth and the Moon, plugging in their masses and distance gives a force of roughly two hundred quintillion newtons.'):
                self.play(FadeIn(ex_group, shift=UP * 0.15), run_time=0.6)

        self.wait(1)
        self.play(FadeOut(*self.mobjects))
        self.wait(0.3)

