"""Provider resolution, spend ceilings, and graceful degradation.

Nothing here touches the network. Where a model answer is needed, a recording
stub stands in for the OpenAI SDK, which also lets us assert on the exact
request that would have been sent.
"""

from __future__ import annotations

import time

import pytest

from factories.extractor_factory import ExtractorFactory
from factories.llm_factory import LlmFactory
from factories.reply_factory import ReplyFactory
from llm.budget import LlmBudget
from llm.client import LlmClient
from llm.config import MODEL_CHAINS, MOVING_MODELS, PROVIDERS, LlmConfig, from_env
from llm.pricing import UNKNOWN_MODEL_RATE, estimate_usd, rate_for
from models.schemas import CustomerAgentContext, ExtractedRequest, Extraction, RequestType, SessionMemory
from products.extractors.heuristic import HeuristicExtractor
from products.extractors.llm import LlmExtractor, needs_model
from products.replies.base import ReplyRenderer
from products.replies.llm import LlmPolishedReplyRenderer
from products.replies.template import TemplateReplyRenderer

PROVIDER_ENV = [spec["key_env"] for spec in PROVIDERS.values()]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """No developer's real key leaks into a test run."""
    for name in PROVIDER_ENV + [
        "LLM_PROVIDER",
        "LLM_MODEL",
        "LLM_BASE_URL",
        "LLM_FALLBACK_MODELS",
        "LLM_MODEL_COOLDOWN_SECONDS",
        "OPENAI_BASE_URL",
        "OPENAI_MODEL",
        "LLM_MAX_CALLS_PER_SESSION",
        "LLM_DAILY_BUDGET_USD",
    ]:
        monkeypatch.delenv(name, raising=False)
    LlmFactory.reset()
    yield
    LlmFactory.reset()


def config(**overrides) -> LlmConfig:
    provider = overrides.get("provider", "gemini")
    spec = PROVIDERS[provider]
    base = {
        "provider": provider,
        "model": spec["default_model"],
        "api_key": "test-key",
        "base_url": spec["base_url"],
        "timeout_seconds": 8.0,
        "max_tokens_extract": 200,
        "max_tokens_respond": 220,
        "max_calls_per_session": 12,
        "max_calls_per_process": 500,
        "daily_budget_usd": 1.0,
        # Defaulted per provider exactly as from_env() would, so overriding
        # `provider` here cannot leave a value the real provider never sees.
        "reasoning_effort": spec.get("reasoning_effort", ""),
    }
    base.update(overrides)
    return LlmConfig(**base)


class StubSdk:
    """Records every request and answers with canned text."""

    def __init__(
        self,
        text: str = "polished",
        prompt_tokens: int = 100,
        completion_tokens: int = 40,
        finish_reason: str = "stop",
    ):
        self.requests: list[dict] = []
        self._text = text
        self._prompt_tokens = prompt_tokens
        self._completion_tokens = completion_tokens
        self._finish_reason = finish_reason
        self.chat = self

    @property
    def completions(self):
        return self

    def create(self, **kwargs):
        self.requests.append(kwargs)
        message = type("Message", (), {"content": self._text})()
        choice = type("Choice", (), {"message": message, "finish_reason": self._finish_reason})()
        usage = type(
            "Usage",
            (),
            {"prompt_tokens": self._prompt_tokens, "completion_tokens": self._completion_tokens},
        )()
        return type("Completion", (), {"choices": [choice], "usage": usage})()


class ExplodingSdk:
    def __init__(self):
        self.chat = self

    @property
    def completions(self):
        return self

    def create(self, **kwargs):
        raise TimeoutError("provider unreachable")


class PickySdk(StubSdk):
    """Serves only the models it was given a quota for; the rest raise 429.

    This is what an exhausted free tier looks like from the client's side: the
    key is valid, the endpoint is up, and one model name stops answering.
    """

    def __init__(self, serves: set[str], **kwargs):
        super().__init__(**kwargs)
        self._serves = serves

    def create(self, **kwargs):
        if kwargs["model"] not in self._serves:
            self.requests.append(kwargs)
            raise RuntimeError(f"429 quota exceeded for {kwargs['model']}")
        return super().create(**kwargs)


def models_tried(sdk) -> list[str]:
    return [request["model"] for request in sdk.requests]


def client_with(sdk, cfg: LlmConfig | None = None) -> LlmClient:
    resolved = cfg or config()
    client = LlmClient(resolved, LlmBudget(resolved))
    client._sdk = sdk
    return client


class Fixed(ReplyRenderer):
    """Stands in for the policy-approved template reply."""

    def __init__(self, text: str):
        self._text = text

    def render(self, ctx, utterance: str) -> str:
        return self._text


def ctx_for(session_id: str) -> CustomerAgentContext:
    return CustomerAgentContext(session_memory=SessionMemory(session_id=session_id), kb_backend="json")


# --- provider resolution ---------------------------------------------------


def test_no_key_anywhere_disables_the_llm_path():
    cfg = from_env()
    assert cfg.provider == "none"
    assert cfg.enabled is False
    # No model or endpoint is reported for a provider that will never be called.
    assert cfg.model == ""
    assert cfg.base_url == ""


def test_gemini_key_alone_selects_gemini(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gem-abc")
    cfg = from_env()
    assert cfg.provider == "gemini"
    assert cfg.model == "gemini-2.5-flash"
    assert cfg.base_url == "https://generativelanguage.googleapis.com/v1beta/openai/"
    assert cfg.enabled is True


def test_groq_key_alone_selects_groq(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk-abc")
    cfg = from_env()
    assert cfg.provider == "groq"
    assert cfg.base_url == "https://api.groq.com/openai/v1"


def test_auto_prefers_the_free_tier_when_several_keys_exist(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-paid")
    monkeypatch.setenv("XAI_API_KEY", "xai-paid")
    monkeypatch.setenv("GEMINI_API_KEY", "gem-free")
    assert from_env().provider == "gemini"


def test_explicit_provider_overrides_detection(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gem-abc")
    monkeypatch.setenv("GROQ_API_KEY", "gsk-abc")
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    assert from_env().provider == "groq"


def test_provider_none_disables_even_with_a_key_present(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gem-abc")
    monkeypatch.setenv("LLM_PROVIDER", "none")
    cfg = from_env()
    assert cfg.enabled is False
    assert cfg.api_key == ""


def test_legacy_openai_base_url_still_honoured(monkeypatch):
    """Anyone who pointed OPENAI_* at Gemini before this layer existed keeps working."""
    monkeypatch.setenv("OPENAI_API_KEY", "gem-abc")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
    monkeypatch.setenv("OPENAI_MODEL", "gemini-2.5-flash")
    cfg = from_env()
    assert cfg.provider == "openai"
    assert cfg.base_url == "https://generativelanguage.googleapis.com/v1beta/openai/"
    assert cfg.model == "gemini-2.5-flash"


def test_malformed_numeric_settings_fall_back_to_defaults(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gem-abc")
    monkeypatch.setenv("LLM_MAX_CALLS_PER_SESSION", "not-a-number")
    assert from_env().max_calls_per_session == 24


# --- which models stand behind the chosen one -----------------------------


def test_gemini_offers_the_whole_family_as_fallback(monkeypatch):
    """One key covers every Gemini model, so quota on one is not quota on all."""
    monkeypatch.setenv("GEMINI_API_KEY", "gem-abc")
    cfg = from_env()
    assert cfg.model_chain == MODEL_CHAINS["gemini"]
    assert cfg.model_chain[0] == "gemini-2.5-flash"


def test_pinned_model_leads_the_chain_without_emptying_it(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gem-abc")
    monkeypatch.setenv("LLM_MODEL", "gemini-2.5-pro")
    chain = from_env().model_chain
    assert chain[0] == "gemini-2.5-pro"
    assert "gemini-2.5-flash" in chain
    # Pinning a family member must not leave it in the queue twice.
    assert len(chain) == len(set(chain))


def test_an_explicit_list_replaces_the_family(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gem-abc")
    monkeypatch.setenv("LLM_FALLBACK_MODELS", "gemini-2.0-flash, gemini-2.5-pro")
    assert from_env().model_chain == (
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.5-pro",
    )


def test_fallback_can_be_turned_off_entirely(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gem-abc")
    monkeypatch.setenv("LLM_FALLBACK_MODELS", "none")
    assert from_env().model_chain == ("gemini-2.5-flash",)


def test_a_redirected_base_url_gets_no_family_chain(monkeypatch):
    """Family names mean nothing at someone else's endpoint, so none are assumed."""
    monkeypatch.setenv("GEMINI_API_KEY", "gem-abc")
    monkeypatch.setenv("LLM_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("LLM_MODEL", "llama3")
    assert from_env().model_chain == ("llama3",)


def test_a_disabled_provider_has_no_models_to_fall_back_to():
    assert from_env().model_chain == ()


def test_every_pinned_chain_model_has_a_published_rate():
    """An unpriced entry would be billed at the conservative default silently."""
    unpriced = [
        model
        for chain in MODEL_CHAINS.values()
        for model in chain
        if model not in MOVING_MODELS and rate_for(model) == UNKNOWN_MODEL_RATE
    ]
    assert unpriced == []


def test_moving_aliases_are_knowingly_billed_at_the_default():
    """An alias points at whatever the provider currently serves, so no rate can
    be pinned to it. That must be a deliberate choice, not an oversight."""
    assert MOVING_MODELS
    for model in MOVING_MODELS:
        assert rate_for(model) == UNKNOWN_MODEL_RATE, model
        # And the alias must actually be in a chain, or the exemption is stale.
        assert any(model in chain for chain in MODEL_CHAINS.values()), model


def test_key_is_never_exposed_by_health(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gem-super-secret-value")
    report = LlmFactory.create(refresh=True).health()
    assert "gem-super-secret-value" not in repr(report)
    assert report["key_present"] is True
    assert report["key_fingerprint"].endswith("alue")


# --- a disabled client cannot reach the network ----------------------------


def test_disabled_client_never_builds_an_sdk():
    client = LlmFactory.disabled()
    assert client.enabled is False
    assert client.complete(purpose="respond", system="s", user="u") is None
    assert client._sdk is None


def test_disabled_client_raises_if_it_ever_tried_to_call_out(monkeypatch):
    """Belt and braces: prove the None above is not a swallowed network error."""
    import openai

    def forbidden(*args, **kwargs):
        raise AssertionError("a disabled client must not construct an SDK")

    monkeypatch.setattr(openai, "OpenAI", forbidden)
    assert LlmFactory.disabled().complete(purpose="extract", system="s", user="u") is None


# --- token caps ------------------------------------------------------------


def test_respond_call_is_token_capped():
    """Regression: the original renderer sent no max_tokens at all."""
    sdk = StubSdk()
    client = client_with(sdk)
    client.complete(purpose="respond", system="s", user="u")
    assert sdk.requests[0]["max_tokens"] == 220


def test_extract_call_is_token_capped_and_asks_for_json():
    sdk = StubSdk(text="{}")
    client = client_with(sdk)
    client.complete(purpose="extract", system="s", user="u", json_mode=True)
    assert sdk.requests[0]["max_tokens"] == 200
    assert sdk.requests[0]["temperature"] == 0
    assert sdk.requests[0]["response_format"] == {"type": "json_object"}


def test_frustration_call_is_json_at_temperature_zero():
    sdk = StubSdk(text="{}")
    client = client_with(sdk)
    client.chat(
        purpose="frustration",
        messages=[{"role": "user", "content": "this is ridiculous"}],
        json_mode=True,
    )
    assert sdk.requests[0]["temperature"] == 0
    assert sdk.requests[0]["response_format"] == {"type": "json_object"}


# --- ceilings degrade, they do not raise -----------------------------------


def test_session_call_ceiling_stops_further_calls():
    sdk = StubSdk()
    client = client_with(sdk, config(max_calls_per_session=2))
    for _ in range(5):
        client.complete(purpose="respond", system="s", user="u", session_id="s-1")
    assert len(sdk.requests) == 2
    # Labelled with the purpose, so the breakdown says which call was starved.
    assert client.budget.snapshot()["degradations"]["respond_session_call_ceiling"] == 3


def test_session_ceilings_are_independent_per_session():
    sdk = StubSdk()
    client = client_with(sdk, config(max_calls_per_session=1))
    client.complete(purpose="respond", system="s", user="u", session_id="s-1")
    client.complete(purpose="respond", system="s", user="u", session_id="s-2")
    assert len(sdk.requests) == 2


def test_daily_usd_ceiling_stops_further_calls():
    sdk = StubSdk(prompt_tokens=2_000_000, completion_tokens=0)
    client = client_with(sdk, config(daily_budget_usd=0.5))
    first = client.complete(purpose="respond", system="s", user="u")
    assert first is not None and first.est_cost_usd == pytest.approx(0.60, rel=1e-3)
    assert client.complete(purpose="respond", system="s", user="u") is None
    assert client.budget.snapshot()["budget_remaining_usd"] == 0.0


def test_process_call_ceiling_stops_further_calls():
    sdk = StubSdk()
    client = client_with(sdk, config(max_calls_per_process=1))
    client.complete(purpose="respond", system="s", user="u")
    assert client.complete(purpose="respond", system="s", user="u") is None


def test_provider_error_degrades_quietly():
    client = client_with(ExplodingSdk())
    assert client.complete(purpose="respond", system="s", user="u") is None
    assert client.budget.snapshot()["degradations"]["respond_provider_error"] == 1


def test_empty_response_is_treated_as_a_degradation():
    client = client_with(StubSdk(text="   "))
    assert client.complete(purpose="respond", system="s", user="u") is None


# --- a model out of quota costs the next model, not the LLM path -----------


GEMINI_CHAIN = MODEL_CHAINS["gemini"]


def chained(**overrides) -> LlmConfig:
    return config(fallback_models=GEMINI_CHAIN[1:], **overrides)


def test_the_next_model_answers_when_the_first_is_out_of_quota():
    sdk = PickySdk(serves={"gemini-2.5-flash-lite"}, text="polished by the sibling")
    client = client_with(sdk, chained())
    result = client.complete(purpose="respond", system="s", user="u")
    assert result is not None and result.text == "polished by the sibling"
    # And the result names the model that actually answered, not the one asked.
    assert result.model == "gemini-2.5-flash-lite"
    assert models_tried(sdk) == ["gemini-2.5-flash", "gemini-2.5-flash-lite"]


def test_the_refusal_is_recorded_against_the_model_that_refused():
    survivor = GEMINI_CHAIN[LlmClient.MAX_ATTEMPTS - 1]
    client = client_with(PickySdk(serves={survivor}), chained())
    client.complete(purpose="respond", system="s", user="u")
    degradations = client.budget.snapshot()["degradations"]
    for refused in GEMINI_CHAIN[: LlmClient.MAX_ATTEMPTS - 1]:
        assert degradations[f"model_unavailable:{refused}"] == 1
    # The model that answered is not blamed for the ones that did not.
    assert f"model_unavailable:{survivor}" not in degradations


def test_an_empty_answer_also_moves_down_the_chain():
    """A model that returns nothing is as useless as one that errors."""
    sdk = PickySdk(serves=set(GEMINI_CHAIN), text="   ")
    client = client_with(sdk, chained())
    assert client.complete(purpose="respond", system="s", user="u") is None
    assert len(sdk.requests) == LlmClient.MAX_ATTEMPTS


def test_the_walk_is_capped_so_a_dead_family_cannot_stack_up_timeouts():
    """One timeout per model would be the whole chain's wait for the passenger."""
    sdk = PickySdk(serves=set())
    client = client_with(sdk, chained())
    assert len(GEMINI_CHAIN) > LlmClient.MAX_ATTEMPTS
    assert client.complete(purpose="respond", system="s", user="u") is None
    assert models_tried(sdk) == list(GEMINI_CHAIN[: LlmClient.MAX_ATTEMPTS])


def test_a_model_that_refused_is_not_asked_first_again():
    """Free-tier quota lasts hours, so re-leading with it would waste the walk."""
    sdk = PickySdk(serves={"gemini-2.5-flash-lite"})
    client = client_with(sdk, chained())
    client.complete(purpose="respond", system="s", user="u")
    client.complete(purpose="respond", system="s", user="u")
    assert models_tried(sdk) == [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash-lite",
    ]


def test_a_cooled_model_leads_again_once_the_cooldown_expires(monkeypatch):
    """Demoted, never retired: quota comes back and the preferred model resumes."""
    clock = {"now": 1_000.0}
    monkeypatch.setattr("llm.client.time.monotonic", lambda: clock["now"])
    sdk = PickySdk(serves={"gemini-2.5-flash-lite"})
    client = client_with(sdk, chained(model_cooldown_seconds=300.0))
    client.complete(purpose="respond", system="s", user="u")
    clock["now"] += 301
    client.complete(purpose="respond", system="s", user="u")
    assert models_tried(sdk)[2:] == ["gemini-2.5-flash", "gemini-2.5-flash-lite"]


def test_the_walk_spends_one_call_of_the_session_budget_not_three():
    """Falling back is a retry of one turn, so it must not buy extra headroom."""
    # The last model the walk can reach, given MAX_ATTEMPTS.
    sdk = PickySdk(serves={GEMINI_CHAIN[LlmClient.MAX_ATTEMPTS - 1]})
    client = client_with(sdk, chained(max_calls_per_session=1))
    assert client.complete(purpose="respond", system="s", user="u", session_id="s-1") is not None
    assert client.complete(purpose="respond", system="s", user="u", session_id="s-1") is None
    assert client.budget.snapshot()["calls_today"] == 1


def test_a_cached_answer_survives_the_model_that_produced_it_being_demoted():
    sdk = PickySdk(serves={"gemini-2.5-flash-lite"}, text='{"emotion": "calm"}')
    client = client_with(sdk, chained())
    first = client.complete(purpose="extract", system="s", user="same", cache=True)
    before = len(sdk.requests)
    second = client.complete(purpose="extract", system="s", user="same", cache=True)
    assert len(sdk.requests) == before
    assert second is not None and second.cached is True
    assert first is not None and second.text == first.text


def test_health_reports_the_queue_and_who_leads_it():
    survivor = GEMINI_CHAIN[LlmClient.MAX_ATTEMPTS - 1]
    client = client_with(PickySdk(serves={survivor}), chained())
    assert client.health()["next_models"][0] == GEMINI_CHAIN[0]
    client.complete(purpose="respond", system="s", user="u")
    report = client.health()
    assert report["model_chain"] == list(GEMINI_CHAIN)
    # The models that refused are now behind the one that answered.
    assert report["next_models"][0] == survivor


def test_falling_back_cannot_be_reached_by_a_disabled_client():
    client = LlmFactory.disabled()
    assert client.config.model_chain == ()
    assert client.health()["next_models"] == []


# --- caching ---------------------------------------------------------------


def test_repeated_extraction_is_served_from_cache():
    sdk = StubSdk(text='{"emotion": "calm"}')
    client = client_with(sdk)
    first = client.complete(purpose="extract", system="s", user="same", cache=True)
    second = client.complete(purpose="extract", system="s", user="same", cache=True)
    assert len(sdk.requests) == 1
    assert first is not None and second is not None
    assert second.cached is True and second.est_cost_usd == 0.0


def test_cache_does_not_confuse_different_utterances():
    sdk = StubSdk(text='{"emotion": "calm"}')
    client = client_with(sdk)
    client.complete(purpose="extract", system="s", user="refund please", cache=True)
    client.complete(purpose="extract", system="s", user="where is my bag", cache=True)
    assert len(sdk.requests) == 2


# --- per-turn metering -----------------------------------------------------


def test_a_turn_reports_its_own_tokens_and_cost():
    """Day totals cannot answer "what did this turn cost" once turns overlap."""
    client = client_with(StubSdk(prompt_tokens=600, completion_tokens=100))
    client.begin_turn("s-1")
    client.complete(purpose="extract", system="s", user="a", session_id="s-1")
    client.complete(purpose="respond", system="s", user="b", session_id="s-1")
    usage = client.end_turn("s-1")
    assert usage["calls"] == 2
    assert usage["prompt_tokens"] == 1200
    assert usage["completion_tokens"] == 200
    # gemini-2.5-flash at $0.30 in / $2.50 out per 1M tokens.
    expected = (1200 / 1_000_000) * 0.30 + (200 / 1_000_000) * 2.50
    assert usage["est_cost_usd"] == pytest.approx(expected, rel=1e-6)
    assert usage["provider"] == "gemini"


def test_usage_from_another_session_is_not_billed_to_this_turn():
    client = client_with(StubSdk(prompt_tokens=600, completion_tokens=100))
    client.begin_turn("s-1")
    client.complete(purpose="respond", system="s", user="b", session_id="s-2")
    assert client.end_turn("s-1")["calls"] == 0


def test_a_turn_records_why_it_degraded():
    client = client_with(ExplodingSdk())
    client.begin_turn("s-1")
    client.complete(purpose="respond", system="s", user="b", session_id="s-1")
    degradations = client.end_turn("s-1")["degradations"]
    assert "respond_provider_error" in degradations
    # The chain also names which model refused, so a turn explains itself.
    assert "model_unavailable:gemini-2.5-flash" in degradations


def test_a_ceiling_breach_is_attributed_to_the_turn_that_hit_it():
    client = client_with(StubSdk(), config(max_calls_per_session=1))
    client.begin_turn("s-1")
    client.complete(purpose="respond", system="s", user="a", session_id="s-1")
    client.complete(purpose="respond", system="s", user="b", session_id="s-1")
    usage = client.end_turn("s-1")
    assert usage["calls"] == 1
    assert usage["degradations"] == ["respond_session_call_ceiling"]


def test_a_cached_call_is_counted_but_not_charged():
    client = client_with(StubSdk(text='{"emotion": "calm"}', prompt_tokens=600, completion_tokens=100))
    client.complete(purpose="extract", system="s", user="same", session_id="s-1", cache=True)
    client.begin_turn("s-2")
    client.complete(purpose="extract", system="s", user="same", session_id="s-2", cache=True)
    usage = client.end_turn("s-2")
    assert usage["cached_calls"] == 1
    assert usage["calls"] == 0
    assert usage["est_cost_usd"] == 0.0


def test_a_turn_names_the_model_that_actually_answered():
    """With a chain, the configured model and the answering model can differ."""
    client = client_with(PickySdk(serves={"gemini-2.5-flash-lite"}), chained())
    client.begin_turn("s-1")
    result = client.complete(purpose="respond", system="s", user="u", session_id="s-1")
    usage = client.end_turn("s-1")
    assert result is not None and result.model == "gemini-2.5-flash-lite"
    assert usage["model"] == "gemini-2.5-flash-lite"
    assert usage["models_used"] == ["gemini-2.5-flash-lite"]
    assert client.config.model == "gemini-2.5-flash"


def test_an_unused_turn_reports_the_configured_model():
    client = client_with(StubSdk())
    client.begin_turn("s-1")
    assert client.end_turn("s-1")["model"] == "gemini-2.5-flash"


def test_ending_a_turn_that_was_never_begun_is_harmless():
    usage = client_with(StubSdk()).end_turn("never-started")
    assert usage["calls"] == 0 and usage["est_cost_usd"] == 0.0


# --- the model is only asked when the regex came up empty ------------------


def test_a_readable_utterance_never_reaches_the_model():
    """Measured live: the regex reads this in 4ms, the model takes 2-5 seconds."""
    sdk = StubSdk(text='{"requests": [{"type": "status"}]}')
    extractor = LlmExtractor(fallback=ExtractorFactory.create("heuristic"), client=client_with(sdk))
    extraction = extractor.extract("I want a full night hotel stay, the fare difference is ₹2000")
    assert sdk.requests == []
    assert {r.type for r in extraction.requests} == {
        RequestType.HOTEL_FULL_NIGHT,
        RequestType.HIGHER_FARE_REBOOK,
    }


def test_an_unreadable_utterance_does_reach_the_model():
    sdk = StubSdk(text='{"requests": [{"type": "refund_original"}], "emotion": "angry"}')
    extractor = LlmExtractor(fallback=ExtractorFactory.create("heuristic"), client=client_with(sdk))
    extraction = extractor.extract("sort out the thing we discussed on the phone yesterday")
    assert len(sdk.requests) == 1
    assert [r.type for r in extraction.requests] == [RequestType.REFUND_ORIGINAL]


def test_general_help_alone_is_the_only_trigger():
    assert needs_model(Extraction(requests=[ExtractedRequest(type=RequestType.GENERAL_HELP)]))
    assert not needs_model(Extraction(requests=[ExtractedRequest(type=RequestType.STATUS)]))
    # A recognised intent alongside the catch-all is still a recognised intent.
    assert not needs_model(
        Extraction(
            requests=[
                ExtractedRequest(type=RequestType.GENERAL_HELP),
                ExtractedRequest(type=RequestType.LOUNGE),
            ]
        )
    )


def test_skipping_the_model_costs_nothing():
    client = client_with(StubSdk())
    extractor = LlmExtractor(fallback=ExtractorFactory.create("heuristic"), client=client)
    client.begin_turn("s-1")
    extractor.extract("Is my flight delayed?", SessionMemory(session_id="s-1"))
    assert client.end_turn("s-1")["est_cost_usd"] == 0.0


# --- an exhausted provider must not cost the passenger a full walk ---------


SHORT_CHAIN = GEMINI_CHAIN[: LlmClient.MAX_ATTEMPTS]


def short_chained(**overrides) -> LlmConfig:
    """A chain no longer than one walk, so a single walk exhausts all of it."""
    return config(fallback_models=SHORT_CHAIN[1:], **overrides)


def test_the_sdk_does_not_retry_underneath_the_chain():
    """Two retry layers multiply. A walk over three rate-limited models took
    20 seconds of passenger wait with the SDK backing off as well."""
    captured = {}

    class Recorder:
        def __init__(self, **kwargs):
            captured.update(kwargs)
            self.chat = self

        @property
        def completions(self):
            return self

        def create(self, **kwargs):
            raise RuntimeError("429")

    import openai

    client = LlmClient(config(), LlmBudget(config()))
    original = openai.OpenAI
    openai.OpenAI = Recorder
    try:
        client.complete(purpose="respond", system="s", user="u")
    finally:
        openai.OpenAI = original
    assert captured["max_retries"] == 0
    assert captured["timeout"] == 8.0


def test_a_fully_exhausted_chain_costs_one_probe_not_three():
    """Measured live: three doomed requests spent 4.8s to reach the template
    reply the agent could have sent immediately."""
    sdk = PickySdk(serves=set())
    client = client_with(sdk, short_chained())
    assert client.complete(purpose="respond", system="s", user="u") is None
    assert models_tried(sdk) == list(SHORT_CHAIN)

    # Everything is cooling now, so the next turn probes once and degrades.
    sdk.requests.clear()
    assert client.complete(purpose="respond", system="s", user="u") is None
    assert len(sdk.requests) == 1


def test_the_probe_picks_the_model_closest_to_recovering():
    sdk = PickySdk(serves=set())
    client = client_with(sdk, short_chained())
    client.complete(purpose="respond", system="s", user="u")
    sidelined_first = models_tried(sdk)[0]
    sdk.requests.clear()
    client.complete(purpose="respond", system="s", user="u")
    # Sidelined earliest, so its cooldown expires earliest.
    assert models_tried(sdk) == [sidelined_first]


def test_recovery_restores_the_full_walk():
    sdk = PickySdk(serves=set())
    client = client_with(sdk, short_chained(model_cooldown_seconds=0.01))
    client.complete(purpose="respond", system="s", user="u")
    time.sleep(0.05)
    sdk.requests.clear()
    sdk._serves = {SHORT_CHAIN[1]}
    assert client.complete(purpose="respond", system="s", user="u") is not None
    assert models_tried(sdk) == list(SHORT_CHAIN[:2])


# --- thinking tokens and truncation ---------------------------------------


def test_gemini_is_asked_not_to_deliberate():
    """Gemini 2.5 charges thinking to max_tokens, which truncated live replies
    mid-word. Rewording a decided answer needs no deliberation."""
    sdk = StubSdk()
    client = client_with(sdk)
    client.complete(purpose="respond", system="s", user="u")
    assert sdk.requests[0]["reasoning_effort"] == "none"


def test_groq_is_asked_for_the_cheapest_effort_it_accepts():
    """Groq validates the value and refuses "none", so "low" is the floor."""
    sdk = StubSdk()
    client = client_with(sdk, config(provider="groq"))
    client.complete(purpose="respond", system="s", user="u")
    assert sdk.requests[0]["reasoning_effort"] == "low"


def test_providers_that_would_reject_the_parameter_never_see_it(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "xai-abc")
    assert from_env().reasoning_effort == ""
    sdk = StubSdk()
    client = client_with(sdk, config(provider="xai", reasoning_effort=""))
    client.complete(purpose="respond", system="s", user="u")
    assert "reasoning_effort" not in sdk.requests[0]


def test_a_redirected_base_url_suppresses_the_parameter(monkeypatch):
    """Behind a proxy we cannot know what is listening, so send nothing extra."""
    monkeypatch.setenv("GEMINI_API_KEY", "gem-abc")
    monkeypatch.setenv("LLM_BASE_URL", "https://my-proxy.example/v1")
    assert from_env().reasoning_effort == ""


def test_the_operator_can_override_the_reasoning_setting(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gem-abc")
    monkeypatch.setenv("LLM_REASONING_EFFORT", "low")
    assert from_env().reasoning_effort == "low"
    monkeypatch.setenv("LLM_REASONING_EFFORT", "")
    assert from_env().reasoning_effort == ""


def test_a_truncated_answer_is_refused():
    """Cut off mid-sentence is worse than not answering: the caller has a
    correct reply to fall back to, and half a JSON object cannot be parsed."""
    client = client_with(StubSdk(text="I understand this delay is frustrating, Me", finish_reason="length"))
    assert client.complete(purpose="respond", system="s", user="u") is None
    assert client.budget.snapshot()["degradations"]["respond_truncated"] == 1


def test_truncation_does_not_walk_the_chain():
    """The cap is ours, so the next model would be cut off in the same place."""
    sdk = PickySdk(serves=set(GEMINI_CHAIN), finish_reason="length")
    client = client_with(sdk, chained())
    assert client.complete(purpose="respond", system="s", user="u") is None
    assert len(sdk.requests) == 1


def test_a_complete_answer_reports_why_it_stopped():
    result = client_with(StubSdk()).complete(purpose="respond", system="s", user="u")
    assert result is not None and result.finish_reason == "stop"


# --- a rewrite may change words, never money ------------------------------


def test_a_faithful_rewrite_is_used():
    approved = "The 2,000 rupee fare difference is above the 1,500 rupee agent limit."
    polished = "Your fare difference of 2,000 rupees exceeds our 1,500 rupee limit, so I have escalated it."
    renderer = LlmPolishedReplyRenderer(fallback=Fixed(approved), client=client_with(StubSdk(text=polished)))
    assert renderer.render(ctx_for("s-1"), "hello") == polished


def test_spelling_a_delay_in_words_is_still_faithful():
    """Only money is held to the digit. "6 hour" to "six-hour" is good writing."""
    approved = "Your 6 hour delay is airline caused. The 1,500 rupee limit applies."
    polished = "Your six-hour delay was caused by the airline. Our 1,500 rupee limit applies."
    renderer = LlmPolishedReplyRenderer(fallback=Fixed(approved), client=client_with(StubSdk(text=polished)))
    assert renderer.render(ctx_for("s-1"), "hello") == polished


def test_an_invented_amount_is_rejected():
    approved = "A meal voucher is approved."
    polished = "A meal voucher worth 2,000 rupees is approved."
    renderer = LlmPolishedReplyRenderer(fallback=Fixed(approved), client=client_with(StubSdk(text=polished)))
    assert renderer.render(ctx_for("s-1"), "hello") == approved


def test_a_dropped_amount_is_rejected():
    """The live failure: a rewrite that silently omits the decision."""
    approved = "The 2,000 rupee fare difference is above the 1,500 rupee limit, so it is escalated."
    polished = "I understand this delay is frustrating."
    renderer = LlmPolishedReplyRenderer(fallback=Fixed(approved), client=client_with(StubSdk(text=polished)))
    assert renderer.render(ctx_for("s-1"), "hello") == approved


def test_amount_drift_is_recorded_so_it_can_be_noticed():
    client = client_with(StubSdk(text="A voucher worth 9,999 rupees is approved."))
    renderer = LlmPolishedReplyRenderer(fallback=Fixed("A voucher is approved."), client=client)
    renderer.render(ctx_for("s-1"), "hello")
    assert client.budget.snapshot()["degradations"]["respond_amount_drift"] == 1


def test_thousands_separators_do_not_count_as_drift():
    approved = "The limit is 1,500 rupees."
    polished = "The limit is 1500 rupees."
    renderer = LlmPolishedReplyRenderer(fallback=Fixed(approved), client=client_with(StubSdk(text=polished)))
    assert renderer.render(ctx_for("s-1"), "hello") == polished


def test_a_thin_space_inside_a_figure_is_not_drift():
    """gpt-oss typesets "1 500" with U+202F. It is the same 1500."""
    approved = "The limit is 1,500 rupees."
    polished = "The limit is 1\u202f500 rupees."
    renderer = LlmPolishedReplyRenderer(fallback=Fixed(approved), client=client_with(StubSdk(text=polished)))
    assert renderer.render(ctx_for("s-1"), "hello") == "The limit is 1500 rupees."


def test_typographic_spacing_is_flattened_before_it_reaches_the_passenger():
    approved = "Your 6 hour delay covers a 500 rupee voucher."
    polished = "Your six\u2011hour delay covers a 500\u202frupee voucher."
    renderer = LlmPolishedReplyRenderer(fallback=Fixed(approved), client=client_with(StubSdk(text=polished)))
    assert renderer.render(ctx_for("s-1"), "hello") == "Your six-hour delay covers a 500 rupee voucher."


# --- pricing ---------------------------------------------------------------


def test_versioned_model_names_match_the_base_rate():
    assert rate_for("gemini-2.5-flash-preview-09-2025") == rate_for("gemini-2.5-flash")


def test_unknown_model_still_prices_conservatively():
    assert estimate_usd("some-new-model", 1_000_000, 0) > 0


# --- the factories honour the client, not an environment variable ----------


def test_factories_choose_deterministic_products_when_no_key_is_set():
    assert isinstance(ExtractorFactory.create("auto"), HeuristicExtractor)
    assert isinstance(ReplyFactory.create("auto"), TemplateReplyRenderer)


def test_factories_choose_llm_products_once_a_key_exists(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gem-abc")
    LlmFactory.reset()
    assert isinstance(ExtractorFactory.create("auto"), LlmExtractor)
    assert isinstance(ReplyFactory.create("auto"), LlmPolishedReplyRenderer)


def test_factories_share_one_budget_so_ceilings_actually_bind(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gem-abc")
    LlmFactory.reset()
    extractor = ExtractorFactory.create("auto")
    renderer = ReplyFactory.create("auto")
    assert extractor._llm() is renderer._llm()


# --- degradation is invisible to the passenger -----------------------------


def test_extractor_falls_back_to_heuristic_when_the_provider_fails():
    extractor = LlmExtractor(
        fallback=ExtractorFactory.create("heuristic"),
        client=client_with(ExplodingSdk()),
    )
    extraction = extractor.extract("I'm Priya Nair, refund please")
    assert extraction.mentioned_name == "Priya Nair"
    assert [r.type for r in extraction.requests] == [RequestType.REFUND_ORIGINAL]


def test_extractor_falls_back_when_the_model_returns_unparseable_json():
    extractor = LlmExtractor(
        fallback=ExtractorFactory.create("heuristic"),
        client=client_with(StubSdk(text="not json at all")),
    )
    assert extractor.extract("I'm Priya Nair, refund please").mentioned_name == "Priya Nair"


def test_reply_renderer_returns_the_approved_text_when_the_provider_fails():
    """A degraded turn still answers the passenger, with the policy-approved wording."""
    template = TemplateReplyRenderer()
    renderer = LlmPolishedReplyRenderer(fallback=template, client=client_with(ExplodingSdk()))
    ctx = CustomerAgentContext(session_memory=SessionMemory(session_id="s-1"), kb_backend="json")
    assert renderer.render(ctx, "hello") == template.render(ctx, "hello")
