import os
import json
from ..prompts import SystemPrompts
from ..languages import get_language


class SceneDirector:
    def __init__(self, client, docs_tool=None):
        self.client = client
        
        # Load cheat sheet once
        cheat_sheet_path = os.path.join("source", "cheat_sheet.txt")
        if os.path.exists(cheat_sheet_path):
            with open(cheat_sheet_path, "r", encoding="utf-8") as f:
                self.cheat_sheet = f.read()
        else:
            self.cheat_sheet = "Cheat sheet not found."

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
        system_prompt += "\n\n=== MANIM CHEAT SHEET ===\n" + self.cheat_sheet
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
            "Return JSON with exactly two keys: 'script' and 'template_data'.\n"
            "You may use the `read_manim_doc` tool to fetch exact documentation for any classes you find in the cheat sheet before you return the final JSON."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "read_manim_doc",
                    "description": "Read the full documentation and code examples for a specific Manim class.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "class_name": {
                                "type": "string",
                                "description": "The fully qualified class name (e.g. 'manim.mobject.graphing.coordinate_systems.Axes')"
                            }
                        },
                        "required": ["class_name"]
                    }
                }
            }
        ]

        for step in range(7):
            # Force at least one tool call on the first iteration
            tool_choice = "required" if step == 0 else "auto"
            message = self.client.chat(messages, json_mode=False, tools=tools, tool_choice=tool_choice)
            
            if hasattr(message, "tool_calls") and message.tool_calls:
                # Add assistant message to history (only the fields providers expect)
                messages.append({
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [
                        tc.model_dump() if hasattr(tc, "model_dump") else tc
                        for tc in message.tool_calls
                    ]
                })
                
                for tool_call in message.tool_calls:
                    if tool_call.function.name == "read_manim_doc":
                        try:
                            args = json.loads(tool_call.function.arguments)
                            class_name = args.get("class_name")
                            print(f"    🔧 read_manim_doc({class_name})")
                            doc_path = os.path.join("source", "classes", f"{class_name}.txt")
                            if os.path.exists(doc_path):
                                with open(doc_path, "r", encoding="utf-8") as f:
                                    doc_content = f.read()
                            else:
                                doc_content = f"Documentation not found for {class_name}."
                        except Exception as e:
                            doc_content = f"Error reading docs: {e}"
                            
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call.function.name,
                            "content": doc_content
                        })
            else:
                content = message.content or ""
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                try:
                    data = json.loads(content)
                    data.setdefault("template_data", {})
                    data.setdefault("script", concept)
                    return data
                except json.JSONDecodeError:
                    messages.append({"role": "assistant", "content": message.content})
                    messages.append({"role": "user", "content": "Please return the final output strictly as a valid JSON object."})
                    
        return {"script": concept, "template_data": {}}

