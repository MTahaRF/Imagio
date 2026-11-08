import base64
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import run_pipeline
from src.agents.planner import ScenePlanner
from src.image_client import (
    ImageClientFactory,
    LiteLLMImageClient,
    NebiusImageClient,
)
from src.templates.picture_slide import PictureSlideTemplate
from src.templates.registry import list_templates


class _PlannerClient:
    def __init__(self, response: str):
        self.response = response
        self.system_prompt = ""
        self.user_prompt = ""
        self.json_mode = False

    def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.json_mode = json_mode
        return self.response


class TemplateCapabilityTest(unittest.TestCase):
    def test_picture_slide_is_only_listed_with_image_capability(self):
        unavailable = {template["name"] for template in list_templates(set())}
        available = {
            template["name"]
            for template in list_templates({"image_generation"})
        }

        self.assertNotIn("picture_slide", unavailable)
        self.assertIn("picture_slide", available)

    def test_planner_prompt_omits_picture_slide_by_default(self):
        client = _PlannerClient('{"scenes":[{"template_type":"title_slide"}]}')
        planner = ScenePlanner(client)

        planner.plan_scenes({})

        self.assertNotIn('"name": "picture_slide"', client.user_prompt)

    def test_planner_rejects_unavailable_template_selection(self):
        client = _PlannerClient('{"scenes":[{"template_type":"picture_slide"}]}')
        planner = ScenePlanner(client)

        with self.assertRaisesRegex(ValueError, "unavailable template 'picture_slide'"):
            planner.plan_scenes({})

    def test_planner_can_select_picture_slide_when_enabled(self):
        client = _PlannerClient('{"scenes":[{"template_type":"picture_slide"}]}')
        planner = ScenePlanner(client)

        scenes = planner.plan_scenes({}, enabled_capabilities={"image_generation"})

        self.assertEqual(scenes[0]["template_type"], "picture_slide")
        self.assertIn('"name": "picture_slide"', client.user_prompt)
        self.assertTrue(client.json_mode)

    @patch("pipeline.ClientFactory.get_client")
    def test_pipeline_fails_before_llm_setup_when_image_settings_are_missing(
        self,
        get_client,
    ):
        with self.assertRaisesRegex(ValueError, "image_provider is missing"):
            run_pipeline("test topic", want_image=True)

        get_client.assert_not_called()

    @patch("pipeline.VideoMerger")
    @patch("pipeline.SceneDirector")
    @patch("pipeline.ScenePlanner")
    @patch("pipeline.FeasibilityAgent")
    @patch("pipeline.ClientFactory.get_client")
    def test_pipeline_disables_image_capability_by_default(
        self,
        get_client,
        feasibility_agent,
        planner,
        _director,
        _merger,
    ):
        feasibility_agent.return_value.analyze_topic.return_value = {
            "feasible": True,
            "curriculum": {"title": "test"},
        }
        planner.return_value.plan_scenes.return_value = []

        self.assertIsNone(run_pipeline("test topic"))

        planner.return_value.plan_scenes.assert_called_once_with(
            {"title": "test"},
            lang_code="en",
            enabled_capabilities=set(),
        )
        self.assertEqual(get_client.call_count, 3)
        _director.assert_called_once()
        _merger.assert_called_once()

    @patch("pipeline.ImageClientFactory.create", return_value=object())
    @patch("pipeline.VideoMerger")
    @patch("pipeline.SceneDirector")
    @patch("pipeline.ScenePlanner")
    @patch("pipeline.FeasibilityAgent")
    @patch("pipeline.ClientFactory.get_client")
    def test_pipeline_enables_image_capability_when_configured(
        self,
        _get_client,
        feasibility_agent,
        planner,
        _director,
        _merger,
        create_image_client,
    ):
        feasibility_agent.return_value.analyze_topic.return_value = {
            "feasible": True,
            "curriculum": {"title": "test"},
        }
        planner.return_value.plan_scenes.return_value = []

        self.assertIsNone(
            run_pipeline(
                "test topic",
                want_image=True,
                image_provider="nebius",
                image_model="image-model",
                image_api_key="separate-key",
            )
        )

        create_image_client.assert_called_once_with(
            "nebius",
            "image-model",
            "separate-key",
        )
        self.assertEqual(_get_client.call_count, 3)
        planner.return_value.plan_scenes.assert_called_once_with(
            {"title": "test"},
            lang_code="en",
            enabled_capabilities={"image_generation"},
        )
        _director.assert_called_once()
        _merger.assert_called_once()


class ImageClientTest(unittest.TestCase):
    def test_image_generation_requires_provider_model_and_key(self):
        for settings in (
            (None, "model", "key"),
            ("nebius", None, "key"),
            ("nebius", "model", None),
        ):
            with self.subTest(settings=settings):
                with self.assertRaises(ValueError):
                    ImageClientFactory.create(*settings)

    def test_factory_rejects_unsupported_provider(self):
        with self.assertRaisesRegex(ValueError, "Currently supported: nebius, litellm"):
            ImageClientFactory.create("openai", "model", "key")

    @patch("src.image_client.OpenAI")
    def test_nebius_client_uses_configured_model_and_caches_image(self, openai):
        image_bytes = b"png-image"
        openai.return_value.images.generate.return_value = SimpleNamespace(
            data=[
                SimpleNamespace(
                    b64_json=base64.b64encode(image_bytes).decode("ascii")
                )
            ]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("src.image_client._IMAGE_CACHE_DIR", Path(temp_dir)):
                client = ImageClientFactory.create(
                    "nebius",
                    "custom-image-model",
                    "separate-image-key",
                )
                self.assertIsInstance(client, NebiusImageClient)

                image_path = Path(client.generate_image("A bright blue planet"))

                self.assertEqual(image_path.read_bytes(), image_bytes)
                openai.return_value.images.generate.assert_called_once_with(
                    model="custom-image-model",
                    prompt="A bright blue planet",
                    response_format="b64_json",
                    n=1,
                )
                self.assertEqual(client.generate_image("A bright blue planet"), str(image_path))
                openai.return_value.images.generate.assert_called_once()

    @patch("src.image_client.litellm.image_generation")
    def test_litellm_client_uses_model_route_and_api_key_and_caches_image(
        self,
        image_generation,
    ):
        image_bytes = b"litellm-image"
        image_generation.return_value = SimpleNamespace(
            data=[
                SimpleNamespace(
                    b64_json=base64.b64encode(image_bytes).decode("ascii"),
                    url=None,
                )
            ]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("src.image_client._IMAGE_CACHE_DIR", Path(temp_dir)):
                client = ImageClientFactory.create(
                    "litellm",
                    "stability/sd3.5-large",
                    "shared-image-key",
                )
                self.assertIsInstance(client, LiteLLMImageClient)

                image_path = Path(client.generate_image("A bright blue planet"))

                self.assertEqual(image_path.read_bytes(), image_bytes)
                image_generation.assert_called_once_with(
                    model="stability/sd3.5-large",
                    prompt="A bright blue planet",
                    api_key="shared-image-key",
                )
                self.assertEqual(
                    client.generate_image("A bright blue planet"),
                    str(image_path),
                )
                image_generation.assert_called_once()

    @patch("src.image_client.urlopen")
    @patch("src.image_client.litellm.image_generation")
    def test_litellm_client_downloads_url_response(
        self,
        image_generation,
        open_image_url,
    ):
        image_generation.return_value = SimpleNamespace(
            data=[SimpleNamespace(b64_json=None, url="https://images.example/image.png")]
        )
        response = open_image_url.return_value.__enter__.return_value
        response.read.return_value = b"downloaded-image"

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("src.image_client._IMAGE_CACHE_DIR", Path(temp_dir)):
                client = ImageClientFactory.create(
                    "litellm",
                    "fal_ai/fal-ai/flux-pro/v1.1-ultra",
                    "shared-image-key",
                )

                image_path = Path(client.generate_image("A quiet mountain landscape"))
                self.assertEqual(image_path.read_bytes(), b"downloaded-image")

        open_image_url.assert_called_once_with(
            "https://images.example/image.png",
            timeout=60,
        )

    def test_picture_template_requires_pipeline_supplied_image(self):
        template = PictureSlideTemplate()

        with self.assertRaisesRegex(ValueError, "requires a generated image_path"):
            template._scene_body({"image_prompt": "a visual"}, "narration")

    def test_picture_template_uses_supplied_image_without_provider_calls(self):
        template = PictureSlideTemplate()
        with tempfile.NamedTemporaryFile(suffix=".png") as image:
            code = template._scene_body(
                {"image_prompt": "a visual", "image_path": image.name},
                "narration",
            )

        self.assertIn(repr(image.name), code)
        self.assertNotIn("[ Image ]", code)


if __name__ == "__main__":
    unittest.main()
