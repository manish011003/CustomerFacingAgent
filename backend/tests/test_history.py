from uuid import uuid4

from agent.loop import SESSIONS, conversation_for, get_session, handle_chat, reset_session
from kb.store import store


def _forget(*customer_ids: str) -> None:
    for customer_id in customer_ids:
        reset_session(f"isolate-{customer_id}", customer_id)
        store.cases.pop(f"case-{customer_id}", None)
    SESSIONS.clear()


def test_two_passengers_keep_separate_chat_histories():
    _forget("CUST-ARVIND", "CUST-PRIYA")
    handle_chat(str(uuid4()), "My flight is delayed. Please tell me what I'm entitled to.", "CUST-ARVIND")
    handle_chat(str(uuid4()), "My flight got cancelled and no one told me anything!", "CUST-PRIYA")

    arvind = conversation_for("CUST-ARVIND")
    priya = conversation_for("CUST-PRIYA")
    arvind_text = " ".join(m.get("content") or "" for m in arvind["messages"])
    priya_text = " ".join(m.get("content") or "" for m in priya["messages"])
    assert "delayed" in arvind_text.lower()
    assert "cancelled" in priya_text.lower()
    assert "cancelled" not in arvind_text.lower()
    assert "delayed" not in priya_text.lower() or "cancelled" in priya_text.lower()


def test_new_browser_session_restores_that_passenger_only():
    _forget("CUST-ARVIND", "CUST-PRIYA")
    handle_chat(str(uuid4()), "My flight is delayed. Please tell me what I'm entitled to.", "CUST-ARVIND")
    handle_chat(str(uuid4()), "Can I have the meal voucher?", "CUST-ARVIND")
    handle_chat(str(uuid4()), "My flight got cancelled and no one told me anything!", "CUST-PRIYA")

    SESSIONS.clear()
    restored = handle_chat(str(uuid4()), "Can I have lounge access?", "CUST-ARVIND")
    session = get_session(restored.session["session_id"], "CUST-ARVIND")
    blob = " ".join(m.get("content") or "" for m in session.messages)
    assert "meal voucher" in blob.lower()
    assert "cancelled" not in blob.lower()
    assert "lounge" in restored.session["executed_actions"]
    assert "meal_voucher" in restored.session["executed_actions"]


def test_restart_clears_only_that_passenger_history():
    _forget("CUST-ARVIND", "CUST-PRIYA")
    arvind_sid = str(uuid4())
    handle_chat(arvind_sid, "My flight is delayed. Please tell me what I'm entitled to.", "CUST-ARVIND")
    handle_chat(str(uuid4()), "My flight got cancelled and no one told me anything!", "CUST-PRIYA")
    reset_session(arvind_sid, "CUST-ARVIND")

    arvind = conversation_for("CUST-ARVIND")
    priya = conversation_for("CUST-PRIYA")
    assert arvind["messages"] == []
    assert any("cancelled" in (m.get("content") or "").lower() for m in priya["messages"])
