from __future__ import annotations

from models.schemas import (
    Booking,
    Customer,
    Extraction,
    IssueFamily,
    RequestType,
    RetrievalPlan,
    SessionMemory,
)

CANCEL = "CANCELLATION_REBOOKING_RULE"
DELAY = "DELAY_COMPENSATION_RULE"
REFUND = "REFUND_PROCESSING_RULE"
FARE = "FARE_DIFFERENCE_RULE"
LOYALTY = "LOYALTY_TIER_RULE"
MUST_ESCALATE = "MUST_ESCALATE"
ALLOWED_ACTIONS = "ALLOWED_ACTIONS"

# Which slices a request type needs. The point is what is absent: a status question
# pulls no policy clauses, no other legs, and no scenario fixture.
NEEDS: dict[RequestType, dict] = {
    RequestType.STATUS: {"rules": []},
    RequestType.GENERAL_HELP: {"rules": [], "help": True},
    RequestType.HELP_QUESTION: {"rules": [], "help": True},
    RequestType.BOOKING_ASSIST: {"rules": [], "help": True},
    RequestType.MEAL_VOUCHER: {"rules": [DELAY]},
    RequestType.LOUNGE: {"rules": [DELAY]},
    RequestType.HOTEL_DELAYED_HOURS: {"rules": [DELAY]},
    RequestType.HOTEL_FULL_NIGHT: {"rules": [DELAY]},
    RequestType.REBOOK_24H: {"rules": [CANCEL, ALLOWED_ACTIONS]},
    RequestType.REFUND_ORIGINAL: {"rules": [CANCEL, REFUND], "related": True},
    RequestType.REFUND_OTHER_METHOD: {"rules": [REFUND, MUST_ESCALATE], "escalation_docs": True},
    RequestType.HIGHER_FARE_REBOOK: {"rules": [FARE, MUST_ESCALATE], "fixture": True, "escalation_docs": True},
    RequestType.FARE_WAIVER: {"rules": [FARE, MUST_ESCALATE], "fixture": True, "escalation_docs": True},
    RequestType.BUSINESS_UPGRADE: {"rules": [MUST_ESCALATE], "related": True, "escalation_docs": True},
    RequestType.COMPENSATION_BEYOND_POLICY: {"rules": [MUST_ESCALATE], "escalation_docs": True},
    RequestType.LEGAL_OR_FORMAL: {"rules": [MUST_ESCALATE], "escalation_docs": True},
    RequestType.NON_AIRLINE_EXCEPTION: {"rules": [MUST_ESCALATE], "escalation_docs": True},
}


def plan_retrieval(extraction: Extraction, session: SessionMemory) -> RetrievalPlan:
    """Classify the turn into the retrievers it needs, before any fetching happens."""
    plan = RetrievalPlan(need_style=True)
    kinds = {"rule"}
    scope: list[str] = []

    for request in extraction.requests:
        spec = NEEDS.get(request.type, {"rules": []})
        for rule_id in spec.get("rules", []):
            if rule_id not in scope:
                scope.append(rule_id)
                plan.reasons.append(f"policy {rule_id} for request {request.type.value}")
        if spec.get("related") and not plan.need_related_legs:
            plan.need_related_legs = True
            plan.reasons.append(f"other legs may be affected by {request.type.value}")
        if spec.get("fixture") and not plan.need_fixture:
            plan.need_fixture = True
            plan.reasons.append(f"fare fixture for {request.type.value}")
        if spec.get("escalation_docs"):
            kinds.add("must_escalate")
        if spec.get("help"):
            plan.need_help = True
            plan.reasons.append(f"help corpus for {request.type.value}")
        if request.type == RequestType.REBOOK_24H:
            kinds.add("allowed_action")

    prior_turns = sum(1 for m in session.messages if m.get("role") == "user") - 1
    if prior_turns > 0:
        plan.need_recall = True
        plan.reasons.append(f"recall prior turns, {prior_turns} earlier in this conversation")

    plan.rule_scope = scope
    plan.doc_kinds = sorted(kinds)
    plan.need_policy = bool(scope)
    plan.query = _query(extraction)
    return plan


def expand_scope(plan: RetrievalPlan, customer: Customer | None, booking: Booking | None) -> RetrievalPlan:
    """Widen the citable scope using facts only known after the booking is loaded.

    A passenger who asks nothing specific still gets the rule that governs their
    disruption, so a status turn can cite why rebooking or a refund is on the table.
    """
    if not booking:
        return plan
    implied: list[str] = []
    if booking.status == "CANCELLED":
        implied.extend([CANCEL, REFUND])
    elif booking.status == "DELAYED":
        implied.append(DELAY)
    if customer and customer.loyalty_tier in {"Gold", "Platinum"}:
        implied.append(LOYALTY)

    for rule_id in implied:
        if rule_id not in plan.rule_scope:
            plan.rule_scope.append(rule_id)
            plan.reasons.append(f"policy {rule_id} implied by booking state")
    plan.need_policy = bool(plan.rule_scope)
    return plan


def _query(extraction: Extraction) -> str:
    if extraction.issue_family in {IssueFamily.HELP, IssueFamily.ASSIST}:
        return (extraction.raw_text or "").strip()
    terms = [extraction.raw_text or ""]
    for request in extraction.requests:
        terms.append(request.type.value.replace("_", " "))
    return " ".join(t for t in terms if t).strip()
