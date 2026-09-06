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
            "- Each point must be a short punchy phrase (max 8-10 words). NEVER write full paragraphs.\n"
            "- points and narrations must have the same number of items (3-5).\n"
            "- Each narration is a natural spoken sentence (max 25 words).\n"
        )

    @staticmethod
    def _bullet_font_size(points: list) -> int:
        n = len(points)
        if n <= 3:   return 28
        elif n <= 4: return 26
        else:        return 24

    @staticmethod
    def _bullet_row_buff(font_size: int) -> float:
        if font_size >= 28: return 0.35
        elif font_size >= 26: return 0.30
        else:                 return 0.25

    def _scene_body(self, data: dict, script: str) -> str:
        raw_title  = data.get("title", "Key Points")
        points     = data.get("points", [])
        narrations = data.get("narrations", [""] * len(points))

        while len(narrations) < len(points):
            narrations.append("")

        wrapped_title   = self._wrap_text(raw_title, width=38)
        wrapped_points  = [self._wrap_text(p, width=44) for p in points]

        title_fs        = self._title_font_size(raw_title)
        font_size       = self._bullet_font_size(points)
        row_buff        = self._bullet_row_buff(font_size)
        points_repr     = "[" + ", ".join(repr(p) for p in wrapped_points) + "]"
        narrations_repr = "[" + ", ".join(repr(n) for n in narrations) + "]"

        return (
            f"        title = Text({wrapped_title!r}, font_size={title_fs}, color=YELLOW, weight=BOLD)\n"
            f"        _safe_fit(title, max_w=11.5, min_scale=0.85)\n"
            f"        title.to_edge(UP, buff=0.4)\n"
            f"        underline = Line(title.get_left(), title.get_right(), color=YELLOW, stroke_width=2)\n"
            f"        underline.next_to(title, DOWN, buff=0.1)\n"
            f"        self.play(\n"
            f"            AnimationGroup(Write(title), Create(underline), lag_ratio=0.4),\n"
            f"            run_time=0.9, rate_func=smooth,\n"
            f"        )\n"
            f"        self.wait(0.3)\n"
            f"\n"
            f"        raw_points       = {points_repr}\n"
            f"        narrations_data  = {narrations_repr}\n"
            f"        bullet_group = VGroup()\n"
            f"        for text in raw_points:\n"
            f"            dot   = Text('•', font_size={font_size}, color=YELLOW)\n"
            f"            label = Text(text, font_size={font_size}, color=WHITE, line_spacing=1.15)\n"
            f"            _safe_fit(label, max_w=10.2, min_scale=0.85)\n"
            f"            row   = VGroup(dot, label).arrange(RIGHT, buff=0.25, aligned_edge=UP)\n"
            f"            bullet_group.add(row)\n"
            f"        bullet_group.arrange(DOWN, buff={row_buff}, aligned_edge=LEFT)\n"
            f"        _safe_fit(bullet_group, max_w=11.0, max_h=4.8, min_scale=0.82)\n"
            f"        bullet_group.next_to(underline, DOWN, buff=0.35)\n"
            f"        bullet_group.to_edge(LEFT, buff=0.8)\n"
            f"\n"
            f"        for i, (row, narration) in enumerate(zip(bullet_group, narrations_data)):\n"
            f"            with self.voiceover(text=narration) as tracker:\n"
            f"                t_anim = max(min(tracker.duration * 0.45, 1.8), 0.7)\n"
            f"                anims = [FadeIn(row, shift=RIGHT * 0.25)]\n"
            f"                if i > 0:\n"
            f"                    anims.append(bullet_group[i - 1].animate.set_opacity(0.45))\n"
            f"                self.play(*anims, run_time=t_anim, rate_func=smooth)\n"
            f"                self.wait(0.2)\n"
            f"\n"
            f"        if len(bullet_group) > 1:\n"
            f"            self.play(*[r.animate.set_opacity(1.0) for r in bullet_group], run_time=0.4)\n"
            f"\n"
            f"        self.wait(1.0)\n"
            f"        self.play(FadeOut(*self.mobjects), run_time=0.6)\n"
        )
