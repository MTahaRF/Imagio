import json
from ..llm_client import ClientFactory
from ..prompts import SystemPrompts
from ..templates.registry import list_templates # Import the list function

class ScenePlanner:
    def __init__(self, client):
        self.client = client

    def plan_scenes(self, outline: dict) -> list:
        outline_str = json.dumps(outline, indent=2)
        
        # 1. Get available templates dynamically from the registry
        templates_info = json.dumps(list_templates(), indent=2)
        
        # 2. Define the strict format we need
        format_instructions = (
            "Return a JSON object with a 'scenes' key containing a list of objects(generate 10 scenes).\n"
            "Each object MUST have these exact keys:\n"
            "- 'concept': A clear description of what happens in the scene.\n"
            "- 'template_type': The name of the template to use.\n"
        )

        user_prompt = (
            f"Available Templates:\n{templates_info}\n\n"
            f"Outline:\n{outline_str}\n\n"
            f"{format_instructions}\n"
            "Create the plan now."
        )
        
        response = self.client.generate(
            system_prompt=SystemPrompts.PLANNER,
            user_prompt=user_prompt,
            json_mode=True
        )
        
        try:
            data = json.loads(response)
            # Standardize output to always be a list
            if isinstance(data, list):
                scenes = data
            else:
                scenes = data.get("scenes", [])
            
            # Final safety check: ensure the pipeline finds 'template_type'
            for s in scenes:
                if "template" in s and "template_type" not in s:
                    s["template_type"] = s["template"]
            return scenes

        except json.JSONDecodeError:
            print("❌ Error: Planner returned invalid JSON")
            return []