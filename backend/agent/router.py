"""Classify turns that are not disruption entitlements.

Disruption money still goes through RequestType handlers. This module only
decides whether the passenger is asking to plan a trip, asking a how-to
question, or saying something the regex genuinely did not understand.
"""

from __future__ import annotations

import json
import re
from typing import Any

from models.schemas import ExtractedRequest, IssueFamily, RequestType, SessionMemory

ASSIST = re.compile(
    r"\b(book(?:ing)?(?:\s+a|\s+me)?(?:\s+new)?(?:\s+flight)?|new (?:ticket|trip|itinerary)|"
    r"want to fly|plan a trip|ticket to|flights? to|need a flight)\b",
    re.I,
)
HELP = re.compile(
    r"\b(check[- ]?in|boarding pass|baggage|luggage|cabin bag|checked bag|"
    r"seat(?:s|ing| map)?|window seat|aisle|how (?:do|can|to)|what can you (?:do|help)|"
    r"help me with my trip|web check)\b",
    re.I,
)
ROUTE = re.compile(
    r"\bfrom\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)(?=\s+to\b)\s+to\s+([A-Za-z]+)(?=\s|$|[.,!?])",
    re.I,
)
DATE = re.compile(
    r"\b(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?|"
    r"(?:today|tomorrow|next\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|week))|"
    r"\d{1,2}\s+(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
    r"(?:\s+\d{2,4})?)\b",
    re.I,
)
PAX = re.compile(r"\b(\d+)\s*(?:pax|passengers?|people|adults?)\b", re.I)

SLOT_KEYS = ("origin", "destination", "date", "passengers")


def classify(message: str, session: SessionMemory | None = None) -> IssueFamily:
    text = message or ""
    if ASSIST.search(text) or (ROUTE.search(text) and re.search(r"\b(book|flight|ticket|fly)\b", text, re.I)):
        return IssueFamily.ASSIST
    if session and (
        session.open_question in SLOT_KEYS
        or (session.choices.get("assist") or {})
    ):
        if ROUTE.search(text) or DATE.search(text) or PAX.search(text) or session.open_question in SLOT_KEYS:
            return IssueFamily.ASSIST
    if HELP.search(text):
        return IssueFamily.HELP
    return IssueFamily.UNCLASSIFIED


def slots_from(message: str, session: SessionMemory | None = None) -> dict[str, str]:
    filled = dict((session.choices.get("assist") or {}) if session else {})
    text = message or ""
    route = ROUTE.search(text)
    if route:
        filled["origin"] = route.group(1).strip(" .")
        filled["destination"] = route.group(2).strip(" .,?!")
    date = DATE.search(text)
    if date:
        filled["date"] = date.group(1).strip()
    pax = PAX.search(text)
    if pax:
        filled["passengers"] = pax.group(1)
    return {key: value for key, value in filled.items() if value}


def missing_slots(filled: dict[str, str]) -> list[str]:
    return [key for key in SLOT_KEYS if not filled.get(key)]


def request_for(family: IssueFamily, message: str, session: SessionMemory | None = None) -> ExtractedRequest:
    if family == IssueFamily.ASSIST:
        filled = slots_from(message, session)
        return ExtractedRequest(
            type=RequestType.BOOKING_ASSIST,
            notes=json.dumps(filled, ensure_ascii=False),
        )
    if family == IssueFamily.HELP:
        return ExtractedRequest(type=RequestType.HELP_QUESTION, notes=message)
    return ExtractedRequest(type=RequestType.GENERAL_HELP)


def persist_assist(session: SessionMemory, filled: dict[str, str]) -> None:
    current = dict(session.choices.get("assist") or {})
    current.update({key: value for key, value in filled.items() if value})
    session.choices["assist"] = current


def parse_notes(notes: str | None) -> dict[str, Any]:
    if not notes:
        return {}
    try:
        data = json.loads(notes)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}
