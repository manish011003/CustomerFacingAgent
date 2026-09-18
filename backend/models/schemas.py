from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class DecisionStatus(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    ASK = "ASK"
    ESCALATE = "ESCALATE"
    INFORM = "INFORM"


class EscalationReason(str, Enum):
    """Why authority ran out, as a closed set so escalations aggregate.

    Every member is a boundary of agent authority stated in the data pack, not
    an agent failure. A containment rate is only meaningful alongside this
    breakdown: it separates "the agent could not cope" from "no agent, human or
    automated, is permitted to decide this alone".
    """

    FARE_WAIVER_ABOVE_LIMIT = "fare_waiver_above_limit"
    LEGAL_OR_FORMAL = "legal_or_formal"
    COMPENSATION_BEYOND_POLICY = "compensation_beyond_policy"
    REFUND_ALTERNATE_METHOD = "refund_alternate_method"
    NON_AIRLINE_CAUSE = "non_airline_cause"
    UNKNOWN_ENTITLEMENT = "unknown_entitlement"


class RequestType(str, Enum):
    STATUS = "status"
    REBOOK_24H = "rebook_24h"
    REFUND_ORIGINAL = "refund_original"
    REFUND_OTHER_METHOD = "refund_other_method"
    MEAL_VOUCHER = "meal_voucher"
    LOUNGE = "lounge"
    HOTEL_DELAYED_HOURS = "hotel_delayed_hours"
    HOTEL_FULL_NIGHT = "hotel_full_night"
    BUSINESS_UPGRADE = "business_upgrade"
    HIGHER_FARE_REBOOK = "higher_fare_rebook"
    FARE_WAIVER = "fare_waiver"
    COMPENSATION_BEYOND_POLICY = "compensation_beyond_policy"
    LEGAL_OR_FORMAL = "legal_or_formal"
    NON_AIRLINE_EXCEPTION = "non_airline_exception"
    GENERAL_HELP = "general_help"


class TravelHistory(BaseModel):
    flights_last_12_months: int = 0
    prior_complaints: int = 0
    prior_complaint_detail: Optional[str] = None


class Customer(BaseModel):
    id: str
    name: str
    loyalty_tier: str
    pnr: str = ""
    email: str
    phone: str
    travel_history: TravelHistory = Field(default_factory=TravelHistory)
    account_origin: Literal["seeded", "self_service"] = "self_service"
    created_at: Optional[str] = None


class Booking(BaseModel):
    id: str
    customer_id: str
    customer_name: str
    pnr: str
    flight: Optional[str] = None
    leg: str
    route: str
    origin: str
    destination: str
    date: str
    date_label: str
    scheduled_departure: str
    status: str
    status_reason: Optional[str] = None
    delay_hours: Optional[int] = None
    new_departure: Optional[str] = None
    airline_caused: bool = False
    quoted_fare_difference_inr: Optional[int] = None


class ScenarioFixture(BaseModel):
    customer_id: str
    pnr: str
    label: str
    fare_difference_inr: int
    note: str


class RuleHit(BaseModel):
    """One retrieved policy clause. Clause-level, never a whole rule body."""

    clause_id: str
    rule_id: str
    title: str
    text: str
    kind: Literal["rule", "allowed_action", "must_escalate", "assumption"] = "rule"
    score: float = 0.0
    for_action: Optional[str] = None


class TurnHit(BaseModel):
    ts: str = ""
    message: str = ""
    reply: str = ""
    score: float = 0.0


class StyleHit(BaseModel):
    id: str
    customer: str
    agent: str
    score: float = 0.0


class KnownFact(BaseModel):
    fact: str
    source: str
    ts: str = ""


class RetrievalPlan(BaseModel):
    """Which retrievers this turn needs. Zia-style function classification."""

    need_booking: bool = True
    need_related_legs: bool = False
    need_fixture: bool = False
    need_policy: bool = False
    rule_scope: list[str] = Field(default_factory=list)
    doc_kinds: list[str] = Field(default_factory=lambda: ["rule"])
    query: str = ""
    need_recall: bool = False
    need_style: bool = False
    max_rules: int = 2
    max_turns: int = 3
    max_chars: int = 400
    reasons: list[str] = Field(default_factory=list)


class Retrieval(BaseModel):
    """What retrieval actually returned, plus how it was asked. Shown in the context panel."""

    backend: Literal["elasticsearch", "json"] = "json"
    rules: list[RuleHit] = Field(default_factory=list)
    recalled_turns: list[TurnHit] = Field(default_factory=list)
    style: Optional[StyleHit] = None
    known_facts: list[KnownFact] = Field(default_factory=list)
    queries: list[dict[str, Any]] = Field(default_factory=list)


class ExtractedRequest(BaseModel):
    type: RequestType
    fare_difference_inr: Optional[int] = None
    notes: Optional[str] = None


class Extraction(BaseModel):
    emotion: Optional[str] = None
    legal_or_formal: bool = False
    requests: list[ExtractedRequest] = Field(default_factory=list)
    mentioned_name: Optional[str] = None
    mentioned_pnr: Optional[str] = None
    raw_text: str = ""


class PolicyDecision(BaseModel):
    action: str
    status: DecisionStatus
    eligible: bool = False
    scope: Optional[str] = None
    reason: str
    source: str
    simulated: bool = True
    amount_inr: Optional[int] = None
    requires_customer_choice: bool = False
    authority_limit_inr: Optional[int] = None
    # Set on every ESCALATE decision. The free-text `reason` above stays for the
    # passenger and the supervisor; this is the field analytics can group by.
    escalation_reason: Optional[EscalationReason] = None


class PolicyEvaluation(BaseModel):
    disruption_type: Optional[str] = None
    delay_hours: Optional[int] = None
    entitlements: list[str] = Field(default_factory=list)
    decisions: list[PolicyDecision] = Field(default_factory=list)
    missing_slots: list[str] = Field(default_factory=list)
    execute: list[str] = Field(default_factory=list)
    deny: list[str] = Field(default_factory=list)
    escalate: list[str] = Field(default_factory=list)
    ask: list[str] = Field(default_factory=list)


class SessionMemory(BaseModel):
    session_id: str
    customer_id: Optional[str] = None
    identified: bool = False
    choices: dict[str, Any] = Field(default_factory=dict)
    executed_actions: list[str] = Field(default_factory=list)
    denied: list[str] = Field(default_factory=list)
    escalations: list[str] = Field(default_factory=list)
    open_question: Optional[str] = None
    messages: list[dict[str, str]] = Field(default_factory=list)
    last_extraction: Optional[Extraction] = None
    last_evaluation: Optional[PolicyEvaluation] = None


class CustomerAgentContext(BaseModel):
    identity: Optional[Customer] = None
    unidentified: bool = True
    booking: Optional[Booking] = None
    related_bookings: list[Booking] = Field(default_factory=list)
    disruption: Optional[dict[str, Any]] = None
    session_memory: SessionMemory
    emotion: Optional[str] = None
    requests_this_turn: list[ExtractedRequest] = Field(default_factory=list)
    policy_decision: Optional[PolicyEvaluation] = None
    scenario_fixture: Optional[ScenarioFixture] = None
    retrieval_plan: Optional[RetrievalPlan] = None
    retrieval: Optional[Retrieval] = None
    authority: dict[str, Any] = Field(default_factory=dict)
    missing_slots: list[str] = Field(default_factory=list)
    style: dict[str, Any] = Field(default_factory=dict)
    retrieved_facts: list[str] = Field(default_factory=list)
    forbidden_notes: list[str] = Field(default_factory=list)
    kb_backend: Literal["elasticsearch", "json"] = "json"


class ChatRequest(BaseModel):
    session_id: str
    message: str


class SignupRequest(BaseModel):
    name: str
    email: str
    phone: str
    password: str
    pnr: Optional[str] = None
    flight: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    date: Optional[str] = None
    scheduled_departure: Optional[str] = None
    status: Optional[str] = None
    delay_hours: Optional[int] = None
    airline_caused: bool = True


class LoginRequest(BaseModel):
    email: str
    password: str


class BookingIntake(BaseModel):
    pnr: str
    flight: Optional[str] = None
    origin: str
    destination: str
    date: str
    scheduled_departure: str = "00:00"
    status: str = "ON_TIME"
    delay_hours: Optional[int] = None
    airline_caused: bool = True
    quoted_fare_difference_inr: Optional[int] = None


class ChatResponse(BaseModel):
    reply: str
    context_packet: dict[str, Any]
    trace: list[dict[str, Any]]
    eligibility: list[dict[str, Any]]
    audit_event: dict[str, Any]
    escalation: Optional[dict[str, Any]] = None
    session: dict[str, Any]
