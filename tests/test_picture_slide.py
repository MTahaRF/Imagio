import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from imageio_ffmpeg import get_ffmpeg_exe
from src.config import Config
from src.templates.picture_slide import PictureSlideTemplate
from src.tools.manim_runner import render_code_string


PICTURE_SLIDE_JSON = json.loads(
    """
    {
      "title": "How steel is made",
      "image_prompt": "A clean scientific illustration of steel production",
      "image_path": "fixture-image.png",
      "caption": "From ore to finished steel",
      "points": [
        {
          "text": "Mining extracts iron ore",
          "narration": "First, miners carefully extract iron ore from deep underground deposits and transport the raw material by rail to a nearby processing plant, where it is sorted before any refining can begin. There, workers use crushing and magnetic separation to remove unwanted rock, concentrating iron-rich material before it is transported to the furnace for the next stage of steel production."
        },
        {
          "text": "Furnaces melt the ore",
          "narration": "Next, a furnace heats the ore until it becomes liquid iron."
        },
        {
          "text": "Refining produces steel",
          "narration": "Finally, refining controls the carbon to create useful steel."
        }
      ]
    }
    """
)


class PictureSlideTemplateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.template = PictureSlideTemplate()
        self.image = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        self.image.close()
        Image.new("RGB", (96, 64), "white").save(self.image.name)
        self.addCleanup(os.unlink, self.image.name)
        self.data = {**PICTURE_SLIDE_JSON, "image_path": self.image.name}

    def test_generated_scene_speaks_each_point_as_it_reveals_it(self):
        source = self.template.code(
            self.data,
            "A short introduction to the steelmaking process.",
        )
        compile(source, "<picture-slide-test>", "exec")

        self.assertIn(
            "('Mining extracts iron ore', "
            "'First, miners carefully extract iron ore from deep underground deposits and transport the raw material by rail to a nearby processing plant, where it is sorted before any refining can begin. "
            "There, workers use crushing and magnetic separation to remove unwanted rock, concentrating iron-rich material before it is transported to the furnace for the next stage of steel production.')",
            source,
        )
        self.assertIn(
            "('Furnaces melt the ore', "
            "'Next, a furnace heats the ore until it becomes liquid iron.')",
            source,
        )
        self.assertIn(
            "with self.voiceover(text=point_narration):",
            source,
        )
        self.assertIn(
            "animations = [FadeIn(row, shift=LEFT * 0.15)]",
            source,
        )
        self.assertIn("image.set_z_index(-1)", source)
        self.assertIn("cap_group = VGroup(*mobs)", source)
        self.assertIn(
            "caption.set_opacity(1 if i == idx else 0)",
            source,
        )
        self.assertIn("cap_group.set_z_index(100)", source)
        self.assertNotIn("mob.submobjects = [target]", source)
        self.assertLess(
            source.index("self.play(FadeOut(caption_obj), run_time=0.3)"),
            source.index("with self.voiceover(text=point_narration):"),
        )
        self.assertLess(
            source.index(
                "with self.voiceover(text='A short introduction to the steelmaking process.')"
            ),
            source.index("self.play(FadeIn(image, shift=RIGHT * 0.15)"),
        )

    def test_legacy_string_points_are_used_as_their_own_narration(self):
        self.data["points"] = ["Ore is mined", "Iron is refined"]

        source = self.template.code(self.data, "A short introduction.")

        self.assertIn(
            "points_data = [('Ore is mined', 'Ore is mined'), "
            "('Iron is refined', 'Iron is refined')]",
            source,
        )
        compile(source, "<picture-slide-legacy-test>", "exec")

    def test_structured_points_require_narration(self):
        self.data["points"] = [{"text": "Ore is mined"}]

        with self.assertRaisesRegex(ValueError, "requires non-empty narration"):
            self.template.code(self.data, "A short introduction.")

    @unittest.skipUnless(
        (Path(Config.PIPER_MODELS_DIR) / "en_US-lessac-medium.onnx").is_file(),
        "English Piper voice model is not installed",
    )
    def test_prewritten_json_renders_with_decodable_voiceover(self):
        source = self.template.code(
            self.data,
            "Steel begins as iron ore, then becomes a material used everywhere.",
        )
        scene_name = "picture_slide_test_fixture"
        scene_file = Path(Config.BASE_DIR) / "workspace" / "code" / f"{scene_name}.py"
        output_dir = Path(Config.OUTPUT_DIR) / "test_renders" / "picture_slide"
        output_dir.mkdir(parents=True, exist_ok=True)
        video_path = output_dir / "picture_slide_test.mp4"
        self.addCleanup(lambda: scene_file.unlink(missing_ok=True))

        result = render_code_string(
            code=source,
            scene_name=scene_name,
            code_dir=str(scene_file.parent),
            output_dir=str(output_dir / "manim"),
            max_retries=1,
        )
        self.assertTrue(result.success, result.error_log)
        self.assertIsNotNone(result.mp4_path)
        assert isinstance(result.mp4_path, str)
        shutil.copy2(result.mp4_path, video_path)
        decode = subprocess.run(
            [
                get_ffmpeg_exe(),
                "-v",
                "error",
                "-i",
                str(video_path),
                "-map",
                "0:a:0",
                "-f",
                "null",
                "-",
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(decode.returncode, 0, decode.stderr)
        self.assertTrue(video_path.is_file())
        self.assertGreater(video_path.stat().st_size, 0)
        frame_path = Path(tempfile.gettempdir()) / f"{scene_name}_caption_frame.png"
        self.addCleanup(lambda: frame_path.unlink(missing_ok=True))
        frame = subprocess.run(
            [
                get_ffmpeg_exe(),
                "-y",
                "-v",
                "error",
                "-ss",
                "8",
                "-i",
                str(video_path),
                "-frames:v",
                "1",
                str(frame_path),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(frame.returncode, 0, frame.stderr)
        with Image.open(frame_path) as rendered_frame:
            overlap_pixel = rendered_frame.convert("RGB").getpixel((350, 545))
        self.assertLess(
            max(overlap_pixel),
            100,
            f"Caption background should cover the image at the overlap, got {overlap_pixel}",
        )


if __name__ == "__main__":
    unittest.main()
