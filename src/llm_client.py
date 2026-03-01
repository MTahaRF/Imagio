from abc import ABC, abstractmethod
from openai import OpenAI
from mistralai import Mistral
from .config import Config

class LLMClient(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        pass

class NebiusClient(LLMClient):
    def __init__(self, model: str):
        api_key = Config.NEBIUS_API_KEY
        if not api_key:
            raise ValueError("Nebius API Key is missing.")
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
        return response.choices[0].message.content

class MistralClient(LLMClient):
    def __init__(self, model: str):
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
        return response.choices[0].message.content

class ClientFactory:
    @staticmethod
    def get_client(agent_config: dict) -> LLMClient:
        provider = agent_config.get("provider")
        model = agent_config.get("model")

        if provider == Config.PROVIDER_NEBIUS:
            return NebiusClient(model=model)
        elif provider == Config.PROVIDER_MISTRAL:
            return MistralClient(model=model)
        else:
            raise ValueError(f"Unsupported provider: {provider}")