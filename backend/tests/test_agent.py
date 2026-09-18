"""LLM agent loop: the model orchestrates, tools enforce policy."""

from __future__ import annotations

from uuid import uuid4

from agent.loop import handle_chat
from agent.orchestrator import run_llm_agent
from agent.tools import ToolRuntime
from factories.llm_factory import LlmFactory
from kb.store import store
from models.schemas import SessionMemory
from tests.test_llm import client_with, config


class ScriptedSdk:
    """Returns a sequence of chat.completions payloads, including tool calls."""

    def __init__(self, steps: list[dict]):
        self.steps = list(steps)
        self.requests: list[dict] = []
        self.chat = self

    @property
    def completions(self):
        return self

    def create(self, **kwargs):
        self.requests.append(kwargs)
        step = self.steps.pop(0) if self.steps else {"text": "I've checked your booking."}
        tool_calls = []
        for call in step.get("tool_calls") or []:
            fn = type("Fn", (), {"name": call["name"], "arguments": call.get("arguments", "{}")})()
            tool_calls.append(type("TC", (), {"id": call.get("id", f"call_{len(tool_calls)}"), "function": fn})())
        message = type("Message", (), {"content": step.get("text"), "tool_calls": tool_calls or None})()
        choice = type("Choice", (), {"message": message, "finish_reason": step.get("finish_reason", "stop")})()
        usage = type("Usage", (), {"prompt_tokens": 80, "completion_tokens": 40})()
        return type("Completion", (), {"choices": [choice], "usage": usage})()


def _args(name: str, payload: dict | None = None) -> dict:
    import json

    return {"name": name, "arguments": json.dumps(payload or {})}


def test_no_key_is_honest_fallback_not_a_live_llm():
    response = handle_chat(str(uuid4()), "Is my flight delayed?", "CUST-ARVIND")
    assert response.audit_event["agent_mode"] == "fallback"
    assert response.context_packet["llm_active"] is False
    assert response.audit_event["provider"] == "none"


def test_agent_calls_booking_then_policy_then_answers():
    sdk = ScriptedSdk(
        [
            {
                "text": "",
                "finish_reason": "tool_calls",
                "tool_calls": [_args("get_booking")],
            },
            {
                "text": "",
                "finish_reason": "tool_calls",
                "tool_calls": [_args("check_eligibility", {"action": "hotel"})],
            },
            {
                "text": "Your Mumbai to Bengaluru flight is delayed 4 hours. I can arrange a meal voucher and lounge access. Hotel cover only applies after more than 5 hours, so I cannot book a hotel for this delay.",
            },
        ]
    )
    client = client_with(sdk, config(provider="groq"))
    session = SessionMemory(session_id="s-agent")
    customer = store.identify(customer_id="CUST-ARVIND")
    reply, runtime = run_llm_agent(
        llm=client, session=session, customer=customer, message="I want a hotel for this delay."
    )
    tools = [event["tool"] for event in runtime.trace]
    assert tools == ["get_booking", "check_eligibility"]
    assert reply is not None and "hotel" in reply.lower()
    hotel = next(d for d in runtime.evaluation.decisions if d.action == "hotel_delayed_hours")
    assert hotel.status.value == "DENY"


def test_execute_hotel_is_blocked_when_policy_denies():
    runtime = ToolRuntime(
        session=SessionMemory(session_id="s-deny"),
        customer=store.identify(customer_id="CUST-ARVIND"),
        utterance="Give me a hotel",
    )
    result = runtime.call("arrange_hotel", {})
    assert result["ok"] is False
    assert result["status"] == "DENY"
    assert "hotel_delayed_hours" not in runtime.session.executed_actions


def test_fare_waiver_above_limit_escalates_and_cannot_be_executed():
    runtime = ToolRuntime(
        session=SessionMemory(session_id="s-fare"),
        customer=store.identify(customer_id="CUST-MEHER"),
        utterance="Waive the 2000 rupee fare difference",
    )
    checked = runtime.call("check_eligibility", {"action": "fare_waiver", "fare_difference_inr": 2000})
    assert checked["status"] == "ESCALATE"
    assert checked["authority"] == "supervisor"
    executed = runtime.call("execute_rebooking", {})
    # Rebook is not the waiver; the waiver itself has no execute tool that can succeed.
    waived = runtime.call("escalate_to_human", {"reason": "fare difference above 1500", "requested_action": "fare_waiver"})
    assert waived["status"] == "ESCALATED"


def test_get_customer_cannot_load_another_passenger():
    runtime = ToolRuntime(
        session=SessionMemory(session_id="s-iso"),
        customer=store.identify(customer_id="CUST-PRIYA"),
        utterance="hello",
    )
    result = runtime.call("get_customer", {"customer_identifier": "CUST-MEHER"})
    assert result["customer"]["id"] == "CUST-PRIYA"
    assert result["customer"]["name"] == "Priya Nair"


def test_live_agent_path_records_tool_calls(monkeypatch):
    sdk = ScriptedSdk(
        [
            {"text": "", "finish_reason": "tool_calls", "tool_calls": [_args("get_booking")]},
            {
                "text": "I've checked booking TR1190B. SK-118 is delayed 4 hours. I can help with a meal voucher and lounge access.",
            },
        ]
    )
    client = client_with(sdk, config(provider="groq"))
    monkeypatch.setattr(LlmFactory, "create", classmethod(lambda cls, refresh=False: client))
    LlmFactory._client = client
    response = handle_chat(str(uuid4()), "What's happening with my flight?", "CUST-ARVIND")
    assert response.audit_event["agent_mode"] == "llm"
    assert response.context_packet["llm_active"] is True
    assert any(step["step"] == "get_booking" for step in response.trace)
    LlmFactory.reset()


def test_agent_chat_sends_tools_to_the_model():
    sdk = ScriptedSdk([{"text": "Hello, I can help with your booking."}])
    client = client_with(sdk, config(provider="groq"))
    session = SessionMemory(session_id="s-tools")
    run_llm_agent(
        llm=client,
        session=session,
        customer=store.identify(customer_id="CUST-PRIYA"),
        message="Help me",
    )
    assert "tools" in sdk.requests[0]
    names = [item["function"]["name"] for item in sdk.requests[0]["tools"]]
    assert "check_eligibility" in names
    assert "escalate_to_human" in names
