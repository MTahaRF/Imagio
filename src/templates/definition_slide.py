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
            "definition": "Full definition sentence; plain text only",
            "formula":    "Optional LaTeX formula (leave empty string if none)",
            "example":    "Concrete example illustrating the term (plain text)",
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
            '  "definition": "Full definition as plain text",\n'
            '  "formula": "LaTeX formula (or empty string)",\n'
            '  "example": "Concrete example as plain text",\n'
            '  "narrations": {\n'
            '    "term": "Spoken intro sentence",\n'
            '    "definition": "Spoken definition explanation",\n'
            '    "formula": "Spoken formula explanation (or empty string)",\n'
            '    "example": "Spoken example explanation"\n'
            "  }\n"
            "}\n\n"
            "Rules:\n"
            "- term is plain text (no LaTeX).\n"
            "- definition is a full sentence in plain text.\n"
            "- formula is pure LaTeX; omit dollar signs. Empty string if not needed.\n"
            "- Each narration is a natural spoken sentence (max 25 words).\n"
        )

    @staticmethod
    def _defn_font_size(text: str) -> int:
        words = len(text.split())
        if words <= 15:   return 30
        elif words <= 25: return 27
        elif words <= 35: return 24
        elif words <= 50: return 21
        else:             return 18

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

        title_fs   = self._title_font_size(term)
        defn_fs    = self._defn_font_size(definition)
        example_fs = self._defn_font_size(example)

        return (
            f"        import textwrap\n"
            f"\n"
            f"        term_text = Text({term!r}, font_size={title_fs}, color=YELLOW, weight=BOLD)\n"
            f"        term_text.to_edge(UP, buff=0.45)\n"
            f"        box = SurroundingRectangle(term_text, color=YELLOW, buff=0.18,\n"
            f"            corner_radius=0.12, stroke_width=2)\n"
            f"        with self.voiceover(text={n_term!r}):\n"
            f"            self.play(\n"
            f"                AnimationGroup(Write(term_text), Create(box), lag_ratio=0.35),\n"
            f"                run_time=0.9, rate_func=smooth,\n"
            f"            )\n"
            f"            self.wait(0.3)\n"
            f"\n"
            f"        defn_label   = Text('Definition:', font_size=22, color='#a0a8d0')\n"
            f"        wrapped_defn = '\\n'.join(textwrap.wrap({definition!r}, width=60))\n"
            f"        defn_text    = Paragraph(wrapped_defn, font_size={defn_fs}, color=WHITE,\n"
            f"            line_spacing=1.2, alignment='left')\n"
            f"        defn_group   = VGroup(defn_label, defn_text).arrange(DOWN, buff=0.2, aligned_edge=LEFT)\n"
            f"        defn_group.next_to(box, DOWN, buff=0.35).to_edge(LEFT, buff=0.8)\n"
            f"        with self.voiceover(text={n_defn!r}):\n"
            f"            self.play(FadeIn(defn_group, shift=UP * 0.15), run_time=0.7, rate_func=smooth)\n"
            f"            self.wait(0.3)\n"
            f"\n"
            f"        y_ref = defn_group\n"
            f"        if {formula!r}:\n"
            f"            formula_obj = MathTex({formula!r}, font_size=52, color=BLUE)\n"
            f"            formula_obj.next_to(defn_group, DOWN, buff=0.45).to_edge(LEFT, buff=1.5)\n"
            f"            with self.voiceover(text={n_formula!r}):\n"
            f"                self.play(Write(formula_obj), run_time=0.9, rate_func=smooth)\n"
            f"                self.wait(0.3)\n"
            f"            y_ref = formula_obj\n"
            f"\n"
            f"        if {example!r}:\n"
            f"            ex_label   = Text('Example:', font_size=22, color='#a0a8d0')\n"
            f"            wrapped_ex = '\\n'.join(textwrap.wrap({example!r}, width=65))\n"
            f"            ex_text    = Paragraph(wrapped_ex, font_size={example_fs},\n"
            f"                color='#c8d0f0', line_spacing=1.2, alignment='left')\n"
            f"            ex_group   = VGroup(ex_label, ex_text).arrange(DOWN, buff=0.15, aligned_edge=LEFT)\n"
            f"            ex_group.next_to(y_ref, DOWN, buff=0.45).to_edge(LEFT, buff=0.8)\n"
            f"            with self.voiceover(text={n_example!r}):\n"
            f"                self.play(FadeIn(ex_group, shift=UP * 0.12), run_time=0.6, rate_func=smooth)\n"
            f"                self.wait(0.3)\n"
            f"\n"
            f"        self.wait(2)\n"
            f"        self.play(FadeOut(*self.mobjects), run_time=0.8)\n"
        )

