from abc import ABC, abstractmethod


class AuthSession(ABC):
    """Product: issue and resolve passenger session tokens."""

    @abstractmethod
    def issue(self, customer_id: str, claims: dict | None = None) -> str:
        raise NotImplementedError

    @abstractmethod
    def resolve(self, token: str | None) -> str | None:
        raise NotImplementedError

    def claims(self, token: str | None) -> dict | None:
        customer_id = self.resolve(token)
        return {"id": customer_id} if customer_id else None

    @abstractmethod
    def revoke(self, token: str | None) -> None:
        raise NotImplementedError
