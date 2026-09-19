import pytest
from factories.onboarding_factory import OnboardingFactory
from factories.policy_factory import PolicyHandlerFactory
from factories.reply_factory import ReplyFactory
from factories.extractor_factory import ExtractorFactory
from factories.embedding_factory import EmbeddingFactory
from factories.knowledge_factory import KnowledgeStoreFactory
from models.schemas import RequestType
from products.extractors.base import IntentExtractor
from products.knowledge.base import PassengerKnowledgeStore
from products.knowledge.json_store import JsonKnowledgeStore
from products.onboarding.base import PassengerOnboarding
from products.replies.base import ReplyRenderer
from policy.handlers.base import PolicyHandler


def test_extractor_factory_returns_product_interface():
    product = ExtractorFactory.create("heuristic")
    assert isinstance(product, IntentExtractor)
    extraction = product.extract("I'm Priya Nair, refund please")
    assert extraction.mentioned_name == "Priya Nair"


def test_reply_factory_returns_product_interface():
    product = ReplyFactory.create("template")
    assert isinstance(product, ReplyRenderer)


def test_policy_factory_returns_handler_interface_for_each_type():
    for request_type in RequestType:
        product = PolicyHandlerFactory.create(request_type)
        assert isinstance(product, PolicyHandler)


def test_embedding_factory_disabled_is_a_noop():
    client = EmbeddingFactory.disabled()
    assert client.enabled is False
    assert client.embed("anything") is None


def test_knowledge_factory_json_product_is_interface_not_elasticsearch():
    product = KnowledgeStoreFactory.create("json")
    assert isinstance(product, PassengerKnowledgeStore)
    assert isinstance(product, JsonKnowledgeStore)
    assert product.backend == "json"
    priya = product.identify(name="Priya Nair")
    assert priya is not None
    assert priya.id == "CUST-PRIYA"
    assert product.affected_booking(priya.id) is not None


def test_knowledge_factory_auto_never_raises_when_es_is_down():
    product = KnowledgeStoreFactory.create("auto")
    assert isinstance(product, PassengerKnowledgeStore)
    assert product.backend in {"json", "elasticsearch", "postgres"}


def test_knowledge_factory_auto_skips_local_elasticsearch_on_render(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("ELASTICSEARCH_URL", raising=False)
    monkeypatch.setenv("RENDER", "true")
    product = KnowledgeStoreFactory.create("auto")
    assert product.backend == "json"


def test_knowledge_factory_postgres_requires_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ConnectionError, match="DATABASE_URL"):
        KnowledgeStoreFactory.create("postgres")


def test_register_passenger_persists_the_account_row():
    store = JsonKnowledgeStore()
    written: list[str] = []
    store._persist = lambda index, doc_id, document: written.append(index)
    from models.schemas import Customer

    store.register_passenger(
        Customer(
            id="CUST-X",
            name="Test Passenger",
            loyalty_tier="Standard",
            email="test.passenger@example.com",
            phone="+91-00",
        ),
        "hash",
    )
    assert "passengers" in written
    assert "accounts" in written
    assert store.account_for_email("test.passenger@example.com")["customer_id"] == "CUST-X"


def test_onboarding_factory_signs_in_seeded_member():
    from products.onboarding.base import PassengerOnboarding
    from products.onboarding.self_service import SEED_PASSWORD

    product = OnboardingFactory.create()
    assert isinstance(product, PassengerOnboarding)
    session = product.login("priya.nair@example.com", SEED_PASSWORD)
    assert session["passenger"]["id"] == "CUST-PRIYA"
    assert product.current(session["token"]).id == "CUST-PRIYA"

