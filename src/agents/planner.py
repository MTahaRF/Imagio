import json
import os
from ..prompts import SystemPrompts
from ..languages import get_language
from ..templates.registry import list_templates


class ScenePlanner:
    def __init__(self, client):
        self.client = client

        # Load cheat sheet once so the Planner knows the real class namespace.
        cheat_sheet_path = os.path.join("source", "cheat_sheet.txt")
        if os.path.exists(cheat_sheet_path):
            with open(cheat_sheet_path, "r", encoding="utf-8") as f:
                self.cheat_sheet = f.read()
        else:
            self.cheat_sheet = "Cheat sheet not found."

    def plan_scenes(self, outline: dict, lang_code: str = "en") -> list:
        lang_cfg       = get_language(lang_code)
        system_prompt  = SystemPrompts.PLANNER.format(
            lang_instruction=lang_cfg["llm_instruction"]
        )
        system_prompt += "\n\n=== MANIM CHEAT SHEET ===\n" + self.cheat_sheet
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
                self._sanitize_scene(s)
            return scenes
        except json.JSONDecodeError:
            print("❌ Planner returned invalid JSON")
            return []

    @staticmethod
    def _sanitize_scene(s: dict) -> None:
        """Filter out malformed entries instead of crashing on bad plans."""
        if "relevant_classes" in s:
            if not isinstance(s["relevant_classes"], list):
                s.pop("relevant_classes", None)
            else:
                s["relevant_classes"] = [
                    c for c in s["relevant_classes"] if isinstance(c, str)
                ]
                if not s["relevant_classes"]:
                    s.pop("relevant_classes", None)
        if "choreography" in s:
            if not isinstance(s["choreography"], list):
                s.pop("choreography", None)
            else:
                s["choreography"] = [
                    b for b in s["choreography"] if isinstance(b, dict)
                ]
                if not s["choreography"]:
                    s.pop("choreography", None)
