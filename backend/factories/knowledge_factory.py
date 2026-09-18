from __future__ import annotations

from dotenv import load_dotenv

from products.knowledge.base import PassengerKnowledgeStore
from products.knowledge.elasticsearch_store import ElasticsearchKnowledgeStore
from products.knowledge.json_store import JsonKnowledgeStore
from products.knowledge.postgres_store import PostgresKnowledgeStore

load_dotenv()


class KnowledgeStoreFactory:
    """Clients request a PassengerKnowledgeStore. They never construct JSON, Postgres, or Elasticsearch products."""

    @classmethod
    def create(cls, kind: str = "auto") -> PassengerKnowledgeStore:
        if kind == "json":
            return JsonKnowledgeStore()
        if kind == "postgres":
            return PostgresKnowledgeStore()
        if kind == "elasticsearch":
            return ElasticsearchKnowledgeStore()
        if kind == "auto":
            from persistence.postgres import database_url

            if database_url():
                try:
                    return PostgresKnowledgeStore()
                except Exception:
                    pass
            try:
                return ElasticsearchKnowledgeStore()
            except Exception:
                return JsonKnowledgeStore()
        raise ValueError(f"Unknown knowledge store: {kind}")
