from products.auth.session_base import AuthSession
from products.auth.signing import sign, verify


class InMemoryTokenSession(AuthSession):
    """Signed tokens — no process-local map, so Vercel isolates can share a login."""

    def issue(self, customer_id: str) -> str:
        return sign(customer_id)

    def resolve(self, token: str | None) -> str | None:
        subject = verify(token)
        if not subject or subject.startswith("staff:"):
            return None
        return subject

    def revoke(self, token: str | None) -> None:
        # Signed tokens expire only when AUTH_SECRET rotates.
        return None
