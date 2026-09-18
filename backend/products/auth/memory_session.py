import secrets

from products.auth.session_base import AuthSession


class InMemoryTokenSession(AuthSession):
    def __init__(self) -> None:
        self._tokens: dict[str, str] = {}

    def issue(self, customer_id: str) -> str:
        token = secrets.token_urlsafe(32)
        self._tokens[token] = customer_id
        return token

    def resolve(self, token: str | None) -> str | None:
        if not token:
            return None
        return self._tokens.get(token)

    def revoke(self, token: str | None) -> None:
        if token:
            self._tokens.pop(token, None)
