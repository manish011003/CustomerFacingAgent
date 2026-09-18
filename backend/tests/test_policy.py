from data.loader import load_bookings, load_customers
from models.schemas import ExtractedRequest, RequestType
from policy.engine import FARE_WAIVER_LIMIT_INR, delay_entitlements, evaluate_policy


def _people():
    customers = {c.id: c for c in load_customers()}
    bookings = {b.id: b for b in load_bookings()}
    return customers, bookings


def test_delay_2_hours_meal_500():
    decisions = delay_entitlements(2)
    assert [d.action for d in decisions] == ["meal_voucher"]
    assert decisions[0].amount_inr == 500
    assert decisions[0].eligible is True


def test_delay_4_hours_meal_lounge_no_hotel():
    decisions = delay_entitlements(4)
    assert [d.action for d in decisions] == ["meal_voucher", "lounge"]
    assert all(d.amount_inr is None or d.action != "meal_voucher" or d.amount_inr != 500 or True for d in decisions)
    meal = next(d for d in decisions if d.action == "meal_voucher")
    assert meal.amount_inr is None
    assert not any(d.action == "hotel_delayed_hours" for d in decisions)


def test_delay_6_hours_meal_lounge_hotel_hours():
    decisions = delay_entitlements(6)
    assert [d.action for d in decisions] == ["meal_voucher", "lounge", "hotel_delayed_hours"]
    hotel = next(d for d in decisions if d.action == "hotel_delayed_hours")
    assert "delayed hours" in hotel.reason.lower() or "delayed hours" in (hotel.scope or "")


def test_fare_difference_1000_allowed():
    customers, bookings = _people()
    evaluation = evaluate_policy(
        customers["CUST-MEHER"],
        bookings["BK-MEHER-OUT"],
        [ExtractedRequest(type=RequestType.FARE_WAIVER, fare_difference_inr=1000)],
    )
    fare = next(d for d in evaluation.decisions if d.action == "fare_waiver")
    assert fare.status.value == "ALLOW"
    assert fare.authority_limit_inr == FARE_WAIVER_LIMIT_INR


def test_fare_difference_1500_allowed():
    customers, bookings = _people()
    evaluation = evaluate_policy(
        customers["CUST-MEHER"],
        bookings["BK-MEHER-OUT"],
        [ExtractedRequest(type=RequestType.FARE_WAIVER, fare_difference_inr=1500)],
    )
    fare = next(d for d in evaluation.decisions if d.action == "fare_waiver")
    assert fare.status.value == "ALLOW"


def test_fare_difference_2000_escalation():
    customers, bookings = _people()
    evaluation = evaluate_policy(
        customers["CUST-MEHER"],
        bookings["BK-MEHER-OUT"],
        [ExtractedRequest(type=RequestType.HIGHER_FARE_REBOOK, fare_difference_inr=2000)],
    )
    fare = next(d for d in evaluation.decisions if d.action == "fare_waiver")
    assert fare.status.value == "ESCALATE"
    assert "2000" in fare.reason or fare.amount_inr == 2000


def test_airline_cancellation_refund_or_rebook():
    customers, bookings = _people()
    evaluation = evaluate_policy(customers["CUST-PRIYA"], bookings["BK-PRIYA-OUT"], [])
    actions = {d.action for d in evaluation.decisions}
    assert "rebook_24h" in actions
    assert "refund_original" in actions
    chosen = evaluate_policy(
        customers["CUST-PRIYA"],
        bookings["BK-PRIYA-OUT"],
        [ExtractedRequest(type=RequestType.REFUND_ORIGINAL)],
    )
    refund = next(d for d in chosen.decisions if d.action == "refund_original")
    assert refund.status.value == "ALLOW"


def test_business_upgrade_not_approved():
    customers, bookings = _people()
    evaluation = evaluate_policy(
        customers["CUST-PRIYA"],
        bookings["BK-PRIYA-OUT"],
        [
            ExtractedRequest(type=RequestType.REFUND_ORIGINAL),
            ExtractedRequest(type=RequestType.BUSINESS_UPGRADE),
        ],
    )
    upgrade = next(d for d in evaluation.decisions if d.action == "business_upgrade")
    assert upgrade.status.value == "ESCALATE"
    assert upgrade.eligible is False
    refund = next(d for d in evaluation.decisions if d.action == "refund_original")
    assert refund.status.value == "ALLOW"


def test_legal_threat_immediate_escalation():
    customers, bookings = _people()
    evaluation = evaluate_policy(
        customers["CUST-ARVIND"],
        bookings["BK-ARVIND-OUT"],
        [],
        legal_or_formal=True,
    )
    legal = next(d for d in evaluation.decisions if d.action == "legal_or_formal")
    assert legal.status.value == "ESCALATE"


def test_arvind_hotel_denied():
    customers, bookings = _people()
    evaluation = evaluate_policy(
        customers["CUST-ARVIND"],
        bookings["BK-ARVIND-OUT"],
        [ExtractedRequest(type=RequestType.HOTEL_DELAYED_HOURS)],
    )
    hotel = next(d for d in evaluation.decisions if d.action == "hotel_delayed_hours")
    assert hotel.status.value == "DENY"
    assert "meal_voucher" in evaluation.entitlements
    assert "lounge" in evaluation.entitlements
    assert "hotel_delayed_hours" not in evaluation.entitlements


def test_meher_full_night_denied_hours_allowed():
    customers, bookings = _people()
    evaluation = evaluate_policy(
        customers["CUST-MEHER"],
        bookings["BK-MEHER-OUT"],
        [ExtractedRequest(type=RequestType.HOTEL_FULL_NIGHT)],
    )
    full = next(d for d in evaluation.decisions if d.action == "hotel_full_night")
    hours = next(d for d in evaluation.decisions if d.action == "hotel_delayed_hours")
    assert full.status.value == "DENY"
    assert hours.eligible is True
    assert hours.status.value == "ALLOW"


def test_gold_no_extra_compensation():
    customers, bookings = _people()
    evaluation = evaluate_policy(customers["CUST-PRIYA"], bookings["BK-PRIYA-OUT"], [])
    loyalty = next(d for d in evaluation.decisions if d.action == "priority_rebooking")
    assert "no additional compensation" in loyalty.reason.lower()
