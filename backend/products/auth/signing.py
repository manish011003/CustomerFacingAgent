"""HMAC tokens that any process can verify.

In-memory maps die on a Vercel isolate. A signed customer id does not.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os

_PREFIX = "v1"


def _secret() -> bytes:
    return (os.getenv("AUTH_SECRET") or os.getenv("STAFF_PASSWORD") or "aeroresolve-signed-v1").encode()


def sign(subject: str) -> str:
    payload = base64.urlsafe_b64encode(subject.encode()).decode().rstrip("=")
    digest = hmac.new(_secret(), f"{_PREFIX}.{payload}".encode(), hashlib.sha256).digest()
    sig = base64.urlsafe_b64encode(digest).decode().rstrip("=")
    return f"{_PREFIX}.{payload}.{sig}"


def verify(token: str | None) -> str | None:
    if not token:
        return None
    parts = token.split(".")
    if len(parts) != 3 or parts[0] != _PREFIX:
        return None
    _, payload, sig = parts
    expected = hmac.new(_secret(), f"{_PREFIX}.{payload}".encode(), hashlib.sha256).digest()
    expected_sig = base64.urlsafe_b64encode(expected).decode().rstrip("=")
    if not hmac.compare_digest(sig, expected_sig):
        return None
    pad = "=" * (-len(payload) % 4)
    try:
        return base64.urlsafe_b64decode(payload + pad).decode()
    except Exception:
        return None


def sign_claims(claims: dict) -> str:
    return sign(json.dumps(claims, separators=(",", ":"), sort_keys=True))


def read_claims(token: str | None) -> dict | None:
    """Passenger claims, or `{id}` for the first signed tokens that carried only an id."""
    subject = verify(token)
    if not subject or subject.startswith("staff:"):
        return None
    if subject.startswith("{"):
        try:
            data = json.loads(subject)
        except json.JSONDecodeError:
            return None
        if isinstance(data, dict) and data.get("id"):
            return data
        return None
    return {"id": subject}
