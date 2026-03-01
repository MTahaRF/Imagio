# src/agents/feasibility.py
import json
from ..llm_client import ClientFactory
from ..prompts import SystemPrompts

class FeasibilityAgent:
    def __init__(self, client):
        self.client = client

    def analyze_topic(self, user_topic: str) -> dict:
        """
        Single-shot analysis.
        Returns a dict containing both feasibility status and the curriculum (if valid).
        
        Structure:
        {
            "feasible": bool,
            "reason": str,
            "curriculum": dict | None
        }
        """
        response = self.client.generate(
            system_prompt=SystemPrompts.FEASIBILITY_ENHANCER,
            user_prompt=f"User Topic: {user_topic}",
            json_mode=True
        )

        try:
            data = json.loads(response)
            
            # Sanity check: Ensure keys exist
            if "feasible" not in data:
                # Fallback if LLM creates a weird structure
                return {
                    "feasible": False, 
                    "reason": "Model error: Missing feasibility flag", 
                    "curriculum": None
                }
            
            return data

        except json.JSONDecodeError:
            return {
                "feasible": False, 
                "reason": "System error: Invalid JSON output", 
                "curriculum": None
            }