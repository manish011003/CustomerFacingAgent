from __future__ import annotations

import threading

from dotenv import load_dotenv

from embeddings.client import EmbeddingClient

load_dotenv()

_LOCK = threading.Lock()


class EmbeddingFactory:
    """Clients request an EmbeddingClient. They never read provider environment variables.

    Deliberately a singleton: one process, one key, one disabled/enabled decision.
    """

    _client: EmbeddingClient | None = None

    @classmethod
    def create(cls, refresh: bool = False) -> EmbeddingClient:
        with _LOCK:
            if cls._client is None or refresh:
                if refresh:
                    load_dotenv(override=True)
                cls._client = EmbeddingClient.from_env()
            return cls._client

    @classmethod
    def disabled(cls) -> EmbeddingClient:
        """A client that can never call out, for tests and for EMBEDDING_PROVIDER=none."""
        return EmbeddingClient.disabled()

    @classmethod
    def reset(cls) -> None:
        with _LOCK:
            cls._client = None
