from .base import BaseTemplate

class BulletPointsTemplate(BaseTemplate):

    def description(self) -> str:
        return (
            "Use when a scene needs to present a list of key concepts, takeaways, "
            "steps, or properties as bullet points. Best for summaries, overviews, "
            "and lists of facts. Do NOT use for equations, graphs, or comparisons."
        )

    def schema(self) -> dict:
        return {
            "title": "Heading displayed at the top of the slide",
            "points": ["First bullet point", "Second bullet point", "Third bullet point"],
            "narrations": [
                "Spoken narration for first bullet",
                "Spoken narration for second bullet",
                "One narration per bullet point",
            ],
        }

    def prompt(self) -> str:
        return (
            "You are filling JSON for a Manim bullet-points scene.\n"
            "Return ONLY a JSON object — no markdown, no explanation.\n\n"
            "Schema:\n"
            "{\n"
            '  "title": "Heading for the slide",\n'
            '  "points": ["First point", "Second point", "Third point"],\n'
            '  "narrations": ["Narration for point 1", "Narration for point 2", "Narration for point 3"]\n'
            "}\n\n"
            "Rules:\n"
            "- All values are plain strings. No LaTeX.\n"
            "- Each point is one concise sentence (max 15 words).\n"
            "- points and narrations must have the same number of items (3-6).\n"
            "- Each narration is a natural spoken sentence (max 20 words).\n"
        )

    @staticmethod
    def _bullet_font_size(points: list) -> int:
        if not points: return 30
        max_words = max(len(p.split()) for p in points)
        n = len(points)
        if max_words <= 6 and n <= 4:   return 32
        elif max_words <= 10 and n <= 5: return 28
        elif max_words <= 13 and n <= 6: return 25
        elif max_words <= 16:            return 22
        else:                            return 19

    @staticmethod
    def _bullet_row_buff(font_size: int) -> float:
        if font_size >= 30:   return 0.42
        elif font_size >= 26: return 0.36
        elif font_size >= 22: return 0.30
        else:                 return 0.25

    def _scene_body(self, data: dict, script: str) -> str:
        title      = data.get("title", "Key Points")
        points     = data.get("points", [])
        narrations = data.get("narrations", [""] * len(points))

        while len(narrations) < len(points):
            narrations.append("")

        title_fs        = self._title_font_size(title)
        font_size       = self._bullet_font_size(points)
        row_buff        = self._bullet_row_buff(font_size)
        points_repr     = "[" + ", ".join(repr(p) for p in points) + "]"
        narrations_repr = "[" + ", ".join(repr(n) for n in narrations) + "]"

        return (
            f"        title = Text({title!r}, font_size={title_fs}, color=YELLOW, weight=BOLD)\n"
            f"        title.to_edge(UP, buff=0.45)\n"
            f"        underline = Line(title.get_left(), title.get_right(), color=YELLOW, stroke_width=2)\n"
            f"        underline.next_to(title, DOWN, buff=0.1)\n"
            f"        self.play(\n"
            f"            AnimationGroup(Write(title), Create(underline), lag_ratio=0.4),\n"
            f"            run_time=0.9, rate_func=smooth,\n"
            f"        )\n"
            f"        self.wait(0.35)\n"
            f"\n"
            f"        raw_points       = {points_repr}\n"
            f"        narrations_data  = {narrations_repr}\n"
            f"        bullet_group = VGroup()\n"
            f"        for text in raw_points:\n"
            f"            dot   = Text('*', font_size={font_size}, color=YELLOW)\n"
            f"            label = Text(text, font_size={font_size}, color=WHITE)\n"
            f"            label.set_width(min(label.width, 10.0))\n"
            f"            row = VGroup(dot, label).arrange(RIGHT, buff=0.28, aligned_edge=UP)\n"
            f"            bullet_group.add(row)\n"
            f"        bullet_group.arrange(DOWN, buff={row_buff}, aligned_edge=LEFT)\n"
            f"        bullet_group.next_to(underline, DOWN, buff=0.4)\n"
            f"        bullet_group.to_edge(LEFT, buff=0.75)\n"
            f"\n"
            f"        for row, narration in zip(bullet_group, narrations_data):\n"
            f"            with self.voiceover(text=narration):\n"
            f"                self.play(\n"
            f"                    FadeIn(row, shift=RIGHT * 0.25),\n"
            f"                    run_time=0.55, rate_func=smooth,\n"
            f"                )\n"
            f"                self.wait(0.2)\n"
            f"\n"
            f"        self.wait(2)\n"
            f"        self.play(FadeOut(*self.mobjects), run_time=0.8)\n"
        )

