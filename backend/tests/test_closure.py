from uuid import uuid4

import pytest

from agent.closure import confirms_resolution, reconcile_open_case, reopens_resolution, thread_declares_resolved
from agent.loop import SESSIONS, handle_chat, reset_session, submit_feedback
from kb.store import store
from models.schemas import SessionMemory
from products.extractors.heuristic import HeuristicExtractor


def _case(customer_id: str) -> dict:
    return store.cases.get(f"case-{customer_id}") or {}


@pytest.fixture(autouse=True)
def isolate_seeded_chats():
    for customer_id in ("CUST-ARVIND", "CUST-PRIYA", "CUST-MEHER"):
        reset_session(f"isolate-{customer_id}", customer_id)
        store.cases.pop(f"case-{customer_id}", None)
    SESSIONS.clear()
    yield


def test_issuing_entitlements_does_not_resolve_the_case():
    sid = str(uuid4())
    handle_chat(sid, "My flight is delayed. Please tell me what I'm entitled to.", "CUST-ARVIND")
    meal = handle_chat(sid, "Can I have the meal voucher?", "CUST-ARVIND")
    lounge = handle_chat(sid, "Can I have lounge access?", "CUST-ARVIND")
    assert "meal_voucher" in meal.session["executed_actions"]
    assert "lounge" in lounge.session["executed_actions"]
    assert _case("CUST-ARVIND")["status"] == "open"
    assert lounge.feedback_prompt is True
    assert "resolved" in lounge.reply.lower()
    assert lounge.feedback_popup is False


def test_escalation_survives_later_turns_that_used_to_look_resolved():
    sid = str(uuid4())
    handle_chat(sid, "My flight is delayed. Please tell me what I'm entitled to.", "CUST-ARVIND")
    handle_chat(sid, "Can I have the meal voucher?", "CUST-ARVIND")
    handle_chat(sid, "Can I have lounge access?", "CUST-ARVIND")
    more = handle_chat(sid, "i want more", "CUST-ARVIND")
    assert more.case_status == "escalated"
    yes = handle_chat(sid, "yes", "CUST-ARVIND")
    assert yes.case_status == "escalated"
    no = handle_chat(sid, "NO!", "CUST-ARVIND")
    assert no.case_status == "escalated"
    again = handle_chat(sid, "i want more!!", "CUST-ARVIND")
    assert again.case_status == "escalated"
    escalate = handle_chat(sid, "i want to escalate", "CUST-ARVIND")
    assert escalate.case_status == "escalated"
    assert _case("CUST-ARVIND")["status"] == "escalated"
    assert _case("CUST-ARVIND")["resolved_at"] is None


def test_passenger_can_close_the_case_in_chat():
    sid = str(uuid4())
    handle_chat(sid, "My flight is delayed. Please tell me what I'm entitled to.", "CUST-ARVIND")
    handle_chat(sid, "Can I have the meal voucher?", "CUST-ARVIND")
    handle_chat(sid, "Can I have lounge access?", "CUST-ARVIND")
    done = handle_chat(sid, "That's all, thank you. This is resolved.", "CUST-ARVIND")
    assert done.case_status == "resolved"
    assert _case("CUST-ARVIND")["status"] == "resolved"
    assert _case("CUST-ARVIND")["resolved_at"]
    assert done.feedback_popup is True
    assert done.feedback_prompt is False


def test_good_feedback_resolves_and_is_saved_in_the_kb():
    sid = str(uuid4())
    handle_chat(sid, "My flight is delayed. Please tell me what I'm entitled to.", "CUST-ARVIND")
    handle_chat(sid, "Can I have the meal voucher?", "CUST-ARVIND")
    handle_chat(sid, "Can I have lounge access?", "CUST-ARVIND")
    rated = handle_chat(sid, "I'd rate this service 5/5.", "CUST-ARVIND")
    assert rated.case_status == "resolved"
    case = _case("CUST-ARVIND")
    assert case["status"] == "resolved"
    assert case["feedback"]["rating"] == 5
    assert case["feedback"]["sentiment"] == "positive"
    facts = store.known_facts("CUST-ARVIND", k=8)
    assert any("Service feedback" in fact.fact and "5/5" in fact.fact for fact in facts)
    assert any(e.get("kind") == "feedback" and e.get("customer_id") == "CUST-ARVIND" for e in store.events)
    assert any(e.get("rel") == "GAVE_FEEDBACK" and e.get("customer_id") == "CUST-ARVIND" for e in store.graph_edges)
    assert rated.feedback_popup is False


def test_poor_feedback_does_not_resolve():
    sid = str(uuid4())
    handle_chat(sid, "My flight is delayed. Please tell me what I'm entitled to.", "CUST-ARVIND")
    handle_chat(sid, "Can I have the meal voucher?", "CUST-ARVIND")
    handle_chat(sid, "Can I have lounge access?", "CUST-ARVIND")
    rated = handle_chat(sid, "I'd rate this service 1/5. This is not resolved.", "CUST-ARVIND")
    assert rated.case_status == "open"
    assert _case("CUST-ARVIND")["status"] == "open"


def test_card_feedback_endpoint_closes_when_rating_is_good():
    sid = str(uuid4())
    handle_chat(sid, "My flight is delayed. Please tell me what I'm entitled to.", "CUST-ARVIND")
    handle_chat(sid, "Can I have the meal voucher?", "CUST-ARVIND")
    handle_chat(sid, "Can I have lounge access?", "CUST-ARVIND")
    result = submit_feedback(sid, "CUST-ARVIND", 5, "All sorted")
    assert result["case_status"] == "resolved"
    assert _case("CUST-ARVIND")["feedback"]["comment"] == "All sorted"


def test_good_feedback_cannot_un_escalate():
    sid = str(uuid4())
    handle_chat(sid, "My flight is delayed. Please tell me what I'm entitled to.", "CUST-ARVIND")
    handle_chat(sid, "i want more", "CUST-ARVIND")
    handle_chat(sid, "i want to escalate", "CUST-ARVIND")
    rated = handle_chat(sid, "I'd rate this service 5/5.", "CUST-ARVIND")
    assert rated.case_status == "escalated"
    assert _case("CUST-ARVIND")["status"] == "escalated"


def test_good_feedback_cannot_un_escalate_an_authority_limit():
    """Priya's unknown_entitlement stays escalated after 'that's fine' + 5★."""
    sid = str(uuid4())
    first = handle_chat(
        sid,
        "I want a full cash refund plus a free upgrade to business class on my return.",
        "CUST-PRIYA",
    )
    assert first.case_status == "escalated"
    assert "unknown_entitlement" in (first.escalation or {}).get("escalation_reason_codes", [])
    second = handle_chat(sid, "never mind, that's fine!", "CUST-PRIYA")
    assert second.case_status == "escalated"
    assert second.feedback_popup is False
    rated = submit_feedback(sid, "CUST-PRIYA", 5, "All good")
    assert rated["case_status"] == "escalated"
    assert rated["feedback_popup"] is False
    assert _case("CUST-PRIYA")["status"] == "escalated"


def test_booking_assist_does_not_append_a_resolved_survey():
    sid = str(uuid4())
    handle_chat(sid, "My flight is delayed. Please tell me what I'm entitled to.", "CUST-ARVIND")
    handle_chat(sid, "Can I have the meal voucher?", "CUST-ARVIND")
    handle_chat(sid, "Can I have lounge access?", "CUST-ARVIND")
    book = handle_chat(sid, "I want to book a new flight.", "CUST-ARVIND")
    assert "resolved" not in book.reply.lower()
    assert "origin" in book.reply.lower() or "invent" in book.reply.lower()


def test_replies_answer_this_turn_instead_of_reciting_the_case():
    sid = str(uuid4())
    first = handle_chat(sid, "My flight is delayed. Please tell me what I'm entitled to.", "CUST-ARVIND")
    assert "already on this case" not in first.reply.lower()
    meal = handle_chat(sid, "Can I have the meal voucher?", "CUST-ARVIND")
    assert "already on this case" not in meal.reply.lower()
    assert "meal voucher" in meal.reply.lower()
    assert "i can arrange" not in meal.reply.lower()


def test_cash_ask_escalates_once_and_greeting_does_not_repeat_the_handover():
    sid = str(uuid4())
    handle_chat(sid, "My flight is delayed. Please tell me what I'm entitled to.", "CUST-ARVIND")
    cash = handle_chat(sid, "can you give me 100000 inr", "CUST-ARVIND")
    assert cash.case_status == "escalated"
    assert cash.escalation is not None
    assert "new trip" not in cash.reply.lower()
    hello = handle_chat(sid, "hi", "CUST-ARVIND")
    assert hello.case_status == "escalated"
    assert hello.escalation is None
    assert "supervisor" in hello.reply.lower()
    assert "new trip" not in hello.reply.lower()


def test_close_the_case_and_yes_its_resolved_marks_resolved():
    sid = str(uuid4())
    handle_chat(sid, "I need help with my trip.", "CUST-ARVIND")
    handle_chat(sid, "i want to book a flight", "CUST-ARVIND")
    handle_chat(sid, "from ahmedabad to hyderabad, day after tomorrow and 1 passenger", "CUST-ARVIND")
    closing = handle_chat(sid, "close the case", "CUST-ARVIND")
    assert closing.case_status == "resolved"
    assert closing.session["resolved_by_customer"] is True
    done = handle_chat(sid, "yes its resolved", "CUST-ARVIND")
    assert done.case_status == "resolved"
    rated = handle_chat(sid, "3", "CUST-ARVIND")
    assert rated.case_status == "resolved"
    case = _case("CUST-ARVIND")
    assert case["status"] == "resolved"
    assert case["resolved_at"]
    assert case["feedback"]["rating"] == 3
    assert case["feedback"]["sentiment"] == "mixed"


def test_spoken_close_phrases_count_as_the_passenger_saying_so():
    session = SessionMemory(session_id="s")
    assert confirms_resolution("close the case", session)
    assert confirms_resolution("please close this case", session)
    assert confirms_resolution("yes its resolved", session)
    assert confirms_resolution("yes, it's resolved", session)
    assert confirms_resolution("it's resolved", session)
    assert not confirms_resolution("thanks you", session)
    assert not confirms_resolution("i want to book a flight", session)


def test_yes_after_anything_else_does_not_resolve_but_yes_after_resolved_prompt_does():
    extra = SessionMemory(
        session_id="s",
        messages=[
            {
                "role": "assistant",
                "content": "Is there anything else I can assist you with regarding this trip?",
            },
            {"role": "user", "content": "yes"},
        ],
    )
    assert confirms_resolution("yes", extra) is False
    prompted = SessionMemory(
        session_id="s2",
        messages=[
            {
                "role": "assistant",
                "content": "Please let me know if everything is resolved or if you need anything else.",
            },
            {"role": "user", "content": "yes"},
        ],
    )
    assert confirms_resolution("yes", prompted) is True


def test_thanks_after_help_is_gratitude_not_a_new_hello():
    sid = str(uuid4())
    handle_chat(sid, "I need help with my trip.", "CUST-ARVIND")
    handle_chat(sid, "i want to book a flight", "CUST-ARVIND")
    handle_chat(sid, "from mumbai to pune, tomorrow and 4 passengers", "CUST-ARVIND")
    thanks = handle_chat(sid, "thanks", "CUST-ARVIND")
    assert "you're welcome" in thanks.reply.lower()
    assert "hi " not in thanks.reply.lower()


def test_profanity_after_close_reopens_the_case():
    sid = str(uuid4())
    handle_chat(sid, "I need help with my trip.", "CUST-ARVIND")
    handle_chat(sid, "i want to book a flight", "CUST-ARVIND")
    handle_chat(sid, "from mumbai to pune, tomorrow and 4 passengers", "CUST-ARVIND")
    closing = handle_chat(sid, "close the case", "CUST-ARVIND")
    assert closing.case_status == "resolved"
    rated = handle_chat(sid, "I'd rate this service 3/5.", "CUST-ARVIND")
    assert rated.case_status == "resolved"
    swear = handle_chat(sid, "fuck you", "CUST-ARVIND")
    assert swear.case_status == "open"
    assert swear.session["resolved_by_customer"] is False
    assert "reopened" in swear.reply.lower()
    assert _case("CUST-ARVIND")["status"] == "open"
    assert _case("CUST-ARVIND")["resolved_at"] is None
    again = handle_chat(sid, "frustrated", "CUST-ARVIND")
    assert again.case_status == "open"


def test_reopens_resolution_is_hostility_not_a_mixed_rating():
    assert reopens_resolution("fuck you") is True
    assert reopens_resolution("fuck off") is True
    assert reopens_resolution("frustrated") is True
    assert reopens_resolution("this is not resolved") is True
    assert reopens_resolution("I'd rate this service 3/5.") is False
    assert reopens_resolution("thanks") is False
    assert reopens_resolution("okay") is False


def test_thread_un_declares_resolved_after_later_hostility():
    session = SessionMemory(
        session_id="s",
        messages=[
            {"role": "user", "content": "close the case"},
            {"role": "assistant", "content": "All set — case closed."},
            {"role": "user", "content": "I'd rate this service 3/5."},
            {"role": "assistant", "content": "Thank you."},
            {"role": "user", "content": "fuck you"},
        ],
    )
    assert thread_declares_resolved(session) is False


def test_resolved_card_reopens_when_transcript_turns_hostile():
    closed = {
        "id": "case-stuck",
        "status": "resolved",
        "resolved_at": "2026-09-19T01:00:00+00:00",
        "resolved_by": "customer",
        "transcript": [
            {"role": "user", "content": "close the case"},
            {"role": "assistant", "content": "All set — case closed."},
            {"role": "user", "content": "I'd rate this service 3/5."},
            {"role": "user", "content": "fuck you"},
        ],
    }
    reopened = reconcile_open_case(closed)
    assert reopened["status"] == "open"
    assert reopened["resolved_at"] is None


def test_open_card_reconciles_when_transcript_already_closed():
    stuck = {
        "id": "case-stuck",
        "status": "open",
        "transcript": [
            {"role": "user", "content": "close the case"},
            {"role": "assistant", "content": "Is everything resolved?"},
            {"role": "user", "content": "yes its resolved"},
            {"role": "assistant", "content": "Could you rate from 1 to 5?"},
            {"role": "user", "content": "3"},
        ],
    }
    closed = reconcile_open_case(stuck)
    assert closed["status"] == "resolved"
    assert reconcile_open_case({**stuck, "status": "escalated"})["status"] == "escalated"


def test_heuristic_reads_more_and_escalate_intents():
    extractor = HeuristicExtractor()
    more = extractor.extract("i want more")
    assert any(r.type.value == "compensation_beyond_policy" for r in more.requests)
    escalate = extractor.extract("i want to escalate")
    assert any(r.type.value == "compensation_beyond_policy" for r in escalate.requests)
