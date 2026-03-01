from .base import BaseTemplate

class CodeWalkthroughTemplate(BaseTemplate):

    def description(self) -> str:
        return (
            "Use when a scene needs to display and explain a block of code line by line. "
            "Each line is highlighted in sequence with an explanation shown below. "
            "Supports scrolling for long code blocks. "
            "Do NOT use for mathematical proofs, graphs, or non-code content."
        )

    def schema(self) -> dict:
        return {
            "title":        "Heading for the code scene",
            "language":     "Programming language label (e.g. 'Python')",
            "code_lines":   ["def factorial(n):", "    if n == 0:", "    return 1"],
            "explanations": ["Explanation for line 1", "Explanation for line 2", "Explanation for line 3"],
            "narrations":   ["Spoken narration for line 1", "Narration for line 2", "Narration for line 3"],
        }

    def prompt(self) -> str:
        return (
            "You are filling JSON for a Manim code-walkthrough scene.\n"
            "Return ONLY a JSON object — no markdown, no explanation.\n\n"
            "Schema:\n"
            "{\n"
            '  "title": "Code scene heading", "language": "Python",\n'
            '  "code_lines": ["line 1", "line 2", "line 3"],\n'
            '  "explanations": ["explain line 1", "explain line 2", "explain line 3"],\n'
            '  "narrations": ["narration 1", "narration 2", "narration 3"]\n'
            "}\n\n"
            "Rules:\n"
            "- code_lines, explanations, and narrations must have the same length (3-12).\n"
            "- Each code_line is one line of real, syntactically correct code.\n"
            "- Each narration is a natural spoken sentence (max 25 words).\n"
            "- Preserve indentation using spaces, not tabs.\n"
        )

    @staticmethod
    def _code_font_size(n_lines: int, max_line_len: int) -> int:
        if n_lines <= 6  and max_line_len <= 40: return 26
        elif n_lines <= 8  and max_line_len <= 50: return 24
        elif n_lines <= 12 and max_line_len <= 55: return 22
        elif max_line_len <= 60:                   return 20
        else:                                      return 18

    @staticmethod
    def _line_h(font_size: int) -> float:
        if font_size >= 24: return 0.52
        elif font_size >= 20: return 0.46
        else: return 0.40

    def _scene_body(self, data: dict, script: str) -> str:
        title        = data.get("title", "Code Walkthrough")
        language     = data.get("language", "Python")
        code_lines   = data.get("code_lines", [])
        explanations = data.get("explanations", [""] * len(code_lines))
        narrations   = data.get("narrations",   [""] * len(code_lines))

        while len(explanations) < len(code_lines): explanations.append("")
        while len(narrations)   < len(code_lines): narrations.append("")

        n_lines      = len(code_lines)
        max_line_len = max((len(l) for l in code_lines), default=20)
        font_size    = self._code_font_size(n_lines, max_line_len)
        line_h       = self._line_h(font_size)
        title_fs     = self._title_font_size(title)

        VIEWPORT     = 8
        block_h      = round(min(VIEWPORT, n_lines) * line_h + 0.55, 3)

        code_lines_repr   = "[" + ", ".join(repr(l) for l in code_lines) + "]"
        explanations_repr = "[" + ", ".join(repr(e) for e in explanations) + "]"
        narrations_repr   = "[" + ", ".join(repr(n) for n in narrations) + "]"

        return (
            f"        # ── Title ─────────────────────────────────────────────────\n"
            f"        title = Text({title!r}, font_size={title_fs}, color=WHITE, weight=BOLD)\n"
            f"        title.to_edge(UP, buff=0.35)\n"
            f"        lang_badge = Text({language!r}, font_size=18, color='#a0a8d0')\n"
            f"        lang_badge.next_to(title, RIGHT, buff=0.4)\n"
            f"        self.play(\n"
            f"            AnimationGroup(Write(title), FadeIn(lang_badge, shift=LEFT*0.1), lag_ratio=0.3),\n"
            f"            run_time=0.8,\n"
            f"        )\n"
            f"        self.wait(0.3)\n"
            f"\n"
            f"        # ── Code block ────────────────────────────────────────────\n"
            f"        code_lines_data   = {code_lines_repr}\n"
            f"        explanations_data = {explanations_repr}\n"
            f"        narrations_data   = {narrations_repr}\n"
            f"        VIEWPORT = {VIEWPORT}\n"
            f"        LINE_H   = {line_h}\n"
            f"\n"
            f"        code_block_bg = Rectangle(\n"
            f"            width=11, height={block_h},\n"
            f"            fill_color='#1e1e2e', fill_opacity=1,\n"
            f"            stroke_color='#44446a', stroke_width=1.5,\n"
            f"        )\n"
            f"        code_block_bg.next_to(title, DOWN, buff=0.25)\n"
            f"        self.play(FadeIn(code_block_bg, shift=UP*0.1), run_time=0.5)\n"
            f"\n"
            f"        # ── Render all lines ──────────────────────────────────────\n"
            f"        CHAR_W   = {round(0.145 * font_size / 24, 4)}\n"
            f"        BASE_PAD = 0.38\n"
            f"        line_objects = []\n"
            f"        for i, raw_line in enumerate(code_lines_data):\n"
            f"            indent   = len(raw_line) - len(raw_line.lstrip(' '))\n"
            f"            visible  = raw_line.lstrip(' ') or ' '\n"
            f"            line_obj = Text(visible, font='Courier New', font_size={font_size}, color='#555577')\n"
            f"            line_obj.move_to(code_block_bg.get_top() + DOWN * (0.35 + i * LINE_H))\n"
            f"            line_obj.align_to(code_block_bg, LEFT)\n"
            f"            line_obj.shift(RIGHT * (BASE_PAD + indent * CHAR_W))\n"
            f"            # Lines beyond the initial viewport start invisible\n"
            f"            if i >= VIEWPORT:\n"
            f"                line_obj.set_opacity(0)\n"
            f"            line_objects.append(line_obj)\n"
            f"        self.add(*line_objects)\n"
            f"\n"
            f"        # ── Explanation box ───────────────────────────────────────\n"
            f"        explain_box = Rectangle(\n"
            f"            width=11, height=0.85,\n"
            f"            fill_color='#16213e', fill_opacity=1,\n"
            f"            stroke_color='#44446a', stroke_width=1.5,\n"
            f"        )\n"
            f"        explain_box.next_to(code_block_bg, DOWN, buff=0.2)\n"
            f"        self.play(FadeIn(explain_box, shift=UP*0.1), run_time=0.4)\n"
            f"        self.wait(0.2)\n"
            f"\n"
            f"        # ── Walkthrough loop with scroll support ──────────────────\n"
            f"        highlight    = None\n"
            f"        explain_text = Text('', font_size=24, color=WHITE)\n"
            f"\n"
            f"        for i, (line_obj, explanation, narration) in enumerate(\n"
            f"            zip(line_objects, explanations_data, narrations_data)\n"
            f"        ):\n"
            f"            new_highlight = SurroundingRectangle(\n"
            f"                line_obj, color=YELLOW, buff=0.07,\n"
            f"                stroke_width=1.5, fill_color='#2a2a4a', fill_opacity=0.5,\n"
            f"            )\n"
            f"            new_explain = Text(explanation, font_size=24, color='#c8d0f0')\n"
            f"            new_explain.move_to(explain_box.get_center())\n"
            f"\n"
            f"            with self.voiceover(text=narration):\n"
            f"                pre_anims = []\n"
            f"\n"
            f"                # Dim and clear previous highlight\n"
            f"                if highlight:\n"
            f"                    pre_anims += [\n"
            f"                        FadeOut(highlight),\n"
            f"                        FadeOut(explain_text),\n"
            f"                        line_objects[i - 1].animate.set_color('#555577'),\n"
            f"                    ]\n"
            f"\n"
            f"                # Scroll: fade out departing line, shift remaining up\n"
            f"                if i >= VIEWPORT:\n"
            f"                    exit_line = line_objects[i - VIEWPORT]\n"
            f"                    pre_anims.append(exit_line.animate.set_opacity(0))\n"
            f"                    for obj in line_objects[i - VIEWPORT + 1 : i + 1]:\n"
            f"                        pre_anims.append(\n"
            f"                            obj.animate.shift(UP * LINE_H).set_opacity(1)\n"
            f"                        )\n"
            f"\n"
            f"                if pre_anims:\n"
            f"                    self.play(*pre_anims, run_time=0.35, rate_func=smooth)\n"
            f"\n"
            f"                self.play(\n"
            f"                    Create(new_highlight),\n"
            f"                    line_obj.animate.set_color(WHITE),\n"
            f"                    FadeIn(new_explain, shift=UP * 0.05),\n"
            f"                    run_time=0.5,\n"
            f"                    rate_func=smooth,\n"
            f"                )\n"
            f"                self.wait(0.2)\n"
            f"\n"
            f"            highlight    = new_highlight\n"
            f"            explain_text = new_explain\n"
            f"\n"
            f"        self.wait(2)\n"
            f"        self.play(FadeOut(*self.mobjects), run_time=0.8)\n"
        )
