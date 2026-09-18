from fastapi.testclient import TestClient

from factories.onboarding_factory import OnboardingFactory
from factories.staff_factory import StaffFactory
from main import app
from products.auth.staff import DEFAULT_STAFF_EMAIL, DEFAULT_STAFF_PASSWORD
from products.onboarding.self_service import SEED_PASSWORD


def test_staff_login_opens_operations_and_rejects_passengers(monkeypatch):
    monkeypatch.setenv("STAFF_EMAIL", DEFAULT_STAFF_EMAIL)
    monkeypatch.setenv("STAFF_PASSWORD", DEFAULT_STAFF_PASSWORD)
    StaffFactory.reset()
    client = TestClient(app)

    denied = client.get("/api/cases")
    assert denied.status_code == 401

    passenger = OnboardingFactory.create().login("priya.nair@example.com", SEED_PASSWORD)
    as_passenger = client.get("/api/cases", headers={"Authorization": f"Bearer {passenger['token']}"})
    assert as_passenger.status_code == 401

    wrong = client.post(
        "/api/auth/staff/login",
        json={"email": "priya.nair@example.com", "password": SEED_PASSWORD},
    )
    assert wrong.status_code == 401

    staff = client.post(
        "/api/auth/staff/login",
        json={"email": DEFAULT_STAFF_EMAIL, "password": DEFAULT_STAFF_PASSWORD},
    )
    assert staff.status_code == 200
    token = staff.json()["token"]
    assert staff.json()["role"] == "staff"

    allowed = client.get("/api/cases", headers={"Authorization": f"Bearer {token}"})
    assert allowed.status_code == 200
    assert isinstance(allowed.json(), list)

    summary = client.get("/api/analytics/summary", headers={"Authorization": f"Bearer {token}"})
    assert summary.status_code == 200
    assert "operations" in summary.json()

    me = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 401
