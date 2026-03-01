import json
from ..llm_client import ClientFactory   # if you still use it directly elsewhere
from ..prompts    import SystemPrompts
from ..languages  import get_language


class FeasibilityAgent:
    def __init__(self, client):
        self.client = client

    def analyze_topic(self, user_topic: str, lang_code: str = "en") -> dict:
        lang_cfg      = get_language(lang_code)
        system_prompt = SystemPrompts.FEASIBILITY_ENHANCER.format(
            lang_instruction=lang_cfg["llm_instruction"]
        )

        response = self.client.generate(
            system_prompt=system_prompt,
            user_prompt=f"User Topic: {user_topic}",
            json_mode=True,
        )

        try:
            data = json.loads(response)

            if "feasible" not in data:
                return {
                    "feasible": False,
                    "reason": "Model error: Missing feasibility flag",
                    "curriculum": None,
                }

            return data

        except json.JSONDecodeError:
            return {
                "feasible": False,
                "reason": "System error: Invalid JSON output",
                "curriculum": None,
            }
