from abc import ABC, abstractmethod


class AuthSession(ABC):
    """Product: issue and resolve passenger session tokens."""

    @abstractmethod
    def issue(self, customer_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def resolve(self, token: str | None) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def revoke(self, token: str | None) -> None:
        raise NotImplementedError
