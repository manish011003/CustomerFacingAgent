import os

from dotenv import load_dotenv

load_dotenv("../.env.local")
key = (os.getenv("GEMINI_API_KEY") or "").strip()
print("key loaded:", bool(key))

from openai import OpenAI  # noqa: E402

from llm.config import MODEL_CHAINS  # noqa: E402

client = OpenAI(
    api_key=key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=30,
)
live = {m.id.replace("models/", "") for m in client.models.list()}
print(f"\n{len(live)} models visible to this key\n")
print("chain entries:")
for name in MODEL_CHAINS["gemini"]:
    print(f"  {'OK   ' if name in live else 'MISS '} {name}")
print("\nall gemini names live:")
for name in sorted(n for n in live if n.startswith("gemini")):
    print("  ", name)
