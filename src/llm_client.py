from abc import ABC, abstractmethod
import litellm
from .config import Config

class LLMClient(ABC):
    model: str

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
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
        params = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2 if json_mode else 0.7,
        }
        if json_mode:
            params["response_format"] = {"type": "json_object"}
        response = self.client.chat.completions.create(**params)
        content = response.choices[0].message.content
        return str(content) if content is not None else ""

class MistralClient(LLMClient):
    def __init__(self, model: str):
        if not Config.MISTRAL_API_KEY:
            raise ValueError("Mistral API Key is missing.")
        from mistralai import Mistral
        self.client = Mistral(api_key=Config.MISTRAL_API_KEY)
        self.model = model

    def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        response = self.client.chat.complete(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"} if json_mode else None
        )
        content = response.choices[0].message.content
        return str(content) if content is not None else ""

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
        params: dict = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2 if json_mode else 0.7,
        }

        if json_mode:
            params["response_format"] = {"type": "json_object"}

        key = self.api_key or Config.LITELLM_KEY
        if key:
            params["api_key"] = key

        response = litellm.completion(**params)
        content = response.choices[0].message.content
        return str(content) if content is not None else ""

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