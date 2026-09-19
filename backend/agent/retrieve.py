from __future__ import annotations

import re

from models.schemas import Customer, PolicyEvaluation, Retrieval, RetrievalPlan

# Style samples (and reused KB phrasing) are tone only. Amounts, PNRs, and
# flight numbers belong to some other passenger's story and must not reach
# the packet as if they were this turn's entitlements.
_AMOUNT = re.compile(
    r"₹\s*[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?|"
    r"(?:rs\.?|inr)\s*[0-9]{1,3}(?:,[0-9]{3})*|"
    r"[0-9]{1,3}(?:,[0-9]{3})+\s*(?:inr|rupees?|rs\.?)|"
    r"\b[0-9]{3,}\s*(?:inr|rupees?)\b",
    re.I,
)
_PNR_LABEL = re.compile(r"\bPNR\s+[A-Z0-9]{5,8}\b", re.I)
_PNR = re.compile(r"\b[A-Z]{2,3}\d{3,5}[A-Z]\b|\b[A-Z]{2}\d{4,5}\b")
_FLIGHT = re.compile(r"\b(?:flight\s+)?[A-Z]{2,3}-\d{2,4}\b", re.I)


def strip_style_identifiers(text: str) -> str:
    """Remove amounts, PNRs, and flight numbers from a tone sample."""
    cleaned = _AMOUNT.sub("[amount]", text or "")
    cleaned = _PNR_LABEL.sub("[PNR]", cleaned)
    cleaned = _PNR.sub("[PNR]", cleaned)
    cleaned = _FLIGHT.sub("[flight]", cleaned)
    return re.sub(r"\s{2,}", " ", cleaned).strip()


def run(
    *,
    plan: RetrievalPlan,
    customer: Customer,
    evaluation: PolicyEvaluation | None,
    kb=None,
) -> Retrieval:
    """Execute a retrieval plan. Facade — always goes through the knowledge store."""
    from kb.store import store as process_store

    store = kb or process_store
    retrieval = Retrieval(backend=store.backend)
    allowed = set(plan.rule_scope)
    kinds = tuple(plan.doc_kinds) or ("rule",)

    if evaluation and plan.need_policy:
        cited: set[tuple[str, str]] = set()
        for decision in evaluation.decisions:
            # A decision may only cite a rule that this turn's plan allows, so the
            # search runs over the intersection rather than dropping hits afterwards.
            scope = [r for r in store.rule_ids_for_source(decision.source) if r in allowed]
            if not scope:
                continue
            hits = store.search_policy(
                f"{decision.reason} {decision.scope or ''}",
                scope=scope,
                kinds=kinds,
                k=1,
                max_chars=plan.max_chars,
            )
            if not hits:
                continue
            hit = hits[0]
            key = (hit.clause_id, decision.action)
            if key in cited:
                continue
            cited.add(key)
            hit.for_action = decision.action
            retrieval.rules.append(hit)
        retrieval.queries.append(
            {
                "index": "policy_rules",
                "scope": sorted(allowed),
                "kinds": list(kinds),
                "hits": len(retrieval.rules),
            }
        )

    if plan.need_help:
        retrieval.rules.extend(store.search_help(plan.query, k=2, max_chars=plan.max_chars))
        retrieval.queries.append(
            {"index": "help_articles", "hits": len(retrieval.rules)}
        )

    if plan.need_recall:
        retrieval.recalled_turns = store.recall_turns(customer.id, plan.query, k=plan.max_turns)
        retrieval.queries.append(
            {
                "index": "events",
                "filter": {"customer_id": customer.id, "kind": "turn"},
                "hits": len(retrieval.recalled_turns),
            }
        )

    if plan.need_style:
        style = store.search_style(plan.query, k=1)
        if style:
            hit = style[0]
            hit.agent = strip_style_identifiers(hit.agent)
            hit.customer = strip_style_identifiers(hit.customer)
            retrieval.style = hit
        retrieval.queries.append(
            {"index": "style_samples", "hits": 1 if retrieval.style else 0}
        )

    retrieval.known_facts = store.known_facts(customer.id)
    if retrieval.known_facts:
        retrieval.queries.append(
            {
                "index": "memories",
                "filter": {"customer_id": customer.id},
                "hits": len(retrieval.known_facts),
            }
        )

    return retrieval
