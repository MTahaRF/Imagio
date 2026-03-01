# check_mistral.py
import os
from dotenv import load_dotenv
from mistralai import Mistral
from pathlib import Path

load_dotenv(Path(".env"))

api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    print("❌ MISTRAL_API_KEY not found in .env")
    exit()

print(f"🔑 Key found: {api_key[:8]}...{api_key[-4:]}")

try:
    client = Mistral(api_key=api_key)
    models = client.models.list()
    
    print(f"\n✅ Key is valid! You have access to {len(models.data)} models:\n")
    for m in sorted(models.data, key=lambda x: x.id):
        print(f"  • {m.id}")

except Exception as e:
    print(f"\n❌ Key is invalid or has no access: {e}")
