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

        notice = Text(
            "This is a custom animation on a blank canvas.",
            font_size=32, color='#ff6b6b'
        )
        notice.move_to(ORIGIN)
        with self.voiceover(text="This is a custom animation on a blank canvas."):
            self.play(Write(notice))
        self.wait(0.3)
