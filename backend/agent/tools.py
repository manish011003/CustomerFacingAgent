"""Deterministic tools the LLM agent may invoke.

The model chooses *when* to call these. It cannot change what they return.
Every passenger lookup is scoped to the signed-in customer, even if the model
passes someone else's identifier.
"""

from __future__ import annotations

import json
import re
from typing import Any, Callable

from agent import frustration
from agent.frustration import LEGAL, detect_emotion, detect_legal_or_formal
from kb.store import store
from models.schemas import (
    Booking,
    Customer,
    DecisionStatus,
    EscalationReason,
    ExtractedRequest,
    Extraction,
    FrustrationAssessment,
    FrustrationCategory,
    PolicyEvaluation,
    RequestType,
    Retrieval,
    SessionMemory,
)
from policy.engine import baseline_for_booking, evaluate_policy

__all__ = ["LEGAL", "TOOL_SCHEMAS", "ToolRuntime", "money_in"]

ACTIONS: dict[str, RequestType] = {
    "status": RequestType.STATUS,
    "rebook": RequestType.REBOOK_24H,
    "rebook_24h": RequestType.REBOOK_24H,
    "rebooking": RequestType.REBOOK_24H,
    "refund": RequestType.REFUND_ORIGINAL,
    "refund_original": RequestType.REFUND_ORIGINAL,
    "full_refund": RequestType.REFUND_ORIGINAL,
    "cash_refund": RequestType.REFUND_ORIGINAL,
    "refund_other_method": RequestType.REFUND_OTHER_METHOD,
    "meal": RequestType.MEAL_VOUCHER,
    "meal_voucher": RequestType.MEAL_VOUCHER,
    "lounge": RequestType.LOUNGE,
    "lounge_access": RequestType.LOUNGE,
    "hotel": RequestType.HOTEL_DELAYED_HOURS,
    "hotel_delayed_hours": RequestType.HOTEL_DELAYED_HOURS,
    "hotel_full_night": RequestType.HOTEL_FULL_NIGHT,
    "full_night_hotel": RequestType.HOTEL_FULL_NIGHT,
    "fare_waiver": RequestType.FARE_WAIVER,
    "higher_fare_rebook": RequestType.HIGHER_FARE_REBOOK,
    "fare_difference": RequestType.FARE_WAIVER,
    "business_upgrade": RequestType.BUSINESS_UPGRADE,
    "upgrade": RequestType.BUSINESS_UPGRADE,
    "compensation_beyond_policy": RequestType.COMPENSATION_BEYOND_POLICY,
    "legal": RequestType.LEGAL_OR_FORMAL,
    "legal_or_formal": RequestType.LEGAL_OR_FORMAL,
    "non_airline_exception": RequestType.NON_AIRLINE_EXCEPTION,
    "booking_assist": RequestType.BOOKING_ASSIST,
    "book": RequestType.BOOKING_ASSIST,
    "booking": RequestType.BOOKING_ASSIST,
    "help_question": RequestType.HELP_QUESTION,
    "help": RequestType.HELP_QUESTION,
}

BENEFIT_UNKNOWN = re.compile(
    r"compensat|waiver|upgrade|voucher|lounge|hotel|refund|cash|₹|inr|entitlement",
    re.I,
)

POLICY_TOPICS: dict[str, tuple[list[str], tuple[str, ...]]] = {
    "cancellation": (["CANCELLATION_REBOOKING_RULE"], ("rule",)),
    "delay": (["DELAY_COMPENSATION_RULE"], ("rule",)),
    "delay compensation": (["DELAY_COMPENSATION_RULE"], ("rule",)),
    "refund": (["REFUND_PROCESSING_RULE"], ("rule",)),
    "fare": (["FARE_DIFFERENCE_RULE"], ("rule",)),
    "fare difference": (["FARE_DIFFERENCE_RULE"], ("rule",)),
    "loyalty": (["LOYALTY_TIER_RULE"], ("rule",)),
    "escalation": (["MUST_ESCALATE"], ("must_escalate",)),
    "authority": (["MUST_ESCALATE", "ALLOWED_ACTIONS"], ("must_escalate", "allowed_action")),
}


def _schema(name: str, description: str, properties: dict, required: list[str] | None = None) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required or [],
                "additionalProperties": False,
            },
        },
    }


TOOL_SCHEMAS: list[dict] = [
    _schema(
        "get_customer",
        "Load the signed-in passenger's profile. Always scoped to the authenticated customer.",
        {"customer_identifier": {"type": "string", "description": "Ignored; isolation uses the session."}},
    ),
    _schema(
        "get_booking",
        "Load this passenger's disrupted booking: flight, route, status, delay. Call this before promising anything.",
        {"booking_reference": {"type": "string", "description": "Optional PNR; ignored if it is not this passenger's."}},
    ),
    _schema(
        "get_policy",
        "Retrieve the relevant policy clauses. Topics: cancellation, delay, refund, fare, loyalty, escalation, authority.",
        {"policy_topic": {"type": "string"}},
        ["policy_topic"],
    ),
    _schema(
        "check_eligibility",
        "Ask the policy engine whether an action is allowed. The model cannot override this result. Actions: rebook, refund, refund_other_method, meal_voucher, lounge, hotel, hotel_full_night, fare_waiver, business_upgrade, compensation_beyond_policy, legal.",
        {
            "action": {"type": "string"},
            "fare_difference_inr": {"type": "integer", "description": "Required for fare waiver / higher-fare rebook."},
        },
        ["action"],
    ),
    _schema(
        "execute_rebooking",
        "Simulate free 24-hour rebooking. Enforces policy; does not invent a flight number.",
        {},
    ),
    _schema(
        "initiate_refund",
        "Simulate a full refund to the original payment method (7 business days). Enforces policy.",
        {},
    ),
    _schema(
        "issue_meal_voucher",
        "Simulate issuing a meal voucher if the delay rule qualifies.",
        {},
    ),
    _schema(
        "grant_lounge_access",
        "Simulate lounge access if the delay is more than 3 hours.",
        {},
    ),
    _schema(
        "arrange_hotel",
        "Simulate hotel cover. Delayed hours only when delay > 5 hours. Full night is never allowed.",
        {"full_night": {"type": "boolean", "description": "True if the passenger asked for a full night."}},
    ),
    _schema(
        "classify_frustration",
        "Assess how distressed this passenger is, from the live message and this "
        "conversation's history. Takes no arguments: it reads the real transcript, "
        "not text you supply. Returns a category, a confidence, the signals observed, "
        "and whether a supervisor is recommended. This grants and denies nothing — "
        "check_eligibility alone decides entitlement.",
        {},
    ),
    _schema(
        "escalate_to_human",
        "Create a supervisor case. Use when authority is exceeded, the passenger wants a benefit not in policy, or they threaten legal/formal action. Do not use this for how-to questions.",
        {
            "reason": {"type": "string"},
            "requested_action": {"type": "string"},
            "notes": {"type": "string"},
        },
        ["reason"],
    ),
    _schema(
        "answer_help",
        "Answer a how-to question from the passenger help guide: booking a trip, check-in, baggage, seats. Not compensation policy.",
        {"topic": {"type": "string", "description": "What the passenger asked, in their words."}},
        ["topic"],
    ),
    _schema(
        "collect_booking_slot",
        "Save one field for a new-trip request: origin, destination, date, or passengers. Does not invent inventory.",
        {
            "name": {"type": "string", "description": "origin, destination, date, or passengers"},
            "value": {"type": "string"},
        },
        ["name", "value"],
    ),
]


class ToolRuntime:
    """Session-scoped tool implementations. Isolation is enforced here, not by the model."""

    def __init__(self, *, session: SessionMemory, customer: Customer | None, utterance: str):
        self.session = session
        self.customer = customer
        self.utterance = utterance
        self.booking: Booking | None = store.affected_booking(customer.id) if customer else None
        self.related: list[Booking] = store.bookings_for(customer.id) if customer else []
        self.fixture = store.fixture_for(customer.id) if customer else None
        self.requests: list[ExtractedRequest] = []
        self.legal_or_formal = detect_legal_or_formal(utterance)
        self.evaluation: PolicyEvaluation | None = None
        self.retrieval = Retrieval(backend=store.backend)
        self.trace: list[dict[str, Any]] = []
        # Set by classify_frustration. A signal on the turn, never an input to
        # any eligibility decision.
        self.frustration: FrustrationAssessment | None = None
        self.frustration_escalation: dict[str, Any] | None = None
        if customer and self.booking:
            self.evaluation = baseline_for_booking(customer, self.booking)

    def handlers(self) -> dict[str, Callable[..., dict[str, Any]]]:
        return {
            "get_customer": self.get_customer,
            "get_booking": self.get_booking,
            "get_policy": self.get_policy,
            "check_eligibility": self.check_eligibility,
            "classify_frustration": self.classify_frustration,
            "execute_rebooking": self.execute_rebooking,
            "initiate_refund": self.initiate_refund,
            "issue_meal_voucher": self.issue_meal_voucher,
            "grant_lounge_access": self.grant_lounge_access,
            "arrange_hotel": self.arrange_hotel,
            "escalate_to_human": self.escalate_to_human,
            "answer_help": self.answer_help,
            "collect_booking_slot": self.collect_booking_slot,
        }

    def call(self, name: str, arguments: dict[str, Any] | None) -> dict[str, Any]:
        handler = self.handlers().get(name)
        payload = arguments or {}
        if handler is None:
            result = {"ok": False, "error": f"Unknown tool {name}. The agent cannot invent tools."}
        else:
            try:
                result = handler(**_accepted(handler, payload))
            except TypeError as exc:
                result = {"ok": False, "error": f"Bad arguments for {name}: {exc}"}
            except Exception as exc:
                result = {"ok": False, "error": f"{name} failed: {type(exc).__name__}"}
        event = {
            "kind": "tool_call",
            "tool": name,
            "status": "success" if result.get("ok", True) is not False else "error",
            "arguments": payload,
            "result": result,
        }
        self.trace.append(event)
        if self.customer:
            store.append_event(
                {
                    "kind": "tool_call",
                    "session_id": self.session.session_id,
                    "customer_id": self.customer.id,
                    "tool": name,
                    "status": event["status"],
                    "action": name,
                    "reason": result.get("reason") or result.get("error"),
                }
            )
        return result

    def extraction(self) -> Extraction:
        requests = self.requests or [ExtractedRequest(type=RequestType.STATUS)]
        return Extraction(
            emotion=detect_emotion(self.utterance),
            legal_or_formal=self.legal_or_formal,
            requests=requests,
            raw_text=self.utterance,
        )

    def frustration_category(self) -> FrustrationCategory | None:
        """The only channel by which frustration reaches the policy engine."""
        return self.frustration.category if self.frustration else None

    def classify_frustration(self) -> dict[str, Any]:
        """Assess the passenger's state from the real transcript.

        Takes no arguments on purpose. The model decides *when* to look, the
        same way it decides when to call `get_booking`; it never supplies the
        text being judged. A model that could pass `latest_message` could hand
        over a sanitised version of an angry turn and quietly suppress the
        duty-of-care escalation below.

        Writing happens here rather than in the caller so both agent paths get
        the identical KB record, and the confidence gate lives in one place.

        Idempotent within a turn. The orchestrator classifies once before the
        loop so the observation exists even if the model never looks, and the
        model may still call the tool itself; the cached answer means that
        costs one KB record rather than two and cannot double-count in
        analytics.
        """
        if self.frustration is not None:
            return self.frustration.payload()
        assessment = frustration.classify(self.utterance, self.session, source="llm_tool")
        self.frustration = assessment
        self.session.last_frustration = assessment
        store.append_frustration(
            assessment,
            session_id=self.session.session_id,
            customer_id=self.customer.id if self.customer else None,
            message=self.utterance,
        )
        from agent.kb_match import ground_prior_resolution

        ground_prior_resolution(
            self.utterance,
            session=self.session,
            customer_id=self.customer.id if self.customer else None,
            assessment=assessment,
        )
        return assessment.payload()

    def get_customer(self, customer_identifier: str | None = None) -> dict[str, Any]:
        if not self.customer:
            return {"ok": False, "error": "No signed-in passenger. Ask them to sign in."}
        return {
            "ok": True,
            "customer": {
                "id": self.customer.id,
                "name": self.customer.name,
                "loyalty_tier": self.customer.loyalty_tier,
                "pnr": self.customer.pnr,
                "email": self.customer.email,
            },
            "note": "Gold/Platinum is priority rebooking only — not extra compensation.",
        }

    def get_booking(self, booking_reference: str | None = None) -> dict[str, Any]:
        if not self.customer:
            return {"ok": False, "error": "No signed-in passenger."}
        booking = self.booking or store.affected_booking(self.customer.id)
        if booking_reference:
            wanted = booking_reference.strip().upper()
            match = next(
                (b for b in self.related if b.pnr.upper() == wanted or (b.flight or "").upper() == wanted),
                None,
            )
            if match:
                booking = match
        if not booking:
            return {
                "ok": False,
                "error": "No booking on this account. Do not invent a flight number.",
            }
        self.booking = booking
        self.related = store.bookings_for(self.customer.id)
        self.fixture = store.fixture_for(self.customer.id)
        self.evaluation = baseline_for_booking(
            self.customer, booking, frustration_category=self.frustration_category()
        )
        payload: dict[str, Any] = {
            "ok": True,
            "booking": {
                "pnr": booking.pnr,
                "flight": booking.flight,
                "route": booking.route,
                "origin": booking.origin,
                "destination": booking.destination,
                "date": booking.date_label,
                "scheduled_departure": booking.scheduled_departure,
                "status": booking.status,
                "status_reason": booking.status_reason,
                "delay_hours": booking.delay_hours,
                "new_departure": booking.new_departure,
                "airline_caused": booking.airline_caused,
            },
            "related_legs": [
                {
                    "leg": other.leg,
                    "route": other.route,
                    "date": other.date_label,
                    "status": other.status,
                }
                for other in self.related
                if other.id != booking.id
            ],
            "baseline_entitlements": self.evaluation.entitlements,
            "choices_needed": list(self.evaluation.ask),
        }
        if self.fixture:
            payload["quoted_fare_difference_inr"] = self.fixture.fare_difference_inr
        return payload

    def get_policy(self, policy_topic: str) -> dict[str, Any]:
        key = (policy_topic or "").strip().lower()
        scope, kinds = POLICY_TOPICS.get(key, (None, ("rule",)))
        if scope is None:
            for name, spec in POLICY_TOPICS.items():
                if name in key or key in name:
                    scope, kinds = spec
                    break
        if not scope:
            return {
                "ok": False,
                "error": "Unknown policy topic. Use cancellation, delay, refund, fare, loyalty, or escalation.",
            }
        hits = store.search_policy(key, scope=scope, kinds=kinds, k=3, max_chars=280)
        for hit in hits:
            if not any(existing.clause_id == hit.clause_id for existing in self.retrieval.rules):
                self.retrieval.rules.append(hit)
        return {
            "ok": True,
            "topic": key,
            "clauses": [
                {"clause_id": hit.clause_id, "title": hit.title, "text": hit.text} for hit in hits
            ],
        }

    def check_eligibility(
        self,
        action: str,
        fare_difference_inr: int | None = None,
    ) -> dict[str, Any]:
        request_type = ACTIONS.get((action or "").strip().lower())
        conversation = request_type in {
            RequestType.BOOKING_ASSIST,
            RequestType.HELP_QUESTION,
            RequestType.GENERAL_HELP,
        }
        if not self.customer:
            return {"ok": False, "error": "Sign in first."}
        if not self.booking and not conversation and request_type is not None:
            return {"ok": False, "error": "Call get_booking first."}
        if request_type is None:
            if BENEFIT_UNKNOWN.search(action or ""):
                return {
                    "ok": True,
                    "eligible": False,
                    "authority": "supervisor",
                    "status": "ESCALATE",
                    "action": action,
                    "reason": "No supplied policy covers that request. Unknown is not allowed.",
                    "escalation_reason": "unknown_entitlement",
                }
            return {
                "ok": True,
                "eligible": False,
                "authority": "agent",
                "status": "INFORM",
                "action": action,
                "reason": "That is not a compensation entitlement. Call answer_help or collect_booking_slot.",
            }
        amount = fare_difference_inr
        if amount is None and self.booking and self.booking.quoted_fare_difference_inr:
            amount = self.booking.quoted_fare_difference_inr
        if amount is None and self.fixture:
            amount = self.fixture.fare_difference_inr
        request = ExtractedRequest(type=request_type, fare_difference_inr=amount)
        if request_type == RequestType.BOOKING_ASSIST:
            request.notes = json.dumps(self.session.choices.get("assist") or {}, ensure_ascii=False)
        self.requests = [r for r in self.requests if r.type != request_type]
        self.requests.append(request)
        if request_type == RequestType.LEGAL_OR_FORMAL:
            self.legal_or_formal = True
        self.evaluation = evaluate_policy(
            self.customer,
            self.booking,
            self.requests,
            fare_difference_inr=amount,
            legal_or_formal=self.legal_or_formal,
            # Reaches ordering and exclusivity only. Drop this argument and
            # every status, reason and amount below is unchanged.
            frustration_category=self.frustration_category(),
        )
        decision = next((d for d in self.evaluation.decisions if d.action == request_type.value), None)
        if decision is None:
            decision = next((d for d in self.evaluation.decisions if d.action.replace("_", "") in action.replace("_", "")), None)
        if decision is None and self.evaluation.decisions:
            # Fare handler uses fare_waiver for both higher-fare types.
            decision = self.evaluation.decisions[-1]
        self._cite(decision)
        return _decision_payload(decision, self.evaluation)

    def execute_rebooking(self) -> dict[str, Any]:
        return self._execute("rebook_24h", RequestType.REBOOK_24H)

    def initiate_refund(self) -> dict[str, Any]:
        return self._execute("refund_original", RequestType.REFUND_ORIGINAL)

    def issue_meal_voucher(self) -> dict[str, Any]:
        return self._execute("meal_voucher", RequestType.MEAL_VOUCHER)

    def grant_lounge_access(self) -> dict[str, Any]:
        return self._execute("lounge", RequestType.LOUNGE)

    def arrange_hotel(self, full_night: bool = False) -> dict[str, Any]:
        if full_night:
            denied = self._execute("hotel_full_night", RequestType.HOTEL_FULL_NIGHT)
            delayed = self.check_eligibility("hotel_delayed_hours")
            if delayed.get("eligible"):
                issued = self._execute("hotel_delayed_hours", RequestType.HOTEL_DELAYED_HOURS)
                denied["delayed_hours_hotel"] = issued
            return denied
        return self._execute("hotel_delayed_hours", RequestType.HOTEL_DELAYED_HOURS)

    def escalate_to_human(
        self,
        reason: str,
        requested_action: str | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        action = (requested_action or "compensation_beyond_policy").strip().lower()
        if "legal" in (reason or "").lower() or "formal" in (reason or "").lower():
            action = "legal_or_formal"
            self.legal_or_formal = True
        checked = self.check_eligibility(action)
        if checked.get("status") != "ESCALATE":
            # Force a supervisor packet even if the mapped action was allow/deny.
            if self.evaluation is None and self.customer and self.booking:
                self.evaluation = evaluate_policy(
                    self.customer,
                    self.booking,
                    self.requests,
                    legal_or_formal=self.legal_or_formal,
                )
        self.session.escalated_to_human = True
        if action not in self.session.escalations:
            self.session.escalations.append(action)
        return {
            "ok": True,
            "status": "ESCALATED",
            "authority": "supervisor",
            "reason": reason,
            "requested_action": action,
            "notes": notes,
            "eligibility": checked,
            "escalation_reason": checked.get("escalation_reason"),
            "simulated": False,
        }

    def answer_help(self, topic: str) -> dict[str, Any]:
        from agent.closure import is_greeting, wants_more

        text = topic or self.utterance or ""
        if is_greeting(text) or wants_more(text) or self.session.escalated_to_human:
            return {
                "ok": True,
                "topic": topic,
                "articles": [],
                "note": "Not a how-to question. Do not paste a help article.",
            }
        hits = store.search_help(topic or "", k=2, max_chars=280)
        for hit in hits:
            if not any(existing.clause_id == hit.clause_id for existing in self.retrieval.rules):
                self.retrieval.rules.append(hit)
        request = ExtractedRequest(type=RequestType.HELP_QUESTION, notes=topic)
        self.requests = [r for r in self.requests if r.type != RequestType.HELP_QUESTION]
        self.requests.append(request)
        if self.customer:
            self.evaluation = evaluate_policy(
                self.customer,
                self.booking,
                self.requests,
                legal_or_formal=self.legal_or_formal,
                frustration_category=self.frustration_category(),
            )
        return {
            "ok": True,
            "topic": topic,
            "articles": [{"title": hit.title, "text": hit.text} for hit in hits],
        }

    def collect_booking_slot(self, name: str, value: str) -> dict[str, Any]:
        from agent.router import SLOT_KEYS, missing_slots, persist_assist

        key = (name or "").strip().lower()
        if key not in SLOT_KEYS:
            return {"ok": False, "error": "Slot must be origin, destination, date, or passengers."}
        persist_assist(self.session, {key: (value or "").strip()})
        filled = dict(self.session.choices.get("assist") or {})
        notes = json.dumps(filled, ensure_ascii=False)
        request = ExtractedRequest(type=RequestType.BOOKING_ASSIST, notes=notes)
        self.requests = [r for r in self.requests if r.type != RequestType.BOOKING_ASSIST]
        self.requests.append(request)
        if self.customer:
            self.evaluation = evaluate_policy(
                self.customer,
                self.booking,
                self.requests,
                legal_or_formal=self.legal_or_formal,
                frustration_category=self.frustration_category(),
            )
        return {
            "ok": True,
            "slots": filled,
            "missing": missing_slots(filled),
            "inventory": "none — do not invent a flight number or fare",
        }

    def _escalate_distress(self, assessment: FrustrationAssessment) -> dict[str, Any]:
        """Duty-of-care handover. Deliberately not a tool the model can call.

        Private for two reasons. `handlers()` is the model's whole menu, so
        absence from it means the model cannot invoke this; and `_accepted()`
        filters arguments by signature, so an `escalation_reason` parameter on
        the public `escalate_to_human` would have been model-reachable — it
        could have relabelled a fare-waiver escalation as distress.

        It does not route through `escalate_to_human`, because that maps its
        `requested_action` through `check_eligibility` and would stamp a
        `compensation_beyond_policy` decision onto the evaluation. Distress is
        its own reason; conflating the two would corrupt the breakdown that
        makes the containment rate readable. So this creates the supervisor
        packet and adds no PolicyDecision at all, leaving whatever
        `check_eligibility` already returned exactly as it was.
        """
        if self.frustration_escalation:
            return self.frustration_escalation
        packet = {
            "ok": True,
            "status": "ESCALATED",
            "authority": "supervisor",
            "reason": (
                "The passenger is in severe distress and a person should take over. "
                "This is a duty-of-care handover, not an entitlement decision."
            ),
            "requested_action": None,
            "escalation_reason": EscalationReason.SEVERE_CUSTOMER_DISTRESS.value,
            "frustration": assessment.payload(),
            "grants": None,
            "simulated": False,
        }
        self.frustration_escalation = packet
        self.session.escalated_to_human = True
        if self.customer:
            store.append_event(
                {
                    "kind": "tool_call",
                    "session_id": self.session.session_id,
                    "customer_id": self.customer.id,
                    "tool": "escalate_to_human",
                    "status": "success",
                    "action": "escalate_to_human",
                    "reason": EscalationReason.SEVERE_CUSTOMER_DISTRESS.value,
                }
            )
        return packet

    def _execute(self, action: str, request_type: RequestType) -> dict[str, Any]:
        checked = self.check_eligibility(request_type.value)
        if not checked.get("eligible") or checked.get("status") != "ALLOW":
            return {
                "ok": False,
                "simulated": False,
                "status": checked.get("status") or "DENY",
                "action": action,
                "reason": checked.get("reason") or "Policy does not allow this action.",
                "authority": checked.get("authority") or "policy",
                "escalation_reason": checked.get("escalation_reason"),
            }
        if action not in self.session.executed_actions:
            self.session.executed_actions.append(action)
            if self.customer:
                store.append_event(
                    {
                        "kind": "action",
                        "session_id": self.session.session_id,
                        "customer_id": self.customer.id,
                        "action": action,
                        "simulated": True,
                    }
                )
        extras: dict[str, Any] = {}
        if action == "refund_original":
            extras = {
                "amount": "full fare, original payment method",
                "processing": "within 7 business days",
            }
        if action == "rebook_24h":
            extras = {"inventory": "next available within 24 hours — flight number not supplied, not invented"}
        return {
            "ok": True,
            "simulated": True,
            "status": "SIMULATED_SUCCESS",
            "action": action,
            "reason": checked.get("reason"),
            "source": checked.get("source"),
            **extras,
        }

    def _cite(self, decision) -> None:
        if decision is None or not decision.source:
            return
        scope = store.rule_ids_for_source(decision.source)
        if not scope:
            return
        hits = store.search_policy(
            f"{decision.reason} {decision.scope or ''}",
            scope=scope,
            kinds=("rule", "must_escalate", "allowed_action"),
            k=1,
            max_chars=280,
        )
        if not hits:
            return
        hit = hits[0]
        hit.for_action = decision.action
        if not any(existing.clause_id == hit.clause_id and existing.for_action == hit.for_action for existing in self.retrieval.rules):
            self.retrieval.rules.append(hit)


def _decision_payload(decision, evaluation: PolicyEvaluation) -> dict[str, Any]:
    if decision is None:
        return {"ok": False, "error": "Policy engine returned no decision for that action."}
    authority = "agent"
    if decision.status == DecisionStatus.ESCALATE:
        authority = "supervisor"
    elif decision.status == DecisionStatus.DENY:
        authority = "policy"
    elif decision.status == DecisionStatus.ASK:
        authority = "passenger"
    return {
        "ok": True,
        "eligible": decision.eligible and decision.status == DecisionStatus.ALLOW,
        "action": decision.action,
        "status": decision.status.value,
        "authority": authority,
        "reason": decision.reason,
        "source": decision.source,
        "scope": decision.scope,
        "amount_inr": decision.amount_inr,
        "authority_limit_inr": decision.authority_limit_inr,
        "escalation_reason": None if not decision.escalation_reason else decision.escalation_reason.value,
        "missing_slots": list(evaluation.missing_slots),
        "entitlements": list(evaluation.entitlements),
        # Which of the already-allowed actions still make sense together, in the
        # order to raise them. A subset of the decisions above; it cannot widen
        # them. See policy/exclusivity.py.
        "offered_actions": list(evaluation.offered_actions),
        "conditions": [decision.reason],
    }


def _accepted(handler: Callable, payload: dict[str, Any]) -> dict[str, Any]:
    import inspect

    names = {name for name in inspect.signature(handler).parameters}
    return {key: value for key, value in payload.items() if key in names}


# Digit groups of three or more — every rupee figure in this domain. The same
# floor as `_invented_money`'s claimed-side parser, so delay hours and two-digit
# confidence fragments cannot license a grant.
_MONEY_DIGITS = re.compile(r"\d[\d,]{2,}")

# json.dumps defaults to ensure_ascii=True, so ₹ becomes the six-character
# escape \u20b9. The trailing 9 sits flush against the following digits:
# "₹1500" serialises as "...u20b91500..." and a regex over that dump reads a
# phantom 91500 that no tool returned. Split on both the escape and the raw
# glyph so neither form (this codebase's dumps, or ensure_ascii=False later)
# can fuse with an adjacent amount.
_RUPEE_BOUNDARY = re.compile(r"(?:\\u20b9|₹)", re.I)


def money_in(payload: Any) -> set[str]:
    """Figures a tool (or the passenger) actually stated.

    Walks the payload instead of regexing json.dumps of the whole blob. A dump
    is what created the 91500 ghost: the default ASCII escape for ₹ has no
    boundary the digit regex can see. Walking ints/floats/strings also stops
    key names and JSON delimiters concatenating into a figure.
    """
    found: set[str] = set()
    _collect_money(payload, found)
    return found


def _collect_money(value: Any, found: set[str]) -> None:
    if value is None or isinstance(value, bool):
        # bool is a subclass of int; True must not become "1".
        return
    if isinstance(value, int):
        if abs(value) >= 100:
            found.add(str(abs(value)))
        return
    if isinstance(value, float):
        # 0.91 and 0.755 are confidence, not rupees. A whole number that
        # arrived as a float is still an amount.
        if value.is_integer() and abs(value) >= 100:
            found.add(str(abs(int(value))))
        return
    if isinstance(value, str):
        found.update(_money_in_text(value))
        return
    if isinstance(value, dict):
        for item in value.values():
            _collect_money(item, found)
        return
    if isinstance(value, (list, tuple, set)):
        for item in value:
            _collect_money(item, found)
        return
    _collect_money(str(value), found)


def _money_in_text(text: str) -> set[str]:
    scrubbed = _RUPEE_BOUNDARY.sub(" ", text)
    return {match.group().replace(",", "") for match in _MONEY_DIGITS.finditer(scrubbed)}
