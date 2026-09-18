from agent.context import assemble, context_contains_forbidden, packet_for_ui, render_respond_prompt
from agent.extract import extract
from data.loader import load_bookings, load_customers
from models.schemas import SessionMemory
from policy.engine import evaluate_policy


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
