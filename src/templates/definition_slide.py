from .base import BaseTemplate

class DefinitionSlideTemplate(BaseTemplate):

    def description(self) -> str:
        return (
            "Use when a scene needs to formally introduce a term with its definition "
            "and an illustrative example. Supports LaTeX in the formula field. "
            "Do NOT use for multi-step derivations or graph plots."
        )

    def schema(self) -> dict:
        return {
            "term":       "The word or concept being defined (plain text)",
            "definition": "Concise definition (max 15 words; plain text)",
            "formula":    "Optional LaTeX formula (leave empty string if none)",
            "example":    "Concise concrete example (max 12 words; plain text)",
            "narrations": {
                "term":       "Spoken intro for the term",
                "definition": "Spoken narration explaining the definition",
                "formula":    "Spoken narration for the formula (or empty string)",
                "example":    "Spoken narration for the example",
            },
        }

    def prompt(self) -> str:
        return (
            "You are filling JSON for a Manim definition-slide scene.\n"
            "Return ONLY a JSON object — no markdown, no explanation.\n\n"
            "Schema:\n"
            "{\n"
            '  "term": "Term to define",\n'
            '  "definition": "Concise definition (max 15 words)",\n'
            '  "formula": "LaTeX formula (or empty string)",\n'
            '  "example": "Short concrete example (max 12 words)",\n'
            '  "narrations": {\n'
            '    "term": "Spoken intro sentence",\n'
            '    "definition": "Spoken definition explanation",\n'
            '    "formula": "Spoken formula explanation (or empty string)",\n'
            '    "example": "Spoken example explanation"\n'
            '  }\n'
            "}\n\n"
            "Rules:\n"
            "- term is plain text (no LaTeX).\n"
            "- definition is concise plain text (max 15 words). NEVER write a long paragraph.\n"
            "- formula is pure LaTeX; omit dollar signs. Empty string if not needed.\n"
            "- example is a short phrase or concise sentence (max 12 words).\n"
            "- Each narration is a natural spoken sentence (max 25 words).\n"
        )

    @staticmethod
    def _defn_font_size(text: str) -> int:
        words = len(text.split())
        if words <= 15:   return 28
        elif words <= 25: return 25
        else:             return 23

    def _scene_body(self, data: dict, script: str) -> str:
        term       = data.get("term", "Definition")
        definition = data.get("definition", "")
        formula    = data.get("formula", "")
        example    = data.get("example", "")
        narrations = data.get("narrations", {})

        n_term    = narrations.get("term",       f"Let us define {term}.")
        n_defn    = narrations.get("definition", definition)
        n_formula = narrations.get("formula",    "")
        n_example = narrations.get("example",    example)

        wrapped_term = self._wrap_text(term, width=32)
        wrapped_defn = self._wrap_text(definition, width=52)
        wrapped_ex   = self._wrap_text(example, width=54)

        title_fs   = self._title_font_size(term)
        defn_fs    = self._defn_font_size(definition)
        example_fs = self._defn_font_size(example)

        return (
            f"        term_text = Text({wrapped_term!r}, font_size={title_fs}, color=YELLOW, weight=BOLD)\n"
            f"        _safe_fit(term_text, max_w=10.5, min_scale=0.85)\n"
            f"        term_text.to_edge(UP, buff=0.4)\n"
            f"        box = SurroundingRectangle(term_text, color=YELLOW, buff=0.16,\n"
            f"            corner_radius=0.12, stroke_width=2)\n"
            f"        with self.voiceover(text={n_term!r}):\n"
            f"            self.play(\n"
            f"                AnimationGroup(Write(term_text), Create(box), lag_ratio=0.35),\n"
            f"                run_time=0.9, rate_func=smooth,\n"
            f"            )\n"
            f"            self.wait(0.3)\n"
            f"\n"
            f"        body_group = VGroup()\n"
            f"        defn_label = Text('Definition:', font_size=22, color='#a0a8d0')\n"
            f"        defn_text  = Text({wrapped_defn!r}, font_size={defn_fs}, color=WHITE, line_spacing=1.2)\n"
            f"        _safe_fit(defn_text, max_w=10.8, min_scale=0.85)\n"
            f"        defn_group = VGroup(defn_label, defn_text).arrange(DOWN, buff=0.15, aligned_edge=LEFT)\n"
            f"        body_group.add(defn_group)\n"
            f"\n"
            f"        has_formula = bool({formula!r})\n"
            f"        if has_formula:\n"
            f"            formula_obj = MathTex({formula!r}, font_size=46, color=BLUE)\n"
            f"            _safe_fit(formula_obj, max_w=9.5, max_h=1.4, min_scale=0.75)\n"
            f"            formula_box = VGroup(formula_obj).shift(RIGHT * 0.4)\n"
            f"            body_group.add(formula_box)\n"
            f"\n"
            f"        has_example = bool({example!r})\n"
            f"        if has_example:\n"
            f"            ex_label = Text('Example:', font_size=22, color='#a0a8d0')\n"
            f"            ex_text  = Text({wrapped_ex!r}, font_size={example_fs}, color='#c8d0f0', line_spacing=1.2)\n"
            f"            _safe_fit(ex_text, max_w=10.8, min_scale=0.85)\n"
            f"            ex_group = VGroup(ex_label, ex_text).arrange(DOWN, buff=0.12, aligned_edge=LEFT)\n"
            f"            body_group.add(ex_group)\n"
            f"\n"
            f"        body_group.arrange(DOWN, buff=0.28, aligned_edge=LEFT)\n"
            f"        _safe_fit(body_group, max_w=11.0, max_h=4.8, min_scale=0.82)\n"
            f"        body_group.next_to(box, DOWN, buff=0.3).to_edge(LEFT, buff=0.8)\n"
            f"\n"
            f"        with self.voiceover(text={n_defn!r}):\n"
            f"            self.play(FadeIn(defn_group, shift=UP * 0.12), run_time=0.7, rate_func=smooth)\n"
            f"            self.wait(0.3)\n"
            f"\n"
            f"        if has_formula:\n"
            f"            with self.voiceover(text={n_formula!r}):\n"
            f"                self.play(Write(formula_obj), run_time=0.8, rate_func=smooth)\n"
            f"                self.wait(0.3)\n"
            f"\n"
            f"        if has_example:\n"
            f"            with self.voiceover(text={n_example!r}):\n"
            f"                self.play(FadeIn(ex_group, shift=UP * 0.12), run_time=0.6, rate_func=smooth)\n"
            f"                self.wait(0.3)\n"
            f"\n"
            f"        self.wait(1.0)\n"
            f"        self.play(FadeOut(*self.mobjects), run_time=0.6)\n"
        )
