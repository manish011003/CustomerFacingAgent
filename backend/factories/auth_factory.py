from __future__ import annotations

import os

from products.auth.memory_session import InMemoryTokenSession
from products.auth.session_base import AuthSession

_SESSION: AuthSession | None = None


class AuthFactory:
    """Session tokens are a singleton product so login survives across requests."""

    @classmethod
    def create(cls, kind: str = "auto") -> AuthSession:
        global _SESSION
        if _SESSION is not None:
            return _SESSION
        resolved = kind
        if kind == "auto":
            from persistence.postgres import database_url

            resolved = "postgres" if database_url() and os.getenv("AERORESOLVE_KB") != "json" else "memory"
        if resolved == "postgres":
            try:
                from products.auth.postgres_session import PostgresTokenSession

                _SESSION = PostgresTokenSession()
                return _SESSION
            except Exception:
                if kind == "postgres":
                    raise
                resolved = "memory"
        if resolved == "memory":
            _SESSION = InMemoryTokenSession()
            return _SESSION
        raise ValueError(f"Unknown auth session: {kind}")
