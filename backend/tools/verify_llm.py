"""End-to-end check of the LLM layer against a real provider.

    cd backend && .venv/bin/python tools/verify_llm.py

Answers, in order: which key loaded, does it authenticate, does a real call
come back within the caps, and does a real conversational turn still produce
the policy-approved outcome. Prints a key fingerprint, never a key.

The pytest suite deliberately never touches the network, so this script is the
only thing that exercises the provider for real. Safe to run repeatedly: it
makes at most four model calls and obeys every ceiling in llm/budget.py.
"""

from __future__ import annotations

import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

from agent.loop import handle_chat
from factories.llm_factory import LlmFactory
from kb.store import store

PASS = "  ok   "
FAIL = "  FAIL "
SKIP = "  --   "


def heading(text: str) -> None:
    print(f"\n{text}\n{'-' * len(text)}")


def resolved_config() -> bool:
    client = LlmFactory.create(refresh=True)
    report = client.health()
    heading("1. Which provider loaded")
    print(f"  provider     {report['provider']}")
    print(f"  model        {report['model']}")
    print(f"  chain        {' -> '.join(report.get('model_chain') or []) or '(none)'}")
    print(f"  base_url     {report['base_url'] or '(sdk default)'}")
    print(f"  key          {report['key_fingerprint'] or '(none)'}")
    caps = report["caps"]
    print(f"  caps         extract {caps['max_tokens_extract']} / respond {caps['max_tokens_respond']} tokens, "
          f"{caps['timeout_seconds']}s timeout")
    print(f"  budget       ${report['budget']['daily_budget_usd']}/day, "
          f"{caps['max_calls_per_session']} calls per conversation")

    if not report["enabled"]:
        print(f"\n{FAIL} No provider configured.")
        print("       Create backend/.env with one of:")
        print("         GEMINI_API_KEY=...   (free tier, https://aistudio.google.com/apikey)")
        print("         GROQ_API_KEY=gsk_... (free tier, https://console.groq.com/keys)")
        return False
    print(f"\n{PASS} Provider resolved without reading OPENAI_API_KEY.")
    return True


def key_authenticates() -> bool:
    heading("2. Does the key authenticate")
    report = LlmFactory.create().health(probe=True)
    if report.get("key_valid"):
        print(f"{PASS} The provider accepted the key.")
        return True
    print(f"{FAIL} Rejected: {report.get('probe_error', 'unknown error')}")
    print("       A bad key is not fatal — the agent falls back to templates —")
    print("       but nothing below will exercise the model.")
    return False


def live_call() -> bool:
    heading("3. A real call, inside the caps")
    client = LlmFactory.create()
    session = f"verify-{uuid4()}"
    client.begin_turn(session)
    result = client.complete(
        purpose="respond",
        system="Reply with exactly the word: ready",
        user="Say ready.",
        session_id=session,
    )
    usage = client.end_turn(session)

    if result is None:
        print(f"{FAIL} No answer. Degradations: {usage['degradations'] or 'none recorded'}")
        return False

    print(f"  answered by  {result.model}")
    print(f"  reply        {result.text[:60]!r}")
    print(f"  tokens       {result.prompt_tokens} in / {result.completion_tokens} out")
    print(f"  cost         ${result.est_cost_usd:.6f}")
    if usage["models_used"][:-1]:
        print(f"  chain walked past {', '.join(usage['models_used'][:-1])} to get here")
    cap = client.config.max_tokens_respond
    if result.completion_tokens > cap:
        print(f"\n{FAIL} Output of {result.completion_tokens} tokens exceeded the {cap} cap.")
        return False
    print(f"\n{PASS} Answered within the {cap}-token cap.")
    return True


def live_turn() -> bool:
    """The real test: does a model in the loop still yield the policy outcome."""
    heading("4. A real conversational turn")
    session = str(uuid4())
    response = handle_chat(
        session,
        "I want a full night hotel stay and move me to a higher-fare flight. The fare difference is Rs 2000.",
        "CUST-MEHER",
    )
    audit = response.audit_event
    actions = {e["action"]: e["status"] for e in response.eligibility}

    print(f"  reply        {response.reply[:100]!r}...")
    print(f"  provider     {audit['provider']} / {audit['model']}")
    print(f"  latency      {audit['latency_ms']}ms")
    print(f"  tokens       {audit['prompt_tokens']} in / {audit['completion_tokens']} out")
    print(f"  cost         ${audit['est_cost_usd']:.6f}")
    print(f"  contained    {audit['contained']}  {audit['escalation_reasons']}")
    print(f"  grounded     {audit['grounded_decisions']}/{audit['decisions']} decisions cited")
    if audit["degradations"]:
        print(f"  degraded     {audit['degradations']}")

    # These three are fixed by the data pack. A model in the loop must not move
    # them, which is the whole claim of the architecture.
    expected = {
        "hotel_full_night": "DENY",
        "hotel_delayed_hours": "ALLOW",
        "fare_waiver": "ESCALATE",
    }
    wrong = {k: (actions.get(k), v) for k, v in expected.items() if actions.get(k) != v}
    if wrong:
        print(f"\n{FAIL} The model moved a policy outcome: {wrong}")
        return False
    print(f"\n{PASS} Policy outcomes unchanged with a live model: "
          + ", ".join(f"{k}={v}" for k, v in expected.items()))

    if audit["llm_calls"] == 0:
        print(f"{SKIP} No model call was made this turn, so phrasing came from the template.")
    return True


def spend() -> None:
    heading("5. What this cost")
    budget = LlmFactory.create().health()["budget"]
    print(f"  calls today  {budget['calls_today']}")
    print(f"  tokens       {budget['prompt_tokens_today']} in / {budget['completion_tokens_today']} out")
    print(f"  spend        ${budget['spend_today_usd']:.6f} of ${budget['daily_budget_usd']} budget")
    if budget["degradations"]:
        print(f"  degradations {budget['degradations']}")
    print("\n  Containment over this run:")
    report = store.containment()
    if report["turns"]:
        print(f"    {report['contained_turns']}/{report['turns']} turns contained, "
              f"grounding {report['grounding_coverage']}")


def main() -> int:
    print("AeroResolve — LLM provider verification")
    if not resolved_config():
        return 1
    if not key_authenticates():
        return 1
    ok = live_call()
    ok = live_turn() and ok
    spend()
    print(f"\n{'All checks passed.' if ok else 'Some checks failed — see FAIL above.'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
