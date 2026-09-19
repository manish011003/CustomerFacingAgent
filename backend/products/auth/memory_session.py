from products.auth.session_base import AuthSession
from products.auth.signing import read_claims, sign_claims


class InMemoryTokenSession(AuthSession):
    """Signed tokens — no process-local map, so Vercel isolates can share a login."""

    def issue(self, customer_id: str, claims: dict | None = None) -> str:
        payload = {"id": customer_id}
        if claims:
            for key in ("name", "email", "loyalty_tier", "pnr", "phone", "account_origin"):
                if claims.get(key) not in (None, ""):
                    payload[key] = claims[key]
        return sign_claims(payload)

    def resolve(self, token: str | None) -> str | None:
        data = read_claims(token)
        return data.get("id") if data else None

    def claims(self, token: str | None) -> dict | None:
        return read_claims(token)

    def revoke(self, token: str | None) -> None:
        return None
