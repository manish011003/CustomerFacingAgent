import hashlib
import hmac
import os

from products.auth.hasher_base import CredentialHasher


class Pbkdf2Hasher(CredentialHasher):
    def hash(self, password: str) -> str:
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 80_000)
        return f"pbkdf2${salt.hex()}${digest.hex()}"

    def verify(self, password: str, stored: str) -> bool:
        try:
            scheme, salt_hex, digest_hex = stored.split("$", 2)
        except ValueError:
            return False
        if scheme != "pbkdf2":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), 80_000)
        return hmac.compare_digest(digest.hex(), digest_hex)
