from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from math import ceil
from typing import Any, Literal
from uuid import uuid4

from data.loader import load_bookings, load_customers, load_fixtures
from models.schemas import (
    DUTY_OF_CARE_REASONS,
    FRUSTRATION_SEVERITY,
    Booking,
    Customer,
    FrustrationAssessment,
    FrustrationCategory,
    KnownFact,
    RuleHit,
    ScenarioFixture,
    StyleHit,
    TurnHit,
)
from products.knowledge.corpus import help_docs, policy_clauses, style_docs
from products.knowledge.scoring import score

ISO = lambda: datetime.now(timezone.utc).isoformat()


def _seconds_between(start: str | None, end: str | None) -> float | None:
    if not start or not end:
        return None
    try:
        began = datetime.fromisoformat(start.replace("Z", "+00:00"))
        finished = datetime.fromisoformat(end.replace("Z", "+00:00"))
    except ValueError:
        return None
    return max(0.0, (finished - began).total_seconds())


def _tally(values) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def _category_counts(events: list[dict[str, Any]]) -> dict[str, int]:
    """Counts in severity order, and only for categories actually observed.

    Fixed key order means the ops panel does not reshuffle between refreshes.
    """
    counts = _tally(event.get("category") or "unknown" for event in events)
    ordered = {
        category.value: counts[category.value]
        for category in FRUSTRATION_SEVERITY
        if category.value in counts
    }
    for category, count in counts.items():
        ordered.setdefault(category, count)
    return ordered


def _percentile(ordered: list[int], pct: int) -> int | None:
    """Nearest-rank percentile over a pre-sorted list."""
    if not ordered:
        return None
    index = max(0, min(len(ordered) - 1, ceil(pct / 100 * len(ordered)) - 1))
    return ordered[index]


class PassengerKnowledgeStore(ABC):
    """Product: passenger 360 / events / cases / graph. Clients never construct a backend."""

    backend: Literal["postgres", "elasticsearch", "json"]

    def __init__(self) -> None:
        self.backend = "json"
        self.passengers: dict[str, dict[str, Any]] = {}
        self.bookings: list[dict[str, Any]] = []
        self.events: list[dict[str, Any]] = []
        self.cases: dict[str, dict[str, Any]] = {}
        self.graph_edges: list[dict[str, Any]] = []
        self.accounts: dict[str, dict[str, Any]] = {}
        self.policy_docs: list[dict[str, Any]] = policy_clauses()
        self.help_docs: list[dict[str, Any]] = help_docs()
        self.style_samples: list[dict[str, Any]] = style_docs()
        self.memories: list[dict[str, Any]] = []
        # Live chat per passenger. Keyed by customer_id so a new browser session
        # can pick up the same transcript instead of starting empty.
        self.sessions: dict[str, dict[str, Any]] = {}
        self._init_backend()
        self.seed()

    @abstractmethod
    def _init_backend(self) -> None:
        raise NotImplementedError

    def _persist(self, index: str, doc_id: str, document: dict[str, Any]) -> None:
        """Optional dual-write. JSON product is in-memory only."""

    def _drop(self, index: str, doc_id: str) -> None:
        """Optional durable delete. JSON product is in-memory only."""

    def seed(self) -> None:
        from factories.hasher_factory import HasherFactory
        from products.onboarding.self_service import SEED_PASSWORD

        hasher = HasherFactory.create()
        customers = load_customers()
        bookings = load_bookings()
        self.bookings = [b.model_dump() for b in bookings]
        self.passengers = {}
        self.accounts = {}
        for c in customers:
            record = c.model_dump() | {
                "known_facts": [],
                "account_origin": "seeded",
                "created_at": c.created_at or ISO(),
            }
            self.passengers[c.id] = record
            account = {
                "customer_id": c.id,
                "email": c.email.lower(),
                "password_hash": hasher.hash(SEED_PASSWORD),
            }
            self.accounts[c.email.lower()] = account
            self._persist("passengers", c.id, {k: v for k, v in record.items() if k != "known_facts"})
            self._persist("accounts", c.email.lower(), account)
        for b in bookings:
            self._persist("bookings", b.id, b.model_dump())
        for doc in self.policy_docs:
            self._persist("policy_rules", doc["clause_id"], doc)
        for doc in self.style_samples:
            self._persist("style_samples", doc["id"], doc)

    def _as_customer(self, record: dict[str, Any]) -> Customer:
        return Customer.model_validate(record)

    def identify(self, name: str | None = None, pnr: str | None = None, customer_id: str | None = None) -> Customer | None:
        customers = [self._as_customer(p) for p in self.passengers.values()]
        if customer_id:
            return next((c for c in customers if c.id == customer_id), None)
        if pnr:
            pnr_u = pnr.upper()
            return next((c for c in customers if c.pnr and c.pnr.upper() == pnr_u), None)
        if name:
            key = name.strip().lower()
            return next((c for c in customers if c.name.lower() == key or key in c.name.lower()), None)
        return None

    def identity_directory(self) -> list[dict[str, str]]:
        return [{"name": p["name"], "pnr": p.get("pnr") or ""} for p in self.passengers.values()]

    def account_for_email(self, email: str) -> dict[str, Any] | None:
        return self.accounts.get((email or "").strip().lower())

    def public_passenger(self, customer_id: str) -> dict[str, Any] | None:
        record = self.passengers.get(customer_id)
        if not record:
            return None
        return {k: v for k, v in record.items() if k != "password_hash"}

    def list_public_passengers(self, origin: str | None = None) -> list[dict[str, Any]]:
        rows = []
        for p in self.passengers.values():
            if origin and p.get("account_origin") != origin:
                continue
            rows.append(
                {
                    "id": p["id"],
                    "name": p["name"],
                    "email": p["email"],
                    "loyalty_tier": p["loyalty_tier"],
                    "pnr": p.get("pnr") or "",
                    "account_origin": p.get("account_origin") or "self_service",
                }
            )
        return rows

    def register_passenger(self, customer: Customer, password_hash: str) -> Customer:
        record = customer.model_dump() | {"known_facts": []}
        self.passengers[customer.id] = record
        account = {
            "customer_id": customer.id,
            "email": customer.email.lower(),
            "password_hash": password_hash,
        }
        self.accounts[customer.email.lower()] = account
        self._persist("passengers", customer.id, customer.model_dump())
        self._persist("accounts", customer.email.lower(), account)
        return customer

    def attach_booking(self, customer: Customer, payload: Any) -> Booking:
        from models.schemas import BookingIntake

        intake = payload if isinstance(payload, BookingIntake) else BookingIntake.model_validate(payload)
        status = (intake.status or "ON_TIME").upper()
        reason = None
        new_departure = None
        if status == "DELAYED" and intake.delay_hours:
            reason = f"Delayed {intake.delay_hours} hours"
        elif status == "CANCELLED":
            reason = "Operational reasons" if intake.airline_caused else "Cancellation recorded by passenger"
        booking = Booking(
            id=f"BK-{customer.id}-{uuid4().hex[:6].upper()}",
            customer_id=customer.id,
            customer_name=customer.name,
            pnr=intake.pnr.strip().upper(),
            flight=(intake.flight or None),
            leg="outbound",
            route=f"{intake.origin.strip()} → {intake.destination.strip()}",
            origin=intake.origin.strip(),
            destination=intake.destination.strip(),
            date=intake.date,
            date_label=intake.date,
            scheduled_departure=intake.scheduled_departure,
            status=status,
            status_reason=reason,
            delay_hours=intake.delay_hours,
            new_departure=new_departure,
            airline_caused=intake.airline_caused,
            quoted_fare_difference_inr=intake.quoted_fare_difference_inr,
        )
        self.bookings.append(booking.model_dump())
        self.passengers[customer.id]["pnr"] = booking.pnr
        self._persist("bookings", booking.id, booking.model_dump())
        self._persist("passengers", customer.id, self._as_customer(self.passengers[customer.id]).model_dump())
        return booking

    def bookings_for(self, customer_id: str) -> list[Booking]:
        return [Booking.model_validate(b) for b in self.bookings if b["customer_id"] == customer_id]

    def affected_booking(self, customer_id: str) -> Booking | None:
        legs = self.bookings_for(customer_id)
        for b in legs:
            if b.status in {"CANCELLED", "DELAYED"}:
                return b
        return legs[0] if legs else None

    def fixture_for(self, customer_id: str) -> ScenarioFixture | None:
        for row in load_fixtures():
            if row.customer_id == customer_id:
                return row
        return None

    # Retrieval. Grounding and citation only — nothing here feeds policy/engine.py.

    def search_policy(
        self,
        query: str,
        *,
        scope: list[str] | None = None,
        kinds: tuple[str, ...] = ("rule",),
        k: int = 2,
        max_chars: int = 400,
    ) -> list[RuleHit]:
        candidates = [d for d in self.policy_docs if d["kind"] in kinds]
        if scope:
            allowed = set(scope)
            candidates = [d for d in candidates if d["rule_id"] in allowed]
        hits = [RuleHit(**doc, score=score(query, doc["title"], doc["text"])) for doc in candidates]
        hits.sort(key=lambda h: (-h.score, h.clause_id))
        chosen = [h for h in hits if h.score > 0][:k]
        if not chosen and scope:
            # Scoped but no lexical overlap: the scope itself is the evidence.
            chosen = hits[:k]
        for hit in chosen:
            if len(hit.text) > max_chars:
                hit.text = hit.text[: max_chars - 3].rstrip() + "..."
        return chosen

    def search_help(self, query: str, *, k: int = 2, max_chars: int = 400) -> list[RuleHit]:
        hits: list[RuleHit] = []
        for doc in self.help_docs:
            ranked = (
                score(query, doc["title"]) * 3
                + score(query, doc.get("topics", "")) * 2
                + score(query, doc["text"])
            )
            payload = {key: value for key, value in doc.items() if key in {"clause_id", "rule_id", "title", "text", "kind"}}
            hits.append(RuleHit(**payload, score=ranked))
        hits.sort(key=lambda h: (-h.score, h.clause_id))
        chosen = [h for h in hits if h.score > 0][:k]
        for hit in chosen:
            if len(hit.text) > max_chars:
                hit.text = hit.text[: max_chars - 3].rstrip() + "..."
        return chosen

    def rule_ids_for_source(self, source: str) -> list[str]:
        """Map a PolicyDecision.source label back onto indexed rule ids."""
        text = source or ""
        ids: list[str] = []
        for doc in self.policy_docs:
            if doc["title"] and doc["title"] in text and doc["rule_id"] not in ids:
                ids.append(doc["rule_id"])
        return ids

    def recall_turns(self, customer_id: str, query: str, *, k: int = 3) -> list[TurnHit]:
        rows = [
            e for e in self.events
            if e.get("kind") == "turn" and e.get("customer_id") == customer_id
        ]
        hits = [
            TurnHit(
                ts=e.get("ts", ""),
                message=e.get("message") or "",
                reply=e.get("reply") or "",
                score=score(query, e.get("message") or "", e.get("reply") or ""),
            )
            for e in rows
        ]
        hits.sort(key=lambda h: (-h.score, h.ts))
        return [h for h in hits if h.score > 0][:k]

    def search_style(self, query: str, *, k: int = 1) -> list[StyleHit]:
        hits = [StyleHit(**doc, score=score(query, doc["customer"])) for doc in self.style_samples]
        hits.sort(key=lambda h: (-h.score, h.id))
        return hits[:k]

    def known_facts(self, customer_id: str, *, k: int = 5) -> list[KnownFact]:
        rows = [m for m in self.memories if m.get("customer_id") == customer_id]
        return [
            KnownFact(fact=m["fact"], source=m["source"], ts=m.get("ts", ""))
            for m in rows[-k:]
        ]

    def remember_fact(self, customer_id: str, fact: str, source: str) -> KnownFact | None:
        if any(m.get("customer_id") == customer_id and m.get("fact") == fact for m in self.memories):
            return None
        row = {
            "id": str(uuid4()),
            "customer_id": customer_id,
            "fact": fact,
            "source": source,
            "ts": ISO(),
        }
        self.memories.append(row)
        record = self.passengers.get(customer_id)
        if record is not None:
            record.setdefault("known_facts", []).append(fact)
        self._persist("memories", row["id"], row)
        return KnownFact(fact=fact, source=source, ts=row["ts"])

    def append_event(self, event: dict[str, Any]) -> dict[str, Any]:
        event = {"id": event.get("id") or str(uuid4()), "ts": event.get("ts") or ISO(), **event}
        self.events.append(event)
        self._persist("events", event["id"], event)
        return event

    def append_edge(self, edge: dict[str, Any]) -> None:
        edge = {"id": edge.get("id") or str(uuid4()), "ts": edge.get("ts") or ISO(), **edge}
        self.graph_edges.append(edge)
        self._persist("graph_edges", edge["id"], edge)

    def append_frustration(
        self,
        assessment: FrustrationAssessment,
        *,
        session_id: str,
        customer_id: str | None = None,
    ) -> dict[str, Any]:
        """Record one frustration observation as an event plus a graph edge.

        Deliberately no new index and no new writer: this goes through
        `append_event` and `append_edge`, so the Elasticsearch dual-write and
        the JSON in-memory path are both inherited and `JsonKnowledgeStore`
        needs no code of its own.

        The confidence gate is expressed as a field, not as a dropped write.
        Every observation is auditable; `low_confidence` decides whether the
        aggregations below count it. An unreviewed guess must not silently
        shape an ops number, but it must also not vanish.

        A NEUTRAL turn gets the event and no edge. "Exhibits frustration:
        neutral" is not a fact about the passenger, and writing it would bury
        the real edges in the passenger graph.
        """
        event = self.append_event(
            {
                "kind": "frustration",
                "session_id": session_id,
                "customer_id": customer_id,
                "category": assessment.category.value,
                "confidence": assessment.confidence,
                "signals": list(assessment.signals),
                "escalation_recommended": assessment.escalation_recommended,
                "low_confidence": assessment.low_confidence,
                "detector": assessment.source,
            }
        )
        if assessment.category is not FrustrationCategory.NEUTRAL:
            self.append_edge(
                {
                    "customer_id": customer_id,
                    "session_id": session_id,
                    "from_id": customer_id or session_id,
                    "from_type": "Customer" if customer_id else "Session",
                    "rel": "EXHIBITS_FRUSTRATION",
                    "to_id": assessment.category.value,
                    "to_type": "FrustrationCategory",
                    "reason": ", ".join(assessment.signals) or "category inferred without a named signal",
                    "source": "Frustration classifier",
                    "signals": list(assessment.signals),
                    "confidence": assessment.confidence,
                    "low_confidence": assessment.low_confidence,
                }
            )
        return event

    def record_feedback(
        self,
        *,
        customer_id: str,
        session_id: str,
        feedback,
    ) -> dict[str, Any]:
        """Persist a passenger rating as an event, a memory, and a graph edge."""
        rating = getattr(feedback, "rating", None)
        sentiment = getattr(feedback, "sentiment", None) or "mixed"
        comment = getattr(feedback, "comment", None)
        if isinstance(feedback, dict):
            rating = feedback.get("rating")
            sentiment = feedback.get("sentiment") or "mixed"
            comment = feedback.get("comment")
        bits = [f"{rating}/5" if rating is not None else None, sentiment]
        if comment:
            bits.append(comment.strip())
        fact = "Service feedback: " + ", ".join(part for part in bits if part) + "."
        event = self.append_event(
            {
                "kind": "feedback",
                "session_id": session_id,
                "customer_id": customer_id,
                "rating": rating,
                "comment": comment,
                "sentiment": sentiment,
            }
        )
        self.remember_fact(customer_id, fact, "customer feedback")
        node_id = f"feedback-{rating}" if rating is not None else f"feedback-{sentiment}"
        self.append_edge(
            {
                "customer_id": customer_id,
                "session_id": session_id,
                "from_id": customer_id,
                "from_type": "Customer",
                "rel": "GAVE_FEEDBACK",
                "to_id": node_id,
                "to_type": "Feedback",
                "reason": fact,
                "source": "Customer feedback",
                "label": f"{rating}/5" if rating is not None else sentiment,
                "rating": rating,
                "sentiment": sentiment,
            }
        )
        return event

    def upsert_session(self, customer_id: str, session) -> dict[str, Any]:
        """Write the passenger's live conversation so the next login can restore it."""
        payload = session.model_dump() if hasattr(session, "model_dump") else dict(session)
        payload["customer_id"] = customer_id
        payload.pop("cleared", None)
        self.sessions[customer_id] = payload
        self._persist("sessions", f"session-{customer_id}", payload)
        return payload

    def load_session(self, customer_id: str) -> dict[str, Any] | None:
        row = self.sessions.get(customer_id)
        if not row:
            return None
        if row.get("cleared"):
            return {
                "session_id": row.get("session_id") or f"session-{customer_id}",
                "customer_id": customer_id,
                "identified": True,
                "messages": [],
            }
        return row

    def clear_session(self, customer_id: str) -> None:
        marker = {
            "customer_id": customer_id,
            "session_id": f"session-{customer_id}",
            "identified": True,
            "messages": [],
            "cleared": True,
        }
        self.sessions[customer_id] = marker
        self._persist("sessions", f"session-{customer_id}", marker)

    def conversation_for(self, customer_id: str) -> dict[str, Any]:
        """What the customer UI should show: this passenger's transcript, nobody else's."""
        row = self.load_session(customer_id)
        messages = list((row or {}).get("messages") or [])
        if not messages and customer_id not in self.sessions:
            case = self.cases.get(f"case-{customer_id}") or {}
            messages = list(case.get("transcript") or [])
            if messages:
                row = {
                    "session_id": f"session-{customer_id}",
                    "customer_id": customer_id,
                    "identified": True,
                    "messages": messages,
                    "executed_actions": list(case.get("action_taken") or []),
                    "escalated_to_human": case.get("status") == "escalated",
                    "feedback": case.get("feedback"),
                }
        return {
            "session_id": (row or {}).get("session_id"),
            "messages": messages,
            "executed_actions": list((row or {}).get("executed_actions") or []),
            "escalated_to_human": bool((row or {}).get("escalated_to_human")),
            "resolved_by_customer": bool((row or {}).get("resolved_by_customer")),
            "feedback": (row or {}).get("feedback"),
        }

    def upsert_case(self, case: dict[str, Any]) -> dict[str, Any]:
        case_id = case.get("id") or str(uuid4())
        existing = self.cases.get(case_id) or {}
        case["id"] = case_id
        case["created_at"] = case.get("created_at") or existing.get("created_at") or ISO()
        case["updated_at"] = ISO()
        self.cases[case_id] = case
        self._persist("cases", case_id, case)
        return case

    def list_cases(self) -> list[dict[str, Any]]:
        return sorted(self.cases.values(), key=lambda c: c.get("updated_at", ""), reverse=True)

    def get_case(self, case_id: str) -> dict[str, Any] | None:
        found = self.cases.get(case_id)
        if not found:
            return None
        customer_id = found.get("customer_id")
        if customer_id and not found.get("timeline"):
            found = {
                **found,
                "timeline": [e for e in self.events if e.get("customer_id") == customer_id][-50:],
            }
        return found

    def passenger_360(self, customer_id: str) -> dict[str, Any] | None:
        p = self.passengers.get(customer_id)
        if not p:
            return None
        return {
            "passenger": p,
            "bookings": [b for b in self.bookings if b["customer_id"] == customer_id],
            "events": [e for e in self.events if e.get("customer_id") == customer_id],
            "cases": [c for c in self.cases.values() if c.get("customer_id") == customer_id],
        }

    def graph_for(self, customer_id: str) -> dict[str, Any]:
        edges = [e for e in self.graph_edges if e.get("customer_id") == customer_id]
        nodes: dict[str, dict[str, Any]] = {}
        for e in edges:
            nodes[e["from_id"]] = {
                "id": e["from_id"],
                "type": e.get("from_type"),
                "label": self._graph_label(e["from_id"], e.get("from_type") or "Unknown"),
            }
            nodes[e["to_id"]] = {
                "id": e["to_id"],
                "type": e.get("to_type"),
                "label": self._graph_label(e["to_id"], e.get("to_type") or "Unknown", e.get("reason") if e.get("to_type") == "Disruption" else None),
            }
        customer = self.passengers.get(customer_id)
        if customer:
            nodes[customer_id] = {"id": customer_id, "type": "Customer", "label": customer["name"]}
        return {"nodes": list(nodes.values()), "edges": edges}

    def knowledge_graph(self) -> dict[str, Any]:
        """The live passenger knowledge base, as a graph Operations can draw.

        Dedupes (from, rel, to) so a conversation that retrieved the same booking
        five times still shows one HAS_BOOKING edge. Raw writes stay in
        `graph_edges` for audit.
        """
        nodes: dict[str, dict[str, Any]] = {}
        unique: dict[tuple[str, str, str], dict[str, Any]] = {}
        types: dict[str, int] = {}
        rels: dict[str, int] = {}

        def ensure(node_id: str | None, node_type: str | None, hint: str | None = None) -> None:
            if not node_id:
                return
            kind = node_type or "Unknown"
            existing = nodes.get(node_id)
            label = self._graph_label(node_id, kind, hint)
            if existing is None:
                nodes[node_id] = {"id": node_id, "type": kind, "label": label}
                types[kind] = types.get(kind, 0) + 1
            elif hint and (not existing.get("label") or existing["label"] == node_id):
                existing["label"] = label

        for edge in self.graph_edges:
            from_id = edge.get("from_id")
            to_id = edge.get("to_id")
            rel = edge.get("rel") or "RELATED"
            if not from_id or not to_id:
                continue
            ensure(from_id, edge.get("from_type"), edge.get("label"))
            ensure(to_id, edge.get("to_type"), edge.get("reason") if edge.get("to_type") == "Disruption" else None)
            key = (str(from_id), str(rel), str(to_id))
            previous = unique.get(key)
            if previous is None:
                unique[key] = {
                    "id": edge.get("id"),
                    "from_id": from_id,
                    "to_id": to_id,
                    "rel": rel,
                    "reason": edge.get("reason"),
                    "source": edge.get("source"),
                    "customer_id": edge.get("customer_id"),
                    "status": edge.get("status"),
                    "action": edge.get("action"),
                    "low_confidence": edge.get("low_confidence"),
                    "writes": 1,
                    "ts": edge.get("ts"),
                }
                rels[rel] = rels.get(rel, 0) + 1
            else:
                previous["writes"] = int(previous.get("writes") or 1) + 1
                previous["ts"] = edge.get("ts") or previous.get("ts")

        return {
            "nodes": list(nodes.values()),
            "edges": list(unique.values()),
            "writes": len(self.graph_edges),
            "unique_edges": len(unique),
            "types": dict(sorted(types.items(), key=lambda kv: -kv[1])),
            "relations": dict(sorted(rels.items(), key=lambda kv: -kv[1])),
            "kb_backend": self.backend,
            "note": "Edges are written as conversations happen. This is the same graph_edges store, not a side table.",
        }

    def _graph_label(self, node_id: str, node_type: str, hint: str | None = None) -> str:
        if node_type == "Customer":
            passenger = self.passengers.get(node_id)
            if passenger:
                return passenger.get("name") or node_id
        if node_type == "Booking":
            booking = next((row for row in self.bookings if row.get("id") == node_id), None)
            if booking:
                return booking.get("flight") or booking.get("pnr") or node_id
        if node_type == "FrustrationCategory":
            return node_id.replace("_", " ")
        if node_type == "Disruption":
            return (hint or node_id).replace("_", " ")
        if node_type == "PolicyRule":
            return node_id
        if node_type == "Session":
            return f"session {node_id[-6:]}" if len(node_id) > 8 else node_id
        if node_type == "Feedback":
            return hint or node_id.replace("feedback-", "").replace("_", " ")
        return hint or node_id

    def operations(self) -> dict[str, Any]:
        """Lightweight dashboard numbers. Policy is not computed here."""
        cases = list(self.cases.values())
        total = len(cases)
        resolved = [c for c in cases if c.get("status") == "resolved"]
        escalated = [c for c in cases if c.get("status") == "escalated"]
        open_cases = [c for c in cases if c.get("status") == "open"]
        durations = [
            seconds
            for c in resolved
            if (seconds := _seconds_between(c.get("created_at"), c.get("resolved_at") or c.get("updated_at"))) is not None
        ]
        return {
            "total_cases": total,
            "resolved_cases": len(resolved),
            "escalated_cases": len(escalated),
            "open_cases": len(open_cases),
            "resolution_rate": round(len(resolved) / total, 4) if total else 0.0,
            "average_resolution_seconds": round(sum(durations) / len(durations)) if durations else None,
        }

    def analytics(self) -> dict[str, Any]:
        decisions = [e for e in self.events if e.get("kind") == "decision"]
        escalations = [e for e in self.events if e.get("kind") == "escalation"]
        return {
            "passengers": len(self.passengers),
            "events": len(self.events),
            "cases": len(self.cases),
            "escalations": len(escalations),
            "decisions": len(decisions),
            "kb_backend": self.backend,
            "seeded_members": sum(1 for p in self.passengers.values() if p.get("account_origin") == "seeded"),
            "self_service_members": sum(1 for p in self.passengers.values() if p.get("account_origin") == "self_service"),
            "containment": self.containment(),
            "operations": self.operations(),
            "frustration": self.frustration(),
            "note": "Operations metrics are derived from cases the resolution agent already wrote.",
        }

    def frustration(self) -> dict[str, Any]:
        """How distressed the traffic was, and whether distress cost containment.

        Low-confidence observations are reported in their own buckets and are
        absent from every primary count. Merging them would let a regex guess
        move a number an operations decision is made on.
        """
        events = [e for e in self.events if e.get("kind") == "frustration"]
        if not events:
            return {
                "observations": 0,
                "note": "No frustration observations yet. Run a conversation to populate this.",
            }

        confident = [e for e in events if not e.get("low_confidence")]
        unconfirmed = [e for e in events if e.get("low_confidence")]

        return {
            "observations": len(events),
            "counted_observations": len(confident),
            "by_category": _category_counts(confident),
            "low_confidence_observations": len(unconfirmed),
            "low_confidence_by_category": _category_counts(unconfirmed),
            "escalation_recommended": sum(1 for e in confident if e.get("escalation_recommended")),
            "detectors": _tally(e.get("detector") or "unknown" for e in confident),
            "containment_by_category": self._containment_by_category(confident),
            "graph": self._frustration_graph(),
            "note": (
                "Primary counts exclude low_confidence observations, which are logged for "
                "audit and await corroboration. Category is a signal: it never granted, "
                "denied, or reordered eligibility, only presentation order and tone."
            ),
        }

    def _containment_by_category(self, confident: list[dict[str, Any]]) -> dict[str, Any]:
        """Did high frustration correlate with needing a human?

        Keyed on the conversation's *peak* category, because a passenger who
        was distressed and then calmed down was still a distressed contact.
        """
        peak: dict[str, FrustrationCategory] = {}
        for event in confident:
            session_id = event.get("session_id")
            if not session_id:
                continue
            try:
                category = FrustrationCategory(event.get("category"))
            except ValueError:
                continue
            current = peak.get(session_id)
            if current is None or FRUSTRATION_SEVERITY.index(category) > FRUSTRATION_SEVERITY.index(current):
                peak[session_id] = category

        buckets: dict[str, dict[str, Any]] = {}
        for turn in self.events:
            if turn.get("kind") != "turn" or "contained" not in turn:
                continue
            category = peak.get(turn.get("session_id"))
            if category is None:
                continue
            bucket = buckets.setdefault(
                category.value, {"turns": 0, "contained_turns": 0, "escalated_turns": 0}
            )
            bucket["turns"] += 1
            if turn.get("contained"):
                bucket["contained_turns"] += 1
            else:
                bucket["escalated_turns"] += 1

        for bucket in buckets.values():
            bucket["containment_rate"] = round(bucket["contained_turns"] / bucket["turns"], 4)
        return {
            category.value: buckets[category.value]
            for category in FRUSTRATION_SEVERITY
            if category.value in buckets
        }

    def _frustration_graph(self) -> dict[str, Any]:
        """Aggregate the EXHIBITS_FRUSTRATION edges themselves.

        Read from `graph_edges` rather than from a parallel table, so what ops
        sees is the same audit trail the passenger graph is drawn from.
        """
        edges = [e for e in self.graph_edges if e.get("rel") == "EXHIBITS_FRUSTRATION"]
        counted = [e for e in edges if not e.get("low_confidence")]
        signals_by_category: dict[str, dict[str, int]] = {}
        for edge in counted:
            bucket = signals_by_category.setdefault(edge.get("to_id") or "unknown", {})
            for signal in edge.get("signals") or []:
                bucket[signal] = bucket.get(signal, 0) + 1
        return {
            "edge": "EXHIBITS_FRUSTRATION",
            "edges": len(edges),
            "counted_edges": len(counted),
            "low_confidence_edges": len(edges) - len(counted),
            "passengers": len({e.get("customer_id") for e in counted if e.get("customer_id")}),
            "top_signals_by_category": {
                category: dict(sorted(signals.items(), key=lambda kv: (-kv[1], kv[0]))[:5])
                for category, signals in signals_by_category.items()
            },
        }

    def containment(self) -> dict[str, Any]:
        """How much of the work needed no human, and where authority ran out.

        Only turns recorded with telemetry count, so histories written before
        measurement existed cannot inflate the rate.
        """
        turns = [e for e in self.events if e.get("kind") == "turn" and "contained" in e]
        if not turns:
            return {
                "turns": 0,
                "note": "No measured turns yet. Run a conversation to populate this.",
            }

        contained = [t for t in turns if t.get("contained")]
        by_reason: dict[str, int] = {}
        duty_of_care = {reason.value for reason in DUTY_OF_CARE_REASONS}
        distress_turns = 0
        for turn in turns:
            reasons = turn.get("escalation_reasons") or []
            for reason in reasons:
                by_reason[reason] = by_reason.get(reason, 0) + 1
            if any(reason in duty_of_care for reason in reasons):
                distress_turns += 1

        claimed = sum(int(t.get("decisions") or 0) for t in turns)
        cited = sum(int(t.get("grounded_decisions") or 0) for t in turns)
        spend = sum(float(t.get("est_cost_usd") or 0.0) for t in turns)
        latencies = sorted(int(t.get("latency_ms") or 0) for t in turns)

        return {
            "turns": len(turns),
            "contained_turns": len(contained),
            "containment_rate": round(len(contained) / len(turns), 4),
            "escalated_turns": len(turns) - len(contained),
            "escalations_by_reason": dict(sorted(by_reason.items(), key=lambda kv: -kv[1])),
            # Duty-of-care handovers are not an authority limit the data pack
            # draws, so they are counted apart rather than read as one.
            "distress_escalations": distress_turns,
            "authority_escalations": sum(
                count for reason, count in by_reason.items() if reason not in duty_of_care
            ),
            "decisions_claimed": claimed,
            "decisions_cited": cited,
            "grounding_coverage": round(cited / claimed, 4) if claimed else None,
            "degraded_turns": sum(1 for t in turns if t.get("degraded")),
            "p50_latency_ms": _percentile(latencies, 50),
            "p95_latency_ms": _percentile(latencies, 95),
            "llm_calls": sum(int(t.get("llm_calls") or 0) for t in turns),
            "prompt_tokens": sum(int(t.get("prompt_tokens") or 0) for t in turns),
            "completion_tokens": sum(int(t.get("completion_tokens") or 0) for t in turns),
            "est_spend_usd": round(spend, 6),
            "est_cost_per_turn_usd": round(spend / len(turns), 6),
            "est_cost_per_contained_turn_usd": round(spend / len(contained), 6) if contained else None,
            "note": (
                "Every authority escalation is a policy boundary, not an agent failure. "
                "Read containment_rate alongside escalations_by_reason, and read "
                "distress_escalations apart from it: a duty-of-care handover means the "
                "passenger needed a person, not that a rule ran out."
            ),
        }
