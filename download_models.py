"""
download_models.py
Run once to download all Piper voice models used by Imagio:

    python download_models.py
    python download_models.py --lang hi      # single language

Models go into Config.PIPER_MODELS_DIR.
"""

import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.languages import LANGUAGES
from src.config    import Config


def download(lang_code: str, cfg: dict):
    model = cfg["piper_model"]
    dest  = os.path.join(Config.PIPER_MODELS_DIR, f"{model}.onnx")

    if os.path.exists(dest):
        print(f"  ✅ {model} already downloaded")
        return

    print(f"  ⬇️  Downloading {model} ({cfg['name']})...")
    os.makedirs(Config.PIPER_MODELS_DIR, exist_ok=True)

    # NOTE: piper.download_voices uses --download-dir (not --output-dir)
    cmd = [
        sys.executable,
        "-m",
        "piper.download_voices",
        model,
        "--download-dir",
        Config.PIPER_MODELS_DIR,
    ]
    subprocess.run(cmd, check=True)
    print(f"  ✅ {model} saved to {Config.PIPER_MODELS_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", default=None, choices=list(LANGUAGES))
    args = parser.parse_args()

    targets = {args.lang: LANGUAGES[args.lang]} if args.lang else LANGUAGES
    for code, cfg in targets.items():
        download(code, cfg)
