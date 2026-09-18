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

    @property
    def enabled(self) -> bool:
        return self.provider != DISABLED and bool(self.api_key)

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
        timeout_seconds=_float("LLM_TIMEOUT_SECONDS", 8.0),
        max_tokens_extract=_int("LLM_MAX_TOKENS_EXTRACT", 200),
        max_tokens_respond=_int("LLM_MAX_TOKENS_RESPOND", 220),
        max_calls_per_session=_int("LLM_MAX_CALLS_PER_SESSION", 12),
        max_calls_per_process=_int("LLM_MAX_CALLS_PER_PROCESS", 500),
        daily_budget_usd=_float("LLM_DAILY_BUDGET_USD", 1.0),
    )
