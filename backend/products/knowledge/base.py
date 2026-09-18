from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from data.loader import load_bookings, load_customers, load_fixtures
from models.schemas import Booking, Customer, KnownFact, RuleHit, ScenarioFixture, StyleHit, TurnHit
from products.knowledge.corpus import policy_clauses, style_docs
from products.knowledge.scoring import score

ISO = lambda: datetime.now(timezone.utc).isoformat()


class PassengerKnowledgeStore(ABC):
    """Product: passenger 360 / events / cases / graph. Clients never construct a backend."""

    backend: Literal["elasticsearch", "json"]

    def __init__(self) -> None:
        self.backend = "json"
        self.passengers: dict[str, dict[str, Any]] = {}
        self.bookings: list[dict[str, Any]] = []
        self.events: list[dict[str, Any]] = []
        self.cases: dict[str, dict[str, Any]] = {}
        self.graph_edges: list[dict[str, Any]] = []
        self.accounts: dict[str, dict[str, Any]] = {}
        self.policy_docs: list[dict[str, Any]] = policy_clauses()
        self.style_samples: list[dict[str, Any]] = style_docs()
        self.memories: list[dict[str, Any]] = []
        self._init_backend()
        self.seed()

    @abstractmethod
    def _init_backend(self) -> None:
        raise NotImplementedError

    def _persist(self, index: str, doc_id: str, document: dict[str, Any]) -> None:
        """Optional dual-write. JSON product is in-memory only."""

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
            self.accounts[c.email.lower()] = {
                "customer_id": c.id,
                "email": c.email.lower(),
                "password_hash": hasher.hash(SEED_PASSWORD),
            }
            self._persist("passengers", c.id, {k: v for k, v in record.items() if k != "known_facts"})
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
        self.accounts[customer.email.lower()] = {
            "customer_id": customer.id,
            "email": customer.email.lower(),
            "password_hash": password_hash,
        }
        self._persist("passengers", customer.id, customer.model_dump())
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

    def upsert_case(self, case: dict[str, Any]) -> dict[str, Any]:
        case_id = case.get("id") or str(uuid4())
        case["id"] = case_id
        case["updated_at"] = ISO()
        self.cases[case_id] = case
        self._persist("cases", case_id, case)
        return case

    def list_cases(self) -> list[dict[str, Any]]:
        return sorted(self.cases.values(), key=lambda c: c.get("updated_at", ""), reverse=True)

    def get_case(self, case_id: str) -> dict[str, Any] | None:
        return self.cases.get(case_id)

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
            nodes[e["from_id"]] = {"id": e["from_id"], "type": e.get("from_type")}
            nodes[e["to_id"]] = {"id": e["to_id"], "type": e.get("to_type")}
        customer = self.passengers.get(customer_id)
        if customer:
            nodes[customer_id] = {"id": customer_id, "type": "Customer", "label": customer["name"]}
        return {"nodes": list(nodes.values()), "edges": edges}

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
            "note": "Live passenger directory. Assignment profiles are pre-enrolled members; new passengers can onboard.",
        }
