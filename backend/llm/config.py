from __future__ import annotations

import os
from dataclasses import dataclass

# Every provider here speaks the OpenAI wire format, so one client library
# reaches all of them. Only the key, the base URL, and the model name differ.
PROVIDERS: dict[str, dict[str, str]] = {
    "gemini": {
        "key_env": "GEMINI_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "default_model": "gemini-2.5-flash",
        # Gemini 2.5 thinks by default and charges the thinking to max_tokens,
        # which starved the visible answer and truncated replies mid-word. This
        # work needs no deliberation: the decision is already made, the model
        # only rewords it. Only Gemini accepts the parameter, hence per-provider.
        "reasoning_effort": "none",
    },
    "groq": {
        "key_env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "openai/gpt-oss-20b",
        # The gpt-oss and qwen families deliberate too, and Groq validates the
        # value against its own set: "none" is rejected outright, so the
        # cheapest accepted setting stands in for switching it off.
        "reasoning_effort": "low",
    },
    "xai": {
        "key_env": "XAI_API_KEY",
        "base_url": "https://api.x.ai/v1",
        "default_model": "grok-4.3",
    },
    "openai": {
        "key_env": "OPENAI_API_KEY",
        "base_url": "",
        "default_model": "gpt-4o-mini",
    },
}

# Free tiers first, so "auto" costs nothing unless nothing free is configured.
PREFERENCE = ("gemini", "groq", "xai", "openai")

# Models to try, in order, when the one before it is unavailable. A free tier
# runs out per model, not per project, and on a free key refusal is the normal
# case rather than the exception: probing this family found 429 "quota
# exceeded" and 503 "high demand" on roughly half of it at once. So the family
# stands behind the chosen model, and exhausting 2.5-flash costs flash-lite's
# slightly plainer wording instead of costing the whole LLM path.
#
# Every name here was confirmed to answer a real request. Appearing in
# `models.list()` is not enough: gemini-2.5-pro is still listed by this
# endpoint and 404s as "no longer available" when actually called.
#
# The `-latest` aliases sit at the back on purpose. Google retires pinned
# versions — the 2.0 pair this table first held is already gone — and an alias
# resolves to a current flash, so the chain survives a retirement nobody
# updated it for. Their target moves, so `MOVING_MODELS` prices them at the
# conservative unknown-model rate rather than pretending to know the figure.
MODEL_CHAINS: dict[str, tuple[str, ...]] = {
    "gemini": (
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-flash-lite-latest",
        "gemini-flash-latest",
    ),
    # Groq retired the Llama 3.x pair this chain first held to open weights and
    # enterprise-only access: both now 404 as "does not exist or you do not
    # have access to it" on a free key. Ordered cheapest-and-fastest first —
    # 20b bills $0.075/$0.30 and streams at ~1000 tok/s, qwen at $0.80/$4.00
    # is thirteen times the output rate and earns its place at the back.
    "groq": ("openai/gpt-oss-20b", "openai/gpt-oss-120b", "qwen/qwen3.8-27b"),
    "xai": ("grok-4.3", "grok-3-mini"),
    "openai": ("gpt-4o-mini",),
}

# Chain entries whose target moves, so no published per-token rate belongs to
# them. `pricing.py` bills these at its conservative default.
MOVING_MODELS = frozenset({"gemini-flash-lite-latest", "gemini-flash-latest"})

DISABLED = "none"


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, "").strip() or default)
    except ValueError:
        return default


def _float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, "").strip() or default)
    except ValueError:
        return default


def _dedupe(names: tuple[str, ...]) -> tuple[str, ...]:
    """Order-preserving, so the head stays the model the operator asked for."""
    seen: dict[str, None] = {}
    for name in names:
        cleaned = name.strip()
        if cleaned:
            seen.setdefault(cleaned, None)
    return tuple(seen)


@dataclass(frozen=True)
class LlmConfig:
    """Resolved provider settings plus every ceiling that bounds spend."""

    provider: str
    model: str
    api_key: str
    base_url: str
    timeout_seconds: float
    max_tokens_extract: int
    max_tokens_respond: int
    max_calls_per_session: int
    max_calls_per_process: int
    daily_budget_usd: float
    max_tokens_agent: int = 1024
    fallback_models: tuple[str, ...] = ()
    model_cooldown_seconds: float = 300.0
    reasoning_effort: str = ""

    @property
    def enabled(self) -> bool:
        return self.provider != DISABLED and bool(self.api_key)

    @property
    def model_chain(self) -> tuple[str, ...]:
        """`model` first, then every sibling worth trying if it will not answer."""
        return _dedupe((self.model,) + self.fallback_models)

    @property
    def key_fingerprint(self) -> str:
        """Enough to confirm which key loaded, never enough to use it."""
        if not self.api_key:
            return ""
        return f"{self.api_key[:6]}...{self.api_key[-4:]}" if len(self.api_key) > 12 else "set"

    def max_tokens_for(self, purpose: str) -> int:
        if purpose == "extract":
            return self.max_tokens_extract
        if purpose == "agent":
            return self.max_tokens_agent
        return self.max_tokens_respond


def _detect_provider() -> str:
    """Honour an explicit choice, else take the first provider holding a key."""
    requested = (os.getenv("LLM_PROVIDER") or "auto").strip().lower()
    if requested in PROVIDERS:
        return requested
    if requested in {DISABLED, "off", "false", "disabled"}:
        return DISABLED
    for name in PREFERENCE:
        if os.getenv(PROVIDERS[name]["key_env"], "").strip():
            return name
    return DISABLED


def _fallback_models(provider: str, base_url: str) -> tuple[str, ...]:
    """The chain behind the chosen model, from env if set and the family if not.

    A pinned `LLM_MODEL` only moves to the head of the chain; it does not empty
    it, so pinning a model does not cost you the family behind it. Set
    `LLM_FALLBACK_MODELS=none` to try exactly one model and nothing else.
    """
    requested = (os.getenv("LLM_FALLBACK_MODELS") or "").strip()
    if requested.lower() in {DISABLED, "off", "false", "disabled"}:
        return ()
    if requested:
        return _dedupe(tuple(requested.split(",")))
    # A redirected base URL is some other endpoint, and this provider's family
    # names mean nothing there. Only an explicit list can speak for it.
    if base_url != PROVIDERS[provider]["base_url"]:
        return ()
    return MODEL_CHAINS.get(provider, ())


def _reasoning_effort(provider: str, base_url: str) -> str:
    """Whether to ask this provider to skip deliberation.

    Sending the parameter to a provider that does not know it fails the call,
    so it is opt-in per provider and suppressed on a redirected base URL, where
    we cannot know what is listening. `LLM_REASONING_EFFORT=` clears it.
    """
    requested = os.getenv("LLM_REASONING_EFFORT")
    if requested is not None:
        return requested.strip()
    if base_url != PROVIDERS[provider]["base_url"]:
        return ""
    return PROVIDERS[provider].get("reasoning_effort", "")


def disabled_config() -> LlmConfig:
    """No provider, no model, no ceilings that could ever be consulted."""
    return LlmConfig(
        provider=DISABLED,
        model="",
        api_key="",
        base_url="",
        timeout_seconds=_float("LLM_TIMEOUT_SECONDS", 15.0),
        max_tokens_extract=0,
        max_tokens_respond=0,
        max_tokens_agent=0,
        max_calls_per_session=0,
        max_calls_per_process=0,
        daily_budget_usd=0.0,
    )


def from_env() -> LlmConfig:
    provider = _detect_provider()
    if provider == DISABLED:
        return disabled_config()

    spec = PROVIDERS[provider]
    api_key = os.getenv(spec["key_env"], "").strip()
    model = (os.getenv("LLM_MODEL") or "").strip() or spec["default_model"]
    base_url = (os.getenv("LLM_BASE_URL") or "").strip() or spec["base_url"]

    # Anyone who already pointed the legacy OPENAI_* variables at a non-OpenAI
    # endpoint keeps working, so upgrading this file breaks no existing setup.
    if provider == "openai":
        model = (os.getenv("LLM_MODEL") or os.getenv("OPENAI_MODEL") or "").strip() or spec["default_model"]
        base_url = (os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL") or "").strip()

    return LlmConfig(
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url,
        fallback_models=_fallback_models(provider, base_url),
        model_cooldown_seconds=_float("LLM_MODEL_COOLDOWN_SECONDS", 300.0),
        reasoning_effort=_reasoning_effort(provider, base_url),
        timeout_seconds=_float("LLM_TIMEOUT_SECONDS", 15.0),
        max_tokens_extract=_int("LLM_MAX_TOKENS_EXTRACT", 200),
        max_tokens_respond=_int("LLM_MAX_TOKENS_RESPOND", 220),
        max_tokens_agent=_int("LLM_MAX_TOKENS_AGENT", 1024),
        max_calls_per_session=_int("LLM_MAX_CALLS_PER_SESSION", 24),
        max_calls_per_process=_int("LLM_MAX_CALLS_PER_PROCESS", 500),
        daily_budget_usd=_float("LLM_DAILY_BUDGET_USD", 1.0),
    )
