from __future__ import annotations

from models.schemas import (
    Booking,
    Customer,
    CustomerAgentContext,
    DecisionStatus,
    Extraction,
    FrustrationAssessment,
    FrustrationCategory,
    PolicyEvaluation,
    Retrieval,
    RetrievalPlan,
    ScenarioFixture,
    SessionMemory,
)
from data.loader import load_style_samples

STYLE = {
    "principle": "Empathy through options and action, not long apology. Ask only missing slots. Never invent entitlements.",
    "samples_are": "tone only — not policy and not facts about this customer",
    "rules": [
        "Never state an entitlement unless policy_decision contains it.",
        "Never invent a replacement flight number.",
        "₹500 appears only when the decision includes amount_inr 500.",
        "DENY and ESCALATE must be stated; do not soften into approval.",
        "Actions are simulated prototype actions.",
    ],
}

RAW_POLICY_MARKERS = (
    "Delay under 3 hours: ₹500 meal voucher. Delay more than 3 hours:",
    "Agents cannot waive fare differences above ₹1,500 without supervisor approval.",
)


def _disruption(booking: Booking | None) -> dict | None:
    if not booking:
        return None
    if booking.status == "CANCELLED":
        return {
            "type": "cancellation",
            "flight": booking.flight,
            "route": booking.route,
            "reason": booking.status_reason,
            "airline_caused": booking.airline_caused,
        }
    if booking.status == "DELAYED":
        return {
            "type": "delay",
            "flight": booking.flight,
            "route": booking.route,
            "delay_hours": booking.delay_hours,
            "new_departure": booking.new_departure,
            "airline_caused": booking.airline_caused,
        }
    return {
        "type": booking.status.lower(),
        "flight": booking.flight,
        "route": booking.route,
        "status": booking.status,
    }


def _facts(customer: Customer | None, booking: Booking | None, related: list[Booking]) -> list[str]:
    facts: list[str] = []
    if not customer or not booking:
        return facts
    facts.append(f"{customer.name} / {customer.loyalty_tier} / PNR {customer.pnr}")
    facts.append(
        f"{booking.flight or booking.leg} {booking.route} {booking.status}"
        + (f" ({booking.delay_hours}h, new {booking.new_departure})" if booking.delay_hours else "")
        + (f" — {booking.status_reason}" if booking.status_reason else "")
    )
    for other in related:
        if other.id == booking.id:
            continue
        facts.append(f"Related leg {other.leg}: {other.route} on {other.date_label} is {other.status}")
    return facts


def assemble(
    *,
    session: SessionMemory,
    customer: Customer | None,
    booking: Booking | None,
    related_bookings: list[Booking],
    extraction: Extraction,
    evaluation: PolicyEvaluation | None,
    fixture: ScenarioFixture | None,
    kb_backend: str = "json",
    plan: RetrievalPlan | None = None,
    retrieval: Retrieval | None = None,
    frustration: FrustrationAssessment | None = None,
    kb_match=None,
) -> CustomerAgentContext:
    unidentified = customer is None
    missing = list(evaluation.missing_slots) if evaluation else []
    if unidentified:
        # Signed-out packet: identity is the account, not a name/PNR guess.
        missing = ["sign_in"]
        evaluation = None
        fixture = None
        booking = None
        related_bookings = []
        retrieval = None
        extraction = Extraction(raw_text=extraction.raw_text)
    elif not booking:
        missing = missing or ["booking"]

    # Isolation: fixture only for the identified customer it belongs to
    if customer and fixture and fixture.customer_id != customer.id:
        fixture = None
    if unidentified:
        fixture = None

    authority = {
        "can_execute": [
            "24h free rebook for airline-caused cancellation (no invented flight number)",
            "refund to original payment method for airline-caused cancellation",
            "meal voucher / lounge / delayed-hours hotel when delay rule qualifies",
            "provide this customer's booking status",
        ],
        "must_escalate": [
            "fare waiver above ₹1500",
            "compensation beyond stated policy",
            "legal action or formal complaint",
            "refund to a different payment method",
            "non-airline-caused exceptions",
        ],
        "unknown_is_not_allowed": True,
    }

    style = dict(STYLE)
    style["sample_hint"] = load_style_samples()["note"]

    return CustomerAgentContext(
        identity=customer,
        unidentified=unidentified,
        booking=booking,
        related_bookings=related_bookings if not unidentified else [],
        disruption=_disruption(booking),
        session_memory=session,
        emotion=extraction.emotion,
        frustration=frustration,
        kb_match=kb_match,
        requests_this_turn=extraction.requests,
        policy_decision=evaluation,
        scenario_fixture=fixture,
        retrieval_plan=plan,
        retrieval=retrieval,
        authority=authority,
        missing_slots=missing,
        style=style,
        retrieved_facts=_facts(customer, booking, related_bookings),
        forbidden_notes=[
            "Do not include other passengers in this packet.",
            "Do not send raw policies.json for the model to reinterpret.",
            "Do not treat travel-history resolutions as new entitlements.",
            "Sample conversations are style only.",
        ],
        kb_backend=kb_backend,  # type: ignore[arg-type]
    )


def packet_for_ui(ctx: CustomerAgentContext) -> dict:
    return {
        "unidentified": ctx.unidentified,
        "identity": None
        if not ctx.identity
        else {
            "id": ctx.identity.id,
            "name": ctx.identity.name,
            "tier": ctx.identity.loyalty_tier,
            "loyalty_tier": ctx.identity.loyalty_tier,
            "pnr": ctx.identity.pnr,
            "email": ctx.identity.email,
        },
        "booking": None
        if not ctx.booking
        else ctx.booking.model_dump(),
        "disruption": ctx.disruption,
        "emotion": ctx.emotion,
        "frustration": None if not ctx.frustration else ctx.frustration.model_dump(),
        "kb_match": None if not ctx.kb_match else ctx.kb_match.model_dump(),
        "prior_resolution_phrasing": (
            ctx.kb_match.phrasing if ctx.kb_match and ctx.kb_match.matched else None
        ),
        "retrieved_facts": ctx.retrieved_facts,
        "requests_this_turn": [r.model_dump() for r in ctx.requests_this_turn],
        "policy_decision": None if not ctx.policy_decision else ctx.policy_decision.model_dump(),
        "scenario_fixture": None if not ctx.scenario_fixture else ctx.scenario_fixture.model_dump(),
        "retrieval_plan": None if not ctx.retrieval_plan else ctx.retrieval_plan.model_dump(),
        "retrieved": None if not ctx.retrieval else ctx.retrieval.model_dump(),
        "missing_slots": ctx.missing_slots,
        "authority": ctx.authority,
        "executed_actions": ctx.session_memory.executed_actions,
        "recalled_turns": [t.model_dump() for t in ctx.session_memory.recalled_turns],
        "known_facts": [f.model_dump() for f in ctx.session_memory.known_facts],
        "kb_backend": ctx.kb_backend,
        "forbidden_notes": ctx.forbidden_notes,
        "suggested_flight": None
        if not ctx.policy_decision or not ctx.policy_decision.suggested_flight
        else ctx.policy_decision.suggested_flight.model_dump(),
    }


def render_extract_prompt(utterance: str, session: SessionMemory) -> str:
    # Last 3 turns verbatim plus whatever recall already retrieved. The whole
    # transcript is not a retrieval strategy — it is how cost and leakage grow.
    memory = {
        "identified": session.identified,
        "customer_id": session.customer_id,
        "open_question": session.open_question,
        "executed_actions": session.executed_actions,
        "recent_turns": session.messages[-6:],
        "recalled_turns": [
            {"message": t.message, "reply": t.reply} for t in session.recalled_turns[:3]
        ],
        "known_facts": [f.fact for f in session.known_facts],
    }
    return (
        "Extract JSON only. Fields: emotion, legal_or_formal, requests[], mentioned_name, mentioned_pnr. "
        "Do not output eligibility, compensation, or policy decisions.\n"
        f"session_memory: {memory}\n"
        f"utterance: {utterance}"
    )


STATUS_LABEL = {
    DecisionStatus.ALLOW: "APPROVED",
    DecisionStatus.DENY: "NOT APPROVED",
    DecisionStatus.ESCALATE: "ESCALATED TO A HUMAN",
    DecisionStatus.ASK: "PASSENGER MUST CHOOSE",
    DecisionStatus.INFORM: "FOR INFORMATION",
}


def narrate(ctx: CustomerAgentContext) -> list[str]:
    """Render the decided packet as prose with clause-level citations.

    Every line is either a field of a PolicyDecision or a retrieved policy clause.
    That is what makes the factual-consistency check mechanical rather than a promise:
    a number in a reply that is not here did not come from the system.
    """
    lines: list[str] = []
    if ctx.emotion:
        lines.append(f"Passenger tone: {ctx.emotion}.")
    if ctx.frustration and ctx.frustration.category is not FrustrationCategory.NEUTRAL:
        # Stated as an observation with an explicit ceiling on what it means, so
        # a model reading these facts cannot treat distress as a reason to
        # approve something. The eligible set above is the only authority.
        lines.append(
            f"Frustration observed: {ctx.frustration.category.value}"
            + (f" (signals: {', '.join(ctx.frustration.signals)})" if ctx.frustration.signals else "")
            + ". This changes wording and which approved option comes first. "
            "It grants nothing."
        )

    if ctx.unidentified:
        lines.append("The passenger is not signed in. No record, booking, or entitlement is available.")
        return lines

    if ctx.identity:
        lines.append(
            f"Passenger: {ctx.identity.name}, {ctx.identity.loyalty_tier} tier, PNR {ctx.identity.pnr}."
        )
    if not ctx.booking:
        lines.append("No booking is attached to this account. Do not invent a flight.")
        return lines

    booking = ctx.booking
    detail = f"Flight {booking.flight or booking.leg} {booking.route} is {booking.status.lower()}"
    if booking.delay_hours:
        detail += f" by {booking.delay_hours} hours, new departure {booking.new_departure}"
    if booking.status_reason:
        detail += f", reason: {booking.status_reason}"
    lines.append(detail + (", airline-caused." if booking.airline_caused else "."))

    citations = {}
    for hit in (ctx.retrieval.rules if ctx.retrieval else []):
        if hit.for_action:
            citations.setdefault(hit.for_action, hit)

    evaluation = ctx.policy_decision
    if not evaluation:
        lines.append("No policy decision is established for this turn.")
        return lines

    for decision in evaluation.decisions:
        label = STATUS_LABEL.get(decision.status, decision.status.value)
        line = f"{label}: {decision.action.replace('_', ' ')}"
        if decision.scope:
            line += f" — {decision.scope}"
        if decision.amount_inr is not None:
            line += f" — amount ₹{decision.amount_inr}"
        lines.append(line + ".")
        lines.append(f"  because: {decision.reason}")
        hit = citations.get(decision.action)
        if hit:
            lines.append(f'  cited {hit.title} [{hit.clause_id}]: "{hit.text}"')
        else:
            lines.append(f"  source: {decision.source}")

    for slot in ctx.missing_slots:
        lines.append(f"Missing and must be asked: {slot}.")

    for other in ctx.related_bookings:
        if other.id == booking.id:
            continue
        lines.append(
            f"Other leg {other.leg} {other.route} on {other.date_label} is {other.status.lower()}."
        )

    if ctx.session_memory.executed_actions:
        lines.append(
            "Already actioned this session (simulated): "
            + ", ".join(ctx.session_memory.executed_actions)
            + ". That does not close the case."
        )
    if ctx.session_memory.escalated_to_human:
        lines.append("This case is with a supervisor. Do not treat later messages as a resolution.")
    if ctx.session_memory.resolved_by_customer:
        lines.append("The passenger has said this case is resolved.")
    elif ctx.frustration and ctx.frustration.category.value not in {"neutral", ""}:
        lines.append(
            "The passenger is still unhappy. This case is open — do not treat an earlier close as current."
        )
    if ctx.session_memory.feedback:
        fb = ctx.session_memory.feedback
        lines.append(
            "Passenger feedback recorded: "
            + (f"{fb.rating}/5, " if fb.rating is not None else "")
            + f"{fb.sentiment}."
        )

    for fact in (ctx.retrieval.known_facts if ctx.retrieval else []):
        lines.append(f"Remembered about this passenger: {fact.fact}")

    for turn in (ctx.retrieval.recalled_turns if ctx.retrieval else []):
        lines.append(f"Earlier in this case the passenger said: {turn.message}")

    return lines


def render_respond_prompt(ctx: CustomerAgentContext, utterance: str) -> str:
    facts = "\n".join(narrate(ctx))
    tone = ""
    style = ctx.retrieval.style if ctx.retrieval else None
    prior = ctx.kb_match.phrasing if ctx.kb_match and ctx.kb_match.matched else None
    if prior:
        tone = (
            "\ntone reference (phrasing only — a prior resolution; strip leftover "
            f"amounts, PNRs, and flight numbers, do not treat as entitlement):\n  {prior}"
        )
    elif style:
        # One retrieved sample instead of all three. Sample numbers belong to an
        # unrelated flight, so the grounding rule above has to override them.
        tone = (
            "\ntone reference (phrasing only — its flight, times and amounts are "
            f"unrelated to this passenger and must not be repeated):\n  {style.agent}"
        )
    mood = ""
    if ctx.emotion:
        mood = (
            f"\nThe passenger sounds {ctx.emotion}. Acknowledge that in at most one short "
            "sentence before the options. Tone never changes what is approved."
        )
    return (
        "You are AeroResolve, a customer-facing airline disruption agent. "
        "Explain the decisions below to the passenger. Every fact, amount, entitlement "
        "and flight you state must already appear in the grounded facts. Do not add "
        "benefits. Do not invent flight numbers. Ask only what is listed as missing. "
        "Keep it short: empathy through options and action."
        f"{mood}\n"
        f"passenger said: {utterance}\n"
        f"grounded facts:\n{facts}{tone}"
    )


def context_contains_forbidden(prompt: str, current_name: str | None) -> list[str]:
    """Code-side gate: other passengers, raw policy bodies, and history-as-benefit."""
    leaks = []
    from kb.store import store

    others = {p["name"] for p in store.passengers.values()}
    if current_name:
        others.discard(current_name)
    for name in others:
        if name in prompt:
            leaks.append(name)
        email = next((p.get("email") for p in store.passengers.values() if p.get("name") == name), None)
        if email and email in prompt:
            leaks.append(email)
    for marker in RAW_POLICY_MARKERS:
        if marker in prompt:
            leaks.append("raw_policy_body")
            break
    if "delayed baggage" in prompt.lower() or "prior complaint" in prompt.lower():
        leaks.append("travel_history_as_benefit")
    return leaks
