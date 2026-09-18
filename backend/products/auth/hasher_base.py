from abc import ABC, abstractmethod


class CredentialHasher(ABC):
    """Product: hash and verify passenger passwords. Clients never pick an algorithm."""

    @abstractmethod
    def hash(self, password: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def verify(self, password: str, stored: str) -> bool:
        raise NotImplementedError
