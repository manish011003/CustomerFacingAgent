from __future__ import annotations

from models.schemas import TurnHit
from products.knowledge.base import PassengerKnowledgeStore


def _cosine(query, document) -> float:
    """In-memory cosine similarity. Numpy only — not the lexical `score()` path."""
    import numpy as np

    left = np.asarray(query, dtype=np.float64)
    right = np.asarray(document, dtype=np.float64)
    if left.size == 0 or right.size == 0 or left.size != right.size:
        return 0.0
    denom = float(np.linalg.norm(left) * np.linalg.norm(right))
    if denom == 0.0:
        return 0.0
    return float(np.dot(left, right) / denom)


class JsonKnowledgeStore(PassengerKnowledgeStore):
    """Concrete product: in-memory passenger KB seeded from the assignment JSON pack."""

    def _init_backend(self) -> None:
        self.backend = "json"

    def semantic_search(self, text: str, k: int, min_score: float) -> list[TurnHit]:
        """Rank approved prior resolutions by numpy cosine similarity."""
        embedder = self._embedding_client()
        query = embedder.embed(text) if embedder.enabled else None
        if not query:
            return []
        hits: list[TurnHit] = []
        for row in self.kb_entries.values():
            if row.get("status") != "approved":
                continue
            vector = row.get("embedding")
            if vector is None:
                vector = embedder.embed(row.get("message") or "")
                if vector is not None:
                    row["embedding"] = vector
            if not vector:
                continue
            similarity = _cosine(query, vector)
            if similarity < min_score:
                continue
            phrasing = row.get("phrasing") or row.get("reply") or ""
            hits.append(
                TurnHit(
                    id=row.get("id") or "",
                    ts=row.get("ts") or "",
                    message=row.get("message") or "",
                    reply=phrasing,
                    score=round(similarity, 4),
                )
            )
        hits.sort(key=lambda hit: (-hit.score, hit.ts))
        return hits[:k]
