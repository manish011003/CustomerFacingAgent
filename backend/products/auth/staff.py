from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from typing import Any

DEFAULT_STAFF_EMAIL = "ops@aeroresolve.local"
DEFAULT_STAFF_PASSWORD = "AeroOps2026!"


def _digest(value: str) -> bytes:
    return hashlib.sha256(value.encode("utf-8")).digest()


class StaffAccess:
    """Operations sign-in is a separate product from passenger accounts."""

    def __init__(self) -> None:
        self._tokens: dict[str, dict[str, Any]] = {}

    def login(self, email: str, password: str) -> dict[str, Any]:
        expected_email = os.getenv("STAFF_EMAIL", DEFAULT_STAFF_EMAIL).strip().lower()
        expected_password = os.getenv("STAFF_PASSWORD", DEFAULT_STAFF_PASSWORD)
        got_email = (email or "").strip().lower()
        got_password = password or ""
        email_ok = hmac.compare_digest(_digest(got_email), _digest(expected_email))
        pass_ok = hmac.compare_digest(_digest(got_password), _digest(expected_password))
        if not (email_ok and pass_ok):
            raise ValueError("Email or password is incorrect.")
        token = secrets.token_urlsafe(32)
        profile = {"id": "STAFF-OPS", "role": "staff", "name": "Operations"}
        self._tokens[token] = profile
        return {"token": token, **profile}

    def current(self, token: str | None) -> dict[str, Any] | None:
        if not token:
            return None
        return self._tokens.get(token)

    def sign_out(self, token: str | None) -> None:
        if token:
            self._tokens.pop(token, None)
