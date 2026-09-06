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
        raw_title    = data.get("title", "Title")
        raw_subtitle = data.get("subtitle", "")
        narration    = data.get("narration", script or "Welcome to this video.")

        wrapped_title = self._wrap_text(raw_title, width=36)
        wrapped_sub   = self._wrap_text(raw_subtitle, width=50)

        title_fs = self._title_font_size(raw_title)
        sub_fs   = self._auto_font_size(raw_subtitle) if raw_subtitle else 28

        return (
            f"        title = Text({wrapped_title!r}, font_size={title_fs}, color=WHITE, weight=BOLD)\n"
            f"        _safe_fit(title, max_w=11.5, max_h=3.0, min_scale=0.85)\n"
            f"\n"
            f"        line_w = max(min(title.width * 0.85, 7.5), 3.0)\n"
            f"        line   = Line(LEFT * (line_w / 2), RIGHT * (line_w / 2), color=YELLOW, stroke_width=3)\n"
            f"\n"
            f"        subtitle = Text({wrapped_sub!r}, font_size={sub_fs}, color='#a0a8d0')\n"
            f"        _safe_fit(subtitle, max_w=11.0, max_h=2.0, min_scale=0.82)\n"
            f"\n"
            f"        content = VGroup(title, line, subtitle).arrange(DOWN, buff=0.28).move_to(ORIGIN)\n"
            f"        _safe_fit(content, max_w=11.5, max_h=5.5, min_scale=0.85)\n"
            f"\n"
            f"        with self.voiceover(text={narration!r}) as tracker:\n"
            f"            t_title = max(min(tracker.duration * 0.35, 1.6), 0.9)\n"
            f"            t_sub   = max(min(tracker.duration * 0.35, 1.4), 0.7)\n"
            f"            self.play(Write(title), run_time=t_title, rate_func=smooth)\n"
            f"            self.wait(0.15)\n"
            f"            self.play(Create(line), run_time=0.4)\n"
            f"            self.play(FadeIn(subtitle, shift=UP * 0.15), run_time=t_sub, rate_func=smooth)\n"
            f"            self.wait(0.3)\n"
            f"\n"
            f"        self.wait(1.0)\n"
            f"        self.play(FadeOut(*self.mobjects), run_time=0.6)\n"
        )
