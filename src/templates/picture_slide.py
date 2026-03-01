from .base import BaseTemplate

class PictureSlideTemplate(BaseTemplate):

    def description(self) -> str:
        return (
            "Use when a scene needs to display an image alongside supporting text. "
            "Image is shown on the left; body text on the right. "
            "Requires an actual image file path. Do NOT use if no image file is available — "
            "use split_slide or bullet_points instead."
        )

    def schema(self) -> dict:
        return {
            "title":      "Heading at the top of the slide",
            "image_path": "Absolute or relative path to the image file (PNG or JPG)",
            "caption":    "Short caption displayed directly below the image",
            "body_text":  "Explanatory paragraph shown on the right side",
            "narrations": {
                "image":   "Spoken narration when the image appears",
                "caption": "Spoken narration for the caption (or empty string)",
                "body":    "Spoken narration for the body text",
            },
        }

    def prompt(self) -> str:
        return (
            "You are filling JSON for a Manim picture-slide scene.\n"
            "Return ONLY a JSON object — no markdown, no explanation.\n\n"
            "Schema:\n"
            "{\n"
            '  "title": "Slide heading",\n'
            '  "image_path": "path/to/image.png",\n'
            '  "caption": "Short caption under the image",\n'
            '  "body_text": "Paragraph explaining the image",\n'
            '  "narrations": {\n'
            '    "image": "Narration when image appears",\n'
            '    "caption": "Narration for caption",\n'
            '    "body": "Narration for body text"\n'
            "  }\n"
            "}\n\n"
            "Rules:\n"
            "- All values are plain strings (no LaTeX).\n"
            "- caption is 1 short sentence.\n"
            "- body_text is 2-4 sentences.\n"
            "- Each narration is a natural spoken sentence (max 25 words).\n"
        )

    def _scene_body(self, data: dict, script: str) -> str:
        title      = data.get("title", "")
        image_path = data.get("image_path", "")
        caption    = data.get("caption", "")
        body_text  = data.get("body_text", "")
        narrations = data.get("narrations", {})

        n_image   = narrations.get("image",   "Let us look at this illustration.")
        n_caption = narrations.get("caption", caption or "")
        n_body    = narrations.get("body",    body_text or script)
        title_fs  = self._title_font_size(title)
        body_fs   = self._auto_font_size(body_text)

        return (
            f"        import os, textwrap\n"
            f"\n"
            f"        title = Text({title!r}, font_size={title_fs}, color=WHITE, weight=BOLD)\n"
            f"        title.to_edge(UP, buff=0.4)\n"
            f"        self.play(Write(title), run_time=0.8, rate_func=smooth)\n"
            f"        self.wait(0.3)\n"
            f"\n"
            f"        image_path = {image_path!r}\n"
            f"        if image_path and os.path.exists(image_path):\n"
            f"            image = ImageMobject(image_path)\n"
            f"            image.set_height(4.0)\n"
            f"        else:\n"
            f"            placeholder = Rectangle(width=5.0, height=3.6,\n"
            f"                fill_color='#2a2a4a', fill_opacity=1,\n"
            f"                stroke_color='#666688', stroke_width=2)\n"
            f"            label = Text('[ Image ]', font_size=26, color='#666688')\n"
            f"            label.move_to(placeholder.get_center())\n"
            f"            image = VGroup(placeholder, label)\n"
            f"        image.move_to(LEFT * 3.0 + DOWN * 0.3)\n"
            f"        with self.voiceover(text={n_image!r}):\n"
            f"            self.play(FadeIn(image, shift=RIGHT * 0.15), run_time=0.8, rate_func=smooth)\n"
            f"            self.wait(0.3)\n"
            f"\n"
            f"        if {caption!r}:\n"
            f"            wrapped_cap = '\\n'.join(textwrap.wrap({caption!r}, width=30))\n"
            f"            caption_obj = Paragraph(wrapped_cap, font_size=18,\n"
            f"                color='#a0a8d0', alignment='center')\n"
            f"            caption_obj.next_to(image, DOWN, buff=0.18)\n"
            f"            with self.voiceover(text={n_caption!r}):\n"
            f"                self.play(FadeIn(caption_obj, shift=UP*0.1), run_time=0.5)\n"
            f"                self.wait(0.25)\n"
            f"\n"
            f"        if {body_text!r}:\n"
            f"            wrapped_body = '\\n'.join(textwrap.wrap({body_text!r}, width=35))\n"
            f"            body = Paragraph(wrapped_body, font_size={body_fs}, color=WHITE,\n"
            f"                line_spacing=1.2, alignment='left')\n"
            f"            body.move_to(RIGHT * 3.2 + DOWN * 0.3)\n"
            f"            if body.height > 5:\n"
            f"                body.scale(5 / body.height)\n"
            f"            with self.voiceover(text={n_body!r}):\n"
            f"                self.play(FadeIn(body, shift=LEFT * 0.15), run_time=0.9, rate_func=smooth)\n"
            f"                self.wait(0.3)\n"
            f"\n"
            f"        self.wait(2)\n"
            f"        self.play(FadeOut(*self.mobjects), run_time=0.8)\n"
        )
