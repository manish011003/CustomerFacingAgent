from __future__ import annotations

import os
from typing import Any

from models.schemas import RuleHit, StyleHit, TurnHit
from products.knowledge.base import PassengerKnowledgeStore


class ElasticsearchKnowledgeStore(PassengerKnowledgeStore):
    """Concrete product: Elasticsearch dual-write plus query-backed retrieval.

    Every search falls back to the in-memory implementation in the base class when
    Elasticsearch errors or returns nothing, so a flaky cluster degrades the ranking
    quality of a turn but never the turn itself.
    """

    def __init__(self) -> None:
        self._es: Any = None
        super().__init__()

    def _init_backend(self) -> None:
        from elasticsearch import Elasticsearch

        url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
        client = Elasticsearch(url, request_timeout=2)
        if not client.ping():
            raise ConnectionError(f"Elasticsearch not reachable at {url}")
        self._es = client
        self.backend = "elasticsearch"
        self._ensure_indices()

    def _ensure_indices(self) -> None:
        mappings = {
            "passengers": {"mappings": {"properties": {"name": {"type": "text"}, "pnr": {"type": "keyword"}, "id": {"type": "keyword"}}}},
            "bookings": {"mappings": {"properties": {"pnr": {"type": "keyword"}, "customer_id": {"type": "keyword"}}}},
            "events": {"mappings": {"properties": {"session_id": {"type": "keyword"}, "customer_id": {"type": "keyword"}, "ts": {"type": "date"}, "kind": {"type": "keyword"}, "message": {"type": "text"}, "reply": {"type": "text"}}}},
            "cases": {"mappings": {"properties": {"id": {"type": "keyword"}, "status": {"type": "keyword"}}}},
            "graph_edges": {"mappings": {"properties": {"from_id": {"type": "keyword"}, "to_id": {"type": "keyword"}, "rel": {"type": "keyword"}}}},
            "policy_rules": {"mappings": {"properties": {"clause_id": {"type": "keyword"}, "rule_id": {"type": "keyword"}, "kind": {"type": "keyword"}, "title": {"type": "text"}, "text": {"type": "text"}}}},
            "style_samples": {"mappings": {"properties": {"id": {"type": "keyword"}, "customer": {"type": "text"}, "agent": {"type": "text"}}}},
            "memories": {"mappings": {"properties": {"customer_id": {"type": "keyword"}, "fact": {"type": "text"}, "ts": {"type": "date"}}}},
        }
        for name, body in mappings.items():
            if not self._es.indices.exists(index=name):
                self._es.indices.create(index=name, mappings=body["mappings"])

    def _persist(self, index: str, doc_id: str, document: dict[str, Any]) -> None:
        try:
            self._es.index(index=index, id=doc_id, document=document)
        except Exception:
            pass

    def seed(self) -> None:
        super().seed()
        try:
            self._es.indices.refresh(index="policy_rules,style_samples")
        except Exception:
            pass

    def search_policy(
        self,
        query: str,
        *,
        scope: list[str] | None = None,
        kinds: tuple[str, ...] = ("rule",),
        k: int = 2,
        max_chars: int = 400,
    ) -> list[RuleHit]:
        try:
            filters: list[dict[str, Any]] = [{"terms": {"kind": list(kinds)}}]
            if scope:
                filters.append({"terms": {"rule_id": list(scope)}})
            response = self._es.search(
                index="policy_rules",
                size=k,
                query={
                    "bool": {
                        "filter": filters,
                        "should": [{"multi_match": {"query": query, "fields": ["text^2", "title"]}}],
                    }
                },
            )
            hits: list[RuleHit] = []
            for row in response["hits"]["hits"]:
                source = row["_source"]
                text = source.get("text", "")
                if len(text) > max_chars:
                    text = text[: max_chars - 3].rstrip() + "..."
                hits.append(
                    RuleHit(
                        clause_id=source["clause_id"],
                        rule_id=source["rule_id"],
                        title=source["title"],
                        text=text,
                        kind=source.get("kind", "rule"),
                        score=round(float(row.get("_score") or 0.0), 4),
                    )
                )
            if hits:
                return hits
        except Exception:
            pass
        return super().search_policy(query, scope=scope, kinds=kinds, k=k, max_chars=max_chars)

    def recall_turns(self, customer_id: str, query: str, *, k: int = 3) -> list[TurnHit]:
        try:
            response = self._es.search(
                index="events",
                size=k,
                query={
                    "bool": {
                        # The customer_id filter is the isolation guarantee: a recall
                        # for one passenger cannot surface another passenger's turn.
                        "filter": [
                            {"term": {"customer_id": customer_id}},
                            {"match": {"kind": "turn"}},
                        ],
                        "must": [{"multi_match": {"query": query, "fields": ["message^2", "reply"]}}],
                    }
                },
            )
            hits = [
                TurnHit(
                    ts=row["_source"].get("ts", ""),
                    message=row["_source"].get("message") or "",
                    reply=row["_source"].get("reply") or "",
                    score=round(float(row.get("_score") or 0.0), 4),
                )
                for row in response["hits"]["hits"]
            ]
            if hits:
                return hits
        except Exception:
            pass
        return super().recall_turns(customer_id, query, k=k)

    def search_style(self, query: str, *, k: int = 1) -> list[StyleHit]:
        try:
            response = self._es.search(
                index="style_samples",
                size=k,
                query={"multi_match": {"query": query, "fields": ["customer"]}},
            )
            hits = [
                StyleHit(
                    id=row["_source"]["id"],
                    customer=row["_source"]["customer"],
                    agent=row["_source"]["agent"],
                    score=round(float(row.get("_score") or 0.0), 4),
                )
                for row in response["hits"]["hits"]
            ]
            if hits:
                return hits
        except Exception:
            pass
        return super().search_style(query, k=k)
