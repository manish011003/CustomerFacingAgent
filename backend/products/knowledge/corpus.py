from __future__ import annotations

import re

from data.loader import load_help, load_policies, load_style_samples

CLAUSE_SPLIT = re.compile(r"(?<=\.)\s+")

AUTHORITY_TITLE = "Allowed vs. Prohibited Actions"

GROUPS = (
    ("allowed_actions", "allowed_action", AUTHORITY_TITLE),
    ("must_escalate", "must_escalate", AUTHORITY_TITLE),
    ("assumptions", "assumption", "Documented Assumption"),
)


def _clauses(text: str) -> list[str]:
    return [c.strip() for c in CLAUSE_SPLIT.split((text or "").strip()) if c.strip()]


def policy_clauses() -> list[dict]:
    """policies.json flattened to clause granularity.

    Clause-level rather than rule-level is deliberate. A reply cites only the clause
    whose band was actually applied, so the model never sees the other bands of the
    same rule and cannot reinterpret them.
    """
    pack = load_policies()
    docs: list[dict] = []
    for rule in pack.get("rules", []):
        for index, clause in enumerate(_clauses(rule["text"]), start=1):
            docs.append(
                {
                    "clause_id": f"{rule['id']}#{index}",
                    "rule_id": rule["id"],
                    "title": rule["title"],
                    "text": clause,
                    "kind": "rule",
                }
            )
    for group, kind, title in GROUPS:
        for index, line in enumerate(pack.get(group, []), start=1):
            docs.append(
                {
                    "clause_id": f"{group.upper()}#{index}",
                    "rule_id": group.upper(),
                    "title": title,
                    "text": line,
                    "kind": kind,
                }
            )
    return docs


def style_docs() -> list[dict]:
    payload = load_style_samples()
    return [
        {"id": s["id"], "customer": s["customer"], "agent": s["agent"]}
        for s in payload.get("samples", [])
    ]


def help_docs() -> list[dict]:
    payload = load_help()
    docs: list[dict] = []
    for article in payload.get("articles", []):
        docs.append(
            {
                "clause_id": article["id"],
                "rule_id": article["id"],
                "title": article["title"],
                "text": article["text"],
                "kind": "help",
                "topics": " ".join(article.get("topics") or []),
            }
        )
    return docs
