"""Reuse a prior resolution's phrasing, or queue the turn for ops approval.

Runs after frustration classification. Policy, amounts, and escalation are
untouched: a close match is tone only, and a miss is a pending row, not a
write into the searchable KB.
"""

from __future__ import annotations

import os

from agent.retrieve import strip_style_identifiers
from factories.embedding_factory import EmbeddingFactory
from kb.store import store
from models.schemas import FrustrationAssessment, KbMatch, SessionMemory

KB_MATCH_THRESHOLD = float(os.getenv("KB_MATCH_THRESHOLD", "0.82"))


def ground_prior_resolution(
    message: str,
    *,
    session: SessionMemory,
    customer_id: str | None = None,
    assessment: FrustrationAssessment | None = None,
) -> KbMatch:
    """Embed this turn, reuse a close prior phrasing, or queue a pending row."""
    if session.last_kb_match is not None:
        return session.last_kb_match

    threshold = KB_MATCH_THRESHOLD
    embedder = store._embedding_client() if hasattr(store, "_embedding_client") else EmbeddingFactory.create()
    query = embedder.embed(message) if getattr(embedder, "enabled", True) else None
    hits = store.semantic_search(message, k=1, min_score=threshold) if query else []
    top = hits[0] if hits else None
    if top is not None and top.score >= threshold:
        match = KbMatch(
            matched=True,
            score=top.score,
            threshold=threshold,
            phrasing=strip_style_identifiers(top.reply),
            entry_id=top.id or None,
        )
        session.last_kb_match = match
        return match

    pending = store.queue_pending_kb_entry(
        {
            "message": message,
            "customer_id": customer_id,
            "session_id": session.session_id,
            "frustration_category": None if not assessment else assessment.category.value,
        }
    )
    match = KbMatch(
        matched=False,
        score=0.0 if top is None else top.score,
        threshold=threshold,
        pending_id=pending["id"],
    )
    session.last_kb_match = match
    return match
