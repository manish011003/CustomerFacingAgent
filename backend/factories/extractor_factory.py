from __future__ import annotations

from factories.llm_factory import LlmFactory
from products.extractors.base import IntentExtractor
from products.extractors.heuristic import HeuristicExtractor
from products.extractors.llm import LlmExtractor


class ExtractorFactory:
    """Clients request an IntentExtractor. They never construct concrete extractors."""

    @classmethod
    def create(cls, kind: str = "auto") -> IntentExtractor:
        from kb.store import store

        heuristic = HeuristicExtractor(directory=store.identity_directory())
        if kind == "heuristic":
            return heuristic
        if kind == "llm":
            return LlmExtractor(fallback=heuristic, client=LlmFactory.create())
        if kind == "auto":
            client = LlmFactory.create()
            return LlmExtractor(fallback=heuristic, client=client) if client.enabled else heuristic
        raise ValueError(f"Unknown extractor: {kind}")
