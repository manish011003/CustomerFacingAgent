from models.schemas import DecisionStatus, EscalationReason, PolicyDecision
from policy.handlers.base import PolicyHandler
from policy.ops import FARE_SOURCE, FARE_WAIVER_LIMIT_INR, append_decision


class FareWaiverHandler(PolicyHandler):
    def apply(self, evaluation, customer, booking, request, fare_difference_inr=None) -> None:
        amount = request.fare_difference_inr if request.fare_difference_inr is not None else fare_difference_inr
        if amount is None:
            evaluation.missing_slots.append("fare_difference_inr")
            append_decision(
                evaluation,
                PolicyDecision(
                    action="fare_waiver",
                    status=DecisionStatus.ASK,
                    eligible=False,
                    reason="A voluntary higher-fare rebook requires a fare difference amount. None is established for this turn.",
                    source=FARE_SOURCE,
                    authority_limit_inr=FARE_WAIVER_LIMIT_INR,
                ),
            )
            return
        if amount > FARE_WAIVER_LIMIT_INR:
            append_decision(
                evaluation,
                PolicyDecision(
                    action="fare_waiver",
                    status=DecisionStatus.ESCALATE,
                    eligible=False,
                    reason=f"Fare difference ₹{amount} is above the ₹{FARE_WAIVER_LIMIT_INR} agent waiver limit. Supervisor approval is required.",
                    source=FARE_SOURCE,
                    amount_inr=amount,
                    authority_limit_inr=FARE_WAIVER_LIMIT_INR,
                    escalation_reason=EscalationReason.FARE_WAIVER_ABOVE_LIMIT,
                ),
            )
        else:
            append_decision(
                evaluation,
                PolicyDecision(
                    action="fare_waiver",
                    status=DecisionStatus.ALLOW,
                    eligible=True,
                    reason=f"Fare difference ₹{amount} is not above the ₹{FARE_WAIVER_LIMIT_INR} agent waiver limit.",
                    source=FARE_SOURCE,
                    amount_inr=amount,
                    authority_limit_inr=FARE_WAIVER_LIMIT_INR,
                ),
            )
