"""Frustration is a signal, and these tests are what keep it one.

Layered the same way `test_containment.py` is. The classifier is checked as a
pure function, the exclusivity rule against the policy engine directly, and the
aggregation arithmetic against a fresh store seeded with synthetic
observations — so none of it depends on what other tests already wrote to the
process-wide store.

The load-bearing assertions are the negative ones: no category, and no
confidence, may change a single eligibility outcome.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from agent import frustration as detector
from agent.loop import handle_chat
from agent.tools import TOOL_SCHEMAS, ToolRuntime
from data.loader import load_bookings, load_customers
from factories.onboarding_factory import OnboardingFactory
from factories.staff_factory import StaffFactory
from kb.store import store
from main import app
from models.schemas import (
    DecisionStatus,
    EscalationReason,
    ExtractedRequest,
    FrustrationAssessment,
    FrustrationCategory,
    RequestType,
    SessionMemory,
)
from policy.engine import evaluate_policy
from policy.exclusivity import offered_actions
from products.auth.staff import DEFAULT_STAFF_EMAIL, DEFAULT_STAFF_PASSWORD
from products.knowledge.json_store import JsonKnowledgeStore
from products.onboarding.self_service import SEED_PASSWORD

SCHEMA_KEYS = {"category", "confidence", "signals", "escalation_recommended"}

CALM = "What is my flight status?"
ANNOYED = "This is ridiculous."
DISTRESSED = (
    "I am STRANDED at the airport with my toddler and nobody is helping me. "
    "This is completely unacceptable!!"
)
HOSTILE = (
    "This is absolutely pathetic. I will never fly with you again and I am telling "
    "everyone on social media. Bloody useless."
)


def _people():
    return {c.id: c for c in load_customers()}, {b.id: b for b in load_bookings()}


def fresh_store() -> JsonKnowledgeStore:
    return JsonKnowledgeStore()


def observation(**overrides) -> FrustrationAssessment:
    payload = {
        "category": FrustrationCategory.FRUSTRATED,
        "confidence": 0.8,
        "signals": ["explicit_complaint"],
        "escalation_recommended": False,
        "low_confidence": False,
    }
    payload.update(overrides)
    return FrustrationAssessment(**payload)


# --- the classifier honours its contract -----------------------------------


@pytest.mark.parametrize("message", [CALM, ANNOYED, DISTRESSED, HOSTILE, "", "   "])
def test_every_classification_matches_the_declared_schema(message):
    assessment = detector.classify(message, SessionMemory(session_id="s"))
    payload = assessment.payload()
    assert set(payload) == SCHEMA_KEYS
    assert payload["category"] in {c.value for c in FrustrationCategory}
    assert isinstance(payload["confidence"], float)
    assert 0.0 <= payload["confidence"] <= 1.0
    assert isinstance(payload["signals"], list)
    assert all(isinstance(signal, str) and signal for signal in payload["signals"])
    assert isinstance(payload["escalation_recommended"], bool)


def test_audit_fields_never_reach_the_model():
    """`low_confidence` and `source` are for the store, not the prompt."""
    assessment = detector.classify(ANNOYED, SessionMemory(session_id="s"))
    assert assessment.low_confidence is True
    assert "low_confidence" not in assessment.payload()
    assert "source" not in assessment.payload()


@pytest.mark.parametrize("message", [CALM, ANNOYED, DISTRESSED, HOSTILE])
def test_the_same_input_always_produces_the_same_output(message):
    """No sampling, no clock, no model. CI must not need a retry."""
    session = SessionMemory(session_id="s")
    first = detector.classify(message, session).model_dump()
    for _ in range(25):
        assert detector.classify(message, session).model_dump() == first


def test_signal_order_is_canonical_not_insertion_order():
    assessment = detector.classify(DISTRESSED, SessionMemory(session_id="s"))
    ranked = [s for s in detector.SIGNAL_ORDER if s in assessment.signals]
    assert assessment.signals == ranked


def test_a_calm_question_is_neutral_with_no_signals():
    assessment = detector.classify(CALM, SessionMemory(session_id="s"))
    assert assessment.category is FrustrationCategory.NEUTRAL
    assert assessment.signals == []
    assert assessment.escalation_recommended is False


def test_distress_outranks_mere_hostility():
    """A stranded passenger with a child is a care case, not an angry one."""
    assert detector.classify(DISTRESSED, SessionMemory(session_id="s")).category is (
        FrustrationCategory.DISTRESSED
    )
    assert detector.classify(HOSTILE, SessionMemory(session_id="s")).category is (
        FrustrationCategory.HOSTILE
    )


def test_asking_the_same_thing_twice_is_itself_a_signal():
    """Repetition means the previous answer did not land, whatever words were used."""
    session = SessionMemory(session_id="s")
    first = detector.classify("Can I get a hotel for this delay?", session)
    assert "repeated_request" not in first.signals

    session.messages.append({"role": "user", "content": "Can I get a hotel for this delay?"})
    session.messages.append({"role": "assistant", "content": "Hotel cover needs a longer delay."})
    again = detector.classify("I am asking about the hotel again", session)
    assert "repeated_request" in again.signals


def test_shouting_needs_more_than_a_short_acronym():
    calm = detector.classify("What is my PNR?", SessionMemory(session_id="s"))
    assert "caps_lock" not in calm.signals
    shouted = detector.classify(
        "WHY HAS NOBODY TOLD ME ANYTHING ABOUT THIS FLIGHT", SessionMemory(session_id="s")
    )
    assert "caps_lock" in shouted.signals


def test_the_legal_detector_is_shared_not_duplicated():
    """One regex, so the escalation rule and the signal cannot disagree."""
    from products.extractors.heuristic import HeuristicExtractor

    threat = "I will be speaking to my lawyer about this."
    assert detector.detect_legal_or_formal(threat) is True
    assert HeuristicExtractor().extract(threat).legal_or_formal is True
    assert "legal_language" in detector.classify(threat, SessionMemory(session_id="s")).signals
    assert ToolRuntime(
        session=SessionMemory(session_id="s"), customer=None, utterance=threat
    ).legal_or_formal is True


# --- the confidence gate ----------------------------------------------------


def test_confidence_at_or_above_the_threshold_is_counted(monkeypatch):
    monkeypatch.setattr(detector, "KB_AUTO_STORE_THRESHOLD", 0.75)
    assert detector.is_low_confidence(0.75) is False
    assert detector.is_low_confidence(0.9) is False
    assert detector.is_low_confidence(0.74) is True


def test_a_confident_observation_is_stored_and_aggregated():
    kb = fresh_store()
    kb.append_frustration(
        observation(confidence=0.9), session_id="s1", customer_id="CUST-ARVIND"
    )
    report = kb.frustration()
    assert report["by_category"] == {"frustrated": 1}
    assert report["counted_observations"] == 1
    assert report["low_confidence_by_category"] == {}
    assert report["low_confidence_observations"] == 0


def test_a_low_confidence_observation_is_logged_but_excluded_from_primary_counts():
    kb = fresh_store()
    kb.append_frustration(
        observation(confidence=0.4, low_confidence=True),
        session_id="s1",
        customer_id="CUST-ARVIND",
    )
    report = kb.frustration()
    # Logged: the observation is auditable.
    assert report["observations"] == 1
    event = next(e for e in kb.events if e.get("kind") == "frustration")
    assert event["low_confidence"] is True
    assert event["confidence"] == 0.4
    # But absent from every number an operations decision would be made on.
    assert report["by_category"] == {}
    assert report["counted_observations"] == 0
    assert report["low_confidence_by_category"] == {"frustrated": 1}


def test_low_confidence_is_filterable_on_both_the_event_and_the_edge():
    kb = fresh_store()
    kb.append_frustration(observation(confidence=0.9), session_id="s1", customer_id="CUST-A")
    kb.append_frustration(
        observation(confidence=0.3, low_confidence=True), session_id="s2", customer_id="CUST-B"
    )
    events = [e for e in kb.events if e.get("kind") == "frustration"]
    assert [e["low_confidence"] for e in events] == [False, True]
    edges = [e for e in kb.graph_edges if e["rel"] == "EXHIBITS_FRUSTRATION"]
    assert [e["low_confidence"] for e in edges] == [False, True]
    assert kb.frustration()["graph"]["counted_edges"] == 1
    assert kb.frustration()["graph"]["low_confidence_edges"] == 1


# --- the graph edge ---------------------------------------------------------


def test_the_edge_goes_through_the_same_writer_as_every_other_edge():
    kb = fresh_store()
    kb.append_frustration(
        observation(signals=["caps_lock", "explicit_complaint"]),
        session_id="s1",
        customer_id="CUST-ARVIND",
    )
    edge = next(e for e in kb.graph_edges if e["rel"] == "EXHIBITS_FRUSTRATION")
    assert edge["from_id"] == "CUST-ARVIND"
    assert edge["from_type"] == "Customer"
    assert edge["to_id"] == "frustrated"
    assert edge["to_type"] == "FrustrationCategory"
    # The same id/ts contract append_edge gives HAS_BOOKING and EVALUATED_UNDER.
    assert edge["id"] and edge["ts"]
    # And it is reachable from the passenger graph, not a side table.
    assert any(
        e["rel"] == "EXHIBITS_FRUSTRATION" for e in kb.graph_for("CUST-ARVIND")["edges"]
    )


def test_an_unidentified_passenger_still_records_a_session_scoped_edge():
    kb = fresh_store()
    kb.append_frustration(observation(), session_id="s-anon", customer_id=None)
    edge = next(e for e in kb.graph_edges if e["rel"] == "EXHIBITS_FRUSTRATION")
    assert edge["from_id"] == "s-anon"
    assert edge["from_type"] == "Session"


def test_a_neutral_turn_records_the_event_but_claims_no_frustration():
    kb = fresh_store()
    kb.append_frustration(
        observation(category=FrustrationCategory.NEUTRAL, signals=[]),
        session_id="s1",
        customer_id="CUST-ARVIND",
    )
    assert kb.frustration()["by_category"] == {"neutral": 1}
    assert not [e for e in kb.graph_edges if e["rel"] == "EXHIBITS_FRUSTRATION"]


def test_knowledge_graph_dedupes_writes_and_labels_nodes():
    """Operations draws the same graph_edges store, not a side table."""
    kb = fresh_store()
    for _ in range(3):
        kb.append_edge(
            {
                "customer_id": "CUST-ARVIND",
                "from_id": "CUST-ARVIND",
                "from_type": "Customer",
                "rel": "HAS_BOOKING",
                "to_id": "bkg-ai202",
                "to_type": "Booking",
                "reason": "Retrieved from passenger knowledge base",
                "source": "Booking / Transaction Data",
                "label": "AI-202",
            }
        )
    kb.append_frustration(observation(), session_id="s1", customer_id="CUST-ARVIND")
    graph = kb.knowledge_graph()
    assert graph["writes"] == 4
    assert graph["unique_edges"] == 2
    assert graph["relations"] == {"HAS_BOOKING": 1, "EXHIBITS_FRUSTRATION": 1}
    by_id = {node["id"]: node for node in graph["nodes"]}
    assert by_id["CUST-ARVIND"]["type"] == "Customer"
    assert by_id["CUST-ARVIND"]["label"] != "CUST-ARVIND"
    assert by_id["frustrated"]["type"] == "FrustrationCategory"
    assert "nodes" in graph and "edges" in graph and "types" in graph


# --- exclusivity: a policy unit test, not an integration test ---------------


@pytest.mark.parametrize("category", list(FrustrationCategory) + [None])
def test_lounge_is_never_offered_on_a_refund_track_whatever_the_frustration(category):
    """The headline guarantee of the surfacing rule.

    A refund-eligible passenger who also asks for lounge gets a lounge
    decision — it is explained, as DENY. What must never happen is lounge
    appearing in the set the agent puts on the table, and no frustration
    category may change that.
    """
    customers, bookings = _people()
    evaluation = evaluate_policy(
        customers["CUST-PRIYA"],
        bookings["BK-PRIYA-OUT"],
        [
            ExtractedRequest(type=RequestType.REFUND_ORIGINAL),
            ExtractedRequest(type=RequestType.LOUNGE),
            ExtractedRequest(type=RequestType.MEAL_VOUCHER),
        ],
        frustration_category=category,
    )
    assert "refund_original" in evaluation.offered_actions
    assert "lounge" not in evaluation.offered_actions
    assert "meal_voucher" not in evaluation.offered_actions

    # The eligibility record is untouched: the denial is still stated and cited.
    lounge = next(d for d in evaluation.decisions if d.action == "lounge")
    assert lounge.status is DecisionStatus.DENY
    assert lounge.reason


@pytest.mark.parametrize("category", list(FrustrationCategory) + [None])
def test_frustration_cannot_move_a_single_eligibility_outcome(category):
    """The whole subsystem, held to the same bar `test_emotion.py` sets for tone."""
    customers, bookings = _people()
    outcomes = {}
    for customer_id, booking_id in (
        ("CUST-PRIYA", "BK-PRIYA-OUT"),
        ("CUST-ARVIND", "BK-ARVIND-OUT"),
        ("CUST-MEHER", "BK-MEHER-OUT"),
    ):
        for request_type in RequestType:
            evaluation = evaluate_policy(
                customers[customer_id],
                bookings[booking_id],
                [ExtractedRequest(type=request_type, fare_difference_inr=2000)],
                fare_difference_inr=2000,
                frustration_category=category,
            )
            for decision in evaluation.decisions:
                outcomes[(customer_id, request_type.value, decision.action)] = (
                    decision.status.value,
                    decision.eligible,
                    decision.reason,
                    decision.amount_inr,
                    decision.escalation_reason,
                )

    baseline = {}
    for customer_id, booking_id in (
        ("CUST-PRIYA", "BK-PRIYA-OUT"),
        ("CUST-ARVIND", "BK-ARVIND-OUT"),
        ("CUST-MEHER", "BK-MEHER-OUT"),
    ):
        for request_type in RequestType:
            evaluation = evaluate_policy(
                customers[customer_id],
                bookings[booking_id],
                [ExtractedRequest(type=request_type, fare_difference_inr=2000)],
                fare_difference_inr=2000,
            )
            for decision in evaluation.decisions:
                baseline[(customer_id, request_type.value, decision.action)] = (
                    decision.status.value,
                    decision.eligible,
                    decision.reason,
                    decision.amount_inr,
                    decision.escalation_reason,
                )

    assert outcomes == baseline


def test_offered_actions_is_always_a_subset_of_what_the_engine_allowed():
    """The structural reason surfacing cannot invent an entitlement."""
    customers, bookings = _people()
    for customer_id, booking_id in (
        ("CUST-PRIYA", "BK-PRIYA-OUT"),
        ("CUST-ARVIND", "BK-ARVIND-OUT"),
        ("CUST-MEHER", "BK-MEHER-OUT"),
    ):
        for request_type in RequestType:
            for category in list(FrustrationCategory) + [None]:
                evaluation = evaluate_policy(
                    customers[customer_id],
                    bookings[booking_id],
                    [ExtractedRequest(type=request_type, fare_difference_inr=1000)],
                    fare_difference_inr=1000,
                    frustration_category=category,
                )
                offerable = {
                    d.action
                    for d in evaluation.decisions
                    if d.status in {DecisionStatus.ALLOW, DecisionStatus.ASK}
                }
                assert set(evaluation.offered_actions) <= offerable


def test_high_frustration_reorders_but_does_not_add_or_drop():
    """Ordering is the only thing the category is allowed to do here."""
    customers, bookings = _people()
    calm = evaluate_policy(customers["CUST-PRIYA"], bookings["BK-PRIYA-OUT"], [])
    urgent = evaluate_policy(
        customers["CUST-PRIYA"],
        bookings["BK-PRIYA-OUT"],
        [],
        frustration_category=FrustrationCategory.DISTRESSED,
    )
    assert set(calm.offered_actions) == set(urgent.offered_actions)
    assert calm.offered_actions != urgent.offered_actions
    # Fastest route to a resolved passenger, first.
    assert urgent.offered_actions[0] == "refund_original"


def test_a_delay_keeps_its_goodwill_because_no_resolution_track_is_open():
    """The rule is about coherence, not about deleting generosity."""
    customers, bookings = _people()
    evaluation = evaluate_policy(
        customers["CUST-ARVIND"],
        bookings["BK-ARVIND-OUT"],
        [ExtractedRequest(type=RequestType.LOUNGE)],
        frustration_category=FrustrationCategory.HOSTILE,
    )
    assert "lounge" in evaluation.offered_actions
    assert "meal_voucher" in evaluation.offered_actions


def test_exclusivity_is_inert_when_there_is_no_track():
    from models.schemas import PolicyEvaluation

    empty = PolicyEvaluation()
    assert offered_actions(empty) == []
    assert offered_actions(empty, FrustrationCategory.HOSTILE) == []


# --- the escalation hook ----------------------------------------------------


@pytest.mark.parametrize(
    "category",
    [FrustrationCategory.DISTRESSED, FrustrationCategory.HOSTILE],
)
def test_escalation_fires_above_both_thresholds(category):
    assert detector.should_escalate(category, 0.85) is True
    assert detector.should_escalate(category, 0.95) is True


@pytest.mark.parametrize(
    "category",
    [FrustrationCategory.DISTRESSED, FrustrationCategory.HOSTILE],
)
def test_escalation_does_not_fire_below_the_confidence_threshold(category):
    assert detector.should_escalate(category, 0.84) is False
    assert detector.should_escalate(category, 0.5) is False


@pytest.mark.parametrize(
    "category",
    [FrustrationCategory.NEUTRAL, FrustrationCategory.ANNOYED, FrustrationCategory.FRUSTRATED],
)
def test_escalation_does_not_fire_below_the_category_threshold(category):
    """A confident read of mild annoyance is not a reason to fetch a human."""
    assert detector.should_escalate(category, 0.99) is False


def test_the_distress_escalation_reason_is_in_the_closed_enum():
    assert EscalationReason("severe_customer_distress") is (
        EscalationReason.SEVERE_CUSTOMER_DISTRESS
    )


def test_distress_escalation_adds_no_policy_decision():
    """It must not borrow another reason's code to get a supervisor."""
    runtime = ToolRuntime(
        session=SessionMemory(session_id="s-distress"),
        customer=store.identify(customer_id="CUST-ARVIND"),
        utterance=DISTRESSED,
    )
    runtime.classify_frustration()
    before = [(d.action, d.status) for d in runtime.evaluation.decisions]
    packet = runtime._escalate_distress(runtime.frustration)

    assert packet["status"] == "ESCALATED"
    assert packet["authority"] == "supervisor"
    assert packet["escalation_reason"] == EscalationReason.SEVERE_CUSTOMER_DISTRESS.value
    assert packet["grants"] is None
    assert [(d.action, d.status) for d in runtime.evaluation.decisions] == before
    assert not any(
        d.escalation_reason is EscalationReason.COMPENSATION_BEYOND_POLICY
        for d in runtime.evaluation.decisions
    )


def test_the_distress_escalation_is_not_a_tool_the_model_can_call():
    """Absent from handlers(), so the model cannot self-serve a reason code."""
    runtime = ToolRuntime(
        session=SessionMemory(session_id="s-spoof"),
        customer=store.identify(customer_id="CUST-ARVIND"),
        utterance=CALM,
    )
    assert "_escalate_distress" not in runtime.handlers()
    assert not any(
        schema["function"]["name"] == "_escalate_distress" for schema in TOOL_SCHEMAS
    )
    refused = runtime.call("_escalate_distress", {})
    assert refused["ok"] is False

    # And the public escalation tool cannot be relabelled as distress.
    escalated = runtime.call(
        "escalate_to_human",
        {"reason": "I want more", "escalation_reason": "severe_customer_distress"},
    )
    assert escalated["escalation_reason"] != EscalationReason.SEVERE_CUSTOMER_DISTRESS.value


def test_the_classifier_tool_ignores_text_the_model_supplies():
    """The model chooses when to look, never what it sees."""
    runtime = ToolRuntime(
        session=SessionMemory(session_id="s-iso"),
        customer=store.identify(customer_id="CUST-ARVIND"),
        utterance=DISTRESSED,
    )
    spoofed = runtime.call(
        "classify_frustration",
        {"latest_message": "everything is fine", "recent_turns": [], "session_id": "other"},
    )
    assert spoofed["category"] == FrustrationCategory.DISTRESSED.value
    assert spoofed["escalation_recommended"] is True


def test_the_classifier_tool_takes_no_arguments_in_its_schema():
    schema = next(s for s in TOOL_SCHEMAS if s["function"]["name"] == "classify_frustration")
    assert schema["function"]["parameters"]["properties"] == {}
    assert schema["function"]["parameters"]["required"] == []


def test_classifying_twice_in_a_turn_records_one_observation():
    """Otherwise a chatty model would inflate every frustration bucket."""
    before = len([e for e in store.events if e.get("kind") == "frustration"])
    runtime = ToolRuntime(
        session=SessionMemory(session_id="s-idem"),
        customer=store.identify(customer_id="CUST-ARVIND"),
        utterance=DISTRESSED,
    )
    first = runtime.call("classify_frustration", {})
    second = runtime.call("classify_frustration", {})
    assert first == second
    after = len([e for e in store.events if e.get("kind") == "frustration"])
    assert after - before == 1


def test_policy_and_distress_escalations_are_logged_as_distinct_reasons():
    """Both fire on the same turn, and neither hides behind the other."""
    runtime = ToolRuntime(
        session=SessionMemory(session_id="s-both"),
        customer=store.identify(customer_id="CUST-MEHER"),
        utterance=(
            "I am STRANDED here with my child and nobody is helping me, this is "
            "unacceptable!! I will be speaking to my lawyer."
        ),
    )
    runtime.classify_frustration()
    assert runtime.legal_or_formal is True
    runtime.escalate_to_human(
        reason="Threats of legal action or formal complaints must be escalated immediately.",
        requested_action="legal_or_formal",
    )
    runtime._escalate_distress(runtime.frustration)

    legal = next(d for d in runtime.evaluation.decisions if d.action == "legal_or_formal")
    assert legal.escalation_reason is EscalationReason.LEGAL_OR_FORMAL
    assert runtime.frustration_escalation["escalation_reason"] == (
        EscalationReason.SEVERE_CUSTOMER_DISTRESS.value
    )
    assert legal.escalation_reason.value != runtime.frustration_escalation["escalation_reason"]


# --- the fallback path, end to end, with no LLM key -------------------------


def test_a_distressed_turn_escalates_and_records_with_zero_llm_key():
    response = handle_chat(str(uuid4()), DISTRESSED, "CUST-ARVIND")

    assert response.audit_event["agent_mode"] == "fallback"
    assert response.audit_event["llm_calls"] == 0
    assert response.audit_event["provider"] == "none"

    # The handover reached containment, rather than the turn claiming it coped.
    assert response.audit_event["contained"] is False
    assert EscalationReason.SEVERE_CUSTOMER_DISTRESS.value in (
        response.audit_event["escalation_reasons"]
    )
    assert response.audit_event["frustration_category"] == FrustrationCategory.DISTRESSED.value
    assert response.audit_event["frustration_low_confidence"] is False

    # A normal supervisor packet, not a special path.
    assert response.escalation is not None
    assert response.escalation["status"] == "escalated"
    assert EscalationReason.SEVERE_CUSTOMER_DISTRESS.value in (
        response.escalation["escalation_reason_codes"]
    )
    assert response.escalation["transcript"]
    assert response.escalation["policy_decisions"]

    # And it granted nothing: the delay rule still governs.
    statuses = {e["action"]: e["status"] for e in response.eligibility}
    assert statuses.get("lounge") == "ALLOW"
    assert "hotel_delayed_hours" not in statuses or statuses["hotel_delayed_hours"] == "DENY"
    assert any(step["step"] == "frustration" for step in response.trace)


def test_a_calm_turn_is_contained_and_names_no_distress():
    response = handle_chat(str(uuid4()), "Is my flight delayed?", "CUST-ARVIND")
    assert response.audit_event["frustration_category"] == FrustrationCategory.NEUTRAL.value
    assert EscalationReason.SEVERE_CUSTOMER_DISTRESS.value not in (
        response.audit_event["escalation_reasons"]
    )
    assert response.audit_event["contained"] is True


def test_frustration_does_not_change_the_outcome_of_an_identical_request():
    """The same assertion `test_emotion.py` makes about tone, for the classifier."""
    calm = handle_chat(str(uuid4()), "I want hotel accommodation for this delay", "CUST-ARVIND")
    upset = handle_chat(
        str(uuid4()),
        "I am STRANDED with my toddler and NOBODY is helping!! I want hotel "
        "accommodation for this delay",
        "CUST-ARVIND",
    )
    assert {e["action"]: e["status"] for e in calm.eligibility} == {
        e["action"]: e["status"] for e in upset.eligibility
    }
    assert calm.audit_event["frustration_category"] == FrustrationCategory.NEUTRAL.value
    assert upset.audit_event["frustration_category"] == FrustrationCategory.DISTRESSED.value


def test_the_reply_never_names_a_category_or_a_score():
    response = handle_chat(str(uuid4()), DISTRESSED, "CUST-ARVIND")
    lowered = response.reply.lower()
    for leak in ("distressed", "hostile", "confidence", "frustration_category", "0.9"):
        assert leak not in lowered


# --- the aggregation arithmetic --------------------------------------------


def test_containment_is_cross_tabbed_against_the_peak_category():
    kb = fresh_store()
    kb.append_frustration(observation(category=FrustrationCategory.ANNOYED), session_id="calm-1")
    kb.append_frustration(
        observation(category=FrustrationCategory.DISTRESSED), session_id="hot-1"
    )
    # Same conversation later calms down; the contact was still a distressed one.
    kb.append_frustration(observation(category=FrustrationCategory.NEUTRAL), session_id="hot-1")

    kb.append_event({"kind": "turn", "session_id": "calm-1", "contained": True})
    kb.append_event({"kind": "turn", "session_id": "hot-1", "contained": False})
    kb.append_event({"kind": "turn", "session_id": "hot-1", "contained": True})

    table = kb.frustration()["containment_by_category"]
    assert table["annoyed"] == {
        "turns": 1,
        "contained_turns": 1,
        "escalated_turns": 0,
        "containment_rate": 1.0,
    }
    assert table["distressed"]["turns"] == 2
    assert table["distressed"]["containment_rate"] == 0.5
    # Severity order, so the panel does not reshuffle between refreshes.
    assert list(table) == ["annoyed", "distressed"]


def test_the_cross_tab_ignores_low_confidence_sessions():
    kb = fresh_store()
    kb.append_frustration(
        observation(category=FrustrationCategory.HOSTILE, confidence=0.3, low_confidence=True),
        session_id="guess-1",
    )
    kb.append_event({"kind": "turn", "session_id": "guess-1", "contained": False})
    assert kb.frustration()["containment_by_category"] == {}


def test_top_signals_are_aggregated_from_the_graph_edges():
    kb = fresh_store()
    for _ in range(3):
        kb.append_frustration(
            observation(signals=["explicit_complaint", "caps_lock"]),
            session_id=str(uuid4()),
            customer_id="CUST-ARVIND",
        )
    kb.append_frustration(
        observation(signals=["caps_lock"]), session_id=str(uuid4()), customer_id="CUST-PRIYA"
    )
    graph = kb.frustration()["graph"]
    assert graph["edge"] == "EXHIBITS_FRUSTRATION"
    assert graph["edges"] == 4
    assert graph["passengers"] == 2
    assert graph["top_signals_by_category"]["frustrated"] == {
        "caps_lock": 4,
        "explicit_complaint": 3,
    }


def test_duty_of_care_escalations_are_counted_apart_from_authority_limits():
    kb = fresh_store()
    kb.append_event(
        {
            "kind": "turn",
            "contained": False,
            "escalation_reasons": [EscalationReason.FARE_WAIVER_ABOVE_LIMIT.value],
        }
    )
    kb.append_event(
        {
            "kind": "turn",
            "contained": False,
            "escalation_reasons": [EscalationReason.SEVERE_CUSTOMER_DISTRESS.value],
        }
    )
    report = kb.containment()
    assert report["distress_escalations"] == 1
    assert report["authority_escalations"] == 1
    assert report["escalations_by_reason"] == {
        "fare_waiver_above_limit": 1,
        "severe_customer_distress": 1,
    }


def test_a_store_with_no_observations_reports_zero_not_a_fake_breakdown():
    report = fresh_store().frustration()
    assert report["observations"] == 0
    assert "by_category" not in report


def test_analytics_summary_embeds_frustration():
    assert "frustration" in fresh_store().analytics()


# --- the endpoint -----------------------------------------------------------


def test_the_frustration_endpoint_is_staff_gated_and_correctly_shaped(monkeypatch):
    monkeypatch.setenv("STAFF_EMAIL", DEFAULT_STAFF_EMAIL)
    monkeypatch.setenv("STAFF_PASSWORD", DEFAULT_STAFF_PASSWORD)
    StaffFactory.reset()
    client = TestClient(app)

    assert client.get("/api/analytics/frustration").status_code == 401

    passenger = OnboardingFactory.create().login("priya.nair@example.com", SEED_PASSWORD)
    as_passenger = client.get(
        "/api/analytics/frustration",
        headers={"Authorization": f"Bearer {passenger['token']}"},
    )
    assert as_passenger.status_code == 401

    staff = client.post(
        "/api/auth/staff/login",
        json={"email": DEFAULT_STAFF_EMAIL, "password": DEFAULT_STAFF_PASSWORD},
    )
    token = staff.json()["token"]

    # Populate at least one confident and one low-confidence observation.
    handle_chat(str(uuid4()), DISTRESSED, "CUST-ARVIND")
    handle_chat(str(uuid4()), ANNOYED, "CUST-PRIYA")

    response = client.get(
        "/api/analytics/frustration", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    body = response.json()

    for key in (
        "observations",
        "counted_observations",
        "by_category",
        "low_confidence_observations",
        "low_confidence_by_category",
        "containment_by_category",
        "graph",
    ):
        assert key in body

    assert body["by_category"].get("distressed", 0) >= 1
    # The low-confidence read of "this is ridiculous" is reported, and only there.
    assert body["low_confidence_by_category"].get("annoyed", 0) >= 1
    assert "annoyed" not in body["by_category"]
    assert body["counted_observations"] + body["low_confidence_observations"] == (
        body["observations"]
    )
    assert body["graph"]["edge"] == "EXHIBITS_FRUSTRATION"


def test_the_knowledge_graph_endpoint_is_staff_gated_and_correctly_shaped(monkeypatch):
    monkeypatch.setenv("STAFF_EMAIL", DEFAULT_STAFF_EMAIL)
    monkeypatch.setenv("STAFF_PASSWORD", DEFAULT_STAFF_PASSWORD)
    StaffFactory.reset()
    client = TestClient(app)

    assert client.get("/api/graph").status_code == 401

    passenger = OnboardingFactory.create().login("priya.nair@example.com", SEED_PASSWORD)
    as_passenger = client.get(
        "/api/graph",
        headers={"Authorization": f"Bearer {passenger['token']}"},
    )
    assert as_passenger.status_code == 401

    staff = client.post(
        "/api/auth/staff/login",
        json={"email": DEFAULT_STAFF_EMAIL, "password": DEFAULT_STAFF_PASSWORD},
    )
    token = staff.json()["token"]

    handle_chat(str(uuid4()), DISTRESSED, "CUST-ARVIND")

    response = client.get("/api/graph", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    for key in ("nodes", "edges", "writes", "unique_edges", "types", "relations", "kb_backend"):
        assert key in body
    assert body["writes"] >= 1
    assert {node["type"] for node in body["nodes"]} >= {"Customer", "Booking"}
    assert any(edge["rel"] == "HAS_BOOKING" for edge in body["edges"])
    assert any(edge["rel"] == "EXHIBITS_FRUSTRATION" for edge in body["edges"])
