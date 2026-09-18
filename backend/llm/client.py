from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, field

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
    finish_reason: str = ""


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass(frozen=True)
class LlmTurn:
    """One model step: either a passenger-facing reply, or tool calls to run."""

    text: str
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    est_cost_usd: float
    finish_reason: str = ""
    tool_calls: tuple[ToolCall, ...] = field(default_factory=tuple)


class LlmClient:
    """The single place this codebase talks to a model.

    `complete` returns None whenever a model answer is unavailable for any
    reason at all: no key, a breached ceiling, a timeout, a provider error.
    Callers treat None as "use the deterministic path", which is why no
    setting here can affect a policy outcome.

    Before giving up it walks `config.model_chain`, so one model being out of
    quota costs the next model in the family rather than the whole LLM path.
    """

    # A walk that tried every model would put one timeout per model in front of
    # the passenger. Three is enough to clear an exhausted quota and still
    # answer inside a sane wait; the cooldown clears the rest for later turns.
    MAX_ATTEMPTS = 3

    def __init__(self, config: LlmConfig, budget: LlmBudget | None = None):
        self._config = config
        self._budget = budget or LlmBudget(config)
        self._sdk = None
        self._lock = threading.Lock()
        # model name -> monotonic time it becomes worth trying again.
        self._cooling: dict[str, float] = {}

    @property
    def config(self) -> LlmConfig:
        return self._config

    @property
    def budget(self) -> LlmBudget:
        return self._budget

    @property
    def enabled(self) -> bool:
        return self._config.enabled

    def begin_turn(self, session_id: str) -> None:
        self._budget.begin_turn(session_id)

    def end_turn(self, session_id: str) -> dict:
        """Tokens, cost, and degradations attributable to one turn."""
        usage = self._budget.end_turn(session_id)
        usage["provider"] = self._config.provider
        used = usage.pop("models", [])
        usage["models_used"] = used
        # The model that answered, which the chain means is not always the one
        # configured. Falls back to the configured name when nothing was called.
        usage["model"] = used[-1] if used else self._config.model
        return usage

    def _sdk_client(self):
        """Built once, on first use. Disabled providers never construct one."""
        with self._lock:
            if self._sdk is None:
                from openai import OpenAI

                kwargs = {
                    "api_key": self._config.api_key,
                    "timeout": self._config.timeout_seconds,
                    # The chain is already our retry strategy, and it retries
                    # against a *different* model, which is the only retry that
                    # helps an exhausted quota. Letting the SDK also back off
                    # and retry multiplied the two: a walk over three
                    # rate-limited models took 20 seconds of passenger wait.
                    "max_retries": 0,
                }
                if self._config.base_url:
                    kwargs["base_url"] = self._config.base_url
                self._sdk = OpenAI(**kwargs)
            return self._sdk

    def _sideline(self, model: str) -> None:
        """Stop leading with a model that just refused, for a cooldown.

        Free-tier quota is exhausted for minutes or hours, not milliseconds, so
        re-offering the same dead model every turn would spend the whole walk
        on it. The entry expires, so a model is demoted and never retired.
        """
        if self._config.model_cooldown_seconds <= 0:
            return
        with self._lock:
            self._cooling[model] = time.monotonic() + self._config.model_cooldown_seconds

    def _attempt_order(self) -> list[str]:
        """The chain, with cooling models moved to the back rather than dropped.

        Nothing is removed: if every model is cooling we would rather spend a
        request finding one recovered than degrade without trying. But only
        one. Measured against an exhausted free tier, walking three cooling
        models spent 4.8 seconds to arrive at the template reply the agent
        could have sent immediately, so a provider that is entirely out of
        quota costs one probe rather than a full walk.
        """
        chain = self._config.model_chain
        now = time.monotonic()
        with self._lock:
            self._cooling = {name: until for name, until in self._cooling.items() if until > now}
            cooling = dict(self._cooling)
        ready = [name for name in chain if name not in cooling]
        if not ready:
            # The one closest to expiry is the likeliest to have recovered.
            soonest = sorted(cooling, key=lambda name: cooling[name])
            return soonest[:1]
        return (ready + [name for name in chain if name in cooling])[: self.MAX_ATTEMPTS]

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

        # Cached text is keyed by the model that produced it, so ask on behalf
        # of the whole chain. An answer from a model since demoted is still a
        # valid answer to this prompt, and serving it costs nothing.
        if cache:
            for model in self._config.model_chain:
                hit = self._budget.cache_get(LlmBudget.cache_key(model, system, user))
                if hit is not None:
                    self._budget.note_cache_hit(session_id)
                    return LlmResult(
                        text=hit,
                        provider=self._config.provider,
                        model=model,
                        prompt_tokens=0,
                        completion_tokens=0,
                        est_cost_usd=0.0,
                        cached=True,
                    )

        turn = self.chat(
            purpose=purpose,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            session_id=session_id,
            json_mode=json_mode,
        )
        if turn is None:
            return None
        if cache:
            self._budget.cache_put(LlmBudget.cache_key(turn.model, system, user), turn.text)
        return LlmResult(
            text=turn.text,
            provider=turn.provider,
            model=turn.model,
            prompt_tokens=turn.prompt_tokens,
            completion_tokens=turn.completion_tokens,
            est_cost_usd=turn.est_cost_usd,
            finish_reason=turn.finish_reason,
        )

    def chat(
        self,
        *,
        purpose: str,
        messages: list[dict],
        session_id: str | None = None,
        tools: list[dict] | None = None,
        json_mode: bool = False,
    ) -> LlmTurn | None:
        """One agent step. Empty text is allowed when the model issued tool calls."""
        if not self.enabled:
            return None

        # One ceiling check for the turn, not one per model: the walk retries a
        # single logical call, so it must not buy itself extra headroom.
        blocked = self._budget.check(session_id)
        if blocked is not None:
            self._budget.note(f"{purpose}_{blocked}", session_id)
            return None

        for model in self._attempt_order():
            request = {
                "model": model,
                "messages": messages,
                "max_tokens": self._config.max_tokens_for(purpose),
                "temperature": 0 if purpose == "extract" else 0.2,
            }
            if json_mode:
                request["response_format"] = {"type": "json_object"}
            if tools:
                request["tools"] = tools
                request["tool_choice"] = "auto"
            if self._config.reasoning_effort:
                request["reasoning_effort"] = self._config.reasoning_effort

            try:
                completion = self._sdk_client().chat.completions.create(**request)
            except Exception:
                # Exhausted quota, a timeout, and a name the provider no longer
                # serves all arrive here, and all mean "ask the next model".
                self._budget.note(f"{purpose}_provider_error", session_id)
                self._budget.note(f"model_unavailable:{model}", session_id)
                self._sideline(model)
                continue

            text = ""
            finish_reason = ""
            message = None
            choices = getattr(completion, "choices", None) or []
            if choices:
                message = choices[0].message
                text = (getattr(message, "content", "") or "").strip()
                finish_reason = getattr(choices[0], "finish_reason", "") or ""
            tool_calls = _parse_tool_calls(message)

            usage = getattr(completion, "usage", None)
            prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
            completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
            cost = estimate_usd(model, prompt_tokens, completion_tokens)
            self._budget.record(session_id, prompt_tokens, completion_tokens, cost)

            if finish_reason == "length":
                # A reply cut off mid-sentence must never reach a passenger, and
                # half a JSON object cannot be parsed. The cap is ours, so the
                # next model would truncate identically: degrade, do not walk.
                self._budget.note(f"{purpose}_truncated", session_id)
                return None
            if not text and not tool_calls:
                self._budget.note(f"{purpose}_empty_response", session_id)
                self._budget.note(f"model_unavailable:{model}", session_id)
                self._sideline(model)
                continue
            self._budget.note_model(model, session_id)
            return LlmTurn(
                text=text,
                provider=self._config.provider,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                est_cost_usd=cost,
                finish_reason=finish_reason,
                tool_calls=tuple(tool_calls),
            )

        return None

    def health(self, probe: bool = False) -> dict:
        """Provider state without leaking the key. `probe` costs one cheap call."""
        # An empty base_url means the SDK's own default, which only matters
        # when a provider is actually configured.
        default_base_url = "https://api.openai.com/v1" if self.enabled else ""
        report = {
            "enabled": self.enabled,
            "provider": self._config.provider,
            "model": self._config.model,
            # Which model the next turn leads with, and the queue behind it.
            # They differ once a model is cooling off after refusing.
            "model_chain": list(self._config.model_chain),
            "next_models": self._attempt_order() if self.enabled else [],
            "base_url": self._config.base_url or default_base_url,
            "key_present": bool(self._config.api_key),
            "key_fingerprint": self._config.key_fingerprint,
            "caps": {
                "max_tokens_extract": self._config.max_tokens_extract,
                "max_tokens_respond": self._config.max_tokens_respond,
                "max_tokens_agent": self._config.max_tokens_agent,
                "timeout_seconds": self._config.timeout_seconds,
                "max_calls_per_session": self._config.max_calls_per_session,
                "max_calls_per_process": self._config.max_calls_per_process,
                "model_attempts_per_call": self.MAX_ATTEMPTS,
                "model_cooldown_seconds": self._config.model_cooldown_seconds,
            },
            "budget": self._budget.snapshot(),
            "agent_mode": "llm" if self.enabled else "fallback",
            "fallback": "deterministic tools and template replies — not a live LLM",
        }
        if probe and self.enabled:
            try:
                self._sdk_client().models.list()
                report["key_valid"] = True
            except Exception as exc:
                report["key_valid"] = False
                report["probe_error"] = type(exc).__name__
        return report


def _parse_tool_calls(message) -> list[ToolCall]:
    if message is None:
        return []
    raw = getattr(message, "tool_calls", None) or []
    parsed: list[ToolCall] = []
    for index, item in enumerate(raw):
        fn = getattr(item, "function", None)
        name = (getattr(fn, "name", None) if fn is not None else None) or ""
        blob = (getattr(fn, "arguments", None) if fn is not None else None) or "{}"
        try:
            arguments = json.loads(blob) if isinstance(blob, str) else dict(blob or {})
        except (TypeError, ValueError, json.JSONDecodeError):
            arguments = {}
        if not isinstance(arguments, dict):
            arguments = {}
        parsed.append(
            ToolCall(
                id=getattr(item, "id", None) or f"call_{index}",
                name=name,
                arguments=arguments,
            )
        )
    return parsed
