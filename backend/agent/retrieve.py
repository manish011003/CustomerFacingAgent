from __future__ import annotations

from models.schemas import Customer, PolicyEvaluation, Retrieval, RetrievalPlan


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
        retrieval.style = style[0] if style else None
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
