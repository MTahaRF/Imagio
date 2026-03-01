from .base import BaseTemplate

class EquationTransformTemplate(BaseTemplate):

    def description(self) -> str:
        return (
            "Use when a scene needs to walk through algebraic or mathematical derivation "
            "step by step. Perfect for proofs, simplifications, and formula derivations. "
            "Requires LaTeX for every step. Do NOT use for graphs, lists, or plain-text explanations."
        )

    def schema(self) -> dict:
        return {
            "title": "Heading for the derivation",
            "steps": ["LaTeX step 1", "LaTeX step 2", "LaTeX step 3"],
            "annotations": ["Note for step 1", "Note for step 2", "Note for step 3"],
            "narrations": ["Spoken narration for step 1", "Narration for step 2", "Narration for step 3"],
        }

    def prompt(self) -> str:
        return (
            "You are filling JSON for a Manim equation-transform scene.\n"
            "Return ONLY a JSON object — no markdown, no explanation.\n\n"
            "Schema:\n"
            "{\n"
            '  "title": "Derivation heading",\n'
            '  "steps": ["LaTeX step 1", "LaTeX step 2", "LaTeX step 3"],\n'
            '  "annotations": ["Note 1", "Note 2", "Note 3"],\n'
            '  "narrations": ["Spoken narration 1", "Narration 2", "Narration 3"]\n'
            "}\n\n"
            "Rules:\n"
            "- Every entry in steps must be valid LaTeX math.\n"
            "- annotations are plain English (no LaTeX); max 10 words each.\n"
            "- narrations are natural spoken sentences (max 25 words each).\n"
            "- steps, annotations, and narrations must all have the same length (2-5).\n"
        )

    def _scene_body(self, data: dict, script: str) -> str:
        title       = data.get("title", "Derivation")
        steps       = data.get("steps", [r"f(x) = x^{2}"])
        annotations = data.get("annotations", [""] * len(steps))
        narrations  = data.get("narrations",  [""] * len(steps))

        while len(annotations) < len(steps): annotations.append("")
        while len(narrations)  < len(steps): narrations.append("")

        title_fs         = self._title_font_size(title)
        steps_repr       = "[" + ", ".join(repr(s) for s in steps) + "]"
        annotations_repr = "[" + ", ".join(repr(a) for a in annotations) + "]"
        narrations_repr  = "[" + ", ".join(repr(n) for n in narrations) + "]"

        return (
            f"        title = Text({title!r}, font_size={title_fs}, color=YELLOW, weight=BOLD)\n"
            f"        title.to_edge(UP, buff=0.4)\n"
            f"        self.play(Write(title), run_time=0.8, rate_func=smooth)\n"
            f"        self.wait(0.3)\n"
            f"\n"
            f"        steps_latex     = {steps_repr}\n"
            f"        annotations     = {annotations_repr}\n"
            f"        narrations_data = {narrations_repr}\n"
            f"\n"
            f"        current_eq   = MathTex(steps_latex[0], font_size=54, color=WHITE)\n"
            f"        current_eq.move_to(ORIGIN + UP * 0.5)\n"
            f"        current_note = Text(annotations[0], font_size=26, color='#a0a8d0')\n"
            f"        current_note.next_to(current_eq, DOWN, buff=0.4)\n"
            f"\n"
            f"        with self.voiceover(text=narrations_data[0]):\n"
            f"            self.play(Write(current_eq), run_time=1.0, rate_func=smooth)\n"
            f"            if annotations[0]:\n"
            f"                self.play(FadeIn(current_note, shift=UP * 0.1), run_time=0.5)\n"
            f"            self.wait(0.3)\n"
            f"\n"
            f"        for i in range(1, len(steps_latex)):\n"
            f"            next_eq   = MathTex(steps_latex[i], font_size=54, color=WHITE)\n"
            f"            next_eq.move_to(ORIGIN + UP * 0.5)\n"
            f"            next_note = Text(annotations[i], font_size=26, color='#a0a8d0')\n"
            f"            next_note.next_to(next_eq, DOWN, buff=0.4)\n"
            f"\n"
            f"            with self.voiceover(text=narrations_data[i]):\n"
            f"                self.play(\n"
            f"                    TransformMatchingShapes(current_eq, next_eq),\n"
            f"                    run_time=1.1, rate_func=smooth,\n"
            f"                )\n"
            f"                self.wait(0.2)\n"
            f"                if annotations[i - 1]:\n"
            f"                    self.play(FadeOut(current_note), run_time=0.3)\n"
            f"                if annotations[i]:\n"
            f"                    self.play(FadeIn(next_note, shift=UP * 0.1), run_time=0.45)\n"
            f"                self.wait(0.25)\n"
            f"\n"
            f"            current_eq   = next_eq\n"
            f"            current_note = next_note\n"
            f"\n"
            f"        self.wait(2)\n"
            f"        self.play(FadeOut(*self.mobjects), run_time=0.8)\n"
        )
