from __future__ import annotations

import time

from agent import closure as case_closure
from agent import frustration as frustration_detector
from agent import retrieve
from agent.context import assemble, packet_for_ui
from agent.orchestrator import run_llm_agent
from agent.planner import expand_scope, plan_retrieval
from factories.extractor_factory import ExtractorFactory
from factories.llm_factory import LlmFactory
from factories.reply_factory import ReplyFactory
from kb.store import store
from models.schemas import (
    ChatResponse,
    Customer,
    DecisionStatus,
    EscalationReason,
    Extraction,
    FrustrationAssessment,
    PolicyEvaluation,
    RequestType,
    Retrieval,
    ServiceFeedback,
    SessionMemory,
)
from policy.engine import evaluate_policy
from products.replies.template import TemplateReplyRenderer

# Statuses that assert something to the passenger and therefore owe a citation.
# ASK and INFORM are conversational moves, not claims about entitlement.
SUBSTANTIVE = {DecisionStatus.ALLOW, DecisionStatus.DENY, DecisionStatus.ESCALATE}

SESSIONS: dict[str, SessionMemory] = {}


def _remember(session: SessionMemory) -> None:
    SESSIONS[session.session_id] = session
    if session.customer_id:
        SESSIONS[f"customer:{session.customer_id}"] = session


def _stored_session(customer_id: str) -> SessionMemory | None:
    alias = f"customer:{customer_id}"
    if alias in SESSIONS:
        return SESSIONS[alias]
    stored = store.load_session(customer_id)
    if not stored:
        conversation = store.conversation_for(customer_id)
        if not conversation.get("messages"):
            return None
        stored = {
            "session_id": conversation.get("session_id") or f"session-{customer_id}",
            "customer_id": customer_id,
            "identified": True,
            "messages": conversation["messages"],
            "executed_actions": conversation.get("executed_actions") or [],
            "escalated_to_human": conversation.get("escalated_to_human") or False,
            "resolved_by_customer": conversation.get("resolved_by_customer") or False,
            "feedback": conversation.get("feedback"),
        }
    try:
        session = SessionMemory.model_validate(stored)
    except Exception:
        session = SessionMemory(
            session_id=stored.get("session_id") or f"session-{customer_id}",
            customer_id=customer_id,
            identified=True,
            messages=list(stored.get("messages") or []),
            executed_actions=list(stored.get("executed_actions") or []),
            escalated_to_human=bool(stored.get("escalated_to_human")),
            resolved_by_customer=bool(stored.get("resolved_by_customer")),
        )
    _remember(session)
    return session


def get_session(session_id: str, customer_id: str | None = None) -> SessionMemory:
    if session_id in SESSIONS:
        session = SESSIONS[session_id]
        if customer_id and not session.customer_id:
            session.customer_id = customer_id
            _remember(session)
        return session
    if customer_id:
        existing = _stored_session(customer_id)
        if existing:
            existing.session_id = existing.session_id or session_id
            SESSIONS[session_id] = existing
            return existing
    session = SessionMemory(session_id=session_id, customer_id=customer_id, identified=bool(customer_id))
    _remember(session)
    return session


def conversation_for(customer_id: str) -> dict:
    live = SESSIONS.get(f"customer:{customer_id}")
    if live and live.messages:
        store.upsert_session(customer_id, live)
    payload = store.conversation_for(customer_id)
    if live and live.messages:
        payload["session_id"] = live.session_id
        payload["messages"] = live.messages
        payload["executed_actions"] = live.executed_actions
        payload["escalated_to_human"] = live.escalated_to_human
        payload["resolved_by_customer"] = live.resolved_by_customer
        payload["feedback"] = None if not live.feedback else live.feedback.model_dump()
    if not payload.get("session_id"):
        payload["session_id"] = f"session-{customer_id}"
    return payload


def _trace(step: str, detail: str, status: str = "ok") -> dict:
    return {"step": step, "detail": detail, "status": status}


def _frustration_trace(assessment: FrustrationAssessment) -> dict:
    """One trace line, identical on both agent paths, so a reviewer can see the
    signal and its confidence without knowing which path ran."""
    return _trace(
        "frustration",
        f"{assessment.category.value} @ {assessment.confidence}"
        + (" (low confidence, not aggregated)" if assessment.low_confidence else "")
        + (f" — {', '.join(assessment.signals)}" if assessment.signals else ""),
    )


def _telemetry(
    *,
    started: float,
    evaluation: PolicyEvaluation | None,
    retrieval: Retrieval | None,
    usage: dict,
    llm_enabled: bool,
    agent_mode: str,
    extra_escalation_reasons: list[str] | None = None,
    frustration: FrustrationAssessment | None = None,
) -> dict:
    """Per-turn measurements, recorded on the turn event so analytics can aggregate.

    Containment here means no human was required. It is deliberately reported
    next to the escalation reasons, because an escalation caused by a policy
    authority limit is a correct outcome, not a miss.

    `extra_escalation_reasons` exists because a duty-of-care handover produces
    no PolicyDecision — there is no entitlement to decide. Without it a
    distress escalation would leave the turn counted as contained, which would
    be a false claim about needing no human.
    """
    decisions = [d for d in (evaluation.decisions if evaluation else []) if d.status in SUBSTANTIVE]
    escalated = [d for d in decisions if d.status == DecisionStatus.ESCALATE]
    cited_actions = {hit.for_action for hit in (retrieval.rules if retrieval else []) if hit.for_action}
    grounded = [d for d in decisions if d.action in cited_actions]
    reasons = [d.escalation_reason.value for d in escalated if d.escalation_reason is not None]
    for reason in extra_escalation_reasons or []:
        if reason not in reasons:
            reasons.append(reason)

    return {
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "contained": not escalated and not (extra_escalation_reasons or []),
        "escalation_reasons": reasons,
        # Denormalised onto the turn so containment can be cross-tabbed against
        # frustration without a join, and so a low-confidence guess stays
        # flagged wherever it is read.
        "frustration_category": None if not frustration else frustration.category.value,
        "frustration_confidence": None if not frustration else frustration.confidence,
        "frustration_low_confidence": None if not frustration else frustration.low_confidence,
        "decisions": len(decisions),
        "grounded_decisions": len(grounded),
        "grounded": len(decisions) > 0 and len(grounded) == len(decisions),
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
        "agent_mode": agent_mode,
    }


def _identify(session: SessionMemory, authenticated_customer_id: str | None, extraction: Extraction | None) -> Customer | None:
    customer = None
    if authenticated_customer_id:
        customer = store.identify(customer_id=authenticated_customer_id)
    if not customer and session.customer_id:
        customer = store.identify(customer_id=session.customer_id)
    if not customer and extraction:
        customer = store.identify(name=extraction.mentioned_name, pnr=extraction.mentioned_pnr)
    if customer:
        session.customer_id = customer.id
        session.identified = True
    return customer


def handle_chat(session_id: str, message: str, authenticated_customer_id: str | None = None) -> ChatResponse:
    started = time.perf_counter()
    session = get_session(session_id, authenticated_customer_id)
    session.messages.append({"role": "user", "content": message})

    llm = LlmFactory.create()
    llm.begin_turn(session_id)

    customer = _identify(session, authenticated_customer_id, None)
    # Survives the fallthrough below. The orchestrator classifies before it
    # calls the model, so if the model then answers nothing and no tool ran,
    # the observation is already recorded and must not be written twice.
    assessed: FrustrationAssessment | None = None
    if llm.enabled:
        reply, runtime = run_llm_agent(llm=llm, session=session, customer=customer, message=message)
        assessed = runtime.frustration
        tools_ran = bool(runtime.trace) or bool(runtime.requests)
        if reply or tools_ran:
            heuristic = ExtractorFactory.create("heuristic").extract(message, session)
            seen = {req.type for req in runtime.requests}
            for req in heuristic.requests:
                if req.type in seen or req.type in {RequestType.GENERAL_HELP, RequestType.STATUS}:
                    continue
                args: dict = {"action": req.type.value}
                if req.fare_difference_inr is not None:
                    args["fare_difference_inr"] = req.fare_difference_inr
                runtime.call("check_eligibility", args)
            extraction = runtime.extraction()
            evaluation = runtime.evaluation
            booking = runtime.booking
            related = runtime.related
            fixture = runtime.fixture
            retrieval = runtime.retrieval
            agent_mode = "llm" if reply else "fallback"
            if customer and evaluation:
                plan = expand_scope(plan_retrieval(extraction, session), customer, booking)
                retrieval = retrieve.run(plan=plan, customer=customer, evaluation=evaluation)
                for hit in runtime.retrieval.rules:
                    if not any(
                        existing.clause_id == hit.clause_id and existing.for_action == hit.for_action
                        for existing in retrieval.rules
                    ):
                        retrieval.rules.append(hit)
            if not reply:
                ctx = assemble(
                    session=session,
                    customer=runtime.customer or customer,
                    booking=booking,
                    related_bookings=related,
                    extraction=extraction,
                    evaluation=evaluation,
                    fixture=fixture,
                    kb_backend=store.backend,
                    retrieval=retrieval,
                    frustration=runtime.frustration,
                )
                reply = TemplateReplyRenderer().render(ctx, message)
            trace = [_trace("agent", "llm orchestrator" if agent_mode == "llm" else "fallback after tools")]
            if runtime.frustration:
                trace.append(_frustration_trace(runtime.frustration))
            for event in runtime.trace:
                trace.append(_trace(event.get("tool", "tool"), event.get("status", "ok"), event.get("status", "ok")))
            if runtime.frustration_escalation:
                trace.append(
                    _trace("escalate", EscalationReason.SEVERE_CUSTOMER_DISTRESS.value, "escalate")
                )
            return _finish(
                started=started,
                session=session,
                message=message,
                customer=runtime.customer or customer,
                booking=booking,
                related=related,
                extraction=extraction,
                evaluation=evaluation,
                fixture=fixture,
                retrieval=retrieval,
                reply=reply,
                trace=trace,
                llm=llm,
                agent_mode=agent_mode,
                apply_execute=False,
                frustration=runtime.frustration,
                distress=runtime.frustration if runtime.frustration_escalation else None,
            )

    return _deterministic_turn(
        started=started,
        session=session,
        message=message,
        authenticated_customer_id=authenticated_customer_id,
        llm=llm,
        assessed=assessed,
    )


def _deterministic_turn(
    *, started, session, message, authenticated_customer_id, llm, assessed=None
) -> ChatResponse:
    trace = [_trace("agent", "fallback — deterministic tools, not a live LLM")]
    extractor = ExtractorFactory.create("auto")
    extraction = extractor.extract(message, session)
    session.last_extraction = extraction
    trace.append(_trace("extract", f"{len(extraction.requests)} request(s), legal={extraction.legal_or_formal}"))

    # Same classifier, same schema, no model. This is the whole reason
    # downstream code never has to ask which agent path produced the signal.
    assessment = assessed or frustration_detector.classify(message, session)
    session.last_frustration = assessment
    trace.append(_frustration_trace(assessment))

    plan = plan_retrieval(extraction, session)
    slices = ["booking"]
    if plan.need_related_legs:
        slices.append("related legs")
    if plan.need_fixture:
        slices.append("fare fixture")
    if plan.need_recall:
        slices.append("prior turns")
    trace.append(_trace("plan", "fetch " + ", ".join(slices)))

    customer = _identify(session, authenticated_customer_id, extraction)
    if customer:
        trace.append(_trace("identify", f"{customer.name} / {customer.pnr}"))
    else:
        trace.append(_trace("identify", "unidentified — sign in required", "ask"))

    # Written after identification so the event and the graph edge can carry the
    # passenger, through the same writers every other turn record uses. Skipped
    # when the orchestrator already recorded this turn's observation.
    if assessed is None:
        store.append_frustration(
            assessment,
            session_id=session.session_id,
            customer_id=customer.id if customer else None,
        )
    distress = assessment if assessment.escalation_recommended else None
    if distress:
        trace.append(
            _trace("escalate", EscalationReason.SEVERE_CUSTOMER_DISTRESS.value, "escalate")
        )

    booking = store.affected_booking(customer.id) if customer else None
    related = store.bookings_for(customer.id) if customer and plan.need_related_legs else []
    fixture = store.fixture_for(customer.id) if customer and plan.need_fixture else None

    if customer and booking:
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
    conversation_only = bool(extraction.requests) and all(
        req.type
        in {RequestType.GENERAL_HELP, RequestType.HELP_QUESTION, RequestType.BOOKING_ASSIST}
        for req in extraction.requests
    )
    if customer and (booking or conversation_only):
        evaluation = evaluate_policy(
            customer,
            booking,
            extraction.requests,
            fare_difference_inr=fare,
            legal_or_formal=extraction.legal_or_formal,
            frustration_category=assessment.category,
        )
        session.last_evaluation = evaluation
        trace.append(_trace("policy", f"{evaluation.disruption_type} entitlements={evaluation.entitlements}"))

        for decision in evaluation.decisions:
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
        session.recalled_turns = retrieval.recalled_turns
        session.known_facts = retrieval.known_facts
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
        frustration=assessment,
    )
    trace.append(_trace("context", f"kb={ctx.kb_backend} unidentified={ctx.unidentified} missing={ctx.missing_slots}"))

    renderer = ReplyFactory.create("auto")
    reply = renderer.render(ctx, message)
    return _finish(
        started=started,
        session=session,
        message=message,
        customer=customer,
        booking=booking,
        related=related,
        extraction=extraction,
        evaluation=evaluation,
        fixture=fixture if customer else None,
        retrieval=retrieval,
        reply=reply,
        trace=trace,
        llm=llm,
        agent_mode="fallback",
        ctx=ctx,
        frustration=assessment,
        distress=distress,
    )


def _finish(
    *,
    started,
    session,
    message,
    customer,
    booking,
    related,
    extraction,
    evaluation,
    fixture,
    retrieval,
    reply,
    trace,
    llm,
    agent_mode,
    ctx=None,
    apply_execute=True,
    frustration=None,
    distress=None,
) -> ChatResponse:
    if ctx is None:
        ctx = assemble(
            session=session,
            customer=customer,
            booking=booking,
            related_bookings=related or [],
            extraction=extraction,
            evaluation=evaluation,
            fixture=fixture,
            kb_backend=store.backend,
            retrieval=retrieval,
            frustration=frustration,
        )

    # A duty-of-care handover is an escalation with no PolicyDecision behind it,
    # so it is carried as its own reason rather than borrowed from one.
    distress_reasons = [EscalationReason.SEVERE_CUSTOMER_DISTRESS.value] if distress else []

    if evaluation:
        session.last_evaluation = evaluation
        if apply_execute:
            for action in evaluation.execute:
                if action not in session.executed_actions:
                    session.executed_actions.append(action)
        for action in evaluation.deny:
            if action not in session.denied:
                session.denied.append(action)
        for action in evaluation.escalate:
            if action not in session.escalations:
                session.escalations.append(action)
            session.escalated_to_human = True
        if evaluation.missing_slots:
            session.open_question = evaluation.missing_slots[0]
        elif not evaluation.ask:
            session.open_question = None

    if distress:
        session.escalated_to_human = True

    newly_closed = _apply_passenger_close(session, message)
    parsed_feedback = newly_closed.get("feedback")

    escalating = bool(session.escalated_to_human or (evaluation and evaluation.escalate) or distress)
    ask_feedback = case_closure.should_prompt_feedback(
        session=session, evaluation=evaluation, escalating=escalating
    )
    if ask_feedback:
        if not session.awaiting_feedback and not case_closure.already_asked_feedback(reply):
            reply = reply.rstrip() + " " + case_closure.FEEDBACK_PROMPT
        session.awaiting_feedback = True
    elif session.feedback or session.resolved_by_customer or session.escalated_to_human:
        session.awaiting_feedback = False

    if customer:
        _record_turn_graph(customer=customer, booking=booking, evaluation=evaluation)

    session.messages.append({"role": "assistant", "content": reply})

    escalation = None
    case = None
    if customer:
        existing = store.cases.get(f"case-{customer.id}") or {}
        was_escalated = existing.get("status") == "escalated"
        if parsed_feedback:
            store.record_feedback(
                customer_id=customer.id,
                session_id=session.session_id,
                feedback=parsed_feedback,
            )
        case = _write_case(
            customer=customer,
            booking=booking,
            session=session,
            evaluation=evaluation,
            extraction=extraction,
            retrieval=retrieval,
            disruption=ctx.disruption,
            distress=distress,
        )
        newly_escalated = bool((evaluation and evaluation.escalate) or distress) and not was_escalated
        if case.get("status") == "escalated":
            escalation = case
        if newly_escalated:
            store.append_event(
                {
                    "kind": "escalation",
                    "session_id": session.session_id,
                    "customer_id": customer.id,
                    "reasons": case.get("escalation_reasons") or [],
                    "reason_codes": case.get("escalation_reason_codes") or [],
                }
            )
            if evaluation and evaluation.escalate:
                trace.append(_trace("escalate", "; ".join(evaluation.escalate), "escalate"))
        if distress and not was_escalated:
            store.remember_fact(
                customer.id,
                "Escalated to a supervisor for severe distress (duty of care, not an entitlement).",
                "frustration classifier",
            )

        if extraction and extraction.legal_or_formal:
            store.remember_fact(customer.id, "Raised a formal complaint or legal escalation.", "conversation")
        for action in session.executed_actions:
            store.remember_fact(customer.id, f"Simulated action already taken: {action}.", "agent action")
        for decision in evaluation.decisions if evaluation else []:
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
        usage=llm.end_turn(session.session_id),
        llm_enabled=llm.enabled,
        agent_mode=agent_mode,
        extra_escalation_reasons=distress_reasons,
        frustration=frustration,
    )
    trace.append(
        _trace(
            "measure",
            f"{telemetry['latency_ms']}ms, "
            f"{'contained' if telemetry['contained'] else 'escalated: ' + ', '.join(telemetry['escalation_reasons'])}, "
            f"{telemetry['grounded_decisions']}/{telemetry['decisions']} decisions cited, "
            f"{telemetry['prompt_tokens'] + telemetry['completion_tokens']} tokens, "
            f"mode={agent_mode}",
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
    if customer:
        store.upsert_session(customer.id, session)

    packet = packet_for_ui(ctx)
    packet["agent_mode"] = agent_mode
    packet["llm_active"] = agent_mode == "llm"
    packet["case_status"] = (case or {}).get("status") or "open"
    packet["feedback_prompt"] = bool(session.awaiting_feedback)
    popup = case_closure.should_show_feedback_popup(case_status=packet["case_status"], session=session)
    packet["feedback_popup"] = popup
    packet["feedback"] = None if not session.feedback else session.feedback.model_dump()

    return ChatResponse(
        reply=reply,
        context_packet=packet,
        trace=trace,
        eligibility=eligibility,
        audit_event=audit,
        escalation=escalation,
        case_status=packet["case_status"],
        feedback_prompt=bool(session.awaiting_feedback),
        feedback_popup=popup,
        feedback=packet["feedback"],
        session={
            "session_id": session.session_id,
            "identified": session.identified,
            "customer_id": session.customer_id,
            "executed_actions": session.executed_actions,
            "denied": session.denied,
            "escalations": session.escalations,
            "escalated_to_human": session.escalated_to_human,
            "resolved_by_customer": session.resolved_by_customer,
            "open_question": session.open_question,
            "recalled_turns": [t.model_dump() for t in session.recalled_turns],
            "known_facts": [f.model_dump() for f in session.known_facts],
            "agent_mode": agent_mode,
        },
    )


def reset_session(session_id: str, customer_id: str | None = None) -> None:
    session = SESSIONS.pop(session_id, None)
    cid = customer_id or (session.customer_id if session else None)
    if cid:
        SESSIONS.pop(f"customer:{cid}", None)
        for key, value in list(SESSIONS.items()):
            if value.customer_id == cid:
                SESSIONS.pop(key, None)
        store.clear_session(cid)


def _apply_passenger_close(session: SessionMemory, message: str) -> dict:
    """Resolution and ratings come from the passenger, never from executed tools."""
    from products.knowledge.base import ISO

    parsed = case_closure.parse_feedback(message, session)
    if case_closure.wants_escalation(message, session):
        session.resolved_by_customer = False
    elif case_closure.confirms_resolution(message, session):
        session.resolved_by_customer = True
    if parsed:
        parsed.ts = parsed.ts or ISO()
        session.feedback = parsed
        if parsed.sentiment == "positive" and not session.escalated_to_human:
            session.resolved_by_customer = True
        if parsed.sentiment == "negative":
            session.resolved_by_customer = False
    return {"feedback": parsed}


def submit_feedback(session_id: str, customer_id: str, rating: int, comment: str | None = None) -> dict:
    """Structured 1–5 rating from the chat UI. Same close rules as a spoken rating."""
    from products.knowledge.base import ISO

    session = get_session(session_id, customer_id)
    session.customer_id = session.customer_id or customer_id
    sentiment = "positive" if rating >= 4 else "negative" if rating <= 2 else "mixed"
    feedback = ServiceFeedback(
        rating=rating,
        comment=comment,
        sentiment=sentiment,
        source="card",
        ts=ISO(),
    )
    session.feedback = feedback
    already_resolved = session.resolved_by_customer
    if already_resolved:
        pass
    elif sentiment == "positive" and not session.escalated_to_human:
        session.resolved_by_customer = True
    elif sentiment != "positive":
        session.resolved_by_customer = False
    session.awaiting_feedback = False

    customer = store.identify(customer_id=customer_id)
    if customer:
        store.record_feedback(customer_id=customer.id, session_id=session.session_id, feedback=feedback)
        thanks = (
            "Thank you — I've recorded your feedback and closed this case."
            if session.resolved_by_customer
            else "Thank you — I've recorded your feedback. This case stays open with a supervisor."
            if session.escalated_to_human
            else "Thank you — I've recorded your feedback. Tell me if anything is still unresolved."
        )
        session.messages.append(
            {
                "role": "user",
                "content": f"I'd rate this service {rating}/5."
                + (f" {comment}" if comment else ""),
            }
        )
        session.messages.append({"role": "assistant", "content": thanks})
        booking = store.affected_booking(customer.id)
        _write_case(
            customer=customer,
            booking=booking,
            session=session,
            evaluation=session.last_evaluation,
            extraction=session.last_extraction,
            retrieval=None,
            disruption=None,
            distress=None,
        )
        store.upsert_session(customer.id, session)
    else:
        thanks = "Thank you — I've recorded your feedback."

    case = store.cases.get(f"case-{customer_id}") or {}
    popup = case_closure.should_show_feedback_popup(
        case_status=case.get("status") or "open", session=session
    )
    return {
        "ok": True,
        "reply": thanks,
        "case_status": case.get("status") or "open",
        "feedback_popup": popup,
        "feedback": feedback.model_dump(),
    }


def _record_turn_graph(*, customer, booking, evaluation: PolicyEvaluation | None) -> None:
    """Same edges on both agent paths, so Operations can draw the live KB."""
    if not customer or not booking:
        return
    disruption_id = f"{booking.status}-{booking.delay_hours or 0}"
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
            "label": booking.flight or booking.pnr,
        }
    )
    if booking.status in {"CANCELLED", "DELAYED"}:
        store.append_edge(
            {
                "customer_id": customer.id,
                "from_id": booking.id,
                "from_type": "Booking",
                "rel": "HAS_DISRUPTION",
                "to_id": disruption_id,
                "to_type": "Disruption",
                "reason": booking.status_reason or booking.status,
                "source": "Booking / Transaction Data",
            }
        )
    if not evaluation:
        return
    for decision in evaluation.decisions:
        store.append_edge(
            {
                "customer_id": customer.id,
                "from_id": disruption_id if booking.status in {"CANCELLED", "DELAYED"} else booking.id,
                "from_type": "Disruption" if booking.status in {"CANCELLED", "DELAYED"} else "Booking",
                "rel": "EVALUATED_UNDER"
                if decision.eligible
                else "DENIED_BY"
                if decision.status.value == "DENY"
                else "ESCALATED_TO"
                if decision.status.value == "ESCALATE"
                else "INFORMED_BY",
                "to_id": decision.source,
                "to_type": "PolicyRule",
                "reason": decision.reason,
                "source": decision.source,
                "action": decision.action,
                "status": decision.status.value,
            }
        )


def _issue_label(evaluation: PolicyEvaluation | None, booking) -> str:
    if evaluation and evaluation.disruption_type == "cancellation":
        return "Flight cancelled"
    if evaluation and evaluation.disruption_type == "delay":
        hours = evaluation.delay_hours
        return f"Flight delayed {hours} hours" if hours is not None else "Flight delayed"
    if booking:
        return booking.status_reason or booking.status.replace("_", " ").title()
    return "Support request"


def _case_status(
    evaluation: PolicyEvaluation | None,
    session: SessionMemory,
    distress: FrustrationAssessment | None = None,
    existing: dict | None = None,
) -> str:
    return case_closure.case_status(
        evaluation=evaluation,
        session=session,
        distress=distress,
        existing=existing,
    )


def _write_case(
    *,
    customer,
    booking,
    session: SessionMemory,
    evaluation: PolicyEvaluation | None,
    extraction,
    retrieval: Retrieval | None,
    disruption,
    distress: FrustrationAssessment | None = None,
) -> dict:
    """One auditable record per passenger conversation. Does not decide policy."""
    from products.knowledge.base import ISO

    case_id = f"case-{customer.id}"
    existing = store.cases.get(case_id) or {}
    status = _case_status(evaluation, session, distress, existing)
    if status == "resolved":
        resolved_at = existing.get("resolved_at") or ISO()
    else:
        resolved_at = None

    decisions = evaluation.decisions if evaluation else existing.get("policy_decisions") or []
    if evaluation:
        decisions = evaluation.decisions
    # Distress is appended, never substituted: a turn that hit a policy
    # authority limit *and* needed a person reports both, so neither reason can
    # hide behind the other in the escalation breakdown.
    escalation_reasons = [d.reason for d in decisions if getattr(d, "status", None) == DecisionStatus.ESCALATE]
    if not escalation_reasons:
        escalation_reasons = list(existing.get("escalation_reasons") or [])
    else:
        for reason in existing.get("escalation_reasons") or []:
            if reason not in escalation_reasons:
                escalation_reasons.append(reason)
    escalation_codes = [
        d.escalation_reason.value
        for d in decisions
        if getattr(d, "status", None) == DecisionStatus.ESCALATE and getattr(d, "escalation_reason", None) is not None
    ]
    if not escalation_codes:
        escalation_codes = list(existing.get("escalation_reason_codes") or [])
    else:
        for code in existing.get("escalation_reason_codes") or []:
            if code not in escalation_codes:
                escalation_codes.append(code)
    if distress:
        distress_reason = (
            "The passenger is in severe distress and a person should take over. "
            f"Signals observed: {', '.join(distress.signals) or 'none named'}. "
            "This is duty of care and grants no entitlement."
        )
        if distress_reason not in escalation_reasons:
            escalation_reasons.append(distress_reason)
        if EscalationReason.SEVERE_CUSTOMER_DISTRESS.value not in escalation_codes:
            escalation_codes.append(EscalationReason.SEVERE_CUSTOMER_DISTRESS.value)

    dumped_decisions = []
    for decision in decisions:
        dumped_decisions.append(decision.model_dump() if hasattr(decision, "model_dump") else decision)

    case = {
        "id": case_id,
        "status": status,
        "customer_id": customer.id,
        "customer": customer.name,
        "loyalty_tier": customer.loyalty_tier,
        "email": customer.email,
        "pnr": customer.pnr,
        "flight": booking.flight if booking else existing.get("flight"),
        "issue": _issue_label(evaluation, booking) if (evaluation or booking) else existing.get("issue"),
        "action_taken": list(session.executed_actions),
        "escalation_status": status == "escalated",
        "escalation_reasons": escalation_reasons,
        "escalation_reason_codes": escalation_codes,
        "frustration": existing.get("frustration") if not distress else distress.model_dump(),
        "booking": existing.get("booking") if not booking else booking.model_dump(),
        "disruption": disruption if disruption is not None else existing.get("disruption"),
        "requests": [r.model_dump() for r in extraction.requests] if extraction else existing.get("requests") or [],
        "policy_decisions": dumped_decisions,
        "policy_rules": [r.model_dump() for r in retrieval.rules] if retrieval else existing.get("policy_rules") or [],
        "transcript": session.messages,
        "timeline": [e for e in store.events if e.get("customer_id") == customer.id][-50:],
        "created_at": existing.get("created_at"),
        "resolved_at": resolved_at,
        "feedback": None if not session.feedback else session.feedback.model_dump(),
        "resolved_by": "customer" if status == "resolved" else existing.get("resolved_by"),
        "manager_assessment": existing.get("manager_assessment"),
        "recommended_human_question": (
            "Review exception / waiver; do not treat agent silence as approval." if status == "escalated" else None
        ),
    }
    return store.upsert_case(case)
