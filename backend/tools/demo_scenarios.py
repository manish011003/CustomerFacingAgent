"""Run the three assignment scenarios and print a transcript with measurements.

    cd backend && .venv/bin/python tools/demo_scenarios.py

Every turn shows what the passenger said, what the agent replied, and the
measurements behind it: latency, which model answered, spend, whether a human
was needed and why, and how many claims carried a policy clause.

Works with or without an LLM key. Without one the replies come from the
templates and the decisions are identical, which is the point.

Free Gemini tiers allow 5 requests per minute per model, so --pace inserts a
wait between turns to keep a recording clean.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from agent.loop import handle_chat
from factories.llm_factory import LlmFactory
from kb.store import store

RULE = "=" * 76

SCENARIOS = [
    (
        "SCENARIO 1 - PRIYA NAIR (Gold), flight cancelled",
        "CUST-PRIYA",
        [
            "My flight got cancelled and no one told me anything!",
            "I'm furious. I want a full cash refund plus a free upgrade to business class on my return.",
        ],
    ),
    (
        "SCENARIO 2 - ARVIND KULKARNI (Silver), 4 hour delay",
        "CUST-ARVIND",
        [
            "This delay will make me miss my meeting. I want hotel accommodation "
            "since it has been such a long delay.",
        ],
    ),
    (
        "SCENARIO 3 - MEHER KAUR (Platinum), 6 hour delay",
        "CUST-MEHER",
        [
            "I want a full night hotel stay and move me to a higher-fare flight. "
            "The fare difference is Rs 2000.",
        ],
    ),
]


def show_turn(session_id: str, message: str, customer_id: str | None) -> None:
    response = handle_chat(session_id, message, customer_id)
    audit = response.audit_event

    print(f"  PASSENGER: {message}")
    print(f"  AGENT    : {response.reply}")

    outcome = (
        "contained"
        if audit["contained"]
        else "escalated -> " + ", ".join(audit["escalation_reasons"])
    )
    print(
        f"  [{audit['latency_ms']}ms | {audit['model'] or 'no model'} | "
        f"{audit['llm_calls']} llm call(s) | ${audit['est_cost_usd']:.6f} | "
        f"{outcome} | cited {audit['grounded_decisions']}/{audit['decisions']}]"
    )
    if audit["degradations"]:
        print(f"  [degraded: {', '.join(sorted(set(audit['degradations'])))}]")

    for row in response.eligibility:
        print(f"      {row['status']:9} {row['action']:22} {row['source']}")
    print()


def summarise() -> None:
    report = store.containment()
    print(RULE)
    print("MEASURED OVER THIS RUN")
    print(RULE)
    if not report["turns"]:
        print("  No measured turns.")
        return
    print(f"  containment     {report['contained_turns']}/{report['turns']} turns "
          f"= {report['containment_rate']:.0%}")
    for reason, count in report["escalations_by_reason"].items():
        print(f"                  {count} x {reason}")
    coverage = report["grounding_coverage"]
    print(f"  grounding       {report['decisions_cited']}/{report['decisions_claimed']} claims cited"
          + (f" = {coverage:.0%}" if coverage is not None else ""))
    print(f"  latency         p50 {report['p50_latency_ms']}ms, p95 {report['p95_latency_ms']}ms")
    print(f"  llm calls       {report['llm_calls']}")
    print(f"  spend           ${report['est_spend_usd']:.6f} total, "
          f"${report['est_cost_per_turn_usd']:.6f} per turn")
    print()
    print("  Every escalation above is a limit the data pack places on agent")
    print("  authority, not a failure to understand the passenger.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pace",
        type=float,
        default=0.0,
        metavar="SECONDS",
        help="wait between turns, to stay inside a free tier's per-minute quota",
    )
    args = parser.parse_args()

    health = LlmFactory.create(refresh=True).health()
    print(f"AeroResolve demo — kb={store.backend}, "
          f"llm={health['provider']}"
          + (f"/{health['model']}" if health["enabled"] else " (templates only)"))
    print()

    first = True
    for title, customer_id, messages in SCENARIOS:
        print(RULE)
        print(title)
        print(RULE)
        session_id = str(uuid4())
        for index, message in enumerate(messages):
            if not first and args.pace:
                time.sleep(args.pace)
            first = False
            # Only the opening turn passes the id; the rest rely on the session,
            # which is how the app behaves once a passenger is signed in.
            show_turn(session_id, message, customer_id if index == 0 else None)

    summarise()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
