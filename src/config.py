import os
from dotenv import load_dotenv
from pathlib import Path
from src.languages import LANGUAGES, DEFAULT_LANG

env_path = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    PROVIDER_NEBIUS  = "nebius"
    PROVIDER_MISTRAL = "mistral"

    # Scripter + Coder merged into SceneDirector
    FEASIBILITY_CONFIG = {"provider": PROVIDER_NEBIUS, "model": "openai/gpt-oss-120b"}
    PLANNER_CONFIG     = {"provider": PROVIDER_NEBIUS, "model": "openai/gpt-oss-120b"}
    DIRECTOR_CONFIG    = {"provider": PROVIDER_NEBIUS, "model": "openai/gpt-oss-120b"}

    NEBIUS_API_KEY  = os.getenv("NEBIUS_API_KEY")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

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

if not Config.NEBIUS_API_KEY:
    print("❌ ERROR: NEBIUS_API_KEY missing from .env!")
