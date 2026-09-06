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
            '  "right_lines": ["Short point one", "Short point two", "Short point three"],\n'
            '  "narrations": {\n'
            '    "intro": "Spoken intro", "formula": "Formula narration",\n'
            '    "lines": ["Line 1 narration", "Line 2 narration", "Line 3 narration"]\n'
            '  }\n'
            "}\n\n"
            "Rules:\n"
            "- left_formula must be valid LaTeX. right_lines are plain text.\n"
            "- right_lines: 2-4 short, punchy points (max 10 words each). NEVER write full paragraphs.\n"
            "- narrations.lines must have the same length as right_lines (2-4).\n"
            "- Each narration is a natural spoken sentence (max 25 words).\n"
        )

    @staticmethod
    def _line_font_size(lines: list) -> int:
        n = len(lines)
        if n <= 3:   return 26
        elif n <= 4: return 24
        else:        return 22

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

        wrapped_title   = self._wrap_text(title, width=38)
        wrapped_lines   = [self._wrap_text(l, width=30) for l in right_lines]

        title_fs         = self._title_font_size(title)
        font_size        = self._line_font_size(right_lines)
        right_lines_repr = "[" + ", ".join(repr(l) for l in wrapped_lines) + "]"
        n_lines_repr     = "[" + ", ".join(repr(n) for n in n_lines) + "]"

        return (
            f"        title   = Text({wrapped_title!r}, font_size={title_fs}, color=WHITE, weight=BOLD)\n"
            f"        _safe_fit(title, max_w=11.5, min_scale=0.85)\n"
            f"        title.to_edge(UP, buff=0.4)\n"
            f"        divider = Line(UP * 2.8, DOWN * 3.0, color='#3a3a5c', stroke_width=2)\n"
            f"        with self.voiceover(text={n_intro!r}):\n"
            f"            self.play(Write(title), run_time=0.8, rate_func=smooth)\n"
            f"            self.wait(0.2)\n"
            f"            self.play(Create(divider), run_time=0.5)\n"
            f"            self.wait(0.2)\n"
            f"\n"
            f"        l_header  = Text({left_header!r}, font_size=28, color=YELLOW)\n"
            f"        _safe_fit(l_header, max_w=5.2, min_scale=0.85)\n"
            f"        l_formula = MathTex({left_formula!r}, font_size=50, color=WHITE)\n"
            f"        _safe_fit(l_formula, max_w=5.4, max_h=3.6, min_scale=0.75)\n"
            f"        l_header.move_to(LEFT * 3.2 + UP * 1.8)\n"
            f"        l_formula.move_to(LEFT * 3.2)\n"
            f"        with self.voiceover(text={n_formula!r}):\n"
            f"            self.play(FadeIn(l_header, shift=DOWN*0.1), run_time=0.4)\n"
            f"            self.wait(0.15)\n"
            f"            self.play(Write(l_formula), run_time=1.1, rate_func=smooth)\n"
            f"            self.wait(0.3)\n"
            f"\n"
            f"        r_header = Text({right_header!r}, font_size=28, color=YELLOW)\n"
            f"        _safe_fit(r_header, max_w=5.2, min_scale=0.85)\n"
            f"        r_header.move_to(RIGHT * 3.1 + UP * 1.8)\n"
            f"        self.play(FadeIn(r_header, shift=DOWN*0.1), run_time=0.4)\n"
            f"        self.wait(0.2)\n"
            f"\n"
            f"        raw_lines       = {right_lines_repr}\n"
            f"        narrations_data = {n_lines_repr}\n"
            f"        r_group = VGroup(*[\n"
            f"            _safe_fit(Text(line, font_size={font_size}, color=WHITE, line_spacing=1.15), max_w=5.2, min_scale=0.85) for line in raw_lines\n"
            f"        ]).arrange(DOWN, buff=0.3, aligned_edge=LEFT)\n"
            f"        _safe_fit(r_group, max_w=5.4, max_h=4.2, min_scale=0.82)\n"
            f"        r_group.move_to(RIGHT * 3.1 + DOWN * 0.2)\n"
            f"\n"
            f"        for i, (line_obj, narration) in enumerate(zip(r_group, narrations_data)):\n"
            f"            with self.voiceover(text=narration) as tracker:\n"
            f"                t_anim = max(min(tracker.duration * 0.45, 1.8), 0.6)\n"
            f"                anims = [FadeIn(line_obj, shift=UP * 0.12)]\n"
            f"                if i > 0:\n"
            f"                    anims.append(r_group[i - 1].animate.set_opacity(0.45))\n"
            f"                self.play(*anims, run_time=t_anim, rate_func=smooth)\n"
            f"                self.wait(0.2)\n"
            f"\n"
            f"        if len(r_group) > 1:\n"
            f"            self.play(*[l.animate.set_opacity(1.0) for l in r_group], run_time=0.4)\n"
            f"        self.wait(1.0)\n"
            f"        self.play(FadeOut(*self.mobjects), run_time=0.6)\n"
        )
