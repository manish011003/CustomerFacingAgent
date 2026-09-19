from uuid import uuid4

from agent.loop import handle_chat, reset_session
from kb.store import store
from models.schemas import EscalationReason
from products.knowledge.json_store import JsonKnowledgeStore

# Priya's scripted "I'm furious..." line only drives reply tone. Distress
# escalation needs stranded / helplessness / punctuation that the classifier
# actually scores — and confidence ≥ 0.85.
PRIYA_DISTRESS_UPGRADE = (
    "I'm stranded and nobody is helping me!! I want a full cash refund "
    "plus a free upgrade to business class on my return for the trouble."
)
PRIYA_STACKED = (
    PRIYA_DISTRESS_UPGRADE + " I'll be filing a formal complaint."
)


def _reset_priya(sid: str) -> None:
    reset_session(sid, "CUST-PRIYA")
    store.cases.pop("case-CUST-PRIYA", None)


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


def test_priya_distress_and_unknown_entitlement_are_both_on_the_case():
    """Duty-of-care and the upgrade authority limit are independent codes."""
    sid = str(uuid4())
    _reset_priya(sid)
    response = handle_chat(sid, PRIYA_DISTRESS_UPGRADE, "CUST-PRIYA")
    actions = {e["action"]: e["status"] for e in response.eligibility}
    assert actions["refund_original"] in {"ALLOW", "ASK"}
    assert actions["business_upgrade"] == "ESCALATE"

    codes = response.escalation["escalation_reason_codes"]
    assert codes.count(EscalationReason.UNKNOWN_ENTITLEMENT.value) == 1
    assert codes.count(EscalationReason.SEVERE_CUSTOMER_DISTRESS.value) == 1
    assert EscalationReason.UNKNOWN_ENTITLEMENT.value in response.audit_event["escalation_reasons"]
    assert EscalationReason.SEVERE_CUSTOMER_DISTRESS.value in response.audit_event["escalation_reasons"]
    assert response.audit_event["contained"] is False

    escalate_actions = [
        d["action"]
        for d in response.escalation["policy_decisions"]
        if d.get("status") == "ESCALATE"
    ]
    assert escalate_actions == ["business_upgrade"]
    _reset_priya(sid)


def test_priya_legal_distress_and_upgrade_stack_three_distinct_reasons():
    """Legal detection must not gate distress; the engine still adds the upgrade."""
    sid = str(uuid4())
    _reset_priya(sid)
    response = handle_chat(sid, PRIYA_STACKED, "CUST-PRIYA")
    codes = response.escalation["escalation_reason_codes"]
    expected = {
        EscalationReason.LEGAL_OR_FORMAL.value,
        EscalationReason.SEVERE_CUSTOMER_DISTRESS.value,
        EscalationReason.UNKNOWN_ENTITLEMENT.value,
    }
    assert expected <= set(codes)
    assert len(codes) == len(set(codes))
    assert response.audit_event["contained"] is False
    for code in expected:
        assert response.audit_event["escalation_reasons"].count(code) == 1

    escalate_actions = {
        d["action"]
        for d in response.escalation["policy_decisions"]
        if d.get("status") == "ESCALATE"
    }
    assert escalate_actions == {"legal_or_formal", "business_upgrade"}

    kb = JsonKnowledgeStore()
    kb.append_event(
        {
            "kind": "turn",
            "contained": False,
            "escalation_reasons": list(expected),
        }
    )
    report = kb.containment()
    assert report["distress_escalations"] == 1
    assert report["authority_escalations"] == 2
    _reset_priya(sid)
