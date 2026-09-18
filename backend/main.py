from __future__ import annotations

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from agent.loop import handle_chat, reset_session
from factories.onboarding_factory import OnboardingFactory
from kb.store import store
from models.schemas import BookingIntake, ChatRequest, LoginRequest, SignupRequest
from policy.engine import baseline_for_booking, evaluate_policy
from models.schemas import ExtractedRequest, RequestType

app = FastAPI(title="AeroResolve", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, value = authorization.partition(" ")
    if scheme.lower() == "bearer" and value:
        return value.strip()
    return authorization.strip()


def require_passenger(authorization: str | None = Header(default=None)):
    customer = OnboardingFactory.create().current(_token(authorization))
    if not customer:
        raise HTTPException(401, "Sign in required")
    return customer


def _eligibility(customer, booking):
    if not customer or not booking:
        return []
    evaluation = baseline_for_booking(customer, booking)
    return [
        {
            "action": d.action,
            "status": d.status.value,
            "reason": d.reason,
            "source": d.source,
            "scope": d.scope,
            "eligible": d.eligible,
        }
        for d in evaluation.decisions
    ]


@app.get("/api/health")
def health():
    return {"ok": True, "kb_backend": store.backend, "product": "AeroResolve"}


@app.post("/api/auth/signup")
def signup(body: SignupRequest):
    try:
        return OnboardingFactory.create().signup(body)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.post("/api/auth/login")
def login(body: LoginRequest):
    try:
        return OnboardingFactory.create().login(body.email, body.password)
    except ValueError as exc:
        raise HTTPException(401, str(exc)) from exc


@app.post("/api/auth/logout")
def logout(authorization: str | None = Header(default=None)):
    OnboardingFactory.create().sign_out(_token(authorization))
    return {"ok": True}


@app.get("/api/auth/members")
def members():
    """Assignment profiles already enrolled — not a chat shortcut."""
    return {
        "members": OnboardingFactory.create().public_members(),
        "seed_password_hint": "Aero2026!",
        "note": "These passengers already have AERO accounts from the airline record. New travellers use Join.",
    }


@app.get("/api/me")
def me(authorization: str | None = Header(default=None)):
    customer = require_passenger(authorization)
    related = store.bookings_for(customer.id)
    booking = store.affected_booking(customer.id)
    return {
        "passenger": store.public_passenger(customer.id),
        "bookings": [b.model_dump() for b in related],
        "affected_booking": booking.model_dump() if booking else None,
        "eligibility": _eligibility(customer, booking),
        "kb_backend": store.backend,
    }


@app.post("/api/me/bookings")
def add_my_booking(body: BookingIntake, authorization: str | None = Header(default=None)):
    customer = require_passenger(authorization)
    try:
        booking = OnboardingFactory.create().add_booking(customer.id, body)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return booking.model_dump()


@app.post("/api/chat")
def chat(body: ChatRequest, authorization: str | None = Header(default=None)):
    customer = require_passenger(authorization)
    return handle_chat(body.session_id, body.message, customer.id).model_dump()


@app.post("/api/session/{session_id}/reset")
def reset(session_id: str, authorization: str | None = Header(default=None)):
    require_passenger(authorization)
    reset_session(session_id)
    return {"ok": True}


@app.get("/api/passengers")
def passengers():
    return store.list_public_passengers()


@app.get("/api/passengers/{customer_id}")
def passenger(customer_id: str):
    data = store.passenger_360(customer_id)
    if not data:
        raise HTTPException(404, "Unknown passenger")
    data["passenger"] = store.public_passenger(customer_id)
    return data


@app.get("/api/passengers/{customer_id}/graph")
def graph(customer_id: str):
    return store.graph_for(customer_id)


@app.get("/api/cases")
def cases():
    return store.list_cases()


@app.get("/api/cases/{case_id}")
def case(case_id: str):
    found = store.get_case(case_id)
    if not found:
        raise HTTPException(404, "Unknown case")
    return found


@app.post("/api/cases/{case_id}/assess")
def assess(case_id: str, payload: dict):
    found = store.get_case(case_id)
    if not found:
        raise HTTPException(404, "Unknown case")
    notes = payload.get("note") or ""
    status = payload.get("status") or "assessed"
    found["manager_assessment"] = {
        "status": status,
        "note": notes,
        "actor": "human_supervisor",
        "warning": "Human assessment is logged separately. It is not agent authority.",
    }
    found["status"] = status
    store.upsert_case(found)
    store.append_event(
        {
            "kind": "manager_assess",
            "customer_id": found.get("customer_id"),
            "case_id": case_id,
            "status": status,
            "note": notes,
        }
    )
    return found


@app.get("/api/analytics/summary")
def analytics():
    return store.analytics()


@app.post("/api/simulate")
def simulate(payload: dict):
    customer = store.identify(customer_id=payload.get("customer_id"))
    if not customer:
        raise HTTPException(400, "customer_id required")
    booking = store.affected_booking(customer.id)
    requests = [ExtractedRequest.model_validate(r) for r in payload.get("requests", [])]
    if not requests and payload.get("request_type"):
        requests = [
            ExtractedRequest(
                type=RequestType(payload["request_type"]),
                fare_difference_inr=payload.get("fare_difference_inr"),
            )
        ]
    evaluation = evaluate_policy(
        customer,
        booking,
        requests,
        fare_difference_inr=payload.get("fare_difference_inr"),
        legal_or_formal=bool(payload.get("legal_or_formal")),
    )
    return evaluation.model_dump()
