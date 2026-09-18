from __future__ import annotations

import hashlib
import threading
from collections import OrderedDict
from datetime import date

from llm.config import LlmConfig

CACHE_CAPACITY = 256


class LlmBudget:
    """Every ceiling that stops a runaway bill, plus an extraction cache.

    A breach is never an error. `check` names the ceiling that was hit and the
    caller degrades to its deterministic fallback, so exhausting the budget
    costs phrasing quality and nothing else.
    """

    def __init__(self, config: LlmConfig):
        self._config = config
        self._lock = threading.Lock()
        self._day = date.today()
        self._calls_today = 0
        self._spend_today = 0.0
        self._prompt_tokens_today = 0
        self._completion_tokens_today = 0
        self._calls_per_session: dict[str, int] = {}
        self._cache: OrderedDict[str, str] = OrderedDict()
        self._blocks: dict[str, int] = {}

    def _roll_day_locked(self) -> None:
        today = date.today()
        if today != self._day:
            self._day = today
            self._calls_today = 0
            self._spend_today = 0.0
            self._prompt_tokens_today = 0
            self._completion_tokens_today = 0
            self._calls_per_session.clear()

    def check(self, session_id: str | None = None) -> str | None:
        """Return the name of the breached ceiling, or None to proceed."""
        with self._lock:
            self._roll_day_locked()
            if self._calls_today >= self._config.max_calls_per_process:
                return self._note_locked("process_call_ceiling")
            if self._spend_today >= self._config.daily_budget_usd:
                return self._note_locked("daily_budget_usd")
            if session_id:
                used = self._calls_per_session.get(session_id, 0)
                if used >= self._config.max_calls_per_session:
                    return self._note_locked("session_call_ceiling")
            return None

    def _note_locked(self, reason: str) -> str:
        self._blocks[reason] = self._blocks.get(reason, 0) + 1
        return reason

    def note(self, reason: str) -> None:
        """Record a degradation the client hit rather than a ceiling, e.g. a timeout."""
        with self._lock:
            self._note_locked(reason)

    def record(
        self,
        session_id: str | None,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float,
    ) -> None:
        with self._lock:
            self._roll_day_locked()
            self._calls_today += 1
            self._spend_today += cost_usd
            self._prompt_tokens_today += prompt_tokens
            self._completion_tokens_today += completion_tokens
            if session_id:
                self._calls_per_session[session_id] = self._calls_per_session.get(session_id, 0) + 1

    @staticmethod
    def cache_key(model: str, system: str, user: str) -> str:
        digest = hashlib.sha256("\x00".join((model, system, user)).encode("utf-8"))
        return digest.hexdigest()

    def cache_get(self, key: str) -> str | None:
        with self._lock:
            if key not in self._cache:
                return None
            self._cache.move_to_end(key)
            return self._cache[key]

    def cache_put(self, key: str, value: str) -> None:
        with self._lock:
            self._cache[key] = value
            self._cache.move_to_end(key)
            while len(self._cache) > CACHE_CAPACITY:
                self._cache.popitem(last=False)

    def snapshot(self) -> dict:
        with self._lock:
            self._roll_day_locked()
            remaining = max(0.0, self._config.daily_budget_usd - self._spend_today)
            return {
                "day": self._day.isoformat(),
                "calls_today": self._calls_today,
                "calls_remaining": max(0, self._config.max_calls_per_process - self._calls_today),
                "spend_today_usd": round(self._spend_today, 6),
                "budget_remaining_usd": round(remaining, 6),
                "daily_budget_usd": self._config.daily_budget_usd,
                "prompt_tokens_today": self._prompt_tokens_today,
                "completion_tokens_today": self._completion_tokens_today,
                "cached_extractions": len(self._cache),
                "degradations": dict(self._blocks),
            }
