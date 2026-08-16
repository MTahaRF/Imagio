from abc import ABC, abstractmethod
from typing import Any
import litellm
from .config import Config

class LLMClient(ABC):
    model: str

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        pass

    @abstractmethod
    def chat(self, messages: list[dict], json_mode: bool = False, tools: list | None = None, tool_choice: str = "auto") -> Any:
        pass

class NebiusClient(LLMClient):
    def __init__(self, model: str):
        api_key = Config.NEBIUS_API_KEY
        if not api_key:
            raise ValueError("Nebius API Key is missing.")
        from openai import OpenAI
        self.client = OpenAI(base_url="https://api.studio.nebius.ai/v1/", api_key=api_key)
        self.model = model

    def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        return self.chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            json_mode=json_mode
        ).content or ""

    def chat(self, messages: list[dict], json_mode: bool = False, tools: list | None = None, tool_choice: str = "auto") -> Any:
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2 if json_mode else 0.7,
        }
        if json_mode:
            params["response_format"] = {"type": "json_object"}
        if tools:
            params["tools"] = tools
            params["tool_choice"] = tool_choice
        response = self.client.chat.completions.create(**params)
        return response.choices[0].message

class MistralClient(LLMClient):
    def __init__(self, model: str):
        if not Config.MISTRAL_API_KEY:
            raise ValueError("Mistral API Key is missing.")
        from mistralai import Mistral
        self.client = Mistral(api_key=Config.MISTRAL_API_KEY)
        self.model = model

    def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        return self.chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            json_mode=json_mode
        ).content or ""

    def chat(self, messages: list[dict], json_mode: bool = False, tools: list | None = None, tool_choice: str = "auto") -> Any:
        params = {
            "model": self.model,
            "messages": messages,
        }
        if json_mode:
            params["response_format"] = {"type": "json_object"}
        if tools:
            params["tools"] = tools
            params["tool_choice"] = tool_choice
        response = self.client.chat.complete(**params)
        return response.choices[0].message

class LiteLLMClient(LLMClient):
    def __init__(self, provider: str, model: str, api_key: str | None = None):
        self.provider = provider
        self.raw_provider = provider.replace("litellm-", "") if provider.startswith("litellm-") else provider
        self.raw_model = model
        self.api_key = api_key
        
        # Ensure litellm model format has provider prefix if needed
        if "/" in model:
            self.model = model
        elif self.raw_provider and self.raw_provider != "openai":
            self.model = f"{self.raw_provider}/{model}"
        else:
            self.model = model

        # Enable json schema validation and drop unsupported params gracefully
        litellm.enable_json_schema_validation = True
        litellm.drop_params = True

    def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        return self.chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            json_mode=json_mode
        ).content or ""

    def chat(self, messages: list[dict], json_mode: bool = False, tools: list | None = None, tool_choice: str = "auto") -> Any:
        params: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2 if json_mode else 0.7,
        }
        if json_mode:
            params["response_format"] = {"type": "json_object"}
        if tools:
            params["tools"] = tools
            params["tool_choice"] = tool_choice

        key = self.api_key or Config.LITELLM_KEY
        if key:
            params["api_key"] = key

        response = litellm.completion(**params)
        return response.choices[0].message

class ClientFactory:
    @staticmethod
    def get_client(agent_config: dict) -> LLMClient:
        provider = agent_config.get("provider", Config.DEFAULT_PROVIDER)
        model = agent_config.get("model", Config.DEFAULT_MODEL)
        api_key = agent_config.get("api_key")

        if provider == Config.PROVIDER_NEBIUS:
            return NebiusClient(model=model)
        elif provider == Config.PROVIDER_MISTRAL:
            return MistralClient(model=model)
        elif provider.startswith("litellm") or provider.startswith("litellm-"):
            return LiteLLMClient(provider=provider, model=model, api_key=api_key)
        else:
            # Fallback to LiteLLM for any registered provider
            return LiteLLMClient(provider=f"litellm-{provider}", model=model, api_key=api_key)