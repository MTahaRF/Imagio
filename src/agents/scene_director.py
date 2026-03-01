import json
from ..prompts import SystemPrompts
from ..languages import get_language


class SceneDirector:
    def __init__(self, client):
        self.client = client

    def direct_scene(
        self,
        template_name:   str,
        schema:          dict,
        concept:         str,
        previous_script: str = "",
        lang_code:       str = "en",
    ) -> dict:
        lang_cfg      = get_language(lang_code)
        system_prompt = SystemPrompts.DIRECTOR.format(
            lang_instruction=lang_cfg["llm_instruction"]
        )
        schema_str  = json.dumps(schema, indent=2)
        user_prompt = (
            f"Template: {template_name}\n"
            f"Scene Concept: {concept}\n"
        )
        if previous_script:
            user_prompt += f"Previous scene narration (for continuity):\n{previous_script}\n"
        user_prompt += (
            f"\nFill this schema completely — all narration fields included:\n"
            f"{schema_str}\n\n"
            "Return JSON with exactly two keys: 'script' and 'template_data'."
        )

        response = self.client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_mode=True,
        )
        try:
            data = json.loads(response)
            data.setdefault("template_data", {})
            data.setdefault("script", concept)
            return data
        except json.JSONDecodeError:
            print(f"  ⚠️  SceneDirector returned invalid JSON for '{concept}'")
            return {"script": concept, "template_data": {}}
