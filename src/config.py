import os
from dotenv import load_dotenv
from pathlib import Path
from src.languages import LANGUAGES, DEFAULT_LANG

env_path = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    PROVIDER_NEBIUS  = "nebius"
    PROVIDER_MISTRAL = "mistral"
    PROVIDER_PREFIX_LITELLM = "litellm"

    NEBIUS_API_KEY  = os.getenv("NEBIUS_API_KEY")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    LITELLM_KEY     = os.getenv("LITELLM_KEY") or os.getenv("LITELLM_API_KEY")

    DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", PROVIDER_NEBIUS)
    DEFAULT_MODEL    = os.getenv("DEFAULT_MODEL", "openai/gpt-oss-120b")

    # Scripter + Coder merged into SceneDirector
    FEASIBILITY_CONFIG = {"provider": DEFAULT_PROVIDER, "model": DEFAULT_MODEL}
    PLANNER_CONFIG     = {"provider": DEFAULT_PROVIDER, "model": DEFAULT_MODEL}
    DIRECTOR_CONFIG    = {"provider": DEFAULT_PROVIDER, "model": DEFAULT_MODEL}

    BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUT_DIR = os.path.join(BASE_DIR, "workspace")
    
        # ── Language ───────────────────────────────────────────────────
    SUPPORTED_LANGUAGES = LANGUAGES
    DEFAULT_LANGUAGE    = DEFAULT_LANG

    # ── Piper model dir (where .onnx files live) ───────────────────
    PIPER_MODELS_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "voices"
    )
