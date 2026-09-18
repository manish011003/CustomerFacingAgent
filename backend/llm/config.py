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
    },
    "groq": {
        "key_env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.3-70b-versatile",
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

# Models to try, in order, when the one before it is unavailable. A free-tier
# key runs out of quota per model, not per project, so the whole family stands
# behind the chosen one: exhausting 2.5-flash leaves flash-lite answering.
#
# The two `-latest` aliases sit in the middle deliberately. Google retires
# pinned versions — this key no longer serves the 2.0 pair at all — and an
# alias always resolves to a current flash, so the chain keeps working through
# a retirement it was not updated for. They are priced at the conservative
# unknown-model rate, since what they resolve to changes under us.
#
# Pro sits last: it is the most capable and by far the most expensive, so it is
# the model of last resort and the daily USD ceiling is what bounds it.
MODEL_CHAINS: dict[str, tuple[str, ...]] = {
    "gemini": (
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-flash-latest",
        "gemini-flash-lite-latest",
        "gemini-2.5-pro",
    ),
    "groq": ("llama-3.3-70b-versatile", "llama-3.1-8b-instant"),
    "xai": ("grok-4.3", "grok-3-mini"),
    "openai": ("gpt-4o-mini",),
}

# Chain entries whose target moves, so no published per-token rate can be
# pinned to them. `pricing.py` bills these at its conservative default.
MOVING_MODELS = frozenset({"gemini-flash-latest", "gemini-flash-lite-latest"})

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
    fallback_models: tuple[str, ...] = ()
    model_cooldown_seconds: float = 300.0

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
        return self.max_tokens_extract if purpose == "extract" else self.max_tokens_respond


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


def disabled_config() -> LlmConfig:
    """No provider, no model, no ceilings that could ever be consulted."""
    return LlmConfig(
        provider=DISABLED,
        model="",
        api_key="",
        base_url="",
        timeout_seconds=_float("LLM_TIMEOUT_SECONDS", 8.0),
        max_tokens_extract=0,
        max_tokens_respond=0,
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
        timeout_seconds=_float("LLM_TIMEOUT_SECONDS", 8.0),
        max_tokens_extract=_int("LLM_MAX_TOKENS_EXTRACT", 200),
        max_tokens_respond=_int("LLM_MAX_TOKENS_RESPOND", 220),
        max_calls_per_session=_int("LLM_MAX_CALLS_PER_SESSION", 12),
        max_calls_per_process=_int("LLM_MAX_CALLS_PER_PROCESS", 500),
        daily_budget_usd=_float("LLM_DAILY_BUDGET_USD", 1.0),
    )
