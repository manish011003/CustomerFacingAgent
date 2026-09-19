"""Prior-resolution reuse and the ops approve/reject gate."""

from uuid import uuid4

from fastapi.testclient import TestClient

from agent.kb_match import KB_MATCH_THRESHOLD, ground_prior_resolution
from agent.loop import handle_chat, reset_session
from agent.retrieve import strip_style_identifiers
from factories.onboarding_factory import OnboardingFactory
from factories.staff_factory import StaffFactory
from kb.store import store
from main import app
from models.schemas import FrustrationAssessment, FrustrationCategory, SessionMemory
from products.auth.staff import DEFAULT_STAFF_EMAIL, DEFAULT_STAFF_PASSWORD
from products.knowledge.json_store import JsonKnowledgeStore
from products.onboarding.self_service import SEED_PASSWORD
from tests.test_embeddings import ScriptedEmbedder


REFUND = [1.0, 0.0, 0.0]
OTHER = [0.0, 0.0, 1.0]


def _scripted() -> ScriptedEmbedder:
    return ScriptedEmbedder({"refund": REFUND, "cancelled": REFUND}, default=OTHER)


def test_strip_style_identifiers_removes_amounts_pnrs_and_flights():
    cleaned = strip_style_identifiers(
        "I can see flight SK-190 was cancelled. PNR SK4821X qualifies for a meal voucher ₹500."
    )
    assert "SK-190" not in cleaned
    assert "SK4821X" not in cleaned
    assert "₹500" not in cleaned
    assert "500" not in cleaned
    assert "[flight]" in cleaned
    assert "[PNR]" in cleaned
    assert "[amount]" in cleaned


def test_style_retrieval_strips_sample_identifiers():
    from agent import retrieve
    from agent.planner import plan_retrieval
    from data.loader import load_customers
    from models.schemas import Extraction

    customer = next(c for c in load_customers() if c.id == "CUST-PRIYA")
    plan = plan_retrieval(Extraction(raw_text="my flight got cancelled"), SessionMemory(session_id="s"))
    plan.need_style = True
    retrieval = retrieve.run(plan=plan, customer=customer, evaluation=None)
    if retrieval.style:
        assert "SK-190" not in retrieval.style.agent
        assert "₹" not in retrieval.style.agent


def test_close_match_adds_stripped_phrasing_to_the_packet():
    store._embedder = _scripted()
    store.index_kb_entry(
        {
            "id": "kb-close",
            "message": "I want a refund for the cancelled flight",
            "phrasing": "I can rebook flight SK-190 or refund PNR SK4821X. Voucher ₹500.",
        }
    )
    sid = str(uuid4())
    reset_session(sid, "CUST-PRIYA")
    response = handle_chat(sid, "I want a refund for the cancelled flight", "CUST-PRIYA")
    phrasing = response.context_packet.get("prior_resolution_phrasing")
    assert phrasing
    assert "SK-190" not in phrasing
    assert "SK4821X" not in phrasing
    assert "₹500" not in phrasing
    assert response.context_packet["kb_match"]["matched"] is True
    assert response.context_packet["kb_match"]["score"] >= KB_MATCH_THRESHOLD
    assert store.kb_pending_entries == {} or all(
        row.get("message") != "I want a refund for the cancelled flight"
        for row in store.kb_pending_entries.values()
        if row.get("status") == "pending"
    )


def test_below_threshold_queues_pending_and_does_not_index():
    store._embedder = _scripted()
    store.index_kb_entry(
        {
            "id": "kb-refund-only",
            "message": "I want a refund for the cancelled flight",
            "phrasing": "Refund to the original method.",
        }
    )
    sid = str(uuid4())
    reset_session(sid, "CUST-PRIYA")
    unique = f"unseen-kb-phrase-{uuid4().hex}"
    response = handle_chat(sid, unique, "CUST-PRIYA")
    match = response.context_packet["kb_match"]
    assert match["matched"] is False
    assert match["pending_id"]
    pending = store.kb_pending_entries[match["pending_id"]]
    assert pending["status"] == "pending"
    assert pending["message"] == unique
    assert match["pending_id"] not in store.kb_entries
    hits = store.semantic_search(unique, k=3, min_score=0.0)
    assert all(hit.id != match["pending_id"] for hit in hits)


def test_approve_embeds_and_indexes_reject_does_not():
    kb = JsonKnowledgeStore()
    kb._embedder = _scripted()
    pending = kb.queue_pending_kb_entry(
        {"id": "pend-1", "message": "I want a refund for the cancelled flight", "phrasing": "Refund approved tone."}
    )
    rejected = kb.queue_pending_kb_entry(
        {"id": "pend-2", "message": "something far away from the corpus", "phrasing": "ignore me"}
    )
    assert kb.semantic_search("I want a refund for the cancelled flight", k=3, min_score=0.5) == []

    approved = kb.approve_pending_kb_entry(pending["id"])
    assert approved["status"] == "approved"
    assert approved["id"] in kb.kb_entries
    hits = kb.semantic_search("I want a refund for the cancelled flight", k=3, min_score=0.5)
    assert hits and hits[0].id == pending["id"]
    assert "Refund approved tone" in hits[0].reply

    kb.reject_pending_kb_entry(rejected["id"])
    assert kb.kb_pending_entries[rejected["id"]]["status"] == "rejected"
    assert rejected["id"] not in kb.kb_entries
    assert all(hit.id != rejected["id"] for hit in kb.semantic_search("something far away", k=5, min_score=0.0))


def test_approve_and_reject_require_staff(monkeypatch):
    monkeypatch.setenv("STAFF_EMAIL", DEFAULT_STAFF_EMAIL)
    monkeypatch.setenv("STAFF_PASSWORD", DEFAULT_STAFF_PASSWORD)
    StaffFactory.reset()
    store._embedder = _scripted()
    pending = store.queue_pending_kb_entry(
        {"message": "I want a refund for the cancelled flight", "phrasing": "Tone only."}
    )
    client = TestClient(app)

    denied = client.post(f"/api/kb/pending/{pending['id']}/approve")
    assert denied.status_code == 401

    passenger = OnboardingFactory.create().login("priya.nair@example.com", SEED_PASSWORD)
    as_passenger = client.post(
        f"/api/kb/pending/{pending['id']}/approve",
        headers={"Authorization": f"Bearer {passenger['token']}"},
    )
    assert as_passenger.status_code == 401

    staff = client.post(
        "/api/auth/staff/login",
        json={"email": DEFAULT_STAFF_EMAIL, "password": DEFAULT_STAFF_PASSWORD},
    )
    token = staff.json()["token"]
    approved = client.post(
        f"/api/kb/pending/{pending['id']}/approve",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
    assert pending["id"] in store.kb_entries

    other = store.queue_pending_kb_entry({"message": "another unseen phrasing"})
    rejected = client.post(
        f"/api/kb/pending/{other['id']}/reject",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "rejected"
    assert other["id"] not in store.kb_entries


def test_ground_is_idempotent_within_a_turn():
    store._embedder = _scripted()
    session = SessionMemory(session_id="once")
    first = ground_prior_resolution(
        "hello unique miss",
        session=session,
        assessment=FrustrationAssessment(category=FrustrationCategory.NEUTRAL, confidence=0.9),
    )
    second = ground_prior_resolution("hello unique miss", session=session)
    assert first.pending_id == second.pending_id
    assert sum(1 for row in store.kb_pending_entries.values() if row.get("session_id") == "once") == 1
