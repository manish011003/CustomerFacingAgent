from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from models.schemas import Booking, BookingIntake, Customer, SignupRequest, TravelHistory
from products.auth.hasher_base import CredentialHasher
from products.auth.session_base import AuthSession
from products.knowledge.base import PassengerKnowledgeStore
from products.onboarding.base import PassengerOnboarding

SEED_PASSWORD = "Aero2026!"


class PassengerSelfServiceOnboarding(PassengerOnboarding):
    def __init__(self, store: PassengerKnowledgeStore, hasher: CredentialHasher, sessions: AuthSession) -> None:
        self._store = store
        self._hasher = hasher
        self._sessions = sessions

    def signup(self, payload: SignupRequest) -> dict[str, Any]:
        email = payload.email.strip().lower()
        if not payload.name.strip() or not email or not payload.password:
            raise ValueError("Name, email, and password are required.")
        if self._store.account_for_email(email):
            raise ValueError("An account already exists for that email. Sign in instead.")
        customer_id = f"CUST-{uuid4().hex[:10].upper()}"
        pnr = (payload.pnr or "").strip().upper()
        customer = Customer(
            id=customer_id,
            name=payload.name.strip(),
            loyalty_tier="Standard",
            pnr=pnr,
            email=email,
            phone=payload.phone.strip(),
            travel_history=TravelHistory(),
            account_origin="self_service",
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._store.register_passenger(customer, self._hasher.hash(payload.password))
        if payload.origin and payload.destination and payload.date and pnr:
            disrupted = (payload.status or "ON_TIME") in {"DELAYED", "CANCELLED"}
            self.add_booking(
                customer_id,
                BookingIntake(
                    pnr=pnr,
                    flight=payload.flight,
                    origin=payload.origin,
                    destination=payload.destination,
                    date=payload.date,
                    scheduled_departure=payload.scheduled_departure or "00:00",
                    status=payload.status or "ON_TIME",
                    delay_hours=payload.delay_hours,
                    airline_caused=payload.airline_caused if disrupted else False,
                ),
            )
            customer = self._store.identify(customer_id=customer_id) or customer
        token = self._sessions.issue(customer_id)
        return {"token": token, "passenger": self._store.public_passenger(customer_id)}

    def login(self, email: str, password: str) -> dict[str, Any]:
        account = self._store.account_for_email(email)
        if not account or not self._hasher.verify(password, account["password_hash"]):
            raise ValueError("Email or password is incorrect.")
        token = self._sessions.issue(account["customer_id"])
        return {"token": token, "passenger": self._store.public_passenger(account["customer_id"])}

    def current(self, token: str | None) -> Customer | None:
        customer_id = self._sessions.resolve(token)
        if not customer_id:
            return None
        return self._store.identify(customer_id=customer_id)

    def sign_out(self, token: str | None) -> None:
        self._sessions.revoke(token)

    def add_booking(self, customer_id: str, payload: BookingIntake) -> Booking:
        customer = self._store.identify(customer_id=customer_id)
        if not customer:
            raise ValueError("Unknown passenger.")
        return self._store.attach_booking(customer, payload)

    def public_members(self) -> list[dict[str, Any]]:
        return self._store.list_public_passengers(origin="seeded")
