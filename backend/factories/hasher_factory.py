from products.auth.hasher_base import CredentialHasher
from products.auth.pbkdf2 import Pbkdf2Hasher


class HasherFactory:
    @classmethod
    def create(cls, kind: str = "pbkdf2") -> CredentialHasher:
        if kind == "pbkdf2":
            return Pbkdf2Hasher()
        raise ValueError(f"Unknown hasher: {kind}")
