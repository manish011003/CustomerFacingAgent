from models.schemas import DecisionStatus, PolicyDecision, PolicyEvaluation

CANCELLATION_SOURCE = "Cancellation Rebooking Rule"
DELAY_SOURCE = "Delay Compensation Rule"
REFUND_SOURCE = "Refund Processing Rule"
FARE_SOURCE = "Fare Difference Rule"
LOYALTY_SOURCE = "Loyalty Tier Rule"
AUTHORITY_SOURCE = "Allowed vs. Prohibited Actions"
HELP_SOURCE = "Passenger Help Guide"
FARE_WAIVER_LIMIT_INR = 1500

# Turns that are conversation, not entitlements. They skip disruption baseline offers.
CONVERSATION_TYPES = frozenset(
    {
        "general_help",
        "booking_assist",
        "help_question",
    }
)


def find_decision(evaluation: PolicyEvaluation, action: str) -> PolicyDecision | None:
    for decision in evaluation.decisions:
        if decision.action == action:
            return decision
    return None


def append_decision(evaluation: PolicyEvaluation, decision: PolicyDecision) -> None:
    evaluation.decisions = [d for d in evaluation.decisions if d.action != decision.action]
    evaluation.decisions.append(decision)
    if decision.status == DecisionStatus.ALLOW:
        evaluation.execute.append(decision.action)
    elif decision.status == DecisionStatus.DENY:
        evaluation.deny.append(decision.action)
    elif decision.status == DecisionStatus.ESCALATE:
        evaluation.escalate.append(decision.action)
    elif decision.status == DecisionStatus.ASK:
        evaluation.ask.append(decision.action)
