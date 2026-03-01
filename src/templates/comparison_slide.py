from .base import BaseTemplate

class ComparisonSlideTemplate(BaseTemplate):

    def description(self) -> str:
        return (
            "Use when a scene needs to place two things side by side for comparison. "
            "Each column has a header and a list of items. "
            "Do NOT use for single-concept explanations, graphs, or code."
        )

    def schema(self) -> dict:
        return {
            "title":        "Heading above both columns",
            "left_header":  "Label for the left column",
            "right_header": "Label for the right column",
            "left_items":   ["First left item", "Second left item"],
            "right_items":  ["First right item", "Second right item"],
            "narrations":   ["Narration for row 1 comparing both sides", "Narration for row 2"],
        }

    def prompt(self) -> str:
        return (
            "You are filling JSON for a Manim comparison-slide scene.\n"
            "Return ONLY a JSON object — no markdown, no explanation.\n\n"
            "Schema:\n"
            "{\n"
            '  "title": "Slide heading",\n'
            '  "left_header": "Left column label",\n'
            '  "right_header": "Right column label",\n'
            '  "left_items": ["Item 1", "Item 2", "Item 3"],\n'
            '  "right_items": ["Item 1", "Item 2", "Item 3"],\n'
            '  "narrations": ["Narration row 1", "Narration row 2", "Narration row 3"]\n'
            "}\n\n"
            "Rules:\n"
            "- All values are plain strings (no LaTeX).\n"
            "- left_items and right_items must have the same number of items (2-5).\n"
            "- narrations must match the number of rows (same length as left_items).\n"
            "- Each narration compares the two items on that row (max 25 words).\n"
        )

    @staticmethod
    def _item_font_size(items: list) -> int:
        if not items: return 24
        max_words = max(len(s.split()) for s in items)
        if max_words <= 5:    return 24
        elif max_words <= 8:  return 21
        elif max_words <= 12: return 18
        else:                 return 15

    def _scene_body(self, data: dict, script: str) -> str:
        title        = data.get("title", "Comparison")
        left_header  = data.get("left_header", "Option A")
        right_header = data.get("right_header", "Option B")
        left_items   = data.get("left_items", [])
        right_items  = data.get("right_items", [])
        narrations   = data.get("narrations", [""] * max(len(left_items), len(right_items)))

        while len(narrations) < max(len(left_items), len(right_items)):
            narrations.append("")

        title_fs   = self._title_font_size(title)
        font_size  = self._item_font_size(left_items + right_items)
        row_height = 0.8 if font_size >= 21 else 0.7

        left_repr       = "[" + ", ".join(repr(i) for i in left_items) + "]"
        right_repr      = "[" + ", ".join(repr(i) for i in right_items) + "]"
        narrations_repr = "[" + ", ".join(repr(n) for n in narrations) + "]"

        return (
            f"        import textwrap\n"
            f"\n"
            f"        title = Text({title!r}, font_size={title_fs}, color=WHITE, weight=BOLD)\n"
            f"        title.to_edge(UP, buff=0.4)\n"
            f"        self.play(Write(title), run_time=0.8, rate_func=smooth)\n"
            f"        self.wait(0.3)\n"
            f"\n"
            f"        col_h    = 5.6\n"
            f"        left_bg  = RoundedRectangle(corner_radius=0.15, width=6.5, height=col_h,\n"
            f"            fill_color='#16213e', fill_opacity=1, stroke_color='#3a5a8a', stroke_width=2)\n"
            f"        right_bg = RoundedRectangle(corner_radius=0.15, width=6.5, height=col_h,\n"
            f"            fill_color='#1e1630', fill_opacity=1, stroke_color='#8a3a5a', stroke_width=2)\n"
            f"        left_bg.next_to(title, DOWN, buff=0.25).to_edge(LEFT, buff=0.2)\n"
            f"        right_bg.next_to(title, DOWN, buff=0.25).to_edge(RIGHT, buff=0.2)\n"
            f"        self.play(\n"
            f"            AnimationGroup(FadeIn(left_bg, shift=RIGHT*0.1), FadeIn(right_bg, shift=LEFT*0.1), lag_ratio=0.1),\n"
            f"            run_time=0.6, rate_func=smooth,\n"
            f"        )\n"
            f"\n"
            f"        l_hdr  = Text({left_header!r}, font_size=28, color=BLUE, weight=BOLD)\n"
            f"        r_hdr  = Text({right_header!r}, font_size=28, color='#ff6b9d', weight=BOLD)\n"
            f"        l_hdr.move_to(left_bg.get_top() + DOWN * 0.42)\n"
            f"        r_hdr.move_to(right_bg.get_top() + DOWN * 0.42)\n"
            f"        l_line = Line(left_bg.get_left()+RIGHT*0.3, left_bg.get_right()+LEFT*0.3,\n"
            f"            color=BLUE).next_to(l_hdr, DOWN, buff=0.12)\n"
            f"        r_line = Line(right_bg.get_left()+RIGHT*0.3, right_bg.get_right()+LEFT*0.3,\n"
            f"            color='#ff6b9d').next_to(r_hdr, DOWN, buff=0.12)\n"
            f"        self.play(\n"
            f"            AnimationGroup(Write(l_hdr), Write(r_hdr), Create(l_line), Create(r_line), lag_ratio=0.15),\n"
            f"            run_time=0.7,\n"
            f"        )\n"
            f"        self.wait(0.25)\n"
            f"\n"
            f"        left_list       = {left_repr}\n"
            f"        right_list      = {right_repr}\n"
            f"        narrations_data = {narrations_repr}\n"
            f"        max_rows = max(len(left_list), len(right_list))\n"
            f"\n"
            f"        for idx in range(max_rows):\n"
            f"            anims    = []\n"
            f"            narration = narrations_data[idx] if idx < len(narrations_data) else ''\n"
            f"            if idx < len(left_list):\n"
            f"                wrapped  = '\\n'.join(textwrap.wrap(left_list[idx], width=28))\n"
            f"                l_bullet = Text('-', font_size={font_size}, color=BLUE)\n"
            f"                l_label  = Paragraph(wrapped, font_size={font_size}, color=WHITE)\n"
            f"                l_item   = VGroup(l_bullet, l_label).arrange(RIGHT, buff=0.2, aligned_edge=UP)\n"
            f"                l_item.next_to(l_line, DOWN, buff=0.3 + idx * {row_height})\n"
            f"                l_item.align_to(left_bg, LEFT).shift(RIGHT * 0.3)\n"
            f"                anims.append(FadeIn(l_item, shift=RIGHT * 0.18))\n"
            f"            if idx < len(right_list):\n"
            f"                wrapped  = '\\n'.join(textwrap.wrap(right_list[idx], width=28))\n"
            f"                r_bullet = Text('-', font_size={font_size}, color='#ff6b9d')\n"
            f"                r_label  = Paragraph(wrapped, font_size={font_size}, color=WHITE)\n"
            f"                r_item   = VGroup(r_bullet, r_label).arrange(RIGHT, buff=0.2, aligned_edge=UP)\n"
            f"                r_item.next_to(r_line, DOWN, buff=0.3 + idx * {row_height})\n"
            f"                r_item.align_to(right_bg, LEFT).shift(RIGHT * 0.3)\n"
            f"                anims.append(FadeIn(r_item, shift=LEFT * 0.18))\n"
            f"            with self.voiceover(text=narration):\n"
            f"                self.play(\n"
            f"                    AnimationGroup(*anims, lag_ratio=0.2),\n"
            f"                    run_time=0.55, rate_func=smooth,\n"
            f"                )\n"
            f"                self.wait(0.2)\n"
            f"\n"
            f"        self.wait(2)\n"
            f"        self.play(FadeOut(*self.mobjects), run_time=0.8)\n"
        )
