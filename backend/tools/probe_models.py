"""Ask the configured provider which models your key can actually serve.

    cd backend && .venv/bin/python tools/probe_models.py

Model availability on a free tier is per key and changes without notice, and an
unavailable name is indistinguishable from an exhausted quota from the client's
side. This walks the configured chain and reports each name, which is how the
Gemini chain in llm/config.py was chosen.

Costs one small call per model and stops at the daily budget like anything else.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

from factories.llm_factory import LlmFactory

PROMPT = [
    {"role": "system", "content": "Reply with one word."},
    {"role": "user", "content": "Say OK"},
]


def main() -> int:
    client = LlmFactory.create(refresh=True)
    config = client.config
    if not config.enabled:
        print("No provider configured. Set a key in backend/.env first.")
        return 1

    print(f"provider {config.provider}, key {config.key_fingerprint}\n")
    sdk = client._sdk_client()
    available = 0

    for name in config.model_chain:
        try:
            done = sdk.chat.completions.create(
                model=name,
                messages=PROMPT,
                max_tokens=config.max_tokens_respond,
                temperature=0,
                **({"reasoning_effort": config.reasoning_effort} if config.reasoning_effort else {}),
            )
            text = (done.choices[0].message.content or "").strip()
            stop = done.choices[0].finish_reason
            print(f"  ok    {name:28} -> {text[:20]!r} ({done.usage.completion_tokens} tokens, {stop})")
            available += 1
        except Exception as exc:
            # A 429 here means the name is real but out of quota, which is the
            # case the chain exists for. Anything else usually means the name
            # is not served to this key at all.
            print(f"  FAIL  {name:28} -> {type(exc).__name__}: {str(exc)[:80]}")

    print(f"\n{available}/{len(config.model_chain)} models in the chain answered.")
    return 0 if available else 1


if __name__ == "__main__":
    raise SystemExit(main())
