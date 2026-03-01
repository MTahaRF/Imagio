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

        self.wait(0.5)  # scene entry buffer

        # ── Title ─────────────────────────────────────────────────
        title = Text('Binary Search in Python', font_size=44, color=WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.35)
        lang_badge = Text('Python', font_size=18, color='#a0a8d0')
        lang_badge.next_to(title, RIGHT, buff=0.4)
        self.play(
            AnimationGroup(Write(title), FadeIn(lang_badge, shift=LEFT*0.1), lag_ratio=0.3),
            run_time=0.8,
        )
        self.wait(0.3)

        # ── Code block ────────────────────────────────────────────
        code_lines_data   = ['def binary_search(arr, target):', '    lo, hi = 0, len(arr) - 1', '    while lo <= hi:', '        mid = (lo + hi) // 2', '        if arr[mid] == target:', '            return mid', '        elif arr[mid] < target:', '            lo = mid + 1', '        else:', '            hi = mid - 1', '    return -1']
        explanations_data = ['Define the function with a sorted list and target', 'Initialise left and right pointers at the array bounds', 'Loop while the search window is valid', 'Compute the middle index', 'Target found — return its index', 'Target is larger — discard the left half', 'Move lo pointer past mid', 'Target is smaller — discard the right half', 'Move hi pointer below mid', 'Close the else block', 'Target not found — return negative one']
        narrations_data   = ['We define the binary search function taking a sorted array and a target value.', 'We initialise two pointers at the leftmost and rightmost positions.', 'We loop as long as the search window contains at least one element.', 'We calculate the middle index to check next.', 'If the middle element matches the target, we return its index immediately.', 'If the target is larger, we discard everything to the left of mid.', 'We shift the left pointer just past mid.', 'If the target is smaller, we discard everything to the right of mid.', 'We shift the right pointer just below mid.', 'This closes the else branch of our conditional check.', 'If the loop ends without a match, we return negative one to signal not found.']
        VIEWPORT = 8
        LINE_H   = 0.46

        code_block_bg = Rectangle(
            width=11, height=4.23,
            fill_color='#1e1e2e', fill_opacity=1,
            stroke_color='#44446a', stroke_width=1.5,
        )
        code_block_bg.next_to(title, DOWN, buff=0.25)
        self.play(FadeIn(code_block_bg, shift=UP*0.1), run_time=0.5)

        # ── Render all lines ──────────────────────────────────────
        CHAR_W   = 0.1329
        BASE_PAD = 0.38
        line_objects = []
        for i, raw_line in enumerate(code_lines_data):
            indent   = len(raw_line) - len(raw_line.lstrip(' '))
            visible  = raw_line.lstrip(' ') or ' '
            line_obj = Text(visible, font='Courier New', font_size=22, color='#555577')
            line_obj.move_to(code_block_bg.get_top() + DOWN * (0.35 + i * LINE_H))
            line_obj.align_to(code_block_bg, LEFT)
            line_obj.shift(RIGHT * (BASE_PAD + indent * CHAR_W))
            # Lines beyond the initial viewport start invisible
            if i >= VIEWPORT:
                line_obj.set_opacity(0)
            line_objects.append(line_obj)
        self.add(*line_objects)

        # ── Explanation box ───────────────────────────────────────
        explain_box = Rectangle(
            width=11, height=0.85,
            fill_color='#16213e', fill_opacity=1,
            stroke_color='#44446a', stroke_width=1.5,
        )
        explain_box.next_to(code_block_bg, DOWN, buff=0.2)
        self.play(FadeIn(explain_box, shift=UP*0.1), run_time=0.4)
        self.wait(0.2)

        # ── Walkthrough loop with scroll support ──────────────────
        highlight    = None
        explain_text = Text('', font_size=24, color=WHITE)

        for i, (line_obj, explanation, narration) in enumerate(
            zip(line_objects, explanations_data, narrations_data)
        ):
            new_highlight = SurroundingRectangle(
                line_obj, color=YELLOW, buff=0.07,
                stroke_width=1.5, fill_color='#2a2a4a', fill_opacity=0.5,
            )
            new_explain = Text(explanation, font_size=24, color='#c8d0f0')
            new_explain.move_to(explain_box.get_center())

            with self.voiceover(text=narration):
                pre_anims = []

                # Dim and clear previous highlight
                if highlight:
                    pre_anims += [
                        FadeOut(highlight),
                        FadeOut(explain_text),
                        line_objects[i - 1].animate.set_color('#555577'),
                    ]

                # Scroll: fade out departing line, shift remaining up
                if i >= VIEWPORT:
                    exit_line = line_objects[i - VIEWPORT]
                    pre_anims.append(exit_line.animate.set_opacity(0))
                    for obj in line_objects[i - VIEWPORT + 1 : i + 1]:
                        pre_anims.append(
                            obj.animate.shift(UP * LINE_H).set_opacity(1)
                        )

                if pre_anims:
                    self.play(*pre_anims, run_time=0.35, rate_func=smooth)

                self.play(
                    Create(new_highlight),
                    line_obj.animate.set_color(WHITE),
                    FadeIn(new_explain, shift=UP * 0.05),
                    run_time=0.5,
                    rate_func=smooth,
                )
                self.wait(0.2)

            highlight    = new_highlight
            explain_text = new_explain

        self.wait(1.5)
        self.play(FadeOut(*self.mobjects), run_time=0.8)

        self.wait(0.5)  # scene exit buffer
