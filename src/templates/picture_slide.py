from __future__ import annotations

import os
import base64
import hashlib
import logging

from .base import BaseTemplate

logger = logging.getLogger(__name__)

# Generated images are saved here so Manim can load them by absolute path.
_IMAGE_CACHE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "..", "..", "workspace", "media", "generated"
    )
)


class PictureSlideTemplate(BaseTemplate):

    # ── Registry interface ────────────────────────────────────────────────────

    def description(self) -> str:
        return (
            "Use when a scene needs a generated illustration alongside supporting text. "
            "Nebius FLUX generates an image from image_prompt at pipeline time; "
            "the image is placed on the left and body_text on the right. "
            "Best for visual concepts, real-world analogies, and scientific diagrams. "
            "Do NOT use for equations, graphs, or code."
        )

    def schema(self) -> dict:
        return {
            "title":        "Heading at the top of the slide",
            "image_prompt": "Vivid plain-English description of the image to generate (10-30 words, scientific illustration style, clean white background)",
            "caption":      "Short caption displayed directly below the image (1 sentence)",
            "body_text":    "Explanatory paragraph shown on the right side (2-4 sentences)",
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
            '  "body_text":    "2-4 sentences explaining the concept"\n'
            "}\n\n"
            "Rules:\n"
            "- All values are plain strings (no LaTeX).\n"
            "- image_prompt: vivid, 10-30 words, scientific illustration style, clean white background.\n"
            "- caption: 1 short sentence.\n"
            "- body_text: 2-4 sentences.\n"
        )

    # ── Nebius FLUX image generation ──────────────────────────────────────────

    def _generate_image(self, image_prompt: str) -> str:
        """
        Call Nebius FLUX-schnell to generate a PNG from image_prompt.
        Saves to workspace/media/generated/pic_<md5>.png.
        Returns the absolute path on success, empty string on any failure.

        Same prompt always reuses the cached file — zero repeat API cost.
        """
        os.makedirs(_IMAGE_CACHE_DIR, exist_ok=True)

        slug     = hashlib.md5(image_prompt.encode()).hexdigest()[:12]
        out_path = os.path.join(_IMAGE_CACHE_DIR, f"pic_{slug}.png")

        if os.path.exists(out_path):
            logger.info(f"[picture_slide] Cache hit: {out_path}")
            return out_path

        api_key = os.environ.get("NEBIUS_API_KEY", "")
        if not api_key:
            logger.warning(
                "[picture_slide] NEBIUS_API_KEY not set — image generation skipped, "
                "placeholder will be shown."
            )
            return ""

        try:
            from openai import OpenAI
            import httpx

            client = OpenAI(
                base_url="https://api.tokenfactory.nebius.com/v1/",
                api_key=api_key,
                http_client=httpx.Client(timeout=60.0),
            )

            logger.info(f"[picture_slide] Generating image for: {image_prompt!r}")
            response = client.images.generate(
                model="black-forest-labs/flux-schnell",
                prompt=image_prompt,
                response_format="b64_json",
                n=1,
            )

            img_bytes = base64.b64decode(response.data[0].b64_json)
            with open(out_path, "wb") as f:
                f.write(img_bytes)

            logger.info(f"[picture_slide] Saved: {out_path}")
            return out_path

        except Exception as exc:
            logger.error(f"[picture_slide] Generation failed: {exc}")
            return ""

    # ── _scene_body — the only abstract method templates must implement ────────

    def _scene_body(self, data: dict, script: str) -> str:
        """
        Returns the indented animation lines for construct().
        base.code() wraps these with imports, VoiceoverScene, speech service, etc.
        Image generation is called here so the resolved path is baked in.
        """
        title        = data.get("title", "")
        image_prompt = data.get("image_prompt", "")
        caption      = data.get("caption", "")
        body_text    = data.get("body_text", "")

        # ── Generate image at pipeline time ───────────────────────────────────
        # The absolute path is baked as a literal into the Manim source.
        # Empty string → scene shows placeholder, no crash.
        image_path = self._generate_image(image_prompt) if image_prompt else ""

        title_fs = self._title_font_size(title)
        body_fs  = self._auto_font_size(body_text)

        # Build the narration text: use script if provided, else body_text
        narration = script or body_text or "Let us examine this illustration."

        # ── Lines that go inside construct() — indented 8 spaces ─────────────
        lines = []

        # Title
        lines += [
            f"        title = Text({title!r}, font_size={title_fs}, color=WHITE, weight=BOLD)",
            f"        title.to_edge(UP, buff=0.4)",
            f"        self.play(Write(title), run_time=0.8, rate_func=smooth)",
            f"        self.wait(0.3)",
            f"",
        ]

        # Image — path is a literal resolved string
        lines += [
            f"        # Image generated by Nebius FLUX from: {image_prompt!r}",
            f"        _image_path = {image_path!r}",
            f"        if _image_path and os.path.exists(_image_path):",
            f"            image = ImageMobject(_image_path)",
            f"            image.set_height(4.0)",
            f"        else:",
            f"            _ph_bg  = Rectangle(width=5.0, height=3.6,",
            f"                fill_color='#2a2a4a', fill_opacity=1,",
            f"                stroke_color='#666688', stroke_width=2)",
            f"            _ph_lbl = Text('[ Image ]', font_size=26, color='#666688')",
            f"            _ph_lbl.move_to(_ph_bg.get_center())",
            f"            image   = VGroup(_ph_bg, _ph_lbl)",
            f"        image.move_to(LEFT * 2.8 + DOWN * 0.3)",
            f"        with self.voiceover(text={narration!r}):",
            f"            self.play(FadeIn(image, shift=RIGHT * 0.15), run_time=0.8, rate_func=smooth)",
            f"        self.wait(0.3)",
            f"",
        ]

        # Caption (optional)
        if caption:
            lines += [
                f"        caption_obj = Text({caption!r}, font_size=20,",
                f"            color='#a0a8d0', slant=ITALIC)",
                f"        caption_obj.next_to(image, DOWN, buff=0.2)",
                f"        self.play(FadeIn(caption_obj, shift=UP * 0.1), run_time=0.5)",
                f"        self.wait(0.25)",
                f"",
            ]

        # Body text (optional)
        if body_text:
            lines += [
                f"        # body_text font size: {len(body_text.split())} words -> {body_fs}pt",
                f"        body = Text({body_text!r}, font_size={body_fs},",
                f"            color=WHITE, line_spacing=1.4)",
                f"        body.set_width(4.8)",
                f"        body.move_to(RIGHT * 3.0 + DOWN * 0.3)",
                f"        if body.height > 5.0:",
                f"            body.scale(5.0 / body.height)",
                f"        self.play(FadeIn(body, shift=LEFT * 0.15), run_time=0.9, rate_func=smooth)",
                f"        self.wait(0.3)",
                f"",
            ]

        # Outro
        lines += [
            f"        self.wait(2)",
            f"        self.play(FadeOut(*self.mobjects), run_time=0.8)",
        ]

        return "\n".join(lines)