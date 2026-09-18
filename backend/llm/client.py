from __future__ import annotations

import threading
from dataclasses import dataclass

from llm.budget import LlmBudget
from llm.config import LlmConfig
from llm.pricing import estimate_usd


@dataclass(frozen=True)
class LlmResult:
    text: str
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    est_cost_usd: float
    cached: bool = False


class LlmClient:
    """The single place this codebase talks to a model.

    `complete` returns None whenever a model answer is unavailable for any
    reason at all: no key, a breached ceiling, a timeout, a provider error.
    Callers treat None as "use the deterministic path", which is why no
    setting here can affect a policy outcome.
    """

    def __init__(self, config: LlmConfig, budget: LlmBudget | None = None):
        self._config = config
        self._budget = budget or LlmBudget(config)
        self._sdk = None
        self._lock = threading.Lock()

    @property
    def config(self) -> LlmConfig:
        return self._config

    @property
    def budget(self) -> LlmBudget:
        return self._budget

    @property
    def enabled(self) -> bool:
        return self._config.enabled

    def _sdk_client(self):
        """Built once, on first use. Disabled providers never construct one."""
        with self._lock:
            if self._sdk is None:
                from openai import OpenAI

                kwargs = {
                    "api_key": self._config.api_key,
                    "timeout": self._config.timeout_seconds,
                    "max_retries": 1,
                }
                if self._config.base_url:
                    kwargs["base_url"] = self._config.base_url
                self._sdk = OpenAI(**kwargs)
            return self._sdk

    def complete(
        self,
        *,
        purpose: str,
        system: str,
        user: str,
        session_id: str | None = None,
        json_mode: bool = False,
        cache: bool = False,
    ) -> LlmResult | None:
        if not self.enabled:
            return None

        key = LlmBudget.cache_key(self._config.model, system, user) if cache else ""
        if key:
            hit = self._budget.cache_get(key)
            if hit is not None:
                return LlmResult(
                    text=hit,
                    provider=self._config.provider,
                    model=self._config.model,
                    prompt_tokens=0,
                    completion_tokens=0,
                    est_cost_usd=0.0,
                    cached=True,
                )

        if self._budget.check(session_id) is not None:
            return None

        request = {
            "model": self._config.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            # The cap the old code was missing entirely on the respond call.
            "max_tokens": self._config.max_tokens_for(purpose),
            "temperature": 0 if purpose == "extract" else 0.2,
        }
        if json_mode:
            request["response_format"] = {"type": "json_object"}

        try:
            completion = self._sdk_client().chat.completions.create(**request)
        except Exception:
            self._budget.note(f"{purpose}_provider_error")
            return None

        text = ""
        choices = getattr(completion, "choices", None) or []
        if choices:
            text = (getattr(choices[0].message, "content", "") or "").strip()

        usage = getattr(completion, "usage", None)
        prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
        completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
        cost = estimate_usd(self._config.model, prompt_tokens, completion_tokens)
        self._budget.record(session_id, prompt_tokens, completion_tokens, cost)

        if not text:
            self._budget.note(f"{purpose}_empty_response")
            return None
        if key:
            self._budget.cache_put(key, text)

        return LlmResult(
            text=text,
            provider=self._config.provider,
            model=self._config.model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            est_cost_usd=cost,
        )

    def health(self, probe: bool = False) -> dict:
        """Provider state without leaking the key. `probe` costs one cheap call."""
        # An empty base_url means the SDK's own default, which only matters
        # when a provider is actually configured.
        default_base_url = "https://api.openai.com/v1" if self.enabled else ""
        report = {
            "enabled": self.enabled,
            "provider": self._config.provider,
            "model": self._config.model,
            "base_url": self._config.base_url or default_base_url,
            "key_present": bool(self._config.api_key),
            "key_fingerprint": self._config.key_fingerprint,
            "caps": {
                "max_tokens_extract": self._config.max_tokens_extract,
                "max_tokens_respond": self._config.max_tokens_respond,
                "timeout_seconds": self._config.timeout_seconds,
                "max_calls_per_session": self._config.max_calls_per_session,
                "max_calls_per_process": self._config.max_calls_per_process,
            },
            "budget": self._budget.snapshot(),
            "fallback": "heuristic extraction and template replies",
        }
        if probe and self.enabled:
            try:
                self._sdk_client().models.list()
                report["key_valid"] = True
            except Exception as exc:
                report["key_valid"] = False
                report["probe_error"] = type(exc).__name__
        return report
