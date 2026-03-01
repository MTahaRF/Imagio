from .base import BaseTemplate

class TitleSlideTemplate(BaseTemplate):

    def description(self) -> str:
        return (
            "Use for the opening scene of a video, chapter headers, or any scene "
            "that needs a bold title with an optional subtitle. Best for introductions "
            "and section breaks. Do NOT use if the scene contains equations or bullet points."
        )

    def schema(self) -> dict:
        return {
            "title":     "Main heading shown large and centred",
            "subtitle":  "Smaller supporting line shown below the title",
            "narration": "Single spoken sentence introducing the topic",
        }

    def prompt(self) -> str:
        return (
            "You are filling JSON for a Manim title-slide scene.\n"
            "Return ONLY a JSON object — no markdown, no explanation.\n\n"
            "Schema:\n"
            "{\n"
            '  "title": "Main heading",\n'
            '  "subtitle": "Supporting subtitle",\n'
            '  "narration": "Welcome spoken sentence"\n'
            "}\n\n"
            "Rules:\n"
            "- Keep title short and punchy (max 8 words). Plain text only, no LaTeX.\n"
            "- subtitle complements, does not repeat, the title.\n"
            "- narration is one natural spoken sentence (max 25 words).\n"
        )

    def _scene_body(self, data: dict, script: str) -> str:
        title     = data.get("title", "Title")
        subtitle  = data.get("subtitle", "")
        narration = data.get("narration", script or "Welcome to this video.")
        title_fs  = self._title_font_size(title)
        sub_fs    = self._auto_font_size(subtitle) if subtitle else 32

        return (
            f"        title    = Text({title!r}, font_size={title_fs}, color=WHITE, weight=BOLD)\n"
            f"        subtitle = Text({subtitle!r}, font_size={sub_fs}, color='#a0a8d0')\n"
            f"        line     = Line(LEFT * 3.5, RIGHT * 3.5, color=YELLOW, stroke_width=3)\n"
            f"        title.move_to(ORIGIN + UP * 0.7)\n"
            f"        line.next_to(title, DOWN, buff=0.22)\n"
            f"        subtitle.next_to(line, DOWN, buff=0.3)\n"
            f"\n"
            f"        with self.voiceover(text={narration!r}):\n"
            f"            self.play(Write(title), run_time=1.0, rate_func=smooth)\n"
            f"            self.wait(0.2)\n"
            f"            self.play(Create(line), run_time=0.5)\n"
            f"            self.play(FadeIn(subtitle, shift=UP * 0.15), run_time=0.7, rate_func=smooth)\n"
            f"            self.wait(0.4)\n"
            f"\n"
            f"        self.wait(2)\n"
            f"        self.play(FadeOut(*self.mobjects), run_time=0.8)\n"
        )
