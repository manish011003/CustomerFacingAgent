from __future__ import annotations

import json

from llm.client import LlmClient
from models.schemas import Extraction, RequestType, SessionMemory
from products.extractors.base import IntentExtractor

SYSTEM = (
    "Return JSON with keys emotion, legal_or_formal, requests, mentioned_name, "
    "mentioned_pnr. No eligibility fields."
)


def needs_model(extraction: Extraction) -> bool:
    """True only when the regex extractor understood nothing.

    Measured on a live Gemini key: the heuristic reads "full night hotel plus a
    higher-fare flight, ₹2000" correctly in 4ms, while the extract call takes
    2-5 seconds. Paying that on a turn the regex already got right doubles the
    wait for no gain in the answer, so the model is reserved for the turns the
    deterministic path genuinely cannot read.

    GENERAL_HELP is the extractor's way of saying no pattern matched, so it is
    the one signal that a model might add something.
    """
    return [request.type for request in extraction.requests] == [RequestType.GENERAL_HELP]


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
        # The regex runs first and for free. It is the answer on most turns and
        # the fallback on the rest, so it is never wasted work.
        baseline = self._fallback.extract(message, session)
        client = self._llm()
        if not client.enabled or not needs_model(baseline):
            return baseline

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
            return baseline
        try:
            data = json.loads(result.text or "{}")
            return Extraction.model_validate({**data, "raw_text": message})
        except Exception:
            return baseline
