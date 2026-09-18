from __future__ import annotations

import threading

from dotenv import load_dotenv

from llm.budget import LlmBudget
from llm.client import LlmClient
from llm.config import disabled_config, from_env

load_dotenv()

_LOCK = threading.Lock()


class LlmFactory:
    """Clients request an LlmClient. They never read provider environment variables.

    Deliberately a singleton: the budget only bounds spend if every caller in
    the process shares one counter.
    """

    _client: LlmClient | None = None

    @classmethod
    def create(cls, refresh: bool = False) -> LlmClient:
        with _LOCK:
            if cls._client is None or refresh:
                if refresh:
                    # Pick up a key that was added to .env after boot.
                    load_dotenv(override=True)
                cls._client = LlmClient(from_env())
            return cls._client

    @classmethod
    def disabled(cls) -> LlmClient:
        """A client that can never call out, for tests and for LLM_PROVIDER=none."""
        config = disabled_config()
        return LlmClient(config, LlmBudget(config))

    @classmethod
    def reset(cls) -> None:
        with _LOCK:
            cls._client = None
