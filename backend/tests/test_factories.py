from factories.onboarding_factory import OnboardingFactory
from factories.policy_factory import PolicyHandlerFactory
from factories.reply_factory import ReplyFactory
from factories.extractor_factory import ExtractorFactory
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
    assert product.backend in {"json", "elasticsearch"}


def test_onboarding_factory_signs_in_seeded_member():
    from products.onboarding.base import PassengerOnboarding
    from products.onboarding.self_service import SEED_PASSWORD

    product = OnboardingFactory.create()
    assert isinstance(product, PassengerOnboarding)
    session = product.login("priya.nair@example.com", SEED_PASSWORD)
    assert session["passenger"]["id"] == "CUST-PRIYA"
    assert product.current(session["token"]).id == "CUST-PRIYA"

