from models.schemas import DecisionStatus, PolicyDecision
from policy.handlers.base import PolicyHandler
from policy.ops import DELAY_SOURCE, append_decision, find_decision


class MealVoucherHandler(PolicyHandler):
    def apply(self, evaluation, customer, booking, request, fare_difference_inr=None) -> None:
        existing = find_decision(evaluation, "meal_voucher")
        if existing and existing.eligible:
            existing.status = DecisionStatus.ALLOW
            evaluation.execute.append("meal_voucher")
        else:
            append_decision(
                evaluation,
                PolicyDecision(
                    action="meal_voucher",
                    status=DecisionStatus.DENY,
                    eligible=False,
                    reason="Meal voucher is not established for this disruption under the Delay Compensation Rule.",
                    source=DELAY_SOURCE,
                ),
            )


class LoungeHandler(PolicyHandler):
    def apply(self, evaluation, customer, booking, request, fare_difference_inr=None) -> None:
        existing = find_decision(evaluation, "lounge")
        if existing and existing.eligible:
            existing.status = DecisionStatus.ALLOW
            evaluation.execute.append("lounge")
        else:
            append_decision(
                evaluation,
                PolicyDecision(
                    action="lounge",
                    status=DecisionStatus.DENY,
                    eligible=False,
                    reason="Lounge access applies when delay is more than 3 hours. This booking does not qualify.",
                    source=DELAY_SOURCE,
                ),
            )


class HotelHoursHandler(PolicyHandler):
    def apply(self, evaluation, customer, booking, request, fare_difference_inr=None) -> None:
        hotel = find_decision(evaluation, "hotel_delayed_hours")
        if hotel and hotel.eligible:
            hotel.status = DecisionStatus.ALLOW
            evaluation.execute.append("hotel_delayed_hours")
        else:
            append_decision(
                evaluation,
                PolicyDecision(
                    action="hotel_delayed_hours",
                    status=DecisionStatus.DENY,
                    eligible=False,
                    reason="Hotel accommodation is only established when delay is more than 5 hours, and then only for delayed hours.",
                    source=DELAY_SOURCE,
                ),
            )


class HotelFullNightHandler(PolicyHandler):
    def apply(self, evaluation, customer, booking, request, fare_difference_inr=None) -> None:
        hotel = find_decision(evaluation, "hotel_delayed_hours")
        qualifies = bool(hotel and hotel.eligible)
        append_decision(
            evaluation,
            PolicyDecision(
                action="hotel_full_night",
                status=DecisionStatus.DENY,
                eligible=False,
                reason="Hotel accommodation covers only the delayed hours. It does not cover a full night's stay."
                + (" Delayed-hours hotel remains available." if qualifies else " This delay also does not meet the more-than-5-hours hotel threshold."),
                source=DELAY_SOURCE,
            ),
        )
        if qualifies and hotel:
            hotel.status = DecisionStatus.ALLOW
            if "hotel_delayed_hours" not in evaluation.execute:
                evaluation.execute.append("hotel_delayed_hours")
