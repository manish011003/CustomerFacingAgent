import os

from dotenv import load_dotenv

load_dotenv("../.env.local")
key = (os.getenv("GEMINI_API_KEY") or "").strip()

from openai import OpenAI  # noqa: E402

client = OpenAI(
    api_key=key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=30,
)

CANDIDATES = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-pro-latest",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
    "gemini-3-flash-preview",
    "gemini-3.1-pro-preview",
]

for name in CANDIDATES:
    try:
        done = client.chat.completions.create(
            model=name,
            messages=[
                {"role": "system", "content": "Reply with one word."},
                {"role": "user", "content": "Say OK"},
            ],
            max_tokens=200,
            temperature=0,
        )
        text = (done.choices[0].message.content or "").strip()
        print(f"  OK   {name:26} -> {text[:20]!r}  ({done.usage.total_tokens} tokens)")
    except Exception as exc:
        print(f"  FAIL {name:26} -> {type(exc).__name__}: {str(exc)[:90]}")
