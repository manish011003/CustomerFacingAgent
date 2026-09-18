from uuid import uuid4

from factories.onboarding_factory import OnboardingFactory
from models.schemas import BookingIntake, SignupRequest
from products.onboarding.self_service import SEED_PASSWORD


def test_seeded_passengers_can_sign_in():
    onboarding = OnboardingFactory.create()
    members = onboarding.public_members()
    emails = {m["email"] for m in members}
    assert emails == {"priya.nair@example.com", "arvind.kulkarni@example.com", "meher.kaur@example.com"}
    for email in emails:
        session = onboarding.login(email, SEED_PASSWORD)
        assert session["token"]
        assert session["passenger"]["account_origin"] == "seeded"


def test_self_service_signup_and_booking():
    onboarding = OnboardingFactory.create()
    email = f"join-{uuid4().hex[:8]}@example.com"
    session = onboarding.signup(
        SignupRequest(
            name="Nisha Rao",
            email=email,
            phone="+91-9000000000",
            password="ChooseAStrong1!",
        )
    )
    customer_id = session["passenger"]["id"]
    assert session["passenger"]["loyalty_tier"] == "Standard"
    assert session["passenger"]["account_origin"] == "self_service"
    booking = onboarding.add_booking(
        customer_id,
        BookingIntake(
            pnr="NX9911A",
            flight="SK-410",
            origin="Delhi",
            destination="Goa",
            date="2026-09-23",
            scheduled_departure="09:00",
            status="DELAYED",
            delay_hours=4,
            airline_caused=True,
        ),
    )
    assert booking.customer_id == customer_id
    assert booking.status == "DELAYED"
    assert onboarding.current(session["token"]).pnr == "NX9911A"
