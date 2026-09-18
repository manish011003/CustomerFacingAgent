from __future__ import annotations

import json

from llm.client import LlmClient
from models.schemas import Extraction, SessionMemory
from products.extractors.base import IntentExtractor

SYSTEM = (
    "Return JSON with keys emotion, legal_or_formal, requests, mentioned_name, "
    "mentioned_pnr. No eligibility fields."
)


class LlmExtractor(IntentExtractor):
    """Optional NLU. Both the fallback extractor and the client are injected."""

    def __init__(self, fallback: IntentExtractor, client: LlmClient | None = None):
        self._fallback = fallback
        self._client = client

    def _llm(self) -> LlmClient:
        if self._client is None:
            from factories.llm_factory import LlmFactory

            self._client = LlmFactory.create()
        return self._client

    def extract(self, message: str, session: SessionMemory | None = None) -> Extraction:
        client = self._llm()
        if not client.enabled:
            return self._fallback.extract(message, session)

        from agent.context import render_extract_prompt

        memory = session or SessionMemory(session_id="anon")
        result = client.complete(
            purpose="extract",
            system=SYSTEM,
            user=render_extract_prompt(message, memory),
            session_id=memory.session_id,
            json_mode=True,
            # Identical utterances are common in a demo and the extraction is
            # deterministic at temperature 0, so a repeat costs nothing.
            cache=True,
        )
        if result is None:
            return self._fallback.extract(message, session)
        try:
            data = json.loads(result.text or "{}")
            return Extraction.model_validate({**data, "raw_text": message})
        except Exception:
            return self._fallback.extract(message, session)
