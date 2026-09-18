from __future__ import annotations

from dotenv import load_dotenv

from products.knowledge.base import PassengerKnowledgeStore
from products.knowledge.elasticsearch_store import ElasticsearchKnowledgeStore
from products.knowledge.json_store import JsonKnowledgeStore

load_dotenv()


class KnowledgeStoreFactory:
    """Clients request a PassengerKnowledgeStore. They never construct JSON or Elasticsearch products."""

    @classmethod
    def create(cls, kind: str = "auto") -> PassengerKnowledgeStore:
        if kind == "json":
            return JsonKnowledgeStore()
        if kind == "elasticsearch":
            return ElasticsearchKnowledgeStore()
        if kind == "auto":
            try:
                return ElasticsearchKnowledgeStore()
            except Exception:
                return JsonKnowledgeStore()
        raise ValueError(f"Unknown knowledge store: {kind}")
