from agent import retrieve
from agent.context import assemble, packet_for_ui
from agent.extract import extract
from agent.planner import expand_scope, plan_retrieval
from agent.prompts import (
    COMPUTE,
    EXTRACT_FIELDS,
    FORBID,
    RAW_POLICY_MARKERS,
    RETRIEVE,
    context_contains_forbidden,
    render_extract_prompt,
    render_respond_prompt,
)
from data.loader import load_bookings, load_customers, load_policies
from agent.tools import ToolRuntime
from models.schemas import EscalationReason, ExtractedRequest, RequestType, SessionMemory
from policy.engine import baseline_for_booking, evaluate_policy
from policy.ops import CANCELLATION_SOURCE


def test_prompt_contracts_name_retrieve_compute_forbid():
    assert "this passenger profile" in RETRIEVE
    assert any("₹1500" in item or "1500" in item for item in COMPUTE)
    assert "other passengers" in FORBID
    assert EXTRACT_FIELDS[0] == "emotion"


def test_unidentified_packet_has_no_booking_or_entitlements():
    extraction = extract("hello I need help")
    session = SessionMemory(session_id="s1")
    ctx = assemble(
        session=session,
        customer=None,
        booking=None,
        related_bookings=[],
        extraction=extraction,
        evaluation=None,
        fixture=None,
    )
    assert ctx.unidentified is True
    assert ctx.booking is None
    assert ctx.policy_decision is None
    assert ctx.missing_slots == ["sign_in"]
    assert ctx.scenario_fixture is None
    assert ctx.requests_this_turn == []
    prompt = render_respond_prompt(ctx, extraction.raw_text)
    assert "₹500" not in prompt
    assert "SK-204" not in prompt
    assert "not signed in" in prompt.lower() or "sign in" in prompt.lower()


def test_priya_packet_never_contains_meher_fare_fixture():
    customers = {c.id: c for c in load_customers()}
    bookings = {b.id: b for b in load_bookings()}
    from kb.store import store

    extraction = extract("I'm Priya Nair and I want a full cash refund plus a free business-class upgrade")
    evaluation = evaluate_policy(customers["CUST-PRIYA"], bookings["BK-PRIYA-OUT"], extraction.requests)
    session = SessionMemory(session_id="s2", customer_id="CUST-PRIYA", identified=True)
    ctx = assemble(
        session=session,
        customer=customers["CUST-PRIYA"],
        booking=bookings["BK-PRIYA-OUT"],
        related_bookings=store.bookings_for("CUST-PRIYA"),
        extraction=extraction,
        evaluation=evaluation,
        fixture=store.fixture_for("CUST-MEHER"),
    )
    assert ctx.scenario_fixture is None
    packet = packet_for_ui(ctx)
    blob = str(packet)
    assert "2000" not in blob
    assert "Meher" not in blob


def test_arvind_hotel_denied_in_injected_decision():
    customers = {c.id: c for c in load_customers()}
    bookings = {b.id: b for b in load_bookings()}
    extraction = extract("I'm frustrated I'll miss my meeting, give me hotel accommodation since it's been such a long delay")
    evaluation = evaluate_policy(customers["CUST-ARVIND"], bookings["BK-ARVIND-OUT"], extraction.requests)
    session = SessionMemory(session_id="s3", customer_id="CUST-ARVIND", identified=True)
    ctx = assemble(
        session=session,
        customer=customers["CUST-ARVIND"],
        booking=bookings["BK-ARVIND-OUT"],
        related_bookings=[],
        extraction=extraction,
        evaluation=evaluation,
        fixture=None,
    )
    hotel = next(d for d in ctx.policy_decision.decisions if d.action == "hotel_delayed_hours")
    assert hotel.status.value == "DENY"
    allowed_full_night = [
        d for d in ctx.policy_decision.decisions if d.action == "hotel_full_night" and d.status.value == "ALLOW"
    ]
    assert allowed_full_night == []
    prompt = render_respond_prompt(ctx, extraction.raw_text)
    assert "full night" not in prompt.lower() or "NOT APPROVED" in prompt or "not" in prompt.lower()


def test_respond_prompt_does_not_include_raw_policy_or_other_names():
    customers = {c.id: c for c in load_customers()}
    bookings = {b.id: b for b in load_bookings()}
    extraction = extract("PNR SK4821X my flight is cancelled")
    evaluation = evaluate_policy(customers["CUST-PRIYA"], bookings["BK-PRIYA-OUT"], extraction.requests)
    session = SessionMemory(session_id="s4", customer_id="CUST-PRIYA", identified=True)
    ctx = assemble(
        session=session,
        customer=customers["CUST-PRIYA"],
        booking=bookings["BK-PRIYA-OUT"],
        related_bookings=[],
        extraction=extraction,
        evaluation=evaluation,
        fixture=None,
    )
    prompt = render_respond_prompt(ctx, extraction.raw_text)
    assert context_contains_forbidden(prompt, "Priya Nair") == []
    assert "Arvind Kulkarni" not in prompt
    assert "Meher Kaur" not in prompt
    delay_rule = next(r["text"] for r in load_policies()["rules"] if r["id"] == "DELAY_COMPENSATION_RULE")
    assert delay_rule not in prompt
    for marker in RAW_POLICY_MARKERS:
        assert marker not in prompt
    history = customers["CUST-PRIYA"].travel_history.prior_complaint_detail
    assert history not in prompt
    assert "delayed baggage" not in prompt


def test_extract_prompt_is_narrow_and_has_no_policy_schema():
    session = SessionMemory(session_id="sx", customer_id="CUST-PRIYA", identified=True)
    prompt = render_extract_prompt("I want a refund", session)
    assert "emotion, legal_or_formal, requests" in prompt
    assert "Do not output eligibility" in prompt
    assert "Meher" not in prompt
    assert "Arvind" not in prompt
    assert "policies.json" not in prompt


def test_executed_action_appears_in_next_packet():
    customers = {c.id: c for c in load_customers()}
    bookings = {b.id: b for b in load_bookings()}
    extraction = extract("I need a meal voucher")
    evaluation = evaluate_policy(customers["CUST-ARVIND"], bookings["BK-ARVIND-OUT"], extraction.requests)
    session = SessionMemory(
        session_id="s5",
        customer_id="CUST-ARVIND",
        identified=True,
        executed_actions=["meal_voucher"],
    )
    ctx = assemble(
        session=session,
        customer=customers["CUST-ARVIND"],
        booking=bookings["BK-ARVIND-OUT"],
        related_bookings=[],
        extraction=extraction,
        evaluation=evaluation,
        fixture=None,
    )
    assert "meal_voucher" in ctx.session_memory.executed_actions
    assert "meal_voucher" in packet_for_ui(ctx)["executed_actions"]
    prompt = render_respond_prompt(ctx, extraction.raw_text)
    assert "meal_voucher" in prompt or "meal voucher" in prompt.lower()


def test_upgrade_on_return_leg_does_not_borrow_outbound_cancellation():
    """BK-PRIYA-RET is UNAFFECTED. Eligibility must not cite SK-204's cancel."""
    from kb.store import store

    customers = {c.id: c for c in load_customers()}
    bookings = {b.id: b for b in load_bookings()}
    priya = customers["CUST-PRIYA"]
    returning = bookings["BK-PRIYA-RET"]
    assert returning.status == "UNAFFECTED"
    assert returning.flight != "SK-204"

    evaluation = evaluate_policy(
        priya,
        returning,
        [ExtractedRequest(type=RequestType.BUSINESS_UPGRADE)],
    )
    upgrade = next(d for d in evaluation.decisions if d.action == "business_upgrade")
    blob = " ".join(f"{d.action} {d.status.value} {d.reason} {d.source}" for d in evaluation.decisions)
    assert upgrade.status.value == "ESCALATE"
    assert upgrade.escalation_reason is EscalationReason.UNKNOWN_ENTITLEMENT
    assert "Loyalty Tier Rule" in upgrade.source
    assert "Allowed vs. Prohibited Actions" in upgrade.source
    assert CANCELLATION_SOURCE not in upgrade.source
    assert "CANCELLATION_REBOOKING_RULE" not in blob
    assert "SK-204" not in blob

    session = SessionMemory(session_id="s-ret-upgrade", customer_id="CUST-PRIYA", identified=True)
    plan = expand_scope(
        plan_retrieval(
            extract("I want a free upgrade to business class on my return flight"),
            session,
        ),
        priya,
        returning,
    )
    retrieval = retrieve.run(plan=plan, customer=priya, evaluation=evaluation)
    cited = {hit.rule_id for hit in retrieval.rules}
    assert "CANCELLATION_REBOOKING_RULE" not in cited
    assert "MUST_ESCALATE" in cited or "LOYALTY_TIER_RULE" in cited

    runtime = ToolRuntime(
        session=session,
        customer=priya,
        utterance="free upgrade to business class on my return",
    )
    runtime.booking = returning
    runtime.evaluation = baseline_for_booking(priya, returning)
    checked = runtime.check_eligibility("business_upgrade")
    assert checked["status"] == "ESCALATE"
    assert checked["escalation_reason"] == EscalationReason.UNKNOWN_ENTITLEMENT.value
    assert CANCELLATION_SOURCE not in (checked.get("source") or "")
    assert "SK-204" not in str(checked)
    assert store.affected_booking(priya.id).id == "BK-PRIYA-OUT"
