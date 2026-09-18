from models.schemas import DecisionStatus, PolicyDecision
from policy.handlers.base import PolicyHandler
from policy.ops import AUTHORITY_SOURCE, LOYALTY_SOURCE, append_decision


class BusinessUpgradeHandler(PolicyHandler):
    def apply(self, evaluation, customer, booking, request, fare_difference_inr=None) -> None:
        append_decision(
            evaluation,
            PolicyDecision(
                action="business_upgrade",
                status=DecisionStatus.ESCALATE,
                eligible=False,
                reason="No supplied policy allows a free business-class upgrade. Unknown is not allowed. Gold/Platinum status does not add compensation. Escalate as compensation beyond stated policy.",
                source=f"{LOYALTY_SOURCE}; {AUTHORITY_SOURCE}",
            ),
        )


class CompensationBeyondPolicyHandler(PolicyHandler):
    def apply(self, evaluation, customer, booking, request, fare_difference_inr=None) -> None:
        append_decision(
            evaluation,
            PolicyDecision(
                action="compensation_beyond_policy",
                status=DecisionStatus.ESCALATE,
                eligible=False,
                reason="Approving compensation beyond stated policy amounts must be escalated.",
                source=AUTHORITY_SOURCE,
            ),
        )


class NonAirlineExceptionHandler(PolicyHandler):
    def apply(self, evaluation, customer, booking, request, fare_difference_inr=None) -> None:
        append_decision(
            evaluation,
            PolicyDecision(
                action="non_airline_exception",
                status=DecisionStatus.ESCALATE,
                eligible=False,
                reason="Exceptions for non-airline-caused disruptions must be escalated.",
                source=AUTHORITY_SOURCE,
            ),
        )


class LegalNoOpHandler(PolicyHandler):
    def apply(self, evaluation, customer, booking, request, fare_difference_inr=None) -> None:
        return
