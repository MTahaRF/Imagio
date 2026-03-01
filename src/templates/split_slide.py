from .base import BaseTemplate

class SplitSlideTemplate(BaseTemplate):

    def description(self) -> str:
        return (
            "Use when a scene pairs a formula on the LEFT with a plain-text "
            "explanation on the RIGHT. Ideal for showing a formula alongside "
            "what each symbol means. Do NOT use for pure text or pure graph scenes."
        )

    def schema(self) -> dict:
        return {
            "title":        "Heading at the top of the slide",
            "left_header":  "Short label above the left panel (e.g. 'Formula')",
            "left_formula": "LaTeX string rendered on the left (e.g. r'E = mc^{2}')",
            "right_header": "Short label above the right panel (e.g. 'What it means')",
            "right_lines":  ["First explanation line", "Second explanation line", "Add 2-4 lines"],
            "narrations": {
                "intro":   "Spoken narration when title and divider appear",
                "formula": "Spoken narration when the formula is revealed",
                "lines":   ["Narration for line 1", "Narration for line 2", "One per right_line"],
            },
        }

    def prompt(self) -> str:
        return (
            "You are filling JSON for a Manim split-slide scene.\n"
            "Return ONLY a JSON object — no markdown, no explanation.\n\n"
            "Schema:\n"
            "{\n"
            '  "title": "Slide heading",\n'
            '  "left_header": "Formula", "left_formula": "LaTeX string",\n'
            '  "right_header": "Explanation",\n'
            '  "right_lines": ["Line one", "Line two", "Line three"],\n'
            '  "narrations": {\n'
            '    "intro": "Spoken intro", "formula": "Formula narration",\n'
            '    "lines": ["Line 1 narration", "Line 2 narration", "Line 3 narration"]\n'
            "  }\n"
            "}\n\n"
            "Rules:\n"
            "- left_formula must be valid LaTeX. right_lines are plain text.\n"
            "- narrations.lines must have the same length as right_lines (2-4).\n"
            "- Each narration is a natural spoken sentence (max 25 words).\n"
        )

    @staticmethod
    def _line_font_size(lines: list) -> int:
        if not lines: return 26
        max_words = max(len(l.split()) for l in lines)
        n = len(lines)
        if max_words <= 8 and n <= 3:    return 28
        elif max_words <= 10 and n <= 4: return 25
        elif max_words <= 14:            return 22
        elif max_words <= 18:            return 19
        else:                            return 17

    def _scene_body(self, data: dict, script: str) -> str:
        title        = data.get("title", "")
        left_header  = data.get("left_header", "Formula")
        left_formula = data.get("left_formula", r"f(x)")
        right_header = data.get("right_header", "Explanation")
        right_lines  = data.get("right_lines", [])
        narrations   = data.get("narrations", {})

        n_intro   = narrations.get("intro",   "Let us examine this formula.")
        n_formula = narrations.get("formula", "Here is the formula.")
        n_lines   = narrations.get("lines",   [""] * len(right_lines))

        while len(n_lines) < len(right_lines):
            n_lines.append("")

        title_fs         = self._title_font_size(title)
        font_size        = self._line_font_size(right_lines)
        right_lines_repr = "[" + ", ".join(repr(l) for l in right_lines) + "]"
        n_lines_repr     = "[" + ", ".join(repr(n) for n in n_lines) + "]"

        return (
            f"        title   = Text({title!r}, font_size={title_fs}, color=WHITE, weight=BOLD)\n"
            f"        divider = Line(UP * 2.8, DOWN * 3.0, color='#3a3a5c', stroke_width=2)\n"
            f"        title.to_edge(UP, buff=0.4)\n"
            f"        with self.voiceover(text={n_intro!r}):\n"
            f"            self.play(Write(title), run_time=0.8, rate_func=smooth)\n"
            f"            self.wait(0.2)\n"
            f"            self.play(Create(divider), run_time=0.5)\n"
            f"            self.wait(0.2)\n"
            f"\n"
            f"        l_header  = Text({left_header!r}, font_size=28, color=YELLOW)\n"
            f"        l_formula = MathTex({left_formula!r}, font_size=54, color=WHITE)\n"
            f"        l_header.move_to(LEFT * 3.2 + UP * 1.8)\n"
            f"        l_formula.move_to(LEFT * 3.2)\n"
            f"        with self.voiceover(text={n_formula!r}):\n"
            f"            self.play(FadeIn(l_header, shift=DOWN*0.1), run_time=0.4)\n"
            f"            self.wait(0.15)\n"
            f"            self.play(Write(l_formula), run_time=1.1, rate_func=smooth)\n"
            f"            self.wait(0.3)\n"
            f"\n"
            f"        r_header = Text({right_header!r}, font_size=28, color=YELLOW)\n"
            f"        r_header.move_to(RIGHT * 3.0 + UP * 1.8)\n"
            f"        self.play(FadeIn(r_header, shift=DOWN*0.1), run_time=0.4)\n"
            f"        self.wait(0.2)\n"
            f"\n"
            f"        raw_lines       = {right_lines_repr}\n"
            f"        narrations_data = {n_lines_repr}\n"
            f"        r_group = VGroup(*[\n"
            f"            Text(line, font_size={font_size}, color=WHITE) for line in raw_lines\n"
            f"        ]).arrange(DOWN, buff=0.3, aligned_edge=LEFT)\n"
            f"        r_group.set_width(min(r_group.width, 5.2))\n"
            f"        r_group.move_to(RIGHT * 3.0)\n"
            f"\n"
            f"        for line_obj, narration in zip(r_group, narrations_data):\n"
            f"            with self.voiceover(text=narration):\n"
            f"                self.play(\n"
            f"                    FadeIn(line_obj, shift=UP * 0.12),\n"
            f"                    run_time=0.5, rate_func=smooth,\n"
            f"                )\n"
            f"                self.wait(0.2)\n"
            f"\n"
            f"        self.wait(2)\n"
            f"        self.play(FadeOut(*self.mobjects), run_time=0.8)\n"
        )
