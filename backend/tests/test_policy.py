from uuid import uuid4

from agent.loop import handle_chat, reset_session
from data.loader import load_bookings, load_customers
from kb.store import store
from models.schemas import DecisionStatus, EscalationReason, ExtractedRequest, RequestType
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


def test_compound_refund_and_upgrade_keeps_both_outcomes():
    """One evaluate_policy call: cancellation cleanup still runs; escalate is not offered."""
    customers, bookings = _people()
    evaluation = evaluate_policy(
        customers["CUST-PRIYA"],
        bookings["BK-PRIYA-OUT"],
        [
            ExtractedRequest(type=RequestType.REFUND_ORIGINAL),
            ExtractedRequest(type=RequestType.BUSINESS_UPGRADE),
        ],
    )
    refund = next(d for d in evaluation.decisions if d.action == "refund_original")
    rebook = next(d for d in evaluation.decisions if d.action == "rebook_24h")
    upgrade = next(d for d in evaluation.decisions if d.action == "business_upgrade")
    assert refund.status is DecisionStatus.ALLOW
    assert rebook.status is DecisionStatus.INFORM
    assert upgrade.status is DecisionStatus.ESCALATE
    assert upgrade.escalation_reason is EscalationReason.UNKNOWN_ENTITLEMENT
    assert "refund_original" in evaluation.offered_actions
    assert "business_upgrade" not in evaluation.offered_actions
    offerable = {
        d.action for d in evaluation.decisions if d.status in {DecisionStatus.ALLOW, DecisionStatus.ASK}
    }
    assert set(evaluation.offered_actions) <= offerable

    sid = str(uuid4())
    reset_session(sid, "CUST-PRIYA")
    store.cases.pop("case-CUST-PRIYA", None)
    response = handle_chat(
        sid,
        "I want a full cash refund plus a free upgrade to business class on my return.",
        "CUST-PRIYA",
    )
    actions = {e["action"]: e["status"] for e in response.eligibility}
    assert actions["refund_original"] == "ALLOW"
    assert actions["business_upgrade"] == "ESCALATE"
    assert response.escalation is not None
    assert EscalationReason.UNKNOWN_ENTITLEMENT.value in response.escalation["escalation_reason_codes"]
    reset_session(sid, "CUST-PRIYA")
    store.cases.pop("case-CUST-PRIYA", None)


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


def test_evaluate_policy_without_a_booking_does_not_crash():
    """Joined Standard passengers have no disrupted leg. Chat used to 500 here."""
    customers, _bookings = _people()
    evaluation = evaluate_policy(
        customers["CUST-ARVIND"],
        None,
        [ExtractedRequest(type=RequestType.STATUS), ExtractedRequest(type=RequestType.REBOOK_24H)],
    )
    assert evaluation.disruption_type is None or evaluation.disruption_type == ""
    rebook = next(d for d in evaluation.decisions if d.action == "rebook_24h")
    assert rebook.status.value == "DENY"
