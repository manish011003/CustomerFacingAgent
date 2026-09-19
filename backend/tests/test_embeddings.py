"""Embedding factory and additive semantic_search. Nothing here calls OpenAI.

Lexical `score()` / `search_policy` stay on their own path — these tests only
exercise approved kb_entries, the corpus semantic_search reads.
"""

from __future__ import annotations

from embeddings.client import EMBEDDING_MODEL, EmbeddingClient
from factories.embedding_factory import EmbeddingFactory
from products.knowledge.elasticsearch_store import ElasticsearchKnowledgeStore
from products.knowledge.json_store import JsonKnowledgeStore
from products.knowledge.postgres_store import SEMANTIC_SEARCH_SQL, PostgresKnowledgeStore


class ScriptedEmbedder:
    """Deterministic vectors so cosine ranking can be asserted without a key."""

    enabled = True
    model = "scripted"

    def __init__(self, table: dict[str, list[float]], default: list[float] | None = None) -> None:
        self.table = table
        self.default = default or [0.0, 0.0, 1.0]

    def embed(self, text: str) -> list[float] | None:
        for needle, vector in self.table.items():
            if needle in (text or ""):
                return list(vector)
        return list(self.default)


class _FakeIndices:
    def exists(self, index):
        return True

    def create(self, index, mappings):
        return None

    def refresh(self, index):
        return None

    def put_mapping(self, index, properties):
        return None


class _FakeEs:
    def __init__(self, hits=None, raises=False):
        self.indices = _FakeIndices()
        self.hits = hits or []
        self.raises = raises
        self.last_call = None

    def ping(self):
        return True

    def index(self, **kwargs):
        return None

    def search(self, **kwargs):
        self.last_call = kwargs
        if self.raises:
            raise RuntimeError("elasticsearch unavailable")
        return {"hits": {"hits": self.hits}}


class _StubEsStore(ElasticsearchKnowledgeStore):
    def __init__(self, hits=None, raises=False):
        self.fake = _FakeEs(hits, raises)
        super().__init__()

    def _init_backend(self) -> None:
        self._es = self.fake
        self.backend = "elasticsearch"


class _StubPgStore(PostgresKnowledgeStore):
    def _init_backend(self) -> None:
        self.backend = "postgres"

    def seed(self) -> None:
        return None

    def _persist(self, index, doc_id, document) -> None:
        return None


REFUND = [1.0, 0.0, 0.0]
HOTEL = [0.0, 1.0, 0.0]


def _embedder() -> ScriptedEmbedder:
    return ScriptedEmbedder(
        {
            "refund": REFUND,
            "hotel": HOTEL,
        },
        default=[0.0, 0.0, 1.0],
    )


def _approved_corpus(store, embedder) -> None:
    store._embedder = embedder
    store.index_kb_entry(
        {
            "id": "kb-refund",
            "customer_id": "CUST-PRIYA",
            "ts": "2026-09-18T10:00:00+00:00",
            "message": "I want a refund for the cancelled flight",
            "phrasing": "I can process a refund to the original payment method.",
        }
    )
    store.queue_pending_kb_entry(
        {
            "id": "kb-hotel-pending",
            "customer_id": "CUST-ARVIND",
            "message": "I need a hotel for this delay",
            "phrasing": "Hotel for delayed hours only is within policy.",
        }
    )
    store.append_event(
        {
            "id": "turn-open",
            "kind": "turn",
            "customer_id": "CUST-OPEN",
            "ts": "2026-09-18T12:00:00+00:00",
            "message": "I want a refund for the cancelled flight",
            "reply": "still looking into this open case",
        }
    )
    store.upsert_case({"id": "case-CUST-OPEN", "customer_id": "CUST-OPEN", "status": "open"})


# --- factory ----------------------------------------------------------------


def test_disabled_client_never_builds_an_sdk(monkeypatch):
    import openai

    def forbidden(*args, **kwargs):
        raise AssertionError("a disabled embedder must not construct an SDK")

    monkeypatch.setattr(openai, "OpenAI", forbidden)
    client = EmbeddingFactory.disabled()
    assert client.enabled is False
    assert client.embed("refund my flight") is None
    assert client.embed_many(["a", "b"]) == [None, None]
    assert client._sdk is None


def test_create_without_a_key_is_a_disabled_client():
    client = EmbeddingFactory.create()
    assert client.enabled is False
    assert client.model == EMBEDDING_MODEL
    assert EmbeddingClient.from_env().enabled is False


def test_disabled_factory_is_not_the_process_singleton():
    EmbeddingFactory.create()
    disabled = EmbeddingFactory.disabled()
    assert disabled is not EmbeddingFactory.create()
    assert disabled.enabled is False


# --- json cosine ------------------------------------------------------------


def test_json_semantic_search_ranks_resolved_conversations_by_cosine():
    store = JsonKnowledgeStore()
    _approved_corpus(store, _embedder())
    hits = store.semantic_search("I need a refund", k=5, min_score=0.5)
    assert hits
    assert "refund" in hits[0].message.lower()
    assert all("hotel" not in hit.message.lower() for hit in hits)
    assert all("open case" not in hit.reply.lower() for hit in hits)


def test_json_semantic_search_respects_min_score_and_k():
    store = JsonKnowledgeStore()
    _approved_corpus(store, _embedder())
    tight = store.semantic_search("I need a refund", k=5, min_score=1.01)
    assert tight == []
    one = store.semantic_search("I need a refund", k=1, min_score=0.5)
    assert len(one) == 1


def test_json_semantic_search_ignores_open_cases_and_policy_clauses():
    store = JsonKnowledgeStore()
    _approved_corpus(store, _embedder())
    store.policy_docs.append(
        {
            "clause_id": "FAKE#1",
            "rule_id": "FAKE",
            "title": "Refund everything",
            "text": "I want a refund for the cancelled flight",
            "kind": "rule",
        }
    )
    hits = store.semantic_search("I need a refund", k=5, min_score=0.1)
    texts = " ".join(f"{hit.message} {hit.reply}" for hit in hits)
    assert "Refund everything" not in texts
    assert "open case" not in texts
    assert all(hit.message for hit in hits)


def test_json_semantic_search_is_empty_when_embedder_is_disabled():
    store = JsonKnowledgeStore()
    store._embedder = EmbeddingFactory.disabled()
    store.append_event(
        {
            "kind": "turn",
            "customer_id": "CUST-PRIYA",
            "message": "refund please",
            "reply": "processed",
        }
    )
    store.upsert_case({"id": "case-CUST-PRIYA", "customer_id": "CUST-PRIYA", "status": "resolved"})
    assert store.semantic_search("refund", k=3, min_score=0.0) == []


def test_lexical_policy_search_is_untouched_by_semantic_search():
    store = JsonKnowledgeStore()
    _approved_corpus(store, _embedder())
    policy = store.search_policy("hotel delayed hours", scope=["DELAY_COMPENSATION_RULE"], k=1)
    assert policy and policy[0].rule_id == "DELAY_COMPENSATION_RULE"
    semantic = store.semantic_search("I need a refund", k=3, min_score=0.5)
    assert semantic and semantic[0].message
    assert not hasattr(semantic[0], "clause_id")


# --- elasticsearch knn ------------------------------------------------------


def test_elasticsearch_semantic_search_uses_knn_on_dense_vector():
    store = _StubEsStore(
        [
            {
                "_score": 0.99,
                "_source": {
                    "ts": "2026-09-18T10:00:00+00:00",
                    "message": "I want a refund for the cancelled flight",
                    "reply": "refund to original method",
                },
            }
        ]
    )
    store._embedder = _embedder()
    store.index_kb_entry(
        {
            "id": "kb-refund",
            "message": "I want a refund for the cancelled flight",
            "phrasing": "refund to original method",
        }
    )
    hits = store.semantic_search("I need a refund", k=3, min_score=0.5)
    assert hits and "refund" in hits[0].message.lower()
    knn = store.fake.last_call["knn"]
    assert knn["field"] == "embedding"
    assert knn["query_vector"] == REFUND
    filters = knn["filter"]["bool"]["filter"]
    assert {"term": {"status": "approved"}} in filters
    assert store.fake.last_call["index"] == "kb_entries"


def test_elasticsearch_semantic_search_falls_back_when_knn_raises():
    store = _StubEsStore(raises=True)
    _approved_corpus(store, _embedder())
    hits = store.semantic_search("I need a refund", k=3, min_score=0.5)
    assert hits and "refund" in hits[0].message.lower()


# --- postgres pgvector ------------------------------------------------------


def test_postgres_semantic_sql_uses_cosine_operator_and_approved_entries_only():
    assert "<=>" in SEMANTIC_SEARCH_SQL
    assert "vector" in SEMANTIC_SEARCH_SQL
    assert "kb_entries" in SEMANTIC_SEARCH_SQL
    assert "approved" in SEMANTIC_SEARCH_SQL
    assert "pending" not in SEMANTIC_SEARCH_SQL
    assert "policy" not in SEMANTIC_SEARCH_SQL.lower()


def test_postgres_semantic_search_falls_back_to_numpy_when_pgvector_is_down(monkeypatch):
    store = _StubPgStore()
    _approved_corpus(store, _embedder())

    def boom():
        raise RuntimeError("pgvector unavailable")

    monkeypatch.setattr("persistence.postgres.connect", boom)
    hits = store.semantic_search("I need a refund", k=3, min_score=0.5)
    assert hits and "refund" in hits[0].message.lower()


def test_abstract_contract_is_implemented_on_every_product():
    from products.knowledge.base import PassengerKnowledgeStore

    assert "semantic_search" in PassengerKnowledgeStore.__abstractmethods__ or hasattr(
        PassengerKnowledgeStore, "semantic_search"
    )
    for product in (JsonKnowledgeStore, PostgresKnowledgeStore, ElasticsearchKnowledgeStore):
        assert product.semantic_search is not PassengerKnowledgeStore.semantic_search
