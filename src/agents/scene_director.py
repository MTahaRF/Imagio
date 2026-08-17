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
        choreography:    list | None = None,
        preloaded_docs:  str  = "",
        template_hint:   str  = "",
    ) -> dict:
        lang_cfg      = get_language(lang_code)
        system_prompt = SystemPrompts.DIRECTOR.format(
            lang_instruction=lang_cfg["llm_instruction"]
        )
        schema_str = json.dumps(schema, indent=2)

        docs_block = ""
        if preloaded_docs:
            docs_block = (
                "\n--- Relevant Manim API Reference ---\n"
                f"{preloaded_docs}\n"
                "--- End Reference ---\n"
            )

        choreo_block = ""
        if choreography:
            choreo_block = (
                "\nPlanned choreography (in temporal order):\n"
                f"{json.dumps(choreography, indent=2)}\n"
            )

        hint_block = ""
        if template_hint:
            hint_block = (
                f"\n--- Template-Specific Instructions ({template_name}) ---\n"
                f"{template_hint}\n"
                "--- End Template Instructions ---\n"
            )

        user_prompt = (
            f"Template: {template_name}\n"
            f"Scene Concept: {concept}\n"
            + choreo_block
            + docs_block
            + hint_block
        )
        if previous_script:
            user_prompt += f"Previous scene narration (for continuity):\n{previous_script}\n"
        user_prompt += (
            f"\nFill this schema completely — all narration fields included:\n"
            f"{schema_str}\n\n"
            "Return JSON with exactly two keys: 'script' and 'template_data'."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ]

        response = self.client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_mode=True,
        )

        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            return {"script": concept, "template_data": {}}

        data.setdefault("template_data", {})
        data.setdefault("script", concept)
        return data
