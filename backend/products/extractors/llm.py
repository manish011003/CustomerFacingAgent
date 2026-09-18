from models.schemas import Extraction, SessionMemory
from products.extractors.base import IntentExtractor


class LlmExtractor(IntentExtractor):
    """Optional NLU. Fallback extractor is injected by the factory."""

    def __init__(self, fallback: IntentExtractor):
        self._fallback = fallback

    def extract(self, message: str, session: SessionMemory | None = None) -> Extraction:
        import json
        import os

        if not os.getenv("OPENAI_API_KEY"):
            return self._fallback.extract(message, session)
        try:
            from openai import OpenAI
            from agent.context import render_extract_prompt

            client = OpenAI()
            memory = session or SessionMemory(session_id="anon")
            completion = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {
                        "role": "system",
                        "content": "Return JSON with keys emotion, legal_or_formal, requests, mentioned_name, mentioned_pnr. No eligibility fields.",
                    },
                    {"role": "user", "content": render_extract_prompt(message, memory)},
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )
            data = json.loads(completion.choices[0].message.content or "{}")
            return Extraction.model_validate({**data, "raw_text": message})
        except Exception:
            return self._fallback.extract(message, session)
