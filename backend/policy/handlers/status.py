from models.schemas import Booking, Customer, DecisionStatus, ExtractedRequest, PolicyDecision, PolicyEvaluation
from policy.handlers.base import PolicyHandler
from policy.ops import AUTHORITY_SOURCE, append_decision


class StatusHandler(PolicyHandler):
    def apply(self, evaluation, customer, booking, request, fare_difference_inr=None) -> None:
        append_decision(
            evaluation,
            PolicyDecision(
                action="status",
                status=DecisionStatus.INFORM,
                eligible=True,
                reason="Agent may provide the customer's own booking and flight status information.",
                source=AUTHORITY_SOURCE,
            ),
        )
