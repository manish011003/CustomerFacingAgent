from abc import ABC, abstractmethod
from typing import Any

from models.schemas import Booking, BookingIntake, Customer, SignupRequest


class PassengerOnboarding(ABC):
    """Product: sign up, sign in, and attach bookings. Pages never write passenger records."""

    @abstractmethod
    def signup(self, payload: SignupRequest) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def login(self, email: str, password: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def current(self, token: str | None) -> Customer | None:
        raise NotImplementedError

    @abstractmethod
    def sign_out(self, token: str | None) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_booking(self, customer_id: str, payload: BookingIntake) -> Booking:
        raise NotImplementedError

    @abstractmethod
    def public_members(self) -> list[dict[str, Any]]:
        raise NotImplementedError
