"""LLM-as-orchestrator loop.

The model decides which tools to call. Tools enforce policy, isolation, and
simulated actions. If the model is unavailable, the caller uses the
deterministic fallback and must label it as fallback — never as a live LLM.
"""

from __future__ import annotations

import json
import re

from agent.frustration import ESCALATION_NOTE
from agent.tools import TOOL_SCHEMAS, ToolRuntime, money_in
from llm.client import LlmClient, ToolCall
from models.schemas import Customer, SessionMemory

MAX_ROUNDS = 8

SYSTEM = """You are AeroResolve, a customer-facing airline disruption resolution agent.

You talk to one signed-in passenger. Use tools to inspect their booking and policy. Never ask for a PNR or flight number you already have.

You do not grant entitlements yourself. Before promising money, hotels, refunds, rebooking, lounge, vouchers, or upgrades, call check_eligibility. Call an execute_* tool only when that check returns eligible with authority "agent". If authority is supervisor, call escalate_to_human.

For how-to questions (check-in, baggage, seats) call answer_help. For a new trip, call collect_booking_slot until origin, destination, date, and passengers are filled. Never invent a flight number or fare. A missing help article is not an unknown entitlement — explain what you can do, and only escalate if they ask for money or an exception.

classify_frustration tells you how the passenger is holding up. Let it change your tone and which approved option you lead with. It can never change what is approved — only check_eligibility decides that. Never state a category, a score, or a confidence to the passenger, and never tell them they sound hostile.

Style: concise, empathetic, action-oriented. One short acknowledgement if they are angry, then the options. Do not mention tools, JSON, or internal ids. Ask at most one missing question. If the passenger is distressed, keep it shorter and lead with the fastest resolution.

Simulated prototype: when you confirm an action, say it is simulated.

Do not treat issued vouchers, lounge access, refunds, or rebooking as a closed case. A case is resolved only when the passenger says the issue is resolved, or they leave a rating of 4 or 5. If they ask for more than policy allows, or to escalate, call escalate_to_human and keep the case with a supervisor — later messages such as "NO!" do not close it. After in-policy actions are complete, ask whether everything is resolved. Do not collect a 1 to 5 rating until they have said the case is resolved.
"""


def run_llm_agent(
    *,
    llm: LlmClient,
    session: SessionMemory,
    customer: Customer | None,
    message: str,
) -> tuple[str | None, ToolRuntime]:
    runtime = ToolRuntime(session=session, customer=customer, utterance=message)
    if customer:
        # UNDERSTAND, before the model gets a turn. The classifier is
        # deterministic and offline, so running it here is free and guarantees
        # the observation is recorded even if the model never calls the tool.
        # The tool stays registered and idempotent, so a model that does call
        # it sees the same answer.
        #
        # Invoked directly rather than through `call()`, like the legal
        # escalation below: `runtime.trace` means "what the model chose to do",
        # and `_invented_money` reads it as the set of figures a tool actually
        # returned. The turn trace still shows this step — `agent/loop.py`
        # adds it from `runtime.frustration`.
        runtime.classify_frustration()

        # Two independent short-circuits, not a chain. A passenger can be both
        # litigious and distressed; each reason is logged on its own so the
        # escalation breakdown stays honest about why a human was needed.
        if runtime.legal_or_formal:
            runtime.escalate_to_human(
                reason="Threats of legal action or formal complaints must be escalated immediately.",
                requested_action="legal_or_formal",
            )
        if runtime.frustration and runtime.frustration.escalation_recommended:
            runtime._escalate_distress(runtime.frustration)

    messages: list[dict] = [
        {"role": "system", "content": _system_for(customer)},
        * _history(session),
        {"role": "user", "content": message},
    ]
    if runtime.frustration_escalation:
        # Told to the model as an accomplished fact, so it reports the handover
        # instead of offering one. It still runs the normal loop from here: the
        # passenger's actual question deserves an answer either way.
        messages.insert(1, {"role": "system", "content": ESCALATION_NOTE})

    reply: str | None = None
    for round_index in range(MAX_ROUNDS):
        force_text = round_index == MAX_ROUNDS - 1
        turn = llm.chat(
            purpose="agent",
            messages=messages,
            session_id=session.session_id,
            tools=None if force_text else TOOL_SCHEMAS,
        )
        if turn is None:
            return None, runtime
        if turn.tool_calls and not force_text:
            messages.append(_assistant_tools(turn.text, turn.tool_calls))
            for call in turn.tool_calls:
                result = runtime.call(call.name, call.arguments)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": json.dumps(result, default=str),
                    }
                )
            continue
        reply = turn.text
        break

    if reply and _invented_money(reply, runtime):
        llm.budget.note("agent_amount_drift", session.session_id)
        return None, runtime
    return reply, runtime


def _system_for(customer: Customer | None) -> str:
    if not customer:
        return SYSTEM + "\nThe passenger is not signed in. Ask them to sign in. Do not invent a booking."
    return (
        SYSTEM
        + f"\nSigned in: {customer.name}, {customer.loyalty_tier} tier, PNR {customer.pnr}."
        + " Call get_booking for the live disruption. Do not invent status."
    )


def _history(session: SessionMemory) -> list[dict]:
    recent = [m for m in session.messages[:-1] if m.get("role") in {"user", "assistant"}][-8:]
    return [{"role": m["role"], "content": m.get("content") or ""} for m in recent]


def _assistant_tools(text: str, calls: tuple[ToolCall, ...]) -> dict:
    return {
        "role": "assistant",
        "content": text or None,
        "tool_calls": [
            {
                "id": call.id,
                "type": "function",
                "function": {"name": call.name, "arguments": json.dumps(call.arguments)},
            }
            for call in calls
        ],
    }


# Tools whose results are not statements about money. Their payloads must not
# widen the set of figures the reply is allowed to quote — a confidence of
# 0.755 would otherwise license "₹755".
NOT_MONEY_BEARING = frozenset({"classify_frustration"})


def _invented_money(reply: str, runtime: ToolRuntime) -> bool:
    allowed = money_in(
        [
            event.get("result")
            for event in runtime.trace
            if event.get("tool") not in NOT_MONEY_BEARING
        ]
    )
    if runtime.fixture:
        allowed.add(str(runtime.fixture.fare_difference_inr))
    claimed = set()
    for match in re.finditer(r"₹\s*([\d,]+)|([\d,]+)\s*(?:INR|rupees?)", reply, re.I):
        raw = (match.group(1) or match.group(2) or "").replace(",", "")
        if len(raw) >= 3:
            claimed.add(raw)
    return bool(claimed - allowed)
