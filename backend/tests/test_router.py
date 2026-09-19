from uuid import uuid4

from agent.loop import handle_chat, reset_session, SESSIONS
from agent.router import classify, slots_from
from kb.store import store
from models.schemas import IssueFamily, RequestType
from products.extractors.heuristic import HeuristicExtractor


def test_vague_utterance_stays_unclassified():
    extraction = HeuristicExtractor().extract("sort out the thing we discussed on the phone yesterday")
    assert extraction.issue_family == IssueFamily.UNCLASSIFIED
    assert [r.type for r in extraction.requests] == [RequestType.GENERAL_HELP]


def test_booking_assist_collects_slots_without_inventing_a_flight():
    extraction = HeuristicExtractor().extract(
        "I want to book a flight from Delhi to Goa next Friday for 2 passengers."
    )
    assert extraction.issue_family == IssueFamily.ASSIST
    assert extraction.requests[0].type == RequestType.BOOKING_ASSIST
    filled = slots_from("I want to book a flight from Delhi to Goa next Friday for 2 passengers.")
    assert filled["origin"].lower() == "delhi"
    assert filled["destination"].lower() == "goa"
    assert filled["passengers"] == "2"


def test_help_question_is_not_status():
    extraction = HeuristicExtractor().extract("What's the baggage allowance and how do I check in?")
    assert extraction.issue_family == IssueFamily.HELP
    assert extraction.requests[0].type == RequestType.HELP_QUESTION


def test_chat_booking_assist_asks_then_confirms_without_a_flight_number():
    sid = str(uuid4())
    reset_session(sid, "CUST-ARVIND")
    first = handle_chat(sid, "I want to book a new flight.", "CUST-ARVIND")
    assert first.case_status != "escalated"
    assert "origin" in (first.context_packet.get("missing_slots") or []) or "invent" in first.reply.lower()
    assert first.context_packet.get("suggested_flight") is None
    done = handle_chat(
        sid,
        "From Delhi to Goa next Friday for 2 passengers.",
        "CUST-ARVIND",
    )
    assert "delhi" in done.reply.lower()
    assert "goa" in done.reply.lower()
    assert "flight number" in done.reply.lower() or "inventory" in done.reply.lower()
    card = done.context_packet.get("suggested_flight") or {}
    assert card.get("flight") == "SK-441"
    assert card.get("source") == "scheduled"
    assert str(card.get("href", "")).startswith("/exit")
    SESSIONS.clear()
    store.cases.pop("case-CUST-ARVIND", None)


def test_bare_book_a_flight_does_not_invent_a_departure():
    sid = str(uuid4())
    reset_session(sid, "CUST-ARVIND")
    first = handle_chat(sid, "book a flight", "CUST-ARVIND")
    assert first.context_packet.get("suggested_flight") is None
    assert first.context_packet.get("missing_slots")
    SESSIONS.clear()
    store.cases.pop("case-CUST-ARVIND", None)


def test_help_chat_cites_the_guide_not_delay_vouchers():
    sid = str(uuid4())
    reset_session(sid, "CUST-ARVIND")
    reply = handle_chat(sid, "How do I check in?", "CUST-ARVIND")
    lower = reply.reply.lower()
    assert "₹500" not in reply.reply
    assert "check-in" in lower or "check in" in lower or "48 hours" in lower
    SESSIONS.clear()


def test_unknown_benefit_still_escalates():
    sid = str(uuid4())
    reset_session(sid, "CUST-PRIYA")
    reply = handle_chat(sid, "Give me extra compensation of ₹10000 please.", "CUST-PRIYA")
    assert reply.case_status == "escalated"
    SESSIONS.clear()
    store.cases.pop("case-CUST-PRIYA", None)


def test_cash_ask_is_beyond_policy_not_help():
    extraction = HeuristicExtractor().extract("can you give me 100000 inr")
    assert extraction.issue_family == IssueFamily.DISRUPTION
    assert any(r.type == RequestType.COMPENSATION_BEYOND_POLICY for r in extraction.requests)


def test_priya_upgrade_phrasing_is_business_upgrade_not_beyond_policy():
    """'for the trouble' is a reason-for-ask. The data-pack code is unknown_entitlement."""
    from agent.closure import wants_more

    line = (
        "I want a full cash refund and a free upgrade to business class "
        "on my return flight for the trouble."
    )
    assert wants_more(line) is False
    extraction = HeuristicExtractor().extract(line)
    types = [r.type for r in extraction.requests]
    assert RequestType.BUSINESS_UPGRADE in types
    assert RequestType.REFUND_ORIGINAL in types
    assert RequestType.COMPENSATION_BEYOND_POLICY not in types


def test_classify_helpers():
    assert classify("book me a ticket") == IssueFamily.ASSIST
    assert classify("how do I check in") == IssueFamily.HELP
    assert classify("hello") == IssueFamily.UNCLASSIFIED


def test_greeting_after_booking_assist_does_not_recite_the_trip():
    sid = str(uuid4())
    reset_session(sid, "CUST-ARVIND")
    handle_chat(sid, "I want to book a new flight.", "CUST-ARVIND")
    hello = handle_chat(sid, "hi", "CUST-ARVIND")
    lower = hello.reply.lower()
    assert "origin" not in lower
    assert "i still need" not in lower
    assert "hi" in lower or "here" in lower
    SESSIONS.clear()
    store.cases.pop("case-CUST-ARVIND", None)


def test_greeting_is_not_a_booking_follow_up():
    from models.schemas import SessionMemory

    session = SessionMemory(session_id="s", open_question="origin", choices={"assist": {}})
    assert classify("hi", session) == IssueFamily.UNCLASSIFIED
    assert classify("From Delhi to Goa next Friday for 2 passengers.", session) == IssueFamily.ASSIST
    assert classify("Delhi", session) == IssueFamily.ASSIST
