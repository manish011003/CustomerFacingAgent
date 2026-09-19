from __future__ import annotations

import os
import threading

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536
DISABLED = "none"


class EmbeddingClient:
    """The single place this codebase talks to an embedding model.

    OpenAI `text-embedding-3-small` only — 1536 dimensions, the size the
    pgvector column and the Elasticsearch dense_vector field are declared as.
    `embed` returns None whenever a vector is unavailable: no key, a disabled
    client, or a provider error. Callers treat None as "skip semantic search",
    which is why nothing here can affect a policy outcome.
    """

    def __init__(
        self,
        api_key: str = "",
        model: str = EMBEDDING_MODEL,
        timeout_seconds: float = 15.0,
        enabled: bool = True,
    ) -> None:
        self._api_key = api_key
        self._model = model or EMBEDDING_MODEL
        self._timeout_seconds = timeout_seconds
        self._enabled = bool(enabled and api_key)
        self._sdk = None
        self._lock = threading.Lock()

    @classmethod
    def from_env(cls) -> EmbeddingClient:
        requested = (os.getenv("EMBEDDING_PROVIDER") or os.getenv("LLM_PROVIDER") or "auto").strip().lower()
        if requested in {DISABLED, "off", "false", "disabled"}:
            return cls.disabled()
        try:
            timeout = float(os.getenv("EMBEDDING_TIMEOUT_SECONDS") or os.getenv("LLM_TIMEOUT_SECONDS") or 15.0)
        except ValueError:
            timeout = 15.0
        return cls(
            api_key=(os.getenv("OPENAI_API_KEY") or "").strip(),
            model=(os.getenv("EMBEDDING_MODEL") or EMBEDDING_MODEL).strip() or EMBEDDING_MODEL,
            timeout_seconds=timeout,
        )

    @classmethod
    def disabled(cls) -> EmbeddingClient:
        """A client that can never call out, for tests and for EMBEDDING_PROVIDER=none."""
        return cls(api_key="", model=EMBEDDING_MODEL, enabled=False)

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def model(self) -> str:
        return self._model

    @property
    def dimensions(self) -> int:
        return EMBEDDING_DIMENSIONS

    def embed(self, text: str) -> list[float] | None:
        """One 1536-d vector, or None when this client must not call out."""
        if not text or not text.strip():
            return None
        vectors = self.embed_many([text])
        return vectors[0] if vectors else None

    def embed_many(self, texts: list[str]) -> list[list[float] | None]:
        if not self.enabled:
            return [None] * len(texts)
        cleaned = [t if (t and t.strip()) else None for t in texts]
        payload = [t for t in cleaned if t is not None]
        if not payload:
            return [None] * len(texts)
        try:
            response = self._sdk_client().embeddings.create(model=self._model, input=payload)
        except Exception:
            return [None] * len(texts)
        by_index: dict[int, list[float]] = {}
        for row in getattr(response, "data", None) or []:
            vector = getattr(row, "embedding", None)
            index = getattr(row, "index", None)
            if vector is None or index is None:
                continue
            by_index[int(index)] = [float(x) for x in vector]
        filled: list[list[float] | None] = []
        cursor = 0
        for original in cleaned:
            if original is None:
                filled.append(None)
                continue
            filled.append(by_index.get(cursor))
            cursor += 1
        return filled

    def _sdk_client(self):
        """Built once, on first use. Disabled clients never construct one."""
        with self._lock:
            if self._sdk is None:
                from openai import OpenAI

                self._sdk = OpenAI(api_key=self._api_key, timeout=self._timeout_seconds, max_retries=0)
            return self._sdk
