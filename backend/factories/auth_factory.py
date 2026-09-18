from products.auth.memory_session import InMemoryTokenSession
from products.auth.session_base import AuthSession

_SESSION: AuthSession | None = None


class AuthFactory:
    """Session tokens are a singleton product so login survives across requests."""

    @classmethod
    def create(cls, kind: str = "memory") -> AuthSession:
        global _SESSION
        if kind != "memory":
            raise ValueError(f"Unknown auth session: {kind}")
        if _SESSION is None:
            _SESSION = InMemoryTokenSession()
        return _SESSION
