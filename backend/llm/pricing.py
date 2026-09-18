from __future__ import annotations

# USD per million tokens, as (input, output). Paid-tier rates: Gemini and Groq
# free tiers bill nothing and throttle instead, so on a free key these numbers
# describe what the same traffic would cost after an upgrade. The call ceilings
# in budget.py are what actually bound a free key.
RATES: dict[str, tuple[float, float]] = {
    "gemini-2.5-flash": (0.30, 2.50),
    "gemini-2.5-flash-lite": (0.10, 0.40),
    "gemini-2.5-pro": (1.25, 10.00),
    "gemini-2.0-flash": (0.10, 0.40),
    "gemini-2.0-flash-lite": (0.075, 0.30),
    "llama-3.3-70b-versatile": (0.59, 0.79),
    "llama-3.1-8b-instant": (0.05, 0.08),
    "openai/gpt-oss-120b": (0.15, 0.75),
    "grok-4.3": (1.25, 2.50),
    "grok-3-mini": (0.30, 0.50),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
}

UNKNOWN_MODEL_RATE = (0.50, 1.50)


def rate_for(model: str) -> tuple[float, float]:
    if model in RATES:
        return RATES[model]
    # Version suffixes are common ("gemini-2.5-flash-preview-09-2025"), so fall
    # back to the longest registered prefix before assuming the default.
    matches = [name for name in RATES if model.startswith(name)]
    if matches:
        return RATES[max(matches, key=len)]
    return UNKNOWN_MODEL_RATE


def estimate_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    prompt_rate, completion_rate = rate_for(model)
    return round(
        (prompt_tokens / 1_000_000) * prompt_rate + (completion_tokens / 1_000_000) * completion_rate,
        8,
    )
