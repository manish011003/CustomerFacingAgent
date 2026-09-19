from uuid import uuid4

from agent.loop import handle_chat, reset_session
from factories.onboarding_factory import OnboardingFactory
from kb.store import store
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


def test_joined_passenger_without_a_leg_can_still_chat():
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
    sid = str(uuid4())
    reset_session(sid, customer_id)
    out = handle_chat(sid, "what happened to my flight", customer_id)
    assert out.reply
    assert out.case_status != "error"


def test_joiner_token_survives_empty_store():
    onboarding = OnboardingFactory.create()
    email = f"join-{uuid4().hex[:8]}@example.com"
    session = onboarding.signup(
        SignupRequest(
            name="Manish Biswas",
            email=email,
            phone="+91-9000000001",
            password="ChooseAStrong1!",
        )
    )
    customer_id = session["passenger"]["id"]
    store.passengers.pop(customer_id, None)
    store.accounts.pop(email, None)
    found = onboarding.current(session["token"])
    assert found is not None
    assert found.id == customer_id
    assert found.name == "Manish Biswas"
    assert store.identify(customer_id=customer_id) is not None
