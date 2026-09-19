from products.auth.memory_session import InMemoryTokenSession
from products.auth.staff import DEFAULT_STAFF_EMAIL, DEFAULT_STAFF_PASSWORD, StaffAccess
from products.auth.signing import sign, verify


def test_signed_passenger_token_resolves_in_a_new_process():
    token = InMemoryTokenSession().issue("CUST-ARVIND")
    assert InMemoryTokenSession().resolve(token) == "CUST-ARVIND"
    assert InMemoryTokenSession().resolve("forged") is None
    assert verify(sign("staff:STAFF-OPS")) == "staff:STAFF-OPS"
    assert InMemoryTokenSession().resolve(sign("staff:STAFF-OPS")) is None


def test_signed_token_carries_passenger_claims():
    token = InMemoryTokenSession().issue(
        "CUST-JOIN",
        claims={"name": "Manish Biswas", "email": "manish@example.com", "loyalty_tier": "Standard"},
    )
    other = InMemoryTokenSession()
    assert other.resolve(token) == "CUST-JOIN"
    claims = other.claims(token)
    assert claims["name"] == "Manish Biswas"
    assert claims["email"] == "manish@example.com"


def test_signed_staff_token_resolves_in_a_new_process():
    token = StaffAccess().login(DEFAULT_STAFF_EMAIL, DEFAULT_STAFF_PASSWORD)["token"]
    assert StaffAccess().current(token)["role"] == "staff"
    assert StaffAccess().current("forged") is None
