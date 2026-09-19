from factories.policy_factory import PolicyHandlerFactory
from models.schemas import (
    Booking,
    Customer,
    DecisionStatus,
    EscalationReason,
    ExtractedRequest,
    FrustrationCategory,
    PolicyDecision,
    PolicyEvaluation,
    RequestType,
)
from policy.exclusivity import offered_actions
from policy.ops import (
    AUTHORITY_SOURCE,
    CANCELLATION_SOURCE,
    DELAY_SOURCE,
    FARE_WAIVER_LIMIT_INR,
    LOYALTY_SOURCE,
    REFUND_SOURCE,
    append_decision,
)

__all__ = [
    "FARE_WAIVER_LIMIT_INR",
    "delay_entitlements",
    "evaluate_policy",
    "baseline_for_booking",
    "offered_actions",
]


def delay_entitlements(delay_hours: int) -> list[PolicyDecision]:
    """Independent thresholds from the data pack. Does not invent amounts for >3h meal vouchers."""
    items: list[PolicyDecision] = []
    if delay_hours < 3:
        items.append(
            PolicyDecision(
                action="meal_voucher",
                status=DecisionStatus.ALLOW,
                eligible=True,
                reason=f"Delay of {delay_hours} hour(s) is under 3 hours.",
                source=DELAY_SOURCE,
                amount_inr=500,
                scope="₹500 meal voucher",
            )
        )
        return items

    items.append(
        PolicyDecision(
            action="meal_voucher",
            status=DecisionStatus.ALLOW,
            eligible=True,
            reason=f"Delay of {delay_hours} hour(s) is more than 3 hours."
            if delay_hours > 3
            else f"Delay of {delay_hours} hour(s) is not under 3 hours; meal voucher without a stated ₹500 amount applies only to the under-3-hours band. More-than-3-hours band is used when delay > 3.",
            source=DELAY_SOURCE,
            scope="meal voucher (amount not stated for this band)",
        )
    )

    if delay_hours > 3:
        items[-1].reason = f"Delay of {delay_hours} hour(s) is more than 3 hours."
        items.append(
            PolicyDecision(
                action="lounge",
                status=DecisionStatus.ALLOW,
                eligible=True,
                reason=f"Delay of {delay_hours} hour(s) is more than 3 hours.",
                source=DELAY_SOURCE,
                scope="lounge access",
            )
        )

    if delay_hours > 5:
        items.append(
            PolicyDecision(
                action="hotel_delayed_hours",
                status=DecisionStatus.ALLOW,
                eligible=True,
                reason=f"Delay of {delay_hours} hour(s) is more than 5 hours. Hotel covers delayed hours only, not a full night.",
                source=DELAY_SOURCE,
                scope=f"hotel for delayed hours only ({delay_hours} hours)",
            )
        )
    return items


def baseline_for_booking(
    customer: Customer,
    booking: Booking,
    *,
    frustration_category: FrustrationCategory | None = None,
) -> PolicyEvaluation:
    """Entitlements this disruption carries before the passenger asks anything.

    `frustration_category` reaches `policy/exclusivity.py` and nothing else. It
    cannot touch a single decision, which is what lets the whole frustration
    subsystem be removed by deleting one argument.
    """
    evaluation = _baseline(customer, booking)
    evaluation.offered_actions = offered_actions(evaluation, frustration_category)
    return evaluation


def _baseline(customer: Customer, booking: Booking | None) -> PolicyEvaluation:
    evaluation = PolicyEvaluation()
    if booking is None:
        return evaluation
    if booking.status == "CANCELLED" and booking.airline_caused:
        evaluation.disruption_type = "cancellation"
        evaluation.entitlements = [
            "free_rebooking_within_24h",
            "full_refund_original_payment_method",
        ]
        if customer.loyalty_tier in {"Gold", "Platinum"}:
            evaluation.entitlements.append("priority_rebooking")
        evaluation.decisions.extend(
            [
                PolicyDecision(
                    action="rebook_24h",
                    status=DecisionStatus.ASK,
                    eligible=True,
                    reason="Airline-caused cancellation: customer may choose free rebooking on the next available flight within 24 hours. No replacement flight number is supplied in the data pack; rebooking is simulated without inventing inventory.",
                    source=CANCELLATION_SOURCE,
                    requires_customer_choice=True,
                    scope="next available within 24 hours (flight number not established)",
                ),
                PolicyDecision(
                    action="refund_original",
                    status=DecisionStatus.ASK,
                    eligible=True,
                    reason="Airline-caused cancellation: customer may choose a full refund to the original payment method, processed within 7 business days.",
                    source=f"{CANCELLATION_SOURCE}; {REFUND_SOURCE}",
                    requires_customer_choice=True,
                    scope="full refund to original payment method",
                ),
            ]
        )
        if customer.loyalty_tier in {"Gold", "Platinum"}:
            evaluation.decisions.append(
                PolicyDecision(
                    action="priority_rebooking",
                    status=DecisionStatus.INFORM,
                    eligible=True,
                    reason=f"{customer.loyalty_tier} status gives priority rebooking (first access to next-available seats) but no additional compensation beyond standard policy.",
                    source=LOYALTY_SOURCE,
                )
            )
        evaluation.ask = ["rebook_24h_or_full_refund"]
        return evaluation

    if booking.status == "DELAYED" and booking.delay_hours is not None:
        evaluation.disruption_type = "delay"
        evaluation.delay_hours = booking.delay_hours
        delay_items = delay_entitlements(booking.delay_hours)
        evaluation.decisions.extend(delay_items)
        evaluation.entitlements = [d.action for d in delay_items if d.eligible]
        if customer.loyalty_tier in {"Gold", "Platinum"}:
            evaluation.decisions.append(
                PolicyDecision(
                    action="priority_rebooking",
                    status=DecisionStatus.INFORM,
                    eligible=True,
                    reason=f"{customer.loyalty_tier} status gives priority rebooking but no additional compensation beyond standard policy.",
                    source=LOYALTY_SOURCE,
                )
            )
            evaluation.entitlements.append("priority_rebooking")
        return evaluation

    evaluation.disruption_type = booking.status.lower()
    evaluation.decisions.append(
        PolicyDecision(
            action="status_only",
            status=DecisionStatus.INFORM,
            eligible=False,
            reason="This leg is not an airline-caused cancellation or delay in the supplied booking data.",
            source="Booking / Transaction Data",
        )
    )
    return evaluation


def evaluate_policy(
    customer: Customer,
    booking: Booking | None,
    requests: list[ExtractedRequest],
    *,
    fare_difference_inr: int | None = None,
    legal_or_formal: bool = False,
    frustration_category: FrustrationCategory | None = None,
) -> PolicyEvaluation:
    conversation_only = bool(requests) and all(
        request.type in {RequestType.HELP_QUESTION, RequestType.BOOKING_ASSIST}
        for request in requests
    )
    if conversation_only or booking is None:
        evaluation = PolicyEvaluation()
        if booking:
            evaluation.disruption_type = booking.status.lower()
    else:
        evaluation = _baseline(customer, booking)

    if legal_or_formal:
        append_decision(
            evaluation,
            PolicyDecision(
                action="legal_or_formal",
                status=DecisionStatus.ESCALATE,
                eligible=False,
                reason="Threats of legal action or formal complaints must be escalated immediately to a human agent.",
                source=AUTHORITY_SOURCE,
                escalation_reason=EscalationReason.LEGAL_OR_FORMAL,
            ),
        )

    if not requests and not legal_or_formal:
        if evaluation.disruption_type == "cancellation" and "rebook_24h_or_full_refund" in evaluation.ask:
            evaluation.missing_slots.append("rebook_or_refund_choice")
        evaluation.offered_actions = offered_actions(evaluation, frustration_category)
        return evaluation

    for request in requests:
        handler = PolicyHandlerFactory.create(request.type)
        handler.apply(evaluation, customer, booking, request, fare_difference_inr)

    if any(d.action == "refund_original" and d.status == DecisionStatus.ALLOW for d in evaluation.decisions):
        for d in evaluation.decisions:
            if d.action == "rebook_24h" and d.status == DecisionStatus.ASK:
                d.status = DecisionStatus.INFORM
                d.reason = "Free 24-hour rebooking remains an available alternative; the customer asked for a refund on this turn."
        evaluation.ask = [a for a in evaluation.ask if a not in {"rebook_24h", "rebook_24h_or_full_refund"}]
        evaluation.missing_slots = [s for s in evaluation.missing_slots if s != "rebook_or_refund_choice"]
    if any(d.action == "rebook_24h" and d.status == DecisionStatus.ALLOW for d in evaluation.decisions):
        for d in evaluation.decisions:
            if d.action == "refund_original" and d.status == DecisionStatus.ASK:
                d.status = DecisionStatus.INFORM
                d.reason = "A full refund remains an available alternative; the customer asked to rebook on this turn."
        evaluation.ask = [a for a in evaluation.ask if a not in {"refund_original", "rebook_24h_or_full_refund"}]
        evaluation.missing_slots = [s for s in evaluation.missing_slots if s != "rebook_or_refund_choice"]

    # Last, so exclusivity and ordering see the final decision set. Frustration
    # reaches this line and no other in the engine.
    evaluation.offered_actions = offered_actions(evaluation, frustration_category)
    return evaluation
