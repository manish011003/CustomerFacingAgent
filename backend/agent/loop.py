from __future__ import annotations

import time

from agent import retrieve
from agent.context import assemble, packet_for_ui
from agent.planner import expand_scope, plan_retrieval
from factories.extractor_factory import ExtractorFactory
from factories.llm_factory import LlmFactory
from factories.reply_factory import ReplyFactory
from kb.store import store
from models.schemas import (
    ChatResponse,
    DecisionStatus,
    PolicyEvaluation,
    RequestType,
    Retrieval,
    SessionMemory,
)
from policy.engine import evaluate_policy

# Statuses that assert something to the passenger and therefore owe a citation.
# ASK and INFORM are conversational moves, not claims about entitlement.
SUBSTANTIVE = {DecisionStatus.ALLOW, DecisionStatus.DENY, DecisionStatus.ESCALATE}

SESSIONS: dict[str, SessionMemory] = {}


def get_session(session_id: str) -> SessionMemory:
    if session_id not in SESSIONS:
        SESSIONS[session_id] = SessionMemory(session_id=session_id)
    return SESSIONS[session_id]


def _trace(step: str, detail: str, status: str = "ok") -> dict:
    return {"step": step, "detail": detail, "status": status}


def _telemetry(
    *,
    started: float,
    evaluation: PolicyEvaluation | None,
    retrieval: Retrieval | None,
    usage: dict,
    llm_enabled: bool,
) -> dict:
    """Per-turn measurements, recorded on the turn event so analytics can aggregate.

    Containment here means no human was required. It is deliberately reported
    next to the escalation reasons, because an escalation caused by a policy
    authority limit is a correct outcome, not a miss.
    """
    decisions = [d for d in (evaluation.decisions if evaluation else []) if d.status in SUBSTANTIVE]
    escalated = [d for d in decisions if d.status == DecisionStatus.ESCALATE]
    cited_actions = {hit.for_action for hit in (retrieval.rules if retrieval else []) if hit.for_action}
    grounded = [d for d in decisions if d.action in cited_actions]

    return {
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "contained": not escalated,
        "escalation_reasons": [
            d.escalation_reason.value for d in escalated if d.escalation_reason is not None
        ],
        "decisions": len(decisions),
        "grounded_decisions": len(grounded),
        # A turn is fully grounded when every claim it made carries a clause.
        "grounded": len(decisions) > 0 and len(grounded) == len(decisions),
        # The LLM was available but produced nothing, so wording came from the
        # template. The answer is still correct; only the phrasing degraded.
        "degraded": bool(llm_enabled and usage.get("degradations")),
        "degradations": usage.get("degradations", []),
        "provider": usage.get("provider", "none"),
        "model": usage.get("model", ""),
        "models_used": usage.get("models_used", []),
        "llm_calls": usage.get("calls", 0),
        "llm_cached_calls": usage.get("cached_calls", 0),
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "est_cost_usd": usage.get("est_cost_usd", 0.0),
    }


def handle_chat(session_id: str, message: str, authenticated_customer_id: str | None = None) -> ChatResponse:
    started = time.perf_counter()
    session = get_session(session_id)
    session.messages.append({"role": "user", "content": message})
    trace = []

    llm = LlmFactory.create()
    llm.begin_turn(session_id)

    extractor = ExtractorFactory.create("auto")
    extraction = extractor.extract(message, session)
    session.last_extraction = extraction
    trace.append(_trace("extract", f"{len(extraction.requests)} request(s), legal={extraction.legal_or_formal}"))

    plan = plan_retrieval(extraction, session)
    slices = ["booking"]
    if plan.need_related_legs:
        slices.append("related legs")
    if plan.need_fixture:
        slices.append("fare fixture")
    if plan.need_recall:
        slices.append("prior turns")
    trace.append(_trace("plan", "fetch " + ", ".join(slices)))

    customer = None
    if authenticated_customer_id:
        customer = store.identify(customer_id=authenticated_customer_id)
    if not customer and session.customer_id:
        customer = store.identify(customer_id=session.customer_id)
    if not customer:
        customer = store.identify(name=extraction.mentioned_name, pnr=extraction.mentioned_pnr)

    if customer:
        session.customer_id = customer.id
        session.identified = True
        trace.append(_trace("identify", f"{customer.name} / {customer.pnr}"))
    else:
        trace.append(_trace("identify", "unidentified — sign in required", "ask"))

    # Selective fetch: only the slices this turn's plan asked for.
    booking = store.affected_booking(customer.id) if customer else None
    related = store.bookings_for(customer.id) if customer and plan.need_related_legs else []
    fixture = store.fixture_for(customer.id) if customer and plan.need_fixture else None

    if customer and booking:
        store.append_edge(
            {
                "customer_id": customer.id,
                "from_id": customer.id,
                "from_type": "Customer",
                "rel": "HAS_BOOKING",
                "to_id": booking.id,
                "to_type": "Booking",
                "reason": "Retrieved from passenger knowledge base",
                "source": "Booking / Transaction Data",
            }
        )
        if booking.status in {"CANCELLED", "DELAYED"}:
            store.append_edge(
                {
                    "customer_id": customer.id,
                    "from_id": booking.id,
                    "from_type": "Booking",
                    "rel": "HAS_DISRUPTION",
                    "to_id": f"{booking.status}-{booking.delay_hours or 0}",
                    "to_type": "Disruption",
                    "reason": booking.status_reason or booking.status,
                    "source": "Booking / Transaction Data",
                }
            )
        trace.append(_trace("booking", f"{booking.flight or booking.leg} {booking.status}"))

    fare = None
    for req in extraction.requests:
        if req.type in {RequestType.HIGHER_FARE_REBOOK, RequestType.FARE_WAIVER}:
            if req.fare_difference_inr is None and booking and booking.quoted_fare_difference_inr:
                req.fare_difference_inr = booking.quoted_fare_difference_inr
            if req.fare_difference_inr is None and fixture:
                req.fare_difference_inr = fixture.fare_difference_inr
            fare = req.fare_difference_inr

    evaluation = None
    if customer and booking:
        evaluation = evaluate_policy(
            customer,
            booking,
            extraction.requests,
            fare_difference_inr=fare,
            legal_or_formal=extraction.legal_or_formal,
        )
        session.last_evaluation = evaluation
        trace.append(_trace("policy", f"{evaluation.disruption_type} entitlements={evaluation.entitlements}"))

        for decision in evaluation.decisions:
            store.append_edge(
                {
                    "customer_id": customer.id,
                    "from_id": f"{booking.status}",
                    "from_type": "Disruption",
                    "rel": "EVALUATED_UNDER" if decision.eligible else "DENIED_BY" if decision.status.value == "DENY" else "ESCALATED_TO" if decision.status.value == "ESCALATE" else "INFORMED_BY",
                    "to_id": decision.source,
                    "to_type": "PolicyRule",
                    "reason": decision.reason,
                    "source": decision.source,
                    "action": decision.action,
                    "status": decision.status.value,
                }
            )
            store.append_event(
                {
                    "kind": "decision",
                    "session_id": session.session_id,
                    "customer_id": customer.id,
                    "action": decision.action,
                    "status": decision.status.value,
                    "reason": decision.reason,
                    "source": decision.source,
                }
            )

        for action in evaluation.execute:
            if action not in session.executed_actions:
                session.executed_actions.append(action)
                store.append_event(
                    {
                        "kind": "action",
                        "session_id": session.session_id,
                        "customer_id": customer.id,
                        "action": action,
                        "simulated": True,
                    }
                )
                trace.append(_trace("action", f"SIMULATED {action}"))

        for action in evaluation.deny:
            if action not in session.denied:
                session.denied.append(action)
        for action in evaluation.escalate:
            if action not in session.escalations:
                session.escalations.append(action)

        if evaluation.missing_slots:
            session.open_question = evaluation.missing_slots[0]
        elif not evaluation.ask:
            session.open_question = None

    retrieval = None
    if customer:
        plan = expand_scope(plan, customer, booking)
        retrieval = retrieve.run(plan=plan, customer=customer, evaluation=evaluation)
        trace.append(
            _trace(
                "retrieve",
                f"{retrieval.backend}: {len(retrieval.rules)} clause(s) from "
                f"[{', '.join(plan.rule_scope) or 'no scope'}], "
                f"{len(retrieval.recalled_turns)} recalled turn(s), "
                f"{len(retrieval.known_facts)} known fact(s)",
            )
        )

    ctx = assemble(
        session=session,
        customer=customer,
        booking=booking,
        related_bookings=related,
        extraction=extraction,
        evaluation=evaluation,
        fixture=fixture if customer else None,
        kb_backend=store.backend,
        plan=plan,
        retrieval=retrieval,
    )
    trace.append(_trace("context", f"kb={ctx.kb_backend} unidentified={ctx.unidentified} missing={ctx.missing_slots}"))

    renderer = ReplyFactory.create("auto")
    reply = renderer.render(ctx, message)
    session.messages.append({"role": "assistant", "content": reply})

    escalation = None
    if evaluation and evaluation.escalate and customer and booking:
        escalation = {
            "id": f"case-{customer.id}",
            "status": "escalated",
            "customer_id": customer.id,
            "customer": customer.name,
            "pnr": customer.pnr,
            "flight": booking.flight,
            "disruption": ctx.disruption,
            "requests": [r.model_dump() for r in extraction.requests],
            "policy_decisions": [d.model_dump() for d in evaluation.decisions],
            # Prose for the supervisor reading the case; codes for the dashboard
            # that needs to group escalations by cause.
            "escalation_reasons": [d.reason for d in evaluation.decisions if d.status == DecisionStatus.ESCALATE],
            "escalation_reason_codes": [
                d.escalation_reason.value
                for d in evaluation.decisions
                if d.status == DecisionStatus.ESCALATE and d.escalation_reason is not None
            ],
            "transcript": session.messages,
            "graph": store.graph_for(customer.id),
            "recommended_human_question": "Review exception / waiver; do not treat agent silence as approval.",
        }
        store.upsert_case(escalation)
        store.append_event(
            {
                "kind": "escalation",
                "session_id": session.session_id,
                "customer_id": customer.id,
                "reasons": escalation["escalation_reasons"],
                "reason_codes": escalation["escalation_reason_codes"],
            }
        )
        trace.append(_trace("escalate", "; ".join(evaluation.escalate), "escalate"))
    elif customer:
        store.upsert_case(
            {
                "id": f"case-{customer.id}",
                "status": "open",
                "customer_id": customer.id,
                "customer": customer.name,
                "pnr": customer.pnr,
                "flight": booking.flight if booking else None,
                "transcript": session.messages,
            }
        )

    # Durable cross-session memory, written after retrieval so this turn's own
    # outcome is not replayed back to the passenger as something "remembered".
    if customer:
        if extraction.legal_or_formal:
            store.remember_fact(
                customer.id, "Raised a formal complaint or legal escalation.", "conversation"
            )
        for action in session.executed_actions:
            store.remember_fact(
                customer.id, f"Simulated action already taken: {action}.", "agent action"
            )
        for decision in (evaluation.decisions if evaluation else []):
            if decision.status == DecisionStatus.ESCALATE:
                store.remember_fact(
                    customer.id, f"Escalated to a supervisor: {decision.action}.", decision.source
                )

    eligibility = []
    if evaluation:
        eligibility = [
            {
                "action": d.action,
                "status": d.status.value,
                "reason": d.reason,
                "source": d.source,
                "scope": d.scope,
                "eligible": d.eligible,
            }
            for d in evaluation.decisions
        ]

    telemetry = _telemetry(
        started=started,
        evaluation=evaluation,
        retrieval=retrieval,
        usage=llm.end_turn(session_id),
        llm_enabled=llm.enabled,
    )
    trace.append(
        _trace(
            "measure",
            f"{telemetry['latency_ms']}ms, "
            f"{'contained' if telemetry['contained'] else 'escalated: ' + ', '.join(telemetry['escalation_reasons'])}, "
            f"{telemetry['grounded_decisions']}/{telemetry['decisions']} decisions cited, "
            f"{telemetry['prompt_tokens'] + telemetry['completion_tokens']} tokens",
            "ok" if telemetry["contained"] else "escalate",
        )
    )

    audit = store.append_event(
        {
            "kind": "turn",
            "session_id": session.session_id,
            "customer_id": customer.id if customer else None,
            "message": message,
            "reply": reply,
            **telemetry,
        }
    )

    return ChatResponse(
        reply=reply,
        context_packet=packet_for_ui(ctx),
        trace=trace,
        eligibility=eligibility,
        audit_event=audit,
        escalation=escalation,
        session={
            "session_id": session.session_id,
            "identified": session.identified,
            "customer_id": session.customer_id,
            "executed_actions": session.executed_actions,
            "denied": session.denied,
            "escalations": session.escalations,
            "open_question": session.open_question,
        },
    )


def reset_session(session_id: str) -> None:
    SESSIONS.pop(session_id, None)
