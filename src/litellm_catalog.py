import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

CATALOG_PATH = Path(__file__).resolve().parent / "litellm-models" / "model_prices_and_context_window.json"

class ModelCatalog:
    _cached_data: Optional[Dict[str, Any]] = None
    _catalog: Optional[Dict[str, List[Dict[str, Any]]]] = None

    @classmethod
    def _load_data(cls) -> Dict[str, Any]:
        if cls._cached_data is None:
            if not CATALOG_PATH.exists():
                raise FileNotFoundError(f"Model catalog JSON not found at: {CATALOG_PATH}")
            with open(CATALOG_PATH, "r", encoding="utf-8") as f:
                cls._cached_data = json.load(f)
        return cls._cached_data

    @classmethod
    def get_providers_and_models(cls) -> Dict[str, Any]:
        """
        Returns all LiteLLM providers and their models that satisfy:
        1. mode == 'chat'
        2. supports_response_schema == True
        """
        if cls._catalog is not None:
            return cls._catalog

        raw_data = cls._load_data()
        providers_map: Dict[str, List[Dict[str, Any]]] = {}

        for model_name, info in raw_data.items():
            if model_name == "sample_spec" or not isinstance(info, dict):
                continue

            mode = info.get("mode")
            supports_schema = info.get("supports_response_schema", False)
            raw_provider = info.get("litellm_provider", "")

            # Filter: chat mode and supports response schema
            if mode == "chat" and supports_schema is True and raw_provider:
                provider_id = f"litellm-{raw_provider}"
                
                model_entry = {
                    "model": model_name,
                    "max_input_tokens": info.get("max_input_tokens"),
                    "max_output_tokens": info.get("max_output_tokens"),
                    "supports_vision": info.get("supports_vision", False),
                    "supports_function_calling": info.get("supports_function_calling", False),
                }

                if provider_id not in providers_map:
                    providers_map[provider_id] = []
                providers_map[provider_id].append(model_entry)

        # Sort providers and models alphabetically
        sorted_catalog = []
        for provider_id in sorted(providers_map.keys()):
            models = sorted(providers_map[provider_id], key=lambda m: m["model"])
            raw_provider_name = provider_id.replace("litellm-", "")
            sorted_catalog.append({
                "provider_id": provider_id,
                "provider_name": raw_provider_name,
                "model_count": len(models),
                "models": models,
            })

        cls._catalog = {"providers": sorted_catalog}
        return cls._catalog

    @classmethod
    def is_valid_provider_and_model(cls, provider: str, model: str) -> bool:
        catalog = cls.get_providers_and_models()
        for p in catalog.get("providers", []):
            if p["provider_id"] == provider or p["provider_name"] == provider:
                for m in p["models"]:
                    if m["model"] == model:
                        return True
        return False
