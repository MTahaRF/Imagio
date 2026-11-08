from __future__ import annotations

import os
from .base import BaseTemplate


class PictureSlideTemplate(BaseTemplate):

    # ── Registry interface ────────────────────────────────────────────────────

    def description(self) -> str:
        return (
            "Use when a scene needs a generated illustration alongside supporting text. "
            "The configured image provider generates an image from image_prompt at pipeline time; "
            "the image is placed on the left and body_text on the right. "
            "Best for visual concepts, real-world analogies, and scientific diagrams. "
            "Do NOT use for equations, graphs, or code."
        )

    def schema(self) -> dict:
        return {
            "title":        "Heading at the top of the slide",
            "image_prompt": "Vivid plain-English description of the image to generate (10-30 words, scientific illustration style, clean white background)",
            "caption":      "Short caption displayed directly below the image (1 sentence)",
            "points": [
                {
                    "text": "Short on-screen takeaway (max 10 words)",
                    "narration": "A spoken sentence explaining this takeaway.",
                },
            ],
        }

    def prompt(self) -> str:
        return (
            "You are filling JSON for a Manim picture-slide scene.\n"
            "Return ONLY a JSON object — no markdown, no explanation.\n\n"
            "Schema:\n"
            "{\n"
            '  "title":        "Slide heading",\n'
            '  "image_prompt": "Detailed visual description for AI image generation",\n'
            '  "caption":      "Short caption under the image",\n'
            '  "points":       [\n'
            '    {"text": "Short takeaway 1", "narration": "Explain takeaway 1."},\n'
            '    {"text": "Short takeaway 2", "narration": "Explain takeaway 2."}\n'
            "  ]\n"
            "}\n\n"
            "Rules:\n"
            "- All values are plain strings (no LaTeX).\n"
            "- image_prompt: vivid, 10-30 words, scientific illustration style, clean white background.\n"
            "- caption: 1 short sentence (max 8 words).\n"
            "- points: 2-3 objects, each with a short on-screen text and matching spoken narration.\n"
            "- Each point's narration explains only that point and is spoken while that point appears.\n"
            "- Keep each point's text short (max 10 words); narration should be 1-2 natural sentences.\n"
            "- The scene-level script is only a brief introduction to the image, not narration for the points.\n"
        )

    # ── _scene_body — the only abstract method templates must implement ────────

    def _scene_body(self, data: dict, script: str) -> str:
        """
        Returns the indented animation lines for construct().
        base.code() wraps these with imports, VoiceoverScene, speech service, etc.
        The pipeline supplies the image path so the template remains provider-agnostic.
        """
        title        = data.get("title", "")
        image_prompt = data.get("image_prompt", "")
        caption      = data.get("caption", "")
        
        # Support legacy string points/body_text while migrating generated slide data.
        raw_points = data.get("points")
        if not raw_points:
            raw_body = data.get("body_text", "")
            if raw_body:
                import re
                sentences = [s.strip() for s in re.split(r'[.!?]+', raw_body) if s.strip()]
                raw_points = sentences[:3] if sentences else [raw_body]
            else:
                raw_points = []

        if not isinstance(raw_points, list):
            raise ValueError("picture_slide points must be a list.")

        points: list[tuple[str, str]] = []
        for point in raw_points:
            if isinstance(point, str):
                text = point.strip()
                narration = text
            elif isinstance(point, dict):
                text = point.get("text")
                narration = point.get("narration")
                if not isinstance(text, str) or not text.strip():
                    raise ValueError(
                        "Each picture_slide point requires non-empty text."
                    )
                if not isinstance(narration, str) or not narration.strip():
                    raise ValueError(
                        "Each picture_slide point requires non-empty narration."
                    )
                text = text.strip()
                narration = narration.strip()
            else:
                raise ValueError(
                    "Each picture_slide point must be text or an object "
                    "containing text and narration."
                )
            if text:
                points.append((text, narration))

        image_path = data.get("image_path")
        if not isinstance(image_path, str) or not image_path:
            raise ValueError("picture_slide requires a generated image_path.")
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Generated picture-slide image not found: {image_path}")

        title_fs        = self._title_font_size(title)
        wrapped_title   = self._wrap_text(title, width=38)
        wrapped_caption = self._wrap_text(caption, width=28)
        points_data = [
            (self._wrap_text(text, width=30), narration)
            for text, narration in points
        ]

        narration = script or "Let us examine this illustration."

        lines = []

        # Title
        lines += [
            f"        title = Text({wrapped_title!r}, font_size={title_fs}, color=WHITE, weight=BOLD)",
            f"        _safe_fit(title, max_w=11.5, min_scale=0.85)",
            f"        title.to_edge(UP, buff=0.4)",
            f"        self.play(Write(title), run_time=0.8, rate_func=smooth)",
            f"        self.wait(0.3)",
            f"",
        ]

        # Image
        lines += [
            f"        # Generated image for: {image_prompt!r}",
            f"        _image_path = {image_path!r}",
            f"        image = ImageMobject(_image_path)",
            f"        image.set_height(4.0)",
            f"        image.move_to(LEFT * 2.8 + DOWN * 0.25)",
            f"        image.set_z_index(-1)",
            f"        with self.voiceover(text={narration!r}):",
            f"            self.play(FadeIn(image, shift=RIGHT * 0.15), run_time=0.8, rate_func=smooth)",
            f"        self.wait(0.3)",
            f"",
        ]

        # Caption
        if caption:
            lines += [
                f"        caption_obj = Text({wrapped_caption!r}, font_size=20,",
                f"            color='#a0a8d0', slant=ITALIC, line_spacing=1.1)",
                f"        _safe_fit(caption_obj, max_w=4.8, min_scale=0.82)",
                f"        caption_obj.next_to(image, DOWN, buff=0.18)",
                f"        self.play(FadeIn(caption_obj, shift=UP * 0.1), run_time=0.5)",
                f"        self.wait(0.25)",
                f"",
            ]

        # Point-by-point narration on the right
        if points:
            lines += [
                f"        points_data = {points_data!r}",
                f"        point_rows = VGroup()",
                f"        for point_text, _point_narration in points_data:",
                f"            dot   = Text('•', font_size=24, color=YELLOW)",
                f"            label = Text(point_text, font_size=24, color=WHITE, line_spacing=1.15)",
                f"            _safe_fit(label, max_w=4.8, min_scale=0.85)",
                f"            row   = VGroup(dot, label).arrange(RIGHT, buff=0.2, aligned_edge=UP)",
                f"            point_rows.add(row)",
                f"        point_rows.arrange(DOWN, buff=0.32, aligned_edge=LEFT)",
                f"        _safe_fit(point_rows, max_w=5.4, max_h=4.6, min_scale=0.82)",
                f"        point_rows.move_to(RIGHT * 3.2 + DOWN * 0.2)",
            ]
            if caption:
                lines.append(
                    "        self.play(FadeOut(caption_obj), run_time=0.3)"
                )
            lines += [
                f"        for i, (row, (_point_text, point_narration)) in enumerate(zip(point_rows, points_data)):",
                f"            with self.voiceover(text=point_narration):",
                f"                animations = [FadeIn(row, shift=LEFT * 0.15)]",
                f"                if i > 0:",
                f"                    animations.append(point_rows[i - 1].animate.set_opacity(0.45))",
                f"                self.play(*animations, run_time=0.8, rate_func=smooth)",
                f"                self.wait(0.2)",
                f"",
            ]

        # Outro
        lines += [
            f"        self.wait(2)",
            f"        self.play(FadeOut(*self.mobjects), run_time=0.8)",
        ]

        return "\n".join(lines)