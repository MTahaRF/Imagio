import json
from ..prompts import SystemPrompts
from ..languages import get_language
from ..templates.registry import list_templates


class ScenePlanner:
    def __init__(self, client):
        self.client = client

    def plan_scenes(self, outline: dict, lang_code: str = "en") -> list:
        lang_cfg       = get_language(lang_code)
        system_prompt  = SystemPrompts.PLANNER.format(
            lang_instruction=lang_cfg["llm_instruction"]
        )
        outline_str    = json.dumps(outline, indent=2)
        templates_info = json.dumps(list_templates(), indent=2)

        user_prompt = (
            f"Available Templates:\n{templates_info}\n\n"
            f"Outline:\n{outline_str}\n\n"
            "Create the plan now."
        )
        response = self.client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_mode=True,
        )
        try:
            data   = json.loads(response)
            scenes = data if isinstance(data, list) else data.get("scenes", [])
            for s in scenes:
                if "template" in s and "template_type" not in s:
                    s["template_type"] = s["template"]
            return scenes
        except json.JSONDecodeError:
            print("❌ Planner returned invalid JSON")
            return []
