from uuid import uuid4

from agent.context import narrate, render_respond_prompt
from agent.extract import extract
from agent.loop import handle_chat, reset_session
from products.replies.template import ACKNOWLEDGEMENT


def test_angry_and_confused_customers_are_both_detected():
    assert extract("I'm furious, this is unacceptable").emotion == "angry"
    assert extract("this whole trip is ruined").emotion == "frustrated"
    assert extract("My flight got cancelled and no one told me anything!").emotion == "confused"
    assert extract("I don't understand what my options are").emotion == "confused"
    assert extract("what is my flight status") .emotion is None


def test_angry_customer_gets_an_acknowledgement_in_the_reply():
    res = handle_chat(
        str(uuid4()),
        "I'm furious. This delay ruined my day. I want hotel accommodation.",
        "CUST-ARVIND",
    )
    assert res.reply.startswith(ACKNOWLEDGEMENT["angry"])
    assert res.context_packet["emotion"] == "angry"


def test_confused_customer_gets_a_plain_orientation_line():
    res = handle_chat(
        str(uuid4()), "My flight got cancelled and no one told me anything!", "CUST-PRIYA"
    )
    assert res.reply.startswith(ACKNOWLEDGEMENT["confused"])
    assert res.context_packet["emotion"] == "confused"


def test_acknowledgement_never_promises_anything():
    # The brief asks the agent to handle anger, not to reward it.
    for line in ACKNOWLEDGEMENT.values():
        lowered = line.lower()
        for promise in ("voucher", "refund", "hotel", "lounge", "upgrade", "compensat", "₹"):
            assert promise not in lowered


def test_tone_does_not_change_a_single_policy_outcome():
    calm = handle_chat(
        str(uuid4()), "I want hotel accommodation for this delay", "CUST-ARVIND"
    )
    reset_session(calm.session["session_id"], "CUST-ARVIND")
    angry = handle_chat(
        str(uuid4()),
        "I am absolutely furious and this is unacceptable. I want hotel accommodation for this delay",
        "CUST-ARVIND",
    )
    assert {e["action"]: e["status"] for e in calm.eligibility} == {
        e["action"]: e["status"] for e in angry.eligibility
    }
    assert calm.context_packet["emotion"] is None
    assert angry.context_packet["emotion"] == "angry"


def test_tone_reaches_the_llm_prompt_as_an_instruction_not_an_entitlement():
    res = handle_chat(
        str(uuid4()), "I'm furious about this delay, I want a hotel", "CUST-ARVIND"
    )
    assert res.context_packet["emotion"] == "angry"
    # narrate() is the only channel the model sees, so tone has to be in it
    assert any("tone: angry" in line for line in _narrated(res))


def _narrated(res):
    # Rebuild the narration from the same packet the turn produced.
    from data.loader import load_bookings, load_customers
    from models.schemas import SessionMemory
    from agent.context import assemble
    from policy.engine import evaluate_policy

    customers = {c.id: c for c in load_customers()}
    bookings = {b.id: b for b in load_bookings()}
    extraction = extract("I'm furious about this delay, I want a hotel")
    evaluation = evaluate_policy(
        customers["CUST-ARVIND"], bookings["BK-ARVIND-OUT"], extraction.requests
    )
    ctx = assemble(
        session=SessionMemory(session_id="s", customer_id="CUST-ARVIND", identified=True),
        customer=customers["CUST-ARVIND"],
        booking=bookings["BK-ARVIND-OUT"],
        related_bookings=[],
        extraction=extraction,
        evaluation=evaluation,
        fixture=None,
    )
    assert "sounds angry" in render_respond_prompt(ctx, extraction.raw_text)
    return narrate(ctx)
