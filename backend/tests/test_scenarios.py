from uuid import uuid4

from agent.loop import handle_chat


def test_priya_scenario_chat():
    sid = str(uuid4())
    first = handle_chat(sid, "My flight got cancelled and no one told me anything!", "CUST-PRIYA")
    assert first.session["identified"] is True
    assert any(e["action"] == "rebook_24h" for e in first.eligibility)
    second = handle_chat(
        sid,
        "I'm furious. I want a full cash refund plus a free upgrade to business class on my return for the trouble.",
    )
    actions = {e["action"]: e["status"] for e in second.eligibility}
    assert actions["refund_original"] == "ALLOW"
    assert actions["business_upgrade"] == "ESCALATE"
    assert "2000" not in str(second.context_packet)
    assert second.escalation is not None


def test_arvind_scenario_chat():
    sid = str(uuid4())
    res = handle_chat(
        sid,
        "This delay will make me miss my meeting. I want hotel accommodation since it's been such a long delay.",
        "CUST-ARVIND",
    )
    actions = {e["action"]: e["status"] for e in res.eligibility}
    assert actions["hotel_delayed_hours"] == "DENY"
    entitlements = res.context_packet["policy_decision"]["entitlements"]
    assert "meal_voucher" in entitlements
    assert "lounge" in entitlements


def test_meher_scenario_chat():
    sid = str(uuid4())
    res = handle_chat(
        sid,
        "I want a full night hotel stay and move me to a different higher-fare flight. The fare difference is ₹2000.",
        "CUST-MEHER",
    )
    actions = {e["action"]: e["status"] for e in res.eligibility}
    assert actions["hotel_full_night"] == "DENY"
    assert actions["hotel_delayed_hours"] == "ALLOW"
    assert actions["fare_waiver"] == "ESCALATE"
    assert res.context_packet["scenario_fixture"]["fare_difference_inr"] == 2000
    assert res.escalation is not None
