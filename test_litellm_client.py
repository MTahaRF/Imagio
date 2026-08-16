"""
test_litellm_client.py
======================
Test script for LiteLLMClient / ClientFactory integration.
"""

import os
import json
from src.config import Config
from src.llm_client import ClientFactory, LiteLLMClient

# ==============================================================================
# CONFIGURATION - Set your provider, model, and API key here
# ==============================================================================
# Examples:
#   Provider: "litellm-ollama",  Model: "ollama/llama3.2" (or "ollama/llama3")
#   Provider: "litellm-openai",  Model: "gpt-4o"
#   Provider: "litellm-gemini",  Model: "gemini/gemini-2.5-flash"
#   Provider: "litellm-groq",    Model: "groq/llama-3.3-70b-versatile"

PROVIDER = "litellm-gemini"
MODEL = "gemini/gemini-3-flash-preview"

# Paste your API key below or set LITELLM_KEY in your .env / environment
API_KEY = os.getenv("LITELLM_KEY", "")

# If your Ollama server runs on a custom host/port, set it here (default is http://localhost:11434)
# os.environ["OLLAMA_API_BASE"] = "http://localhost:11434"

# ==============================================================================


def run_test():
    # Set single LiteLLM key in Config if provided
    if API_KEY:
        Config.LITELLM_KEY = API_KEY
        os.environ["LITELLM_KEY"] = API_KEY

    print(f"🔧 Testing LiteLLMClient with Provider: {PROVIDER!r} | Model: {MODEL!r}")
    print("-" * 60)

    # 1. Instantiate via ClientFactory
    client = ClientFactory.get_client({
        "provider": PROVIDER,
        "model": MODEL
    })

    print(f"✅ Created client instance: {type(client).__name__} (target model: {client.model})")

    # 2. Test Standard Text Generation
    print("\n📝 1. Testing standard text generation...")
    system_prompt = "You are a concise educational tutor."
    user_prompt = "Explain in one sentence why the sky is blue."

    try:
        response_text = client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_mode=False
        )
        print("📥 Text Response:")
        print(response_text)
    except Exception as e:
        print(f"❌ Text generation failed: {e}")

    # 3. Test JSON Mode Generation
    print("\n📦 2. Testing JSON mode generation...")
    json_system_prompt = "You are a helpful assistant designed to output valid JSON only."
    json_user_prompt = (
        "Provide 2 educational concepts in science with a short description. "
        "Format as JSON with a 'concepts' list containing 'title' and 'description' keys."
    )

    try:
        response_json_str = client.generate(
            system_prompt=json_system_prompt,
            user_prompt=json_user_prompt,
            json_mode=True
        )
        print("📥 Raw JSON Response:")
        print(response_json_str)

        # Validate JSON parse
        parsed = json.loads(response_json_str)
        print("\n✅ Successfully parsed response as valid JSON:")
        print(json.dumps(parsed, indent=2))
    except Exception as e:
        print(f"❌ JSON generation/parsing failed: {e}")

    print("\n" + "=" * 60)
    print("Test run completed.")


if __name__ == "__main__":
    run_test()
