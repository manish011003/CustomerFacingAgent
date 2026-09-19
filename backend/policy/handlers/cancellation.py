from models.schemas import DecisionStatus, EscalationReason, PolicyDecision
from policy.handlers.base import PolicyHandler
from policy.ops import CANCELLATION_SOURCE, REFUND_SOURCE, AUTHORITY_SOURCE, append_decision


class RebookHandler(PolicyHandler):
    def apply(self, evaluation, customer, booking, request, fare_difference_inr=None) -> None:
        if booking and booking.status == "CANCELLED" and booking.airline_caused:
            append_decision(
                evaluation,
                PolicyDecision(
                    action="rebook_24h",
                    status=DecisionStatus.ALLOW,
                    eligible=True,
                    reason="Airline-caused cancellation: free rebooking on the next available flight within 24 hours is allowed. Simulated without inventing a flight number.",
                    source=CANCELLATION_SOURCE,
                    scope="next available within 24 hours (inventory not established)",
                ),
            )
        else:
            append_decision(
                evaluation,
                PolicyDecision(
                    action="rebook_24h",
                    status=DecisionStatus.DENY,
                    eligible=False,
                    reason="Free 24-hour rebooking is established only for airline-caused cancellations.",
                    source=CANCELLATION_SOURCE,
                ),
            )


class RefundOriginalHandler(PolicyHandler):
    def apply(self, evaluation, customer, booking, request, fare_difference_inr=None) -> None:
        if booking and booking.status == "CANCELLED" and booking.airline_caused:
            append_decision(
                evaluation,
                PolicyDecision(
                    action="refund_original",
                    status=DecisionStatus.ALLOW,
                    eligible=True,
                    reason="Airline-caused cancellation: full refund to the original payment method, processed within 7 business days.",
                    source=f"{CANCELLATION_SOURCE}; {REFUND_SOURCE}",
                ),
            )
        else:
            append_decision(
                evaluation,
                PolicyDecision(
                    action="refund_original",
                    status=DecisionStatus.DENY,
                    eligible=False,
                    reason="Full refund processing rule is established for airline-caused cancellations only.",
                    source=REFUND_SOURCE,
                ),
            )


class RefundOtherMethodHandler(PolicyHandler):
    def apply(self, evaluation, customer, booking, request, fare_difference_inr=None) -> None:
        append_decision(
            evaluation,
            PolicyDecision(
                action="refund_other_method",
                status=DecisionStatus.ESCALATE,
                eligible=False,
                reason="Refunds to a payment method different from the original must be escalated.",
                source=f"{REFUND_SOURCE}; {AUTHORITY_SOURCE}",
                escalation_reason=EscalationReason.REFUND_ALTERNATE_METHOD,
            ),
        )
