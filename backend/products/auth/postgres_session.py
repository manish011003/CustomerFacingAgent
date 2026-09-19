import secrets

from products.auth.session_base import AuthSession


class PostgresTokenSession(AuthSession):
    """Passenger login tokens survive a process restart when Postgres is up."""

    def __init__(self) -> None:
        from persistence.postgres import connect

        connect()

    def issue(self, customer_id: str, claims: dict | None = None) -> str:
        from persistence.postgres import connect

        token = secrets.token_urlsafe(32)
        connect().execute(
            "INSERT INTO auth_tokens (token, customer_id) VALUES (%s, %s)",
            (token, customer_id),
        )
        return token

    def resolve(self, token: str | None) -> str | None:
        from persistence.postgres import connect

        if not token:
            return None
        row = connect().execute(
            "SELECT customer_id FROM auth_tokens WHERE token = %s",
            (token,),
        ).fetchone()
        return row[0] if row else None

    def revoke(self, token: str | None) -> None:
        from persistence.postgres import connect

        if token:
            connect().execute("DELETE FROM auth_tokens WHERE token = %s", (token,))
