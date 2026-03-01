# src/agents/scene_director.py
import json
from ..prompts import SystemPrompts


class SceneDirector:
    def __init__(self, client):
        self.client = client

    def direct_scene(
        self,
        template_name: str,
        schema: dict,
        concept: str,
        previous_script: str = "",
    ) -> dict:
        """
        Returns:
            {
                "script":        str,   # full scene narration (for context continuity)
                "template_data": dict,  # filled schema with narrations baked in
            }
        """
        schema_str = json.dumps(schema, indent=2)

        user_prompt = (
            f"Template: {template_name}\n"
            f"Scene Concept: {concept}\n"
        )
        if previous_script:
            user_prompt += f"Previous scene narration (for continuity): {previous_script}\n"

        user_prompt += (
            f"\nFill this JSON schema completely, including all narration fields:\n"
            f"{schema_str}\n\n"
            f"Return a JSON object with exactly two keys:\n"
            f"  'script': a single flowing narration paragraph for this scene (30-45 seconds when spoken)\n"
            f"  'template_data': the fully filled schema above\n"
        )

        response = self.client.generate(
            system_prompt=SystemPrompts.DIRECTOR,
            user_prompt=user_prompt,
            json_mode=True,
        )

        try:
            data = json.loads(response)
            # Ensure both keys exist
            if "template_data" not in data:
                data["template_data"] = {}
            if "script" not in data:
                data["script"] = concept
            return data
        except json.JSONDecodeError:
            print(f"  ⚠️  SceneDirector returned invalid JSON for '{concept}'")
            return {"script": concept, "template_data": {}}
