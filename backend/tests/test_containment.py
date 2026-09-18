"""Containment: the metric that answers how much work needed no human.

Two layers are tested separately. The escalation taxonomy is checked against the
policy engine directly, and the aggregation arithmetic is checked against a
fresh store seeded with synthetic turns, so neither depends on how many other
tests have already written to the process-wide store.
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from agent.loop import handle_chat
from kb.store import store
from models.schemas import DecisionStatus, EscalationReason, ExtractedRequest, RequestType
from policy.engine import evaluate_policy
from products.knowledge.base import _percentile
from products.knowledge.json_store import JsonKnowledgeStore

TELEMETRY_FIELDS = [
    "latency_ms",
    "contained",
    "escalation_reasons",
    "decisions",
    "grounded_decisions",
    "grounded",
    "degraded",
    "provider",
    "llm_calls",
    "prompt_tokens",
    "completion_tokens",
    "est_cost_usd",
]


# --- the taxonomy is complete ----------------------------------------------


def test_every_escalation_carries_a_reason_code():
    """Guards new handlers: an ESCALATE with no code would vanish from the breakdown."""
    uncoded = []
    for customer_id in ("CUST-PRIYA", "CUST-ARVIND", "CUST-MEHER"):
        customer = store.identify(customer_id=customer_id)
        booking = store.affected_booking(customer.id)
        if not booking:
            continue
        for request_type in RequestType:
            for legal in (False, True):
                evaluation = evaluate_policy(
                    customer,
                    booking,
                    [ExtractedRequest(type=request_type, fare_difference_inr=2000)],
                    fare_difference_inr=2000,
                    legal_or_formal=legal,
                )
                for decision in evaluation.decisions:
                    if decision.status == DecisionStatus.ESCALATE and decision.escalation_reason is None:
                        uncoded.append((customer_id, request_type.value, decision.action))
    assert uncoded == []


@pytest.mark.parametrize(
    "customer_id,request_type,action,expected",
    [
        (
            "CUST-PRIYA",
            RequestType.BUSINESS_UPGRADE,
            "business_upgrade",
            EscalationReason.UNKNOWN_ENTITLEMENT,
        ),
        (
            "CUST-MEHER",
            RequestType.FARE_WAIVER,
            "fare_waiver",
            EscalationReason.FARE_WAIVER_ABOVE_LIMIT,
        ),
        (
            "CUST-PRIYA",
            RequestType.REFUND_OTHER_METHOD,
            "refund_other_method",
            EscalationReason.REFUND_ALTERNATE_METHOD,
        ),
        (
            "CUST-ARVIND",
            RequestType.COMPENSATION_BEYOND_POLICY,
            "compensation_beyond_policy",
            EscalationReason.COMPENSATION_BEYOND_POLICY,
        ),
        (
            "CUST-ARVIND",
            RequestType.NON_AIRLINE_EXCEPTION,
            "non_airline_exception",
            EscalationReason.NON_AIRLINE_CAUSE,
        ),
    ],
)
def test_each_authority_boundary_maps_to_its_own_reason(customer_id, request_type, action, expected):
    customer = store.identify(customer_id=customer_id)
    booking = store.affected_booking(customer.id)
    evaluation = evaluate_policy(
        customer,
        booking,
        [ExtractedRequest(type=request_type, fare_difference_inr=2000)],
        fare_difference_inr=2000,
    )
    decision = next(d for d in evaluation.decisions if d.action == action)
    assert decision.status == DecisionStatus.ESCALATE
    assert decision.escalation_reason == expected


def test_legal_threat_is_its_own_reason():
    customer = store.identify(customer_id="CUST-MEHER")
    booking = store.affected_booking(customer.id)
    evaluation = evaluate_policy(customer, booking, [], legal_or_formal=True)
    decision = next(d for d in evaluation.decisions if d.action == "legal_or_formal")
    assert decision.escalation_reason == EscalationReason.LEGAL_OR_FORMAL


def test_a_reason_code_never_appears_without_an_escalation():
    """Allowed and denied outcomes must not carry an escalation cause."""
    customer = store.identify(customer_id="CUST-ARVIND")
    booking = store.affected_booking(customer.id)
    evaluation = evaluate_policy(
        customer,
        booking,
        [ExtractedRequest(type=t) for t in RequestType],
        fare_difference_inr=1000,
    )
    for decision in evaluation.decisions:
        if decision.status != DecisionStatus.ESCALATE:
            assert decision.escalation_reason is None, decision.action


# --- every turn is measured ------------------------------------------------


def test_turn_event_carries_the_full_telemetry_set():
    response = handle_chat(str(uuid4()), "What is the status of my flight?", "CUST-ARVIND")
    missing = [f for f in TELEMETRY_FIELDS if f not in response.audit_event]
    assert missing == []
    assert response.audit_event["latency_ms"] >= 0


def test_an_entitlement_turn_is_contained_and_fully_cited():
    response = handle_chat(
        str(uuid4()),
        "This delay will make me miss my meeting. I want hotel accommodation.",
        "CUST-ARVIND",
    )
    audit = response.audit_event
    assert audit["contained"] is True
    assert audit["escalation_reasons"] == []
    assert audit["decisions"] > 0
    # Every claim made to the passenger traces to a retrieved clause.
    assert audit["grounded_decisions"] == audit["decisions"]
    assert audit["grounded"] is True


def test_a_waiver_above_the_limit_reports_itself_as_escalated():
    response = handle_chat(
        str(uuid4()),
        "Move me to a higher-fare flight, the fare difference is ₹2000.",
        "CUST-MEHER",
    )
    audit = response.audit_event
    assert audit["contained"] is False
    assert EscalationReason.FARE_WAIVER_ABOVE_LIMIT.value in audit["escalation_reasons"]


def test_the_escalation_case_carries_both_prose_and_codes():
    response = handle_chat(
        str(uuid4()),
        "Move me to a higher-fare flight, the fare difference is ₹2000.",
        "CUST-MEHER",
    )
    assert response.escalation is not None
    # Prose for the supervisor, codes for the dashboard.
    assert response.escalation["escalation_reasons"]
    assert EscalationReason.FARE_WAIVER_ABOVE_LIMIT.value in response.escalation["escalation_reason_codes"]


def test_the_turn_trace_reports_the_measurement_to_the_reviewer():
    response = handle_chat(str(uuid4()), "Is my flight delayed?", "CUST-ARVIND")
    steps = {step["step"] for step in response.trace}
    assert "measure" in steps


def test_no_llm_key_means_no_spend():
    response = handle_chat(str(uuid4()), "Is my flight delayed?", "CUST-ARVIND")
    assert response.audit_event["llm_calls"] == 0
    assert response.audit_event["est_cost_usd"] == 0.0
    assert response.audit_event["provider"] == "none"
    # Nothing degraded, because nothing was attempted.
    assert response.audit_event["degraded"] is False


# --- the aggregation arithmetic --------------------------------------------


def fresh_store() -> JsonKnowledgeStore:
    return JsonKnowledgeStore()


def measured_turn(**overrides) -> dict:
    turn = {
        "kind": "turn",
        "contained": True,
        "decisions": 2,
        "grounded_decisions": 2,
        "latency_ms": 100,
        "est_cost_usd": 0.001,
        "llm_calls": 1,
        "prompt_tokens": 600,
        "completion_tokens": 100,
        "escalation_reasons": [],
        "degraded": False,
    }
    turn.update(overrides)
    return turn


def test_a_store_with_no_measured_turns_reports_zero_not_a_fake_rate():
    report = fresh_store().containment()
    assert report["turns"] == 0
    assert "containment_rate" not in report


def test_containment_rate_is_contained_over_measured():
    kb = fresh_store()
    for _ in range(3):
        kb.append_event(measured_turn())
    kb.append_event(
        measured_turn(contained=False, escalation_reasons=[EscalationReason.LEGAL_OR_FORMAL.value])
    )
    report = kb.containment()
    assert report["turns"] == 4
    assert report["contained_turns"] == 3
    assert report["escalated_turns"] == 1
    assert report["containment_rate"] == 0.75


def test_escalations_group_by_reason_and_sort_by_frequency():
    kb = fresh_store()
    for _ in range(2):
        kb.append_event(
            measured_turn(
                contained=False,
                escalation_reasons=[EscalationReason.FARE_WAIVER_ABOVE_LIMIT.value],
            )
        )
    kb.append_event(
        measured_turn(contained=False, escalation_reasons=[EscalationReason.LEGAL_OR_FORMAL.value])
    )
    by_reason = kb.containment()["escalations_by_reason"]
    assert by_reason == {"fare_waiver_above_limit": 2, "legal_or_formal": 1}
    assert list(by_reason)[0] == "fare_waiver_above_limit"


def test_grounding_coverage_counts_claims_not_turns():
    kb = fresh_store()
    kb.append_event(measured_turn(decisions=4, grounded_decisions=4))
    kb.append_event(measured_turn(decisions=4, grounded_decisions=2))
    report = kb.containment()
    assert report["decisions_claimed"] == 8
    assert report["decisions_cited"] == 6
    assert report["grounding_coverage"] == 0.75


def test_cost_is_reported_per_turn_and_per_contained_turn():
    kb = fresh_store()
    kb.append_event(measured_turn(est_cost_usd=0.002))
    kb.append_event(measured_turn(contained=False, est_cost_usd=0.002))
    report = kb.containment()
    assert report["est_spend_usd"] == 0.004
    assert report["est_cost_per_turn_usd"] == 0.002
    # Two turns of spend bought one resolution without a human.
    assert report["est_cost_per_contained_turn_usd"] == 0.004


def test_unmeasured_legacy_turns_cannot_inflate_the_rate():
    kb = fresh_store()
    kb.append_event({"kind": "turn", "message": "written before telemetry existed"})
    kb.append_event(measured_turn())
    assert kb.containment()["turns"] == 1


def test_analytics_summary_embeds_containment():
    assert "containment" in fresh_store().analytics()


def test_operations_metrics_come_from_cases():
    kb = fresh_store()
    kb.upsert_case(
        {
            "id": "case-a",
            "status": "resolved",
            "created_at": "2026-09-18T10:00:00+00:00",
            "resolved_at": "2026-09-18T10:05:00+00:00",
        }
    )
    kb.upsert_case({"id": "case-b", "status": "escalated"})
    kb.upsert_case({"id": "case-c", "status": "open"})
    ops = kb.operations()
    assert ops["total_cases"] == 3
    assert ops["resolved_cases"] == 1
    assert ops["escalated_cases"] == 1
    assert ops["open_cases"] == 1
    assert ops["resolution_rate"] == 0.3333
    assert ops["average_resolution_seconds"] == 300
    first = kb.get_case("case-a")["created_at"]
    kb.upsert_case({"id": "case-a", "status": "resolved", "note": "updated"})
    assert kb.get_case("case-a")["created_at"] == first
    assert "operations" in kb.analytics()


def test_percentile_uses_nearest_rank():
    ordered = [10, 20, 30, 40, 100]
    assert _percentile(ordered, 50) == 30
    assert _percentile(ordered, 95) == 100
    assert _percentile([], 95) is None
    assert _percentile([7], 95) == 7
