from __future__ import annotations

from typing import Any

from data.loader import load_bookings, load_customers
from products.knowledge.base import ISO, PassengerKnowledgeStore
from models.schemas import TurnHit

DOCUMENTS = frozenset(
    {"events", "cases", "graph_edges", "memories", "sessions", "kb_entries", "kb_pending_entries"}
)

# CREATE EXTENSION vector is required (pgvector) before this query can run.
# `<=>` is cosine distance; text-embedding-3-small is normalized, so similarity
# is 1 - distance. The corpus is approved kb_entries only — never pending rows
# and never policy clauses.
SEMANTIC_SEARCH_SQL = """
SELECT body, 1 - (embedding <=> %s::vector) AS score
FROM documents
WHERE collection = 'kb_entries'
  AND embedding IS NOT NULL
  AND coalesce(body->>'status', 'approved') = 'approved'
  AND 1 - (embedding <=> %s::vector) >= %s
ORDER BY embedding <=> %s::vector
LIMIT %s
"""


def _as_vector(values: list[float]) -> str:
    return "[" + ",".join(str(float(x)) for x in values) + "]"


def _json(document: dict[str, Any]):
    from psycopg.types.json import Json

    return Json(document)


class PostgresKnowledgeStore(PassengerKnowledgeStore):
    """Concrete product: Postgres is the system of record, RAM is a cache.

    Seed upserts the assignment demo passengers without deleting self-service
    accounts, cases, or memories written in an earlier process.
    """

    def _init_backend(self) -> None:
        from persistence.postgres import connect

        connect()
        self.backend = "postgres"

    def seed(self) -> None:
        self._hydrate()
        self._upsert_seed_pack()

    def _hydrate(self) -> None:
        from persistence.postgres import connect

        conn = connect()
        self.passengers = {}
        for row in conn.execute("SELECT id, body FROM passengers"):
            body = dict(row[1])
            body.setdefault("known_facts", [])
            self.passengers[row[0]] = body

        self.accounts = {}
        for row in conn.execute("SELECT email, customer_id, password_hash FROM accounts"):
            email = row[0]
            self.accounts[email] = {
                "customer_id": row[1],
                "email": email,
                "password_hash": row[2],
            }

        self.bookings = [dict(row[0]) for row in conn.execute("SELECT body FROM bookings")]

        self.events = []
        self.cases = {}
        self.graph_edges = []
        self.memories = []
        self.sessions = {}
        self.kb_entries = {}
        self.kb_pending_entries = {}
        for collection, _doc_id, body in conn.execute("SELECT collection, id, body FROM documents"):
            document = dict(body)
            if collection == "events":
                self.events.append(document)
            elif collection == "cases":
                self.cases[document.get("id") or _doc_id] = document
            elif collection == "graph_edges":
                self.graph_edges.append(document)
            elif collection == "memories":
                self.memories.append(document)
            elif collection == "sessions":
                customer_id = document.get("customer_id")
                if customer_id:
                    self.sessions[customer_id] = document
            elif collection == "kb_entries":
                self.kb_entries[document.get("id") or _doc_id] = document
            elif collection == "kb_pending_entries":
                self.kb_pending_entries[document.get("id") or _doc_id] = document

        self.events.sort(key=lambda e: e.get("ts") or "")
        self.graph_edges.sort(key=lambda e: e.get("ts") or "")
        self.memories.sort(key=lambda e: e.get("ts") or "")

        facts: dict[str, list[str]] = {}
        for memory in self.memories:
            customer_id = memory.get("customer_id")
            fact = memory.get("fact")
            if customer_id and fact:
                facts.setdefault(customer_id, []).append(fact)
        for customer_id, record in self.passengers.items():
            record["known_facts"] = facts.get(customer_id, record.get("known_facts") or [])

    def _upsert_seed_pack(self) -> None:
        from factories.hasher_factory import HasherFactory
        from products.onboarding.self_service import SEED_PASSWORD

        hasher = HasherFactory.create()
        customers = load_customers()
        bookings = load_bookings()
        seed_booking_ids = {b.id for b in bookings}

        for customer in customers:
            existing = self.passengers.get(customer.id) or {}
            record = customer.model_dump() | {
                "known_facts": existing.get("known_facts") or [],
                "account_origin": "seeded",
                "created_at": existing.get("created_at") or customer.created_at or ISO(),
            }
            self.passengers[customer.id] = record
            email = customer.email.lower()
            self.accounts[email] = {
                "customer_id": customer.id,
                "email": email,
                "password_hash": hasher.hash(SEED_PASSWORD),
            }
            self._persist("passengers", customer.id, {k: v for k, v in record.items() if k != "known_facts"})
            self._persist("accounts", email, self.accounts[email])

        kept = [b for b in self.bookings if b.get("id") not in seed_booking_ids]
        seeded = [b.model_dump() for b in bookings]
        self.bookings = kept + seeded
        for booking in seeded:
            self._persist("bookings", booking["id"], booking)

    def _persist(self, index: str, doc_id: str, document: dict[str, Any]) -> None:
        from persistence.postgres import connect

        conn = connect()
        if index == "passengers":
            email = (document.get("email") or "").strip().lower()
            body = {k: v for k, v in document.items() if k != "password_hash"}
            conn.execute(
                """
                INSERT INTO passengers (id, email, body) VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET email = EXCLUDED.email, body = EXCLUDED.body
                """,
                (document.get("id") or doc_id, email, _json(body)),
            )
            return
        if index == "accounts":
            conn.execute(
                """
                INSERT INTO accounts (email, customer_id, password_hash) VALUES (%s, %s, %s)
                ON CONFLICT (email) DO UPDATE SET
                    customer_id = EXCLUDED.customer_id,
                    password_hash = EXCLUDED.password_hash
                """,
                (doc_id, document["customer_id"], document["password_hash"]),
            )
            return
        if index == "bookings":
            conn.execute(
                """
                INSERT INTO bookings (id, customer_id, body) VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET customer_id = EXCLUDED.customer_id, body = EXCLUDED.body
                """,
                (document.get("id") or doc_id, document.get("customer_id"), _json(document)),
            )
            return
        if index in DOCUMENTS:
            self._upsert_document(conn, index, doc_id, document)
            return

    def _upsert_document(self, conn, index: str, doc_id: str, document: dict[str, Any]) -> None:
        vector = self._embedding_literal(index, document)
        if vector is not None:
            try:
                conn.execute(
                    """
                    INSERT INTO documents (collection, id, customer_id, body, embedding)
                    VALUES (%s, %s, %s, %s, %s::vector)
                    ON CONFLICT (collection, id) DO UPDATE SET
                        customer_id = EXCLUDED.customer_id,
                        body = EXCLUDED.body,
                        embedding = COALESCE(EXCLUDED.embedding, documents.embedding),
                        updated_at = now()
                    """,
                    (index, doc_id, document.get("customer_id"), _json(document), vector),
                )
                return
            except Exception:
                pass
        conn.execute(
            """
            INSERT INTO documents (collection, id, customer_id, body) VALUES (%s, %s, %s, %s)
            ON CONFLICT (collection, id) DO UPDATE SET
                customer_id = EXCLUDED.customer_id,
                body = EXCLUDED.body,
                updated_at = now()
            """,
            (index, doc_id, document.get("customer_id"), _json(document)),
        )

    def _embedding_literal(self, index: str, document: dict[str, Any]) -> str | None:
        if index != "kb_entries" or document.get("status") != "approved":
            return None
        stored = document.get("embedding")
        if stored:
            return _as_vector(stored)
        embedder = self._embedding_client()
        if not embedder.enabled:
            return None
        vector = embedder.embed(document.get("message") or "")
        return _as_vector(vector) if vector else None

    def semantic_search(self, text: str, k: int, min_score: float) -> list[TurnHit]:
        embedder = self._embedding_client()
        query = embedder.embed(text) if embedder.enabled else None
        if not query:
            return []
        try:
            from persistence.postgres import connect

            # CREATE EXTENSION vector is required (pgvector) for the <=> operator.
            rows = connect().execute(SEMANTIC_SEARCH_SQL, (_as_vector(query), _as_vector(query), min_score, _as_vector(query), k))
            hits = [
                TurnHit(
                    id=body.get("id") or "",
                    ts=body.get("ts") or "",
                    message=body.get("message") or "",
                    reply=body.get("phrasing") or body.get("reply") or "",
                    score=round(float(score), 4),
                )
                for body, score in ((dict(row[0]), row[1]) for row in rows)
                if float(score) >= min_score
            ]
            if hits:
                return hits
        except Exception:
            pass
        from products.knowledge.json_store import JsonKnowledgeStore

        return JsonKnowledgeStore.semantic_search(self, text, k, min_score)

    def _drop(self, index: str, doc_id: str) -> None:
        from persistence.postgres import connect

        conn = connect()
        if index in DOCUMENTS:
            conn.execute("DELETE FROM documents WHERE collection = %s AND id = %s", (index, doc_id))
