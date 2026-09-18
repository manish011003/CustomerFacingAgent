from __future__ import annotations

import hashlib
import threading
from collections import OrderedDict
from datetime import date

from llm.config import LlmConfig

CACHE_CAPACITY = 256

# Mutable members are supplied per turn so the template cannot be shared.
_EMPTY_TURN = {
    "calls": 0,
    "cached_calls": 0,
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "est_cost_usd": 0.0,
}


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
        self._turns: dict[str, dict] = {}

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
        """Name the breached ceiling, or None to proceed. Records nothing —
        the caller knows the purpose of the call and logs it with that label."""
        with self._lock:
            self._roll_day_locked()
            if self._calls_today >= self._config.max_calls_per_process:
                return "process_call_ceiling"
            if self._spend_today >= self._config.daily_budget_usd:
                return "daily_budget_usd"
            if session_id:
                used = self._calls_per_session.get(session_id, 0)
                if used >= self._config.max_calls_per_session:
                    return "session_call_ceiling"
            return None

    def _note_locked(self, reason: str) -> None:
        self._blocks[reason] = self._blocks.get(reason, 0) + 1

    def note(self, reason: str, session_id: str | None = None) -> None:
        """Record a degradation the client hit rather than a ceiling, e.g. a timeout."""
        with self._lock:
            self._note_locked(reason)
            turn = self._turns.get(session_id or "")
            if turn is not None:
                turn["degradations"].append(reason)

    def begin_turn(self, session_id: str) -> None:
        """Start metering one conversational turn, so its cost can be reported.

        Day totals cannot answer "what did this turn cost" once turns overlap,
        and cost per resolved contact is the number worth reporting.
        """
        with self._lock:
            self._turns[session_id] = dict(_EMPTY_TURN, degradations=[], models=[])

    def end_turn(self, session_id: str) -> dict:
        with self._lock:
            turn = self._turns.pop(session_id, None)
        if turn is None:
            return dict(_EMPTY_TURN, degradations=[], models=[])
        turn["est_cost_usd"] = round(turn["est_cost_usd"], 8)
        return turn

    def note_cache_hit(self, session_id: str | None) -> None:
        with self._lock:
            turn = self._turns.get(session_id or "")
            if turn is not None:
                turn["cached_calls"] += 1

    def note_model(self, model: str, session_id: str | None) -> None:
        """Which model actually answered. The chain means it may not be the first."""
        with self._lock:
            turn = self._turns.get(session_id or "")
            if turn is not None and model not in turn["models"]:
                turn["models"].append(model)

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
            turn = self._turns.get(session_id or "")
            if turn is not None:
                turn["calls"] += 1
                turn["prompt_tokens"] += prompt_tokens
                turn["completion_tokens"] += completion_tokens
                turn["est_cost_usd"] += cost_usd

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
