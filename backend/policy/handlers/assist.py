"""Informational handlers. They never grant money or execute simulated tools."""

from models.schemas import DecisionStatus, PolicyDecision
from policy.handlers.base import PolicyHandler
from policy.ops import HELP_SOURCE, append_decision


class BookingAssistHandler(PolicyHandler):
    def apply(self, evaluation, customer, booking, request, fare_difference_inr=None) -> None:
        from agent.router import SLOT_KEYS, missing_slots, parse_notes

        filled = parse_notes(request.notes)
        missing = missing_slots({key: str(filled.get(key) or "") for key in SLOT_KEYS})
        if missing:
            evaluation.missing_slots.extend(slot for slot in missing if slot not in evaluation.missing_slots)
            asked = ", ".join(missing)
            append_decision(
                evaluation,
                PolicyDecision(
                    action="booking_assist",
                    status=DecisionStatus.ASK,
                    eligible=True,
                    reason=(
                        "I can help plan a new booking. I still need "
                        f"{asked}. I will not invent a flight number or fare."
                    ),
                    source=HELP_SOURCE,
                    requires_customer_choice=True,
                    scope="new booking (no inventory)",
                ),
            )
            return

        from products.inventory import suggest_flight

        evaluation.suggested_flight = suggest_flight(
            origin=str(filled.get("origin") or "") or None,
            destination=str(filled.get("destination") or "") or None,
            date=str(filled.get("date") or "") or None,
            passengers=str(filled.get("passengers") or "") or None,
        )
        summary = (
            f"{filled.get('origin')} → {filled.get('destination')} on {filled.get('date')} "
            f"for {filled.get('passengers')} passenger(s)"
        )
        append_decision(
            evaluation,
            PolicyDecision(
                action="booking_assist",
                status=DecisionStatus.INFORM,
                eligible=True,
                reason=(
                    f"I have your request for {summary}. This prototype has no live inventory, "
                    "so I will not invent a flight number or fare. A supervisor can ticket it if you want."
                ),
                source=HELP_SOURCE,
                scope=summary,
            ),
        )


class HelpQuestionHandler(PolicyHandler):
    def apply(self, evaluation, customer, booking, request, fare_difference_inr=None) -> None:
        append_decision(
            evaluation,
            PolicyDecision(
                action="help_question",
                status=DecisionStatus.INFORM,
                eligible=True,
                reason=(
                    "I can help with booking a trip, check-in, baggage, and seats. "
                    "Those answers come from the passenger help guide — they are not extra compensation. "
                    "If you want money, a hotel night, or an upgrade not in policy, that still escalates."
                ),
                source=HELP_SOURCE,
            ),
        )
