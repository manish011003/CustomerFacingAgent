from uuid import uuid4

from agent import retrieve
from agent.context import assemble, narrate, render_respond_prompt, context_contains_forbidden
from agent.extract import extract
from agent.loop import handle_chat
from agent.planner import expand_scope, plan_retrieval
from data.loader import load_bookings, load_customers
from kb.store import store
from models.schemas import RequestType, SessionMemory
from policy.engine import evaluate_policy
from products.knowledge.corpus import policy_clauses
from products.knowledge.elasticsearch_store import ElasticsearchKnowledgeStore

CUSTOMERS = {c.id: c for c in load_customers()}
BOOKINGS = {b.id: b for b in load_bookings()}


def _turn(customer_id: str, booking_id: str, message: str):
    """Build one turn's plan, evaluation, retrieval, and context outside the API."""
    customer = CUSTOMERS[customer_id]
    booking = BOOKINGS[booking_id]
    extraction = extract(message)
    session = SessionMemory(session_id=str(uuid4()), customer_id=customer_id, identified=True)
    plan = plan_retrieval(extraction, session)
    fixture = store.fixture_for(customer_id) if plan.need_fixture else None
    evaluation = evaluate_policy(
        customer,
        booking,
        extraction.requests,
        fare_difference_inr=fixture.fare_difference_inr if fixture else None,
        legal_or_formal=extraction.legal_or_formal,
    )
    plan = expand_scope(plan, customer, booking)
    retrieval = retrieve.run(plan=plan, customer=customer, evaluation=evaluation)
    ctx = assemble(
        session=session,
        customer=customer,
        booking=booking,
        related_bookings=store.bookings_for(customer_id) if plan.need_related_legs else [],
        extraction=extraction,
        evaluation=evaluation,
        fixture=fixture,
        plan=plan,
        retrieval=retrieval,
    )
    return plan, evaluation, retrieval, ctx


# --- corpus is clause level -------------------------------------------------


def test_policy_corpus_is_clause_level_not_rule_level():
    delay = [d for d in policy_clauses() if d["rule_id"] == "DELAY_COMPENSATION_RULE"]
    assert len(delay) == 3
    # No single indexed document may carry two delay bands, or citing one band
    # would hand the model the others to reinterpret.
    for doc in delay:
        bands = sum(
            marker in doc["text"]
            for marker in ("under 3 hours", "more than 3 hours", "more than 5 hours")
        )
        assert bands == 1, doc


def test_every_clause_stays_within_the_retrieval_char_budget():
    for doc in policy_clauses():
        assert len(doc["text"]) <= 400, doc["clause_id"]


# --- planner selectivity ----------------------------------------------------


def test_status_turn_fetches_no_related_legs_fixture_or_request_policy():
    extraction = extract("what happened to my flight")
    assert [r.type for r in extraction.requests] == [RequestType.STATUS]
    plan = plan_retrieval(extraction, SessionMemory(session_id="s"))
    assert plan.need_related_legs is False
    assert plan.need_fixture is False
    assert plan.rule_scope == []
    assert plan.need_recall is False


def test_fare_turn_fetches_the_fixture_and_scopes_to_the_fare_rule():
    extraction = extract("move me to another flight, the fare difference is 2000 rupees")
    plan = plan_retrieval(extraction, SessionMemory(session_id="s"))
    assert plan.need_fixture is True
    assert "FARE_DIFFERENCE_RULE" in plan.rule_scope


def test_recall_only_switches_on_after_the_first_turn():
    extraction = extract("and the refund?")
    first = SessionMemory(session_id="s", messages=[{"role": "user", "content": "hi"}])
    assert plan_retrieval(extraction, first).need_recall is False
    later = SessionMemory(
        session_id="s",
        messages=[
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "..."},
            {"role": "user", "content": "and the refund?"},
        ],
    )
    assert plan_retrieval(extraction, later).need_recall is True


# --- citation correctness ---------------------------------------------------


def test_six_hour_delay_cites_the_over_five_hours_clause_for_hotel():
    _, _, retrieval, _ = _turn(
        "CUST-MEHER", "BK-MEHER-OUT", "I want a full night hotel stay, the fare difference is 2000 rupees"
    )
    hotel = next(h for h in retrieval.rules if h.for_action == "hotel_delayed_hours")
    assert hotel.clause_id == "DELAY_COMPENSATION_RULE#3"
    assert "more than 5 hours" in hotel.text
    waiver = next(h for h in retrieval.rules if h.for_action == "fare_waiver")
    assert waiver.rule_id == "FARE_DIFFERENCE_RULE"
    assert "1,500" in waiver.text


def test_four_hour_delay_never_cites_or_states_the_under_three_hours_band():
    _, _, retrieval, ctx = _turn(
        "CUST-ARVIND", "BK-ARVIND-OUT", "I want hotel accommodation, this delay is long"
    )
    cited = {h.clause_id for h in retrieval.rules}
    assert "DELAY_COMPENSATION_RULE#1" not in cited
    facts = "\n".join(narrate(ctx))
    # The 500 rupee amount belongs to the under-3-hours band only. A 4 hour delay
    # must never surface it, in a citation or in a narrated fact.
    assert "500" not in facts


def test_under_three_hour_delay_does_cite_the_500_rupee_clause():
    short = BOOKINGS["BK-ARVIND-OUT"].model_copy(update={"delay_hours": 2})
    customer = CUSTOMERS["CUST-ARVIND"]
    extraction = extract("can I get a meal voucher")
    session = SessionMemory(session_id="s", customer_id=customer.id, identified=True)
    plan = expand_scope(plan_retrieval(extraction, session), customer, short)
    evaluation = evaluate_policy(customer, short, extraction.requests)
    retrieval = retrieve.run(plan=plan, customer=customer, evaluation=evaluation)
    meal = next(h for h in retrieval.rules if h.for_action == "meal_voucher")
    assert meal.clause_id == "DELAY_COMPENSATION_RULE#1"
    assert "500" in meal.text


def test_citations_stay_inside_the_plan_scope():
    plan, _, retrieval, _ = _turn("CUST-ARVIND", "BK-ARVIND-OUT", "I want hotel accommodation")
    assert retrieval.rules
    for hit in retrieval.rules:
        assert hit.rule_id in plan.rule_scope


# --- prompt safety ----------------------------------------------------------


def test_narrated_prompt_still_hides_other_passengers_and_raw_policy():
    _, _, _, ctx = _turn("CUST-PRIYA", "BK-PRIYA-OUT", "my flight is cancelled, I want a refund")
    prompt = render_respond_prompt(ctx, "my flight is cancelled, I want a refund")
    assert context_contains_forbidden(prompt, "Priya Nair") == []
    assert "Arvind Kulkarni" not in prompt
    assert "Meher Kaur" not in prompt


def test_every_decision_in_the_narration_carries_a_source_or_citation():
    _, evaluation, _, ctx = _turn("CUST-MEHER", "BK-MEHER-OUT", "full night hotel and a higher fare flight")
    lines = narrate(ctx)
    attributions = sum(1 for line in lines if line.startswith("  cited ") or line.startswith("  source: "))
    assert attributions == len(evaluation.decisions)


# --- isolation --------------------------------------------------------------


def test_recall_and_memory_never_cross_passengers():
    handle_chat(str(uuid4()), "my flight is cancelled and I want a refund", "CUST-PRIYA")
    handle_chat(str(uuid4()), "I want hotel accommodation for this delay", "CUST-ARVIND")

    priya = store.recall_turns("CUST-PRIYA", "refund hotel delay cancelled", k=10)
    assert priya, "expected at least one recalled turn for Priya"
    for hit in priya:
        assert "hotel accommodation for this delay" not in hit.message

    for fact in store.known_facts("CUST-ARVIND"):
        assert "refund" not in fact.fact.lower()


# --- Elasticsearch product --------------------------------------------------
# Docker is not required: a stub client proves the query shape and the fallback.


class _FakeIndices:
    def exists(self, index):
        return True

    def create(self, index, mappings):
        return None

    def refresh(self, index):
        return None


class _FakeEs:
    def __init__(self, hits, raises=False):
        self.indices = _FakeIndices()
        self.hits = hits
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
    def __init__(self, hits, raises=False):
        self.fake = _FakeEs(hits, raises)
        super().__init__()

    def _init_backend(self) -> None:
        self._es = self.fake
        self.backend = "elasticsearch"


CANNED = [
    {
        "_score": 7.5,
        "_source": {
            "clause_id": "DELAY_COMPENSATION_RULE#3",
            "rule_id": "DELAY_COMPENSATION_RULE",
            "title": "Delay Compensation Rule",
            "text": "Delay more than 5 hours: hotel for delayed hours only.",
            "kind": "rule",
        },
    }
]


def test_elasticsearch_backend_parses_query_hits():
    store_es = _StubEsStore(CANNED)
    hits = store_es.search_policy("hotel delayed hours", scope=["DELAY_COMPENSATION_RULE"], k=1)
    assert [h.clause_id for h in hits] == ["DELAY_COMPENSATION_RULE#3"]
    assert hits[0].score == 7.5
    assert store_es.backend == "elasticsearch"


def test_elasticsearch_recall_always_filters_by_customer_id():
    store_es = _StubEsStore([])
    store_es.recall_turns("CUST-PRIYA", "refund")
    filters = store_es.fake.last_call["query"]["bool"]["filter"]
    assert {"term": {"customer_id": "CUST-PRIYA"}} in filters


def test_elasticsearch_failure_falls_back_to_in_memory_retrieval():
    store_es = _StubEsStore([], raises=True)
    hits = store_es.search_policy(
        "hotel more than 5 hours", scope=["DELAY_COMPENSATION_RULE"], k=1
    )
    assert hits and hits[0].rule_id == "DELAY_COMPENSATION_RULE"


def test_elasticsearch_identify_is_a_term_filter_not_a_scan():
    store_es = _StubEsStore([])
    store_es.identify(customer_id="CUST-PRIYA")
    query = store_es.fake.last_call["query"]["bool"]
    assert {"term": {"id": "CUST-PRIYA"}} in query["filter"]
    assert store_es.fake.last_call["index"] == "passengers"


def test_elasticsearch_known_facts_always_filter_by_customer_id():
    store_es = _StubEsStore([])
    store_es.known_facts("CUST-ARVIND")
    filters = store_es.fake.last_call["query"]["bool"]["filter"]
    assert {"term": {"customer_id": "CUST-ARVIND"}} in filters
    assert store_es.fake.last_call["index"] == "memories"


# --- both backends, same cited clauses -------------------------------------


SCENARIOS = (
    ("CUST-PRIYA", "BK-PRIYA-OUT", "my flight got cancelled and I want a refund"),
    ("CUST-ARVIND", "BK-ARVIND-OUT", "I want hotel accommodation since it has been such a long delay"),
    ("CUST-MEHER", "BK-MEHER-OUT", "full night hotel and a higher fare flight, the fare difference is 2000 rupees"),
)


def _cited_clauses(kb, customer_id: str, booking_id: str, message: str) -> list[str]:
    customer = CUSTOMERS[customer_id]
    booking = BOOKINGS[booking_id]
    extraction = extract(message)
    session = SessionMemory(session_id=str(uuid4()), customer_id=customer_id, identified=True)
    plan = plan_retrieval(extraction, session)
    fixture = kb.fixture_for(customer_id) if plan.need_fixture else None
    evaluation = evaluate_policy(
        customer,
        booking,
        extraction.requests,
        fare_difference_inr=fixture.fare_difference_inr if fixture else None,
        legal_or_formal=extraction.legal_or_formal,
    )
    plan = expand_scope(plan, customer, booking)
    retrieval = retrieve.run(plan=plan, customer=customer, evaluation=evaluation, kb=kb)
    return sorted(h.clause_id for h in retrieval.rules)


def test_json_backend_cites_stable_clauses_for_the_three_scenarios():
    """The demo's citations cannot depend on which store is wired."""
    from products.knowledge.json_store import JsonKnowledgeStore

    kb = JsonKnowledgeStore()
    cited = {customer_id: _cited_clauses(kb, customer_id, booking_id, message)
             for customer_id, booking_id, message in SCENARIOS}
    assert cited["CUST-PRIYA"]
    assert cited["CUST-ARVIND"]
    assert "DELAY_COMPENSATION_RULE#3" in cited["CUST-MEHER"]
    assert any(c.startswith("FARE_DIFFERENCE_RULE") for c in cited["CUST-MEHER"])


def test_json_and_elasticsearch_cite_the_same_clauses_for_the_three_scenarios():
    import pytest
    from products.knowledge.json_store import JsonKnowledgeStore

    json_kb = JsonKnowledgeStore()
    try:
        es_kb = ElasticsearchKnowledgeStore()
    except Exception:
        pytest.skip("elasticsearch not reachable")
    for customer_id, booking_id, message in SCENARIOS:
        json_ids = _cited_clauses(json_kb, customer_id, booking_id, message)
        es_ids = _cited_clauses(es_kb, customer_id, booking_id, message)
        assert json_ids == es_ids, (customer_id, json_ids, es_ids)


def test_narration_contains_no_rupee_amount_absent_from_decisions_or_citations():
    import re

    _, evaluation, retrieval, ctx = _turn(
        "CUST-MEHER",
        "BK-MEHER-OUT",
        "I want a full night hotel stay and a higher-fare flight, the fare difference is 2000 rupees",
    )
    allowed: set[str] = set()
    for decision in evaluation.decisions:
        if decision.amount_inr is not None:
            allowed.add(str(decision.amount_inr))
        if decision.authority_limit_inr is not None:
            allowed.add(str(decision.authority_limit_inr))
    for hit in retrieval.rules:
        allowed.update(re.findall(r"\d+", hit.text.replace(",", "")))
    if ctx.booking and ctx.booking.delay_hours:
        allowed.add(str(ctx.booking.delay_hours))
    if ctx.identity:
        allowed.update(re.findall(r"\d+", ctx.identity.pnr or ""))
    if ctx.booking:
        for value in (ctx.booking.flight, ctx.booking.pnr, ctx.booking.new_departure):
            allowed.update(re.findall(r"\d+", str(value or "")))
    facts = "\n".join(narrate(ctx))
    for amount in re.findall(r"\d[\d,]{2,}", facts):
        assert amount.replace(",", "") in allowed, amount


def test_cited_rules_are_exactly_the_ones_retrieval_returned():
    _, _, retrieval, ctx = _turn(
        "CUST-MEHER", "BK-MEHER-OUT", "full night hotel and a higher fare flight"
    )
    cited_ids = {
        line.split("[", 1)[1].split("]", 1)[0]
        for line in narrate(ctx)
        if line.startswith("  cited ")
    }
    retrieved_ids = {hit.clause_id for hit in retrieval.rules}
    assert cited_ids <= retrieved_ids


def test_session_memory_exposes_recall_and_facts_on_the_packet():
    first = str(uuid4())
    handle_chat(first, "my flight is cancelled, I want a refund", "CUST-PRIYA")
    second = handle_chat(first, "and can I get a cash refund to another account?", "CUST-PRIYA")
    packet = second.context_packet
    assert "recalled_turns" in packet
    assert "known_facts" in packet
    assert second.session["known_facts"] or packet["retrieved"]["known_facts"]


def test_extract_prompt_does_not_replay_the_whole_transcript():
    from agent.context import render_extract_prompt
    from models.schemas import TurnHit

    session = SessionMemory(
        session_id="s",
        messages=[{"role": "user", "content": f"turn {i}"} for i in range(20)],
        recalled_turns=[TurnHit(message="earlier refund question", reply="offered original method")],
    )
    prompt = render_extract_prompt("and the upgrade?", session)
    assert "turn 19" in prompt
    assert "turn 0" not in prompt
    assert "earlier refund question" in prompt
