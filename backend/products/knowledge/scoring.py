from __future__ import annotations

import math
import re

TOKEN = re.compile(r"[a-z0-9]+")

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "to", "of", "for", "and", "or", "in", "on", "at", "by", "with", "from",
    "my", "me", "i", "you", "your", "we", "us", "they", "them", "it", "its",
    "this", "that", "these", "those", "there", "here", "as", "if", "but",
    "so", "than", "then", "will", "would", "can", "could", "do", "does",
    "did", "have", "has", "had", "not", "no", "am", "any", "all", "out",
}


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN.findall((text or "").lower()) if len(t) > 1 and t not in STOPWORDS]


def score(query: str, *fields: str) -> float:
    """Length-normalized term overlap.

    Dependency-free on purpose: the JSON backend has to rank without Docker so the
    demo never depends on Elasticsearch being up. Ranking is not BM25-identical to
    the Elasticsearch backend, which is why the planner narrows candidates by rule
    scope before either backend ranks them.
    """
    q = set(tokenize(query))
    if not q:
        return 0.0
    doc = set(tokenize(" ".join(f for f in fields if f)))
    if not doc:
        return 0.0
    hits = len(q & doc)
    if not hits:
        return 0.0
    return round(hits / math.sqrt(len(doc)), 4)
