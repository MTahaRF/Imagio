import base64
import hashlib
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from urllib.request import urlopen

import litellm
from openai import OpenAI

from src.config import Config

logger = logging.getLogger(__name__)

_IMAGE_CACHE_DIR = Path(Config.OUTPUT_DIR) / "media" / "generated"
_NEBIUS_IMAGE_API_BASE = "https://api.tokenfactory.nebius.com/v1/"


def validate_image_settings(
    provider: str | None,
    model: str | None,
    api_key: str | None,
) -> tuple[str, str, str]:
    if not isinstance(provider, str) or not provider.strip():
        raise ValueError(
            "Image generation was requested, but image_provider is missing."
        )
    if not isinstance(model, str) or not model.strip():
        raise ValueError(
            "Image generation was requested, but image_model is missing."
        )
    if not isinstance(api_key, str) or not api_key.strip():
        raise ValueError(
            "Image generation was requested, but image_api_key is missing."
        )

    normalized_provider = provider.strip().lower()
    if normalized_provider not in {"nebius", "litellm"}:
        raise ValueError(
            f"Unsupported image provider '{provider}'. "
            "Currently supported: nebius, litellm."
        )

    return normalized_provider, model.strip(), api_key.strip()


class ImageClient(ABC):
    @abstractmethod
    def generate_image(self, prompt: str) -> str:
        """Generate an image and return its absolute file path."""


class NebiusImageClient(ImageClient):
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.client = OpenAI(
            base_url=_NEBIUS_IMAGE_API_BASE,
            api_key=api_key,
            timeout=60.0,
        )

    def generate_image(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("Image prompt cannot be empty.")

        cache_key = hashlib.md5(
            f"{self.model}\0{prompt}".encode("utf-8")
        ).hexdigest()[:12]
        output_path = _IMAGE_CACHE_DIR / f"pic_{cache_key}.png"

        if output_path.is_file():
            logger.info("Image cache hit: %s", output_path)
            return str(output_path.resolve())

        _IMAGE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        response = self.client.images.generate(
            model=self.model,
            prompt=prompt,
            response_format="b64_json",
            n=1,
        )
        if not response.data:
            raise RuntimeError("Image provider returned no image data.")
        image_data = response.data[0].b64_json
        if not image_data:
            raise RuntimeError("Image provider returned no image data.")

        image_bytes = base64.b64decode(image_data)
        if not image_bytes:
            raise RuntimeError("Image provider returned an empty image.")
        output_path.write_bytes(image_bytes)
        logger.info("Generated image: %s", output_path)
        return str(output_path.resolve())


class LiteLLMImageClient(ImageClient):
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key

    def generate_image(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("Image prompt cannot be empty.")

        cache_key = hashlib.md5(
            f"litellm\0{self.model}\0{prompt}".encode("utf-8")
        ).hexdigest()[:12]
        output_path = _IMAGE_CACHE_DIR / f"pic_{cache_key}.png"

        if output_path.is_file():
            logger.info("Image cache hit: %s", output_path)
            return str(output_path.resolve())

        response = litellm.image_generation(
            model=self.model,
            prompt=prompt,
            api_key=self.api_key,
        )
        if not response.data:
            raise RuntimeError("LiteLLM image generation returned no image data.")

        image = response.data[0]
        image_data = image.b64_json
        if image_data:
            image_bytes = base64.b64decode(image_data)
        elif image.url:
            with urlopen(image.url, timeout=60) as image_response:
                image_bytes = image_response.read()
        else:
            raise RuntimeError(
                "LiteLLM image response contained neither base64 data nor a URL."
            )

        if not image_bytes:
            raise RuntimeError("LiteLLM image generation returned an empty image.")

        _IMAGE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(image_bytes)
        logger.info("Generated image via LiteLLM: %s", output_path)
        return str(output_path.resolve())


class ImageClientFactory:
    @staticmethod
    def create(
        provider: str | None,
        model: str | None,
        api_key: str | None,
    ) -> ImageClient:
        normalized_provider, normalized_model, normalized_api_key = (
            validate_image_settings(provider, model, api_key)
        )
        if normalized_provider == "nebius":
            return NebiusImageClient(
                model=normalized_model,
                api_key=normalized_api_key,
            )
        if normalized_provider == "litellm":
            return LiteLLMImageClient(
                model=normalized_model,
                api_key=normalized_api_key,
            )
        raise ValueError(f"Unsupported image provider '{provider}'.")
