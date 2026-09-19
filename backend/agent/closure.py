"""When a passenger conversation is still open, handed over, or actually closed.

Issuing a meal voucher is not a resolution. A case is resolved only when the
passenger says so, or leaves good feedback. Escalation, once opened, stays
opened: later chatter such as "NO!" must not flip the operations board back
to resolved. The inverse is also sticky in the other direction: after a close,
later hostility or "I'm frustrated" reopens the card. A 3/5 rating alone does
not — swearing or saying the issue is still wrong does.
"""

from __future__ import annotations

import re
from typing import Any

from agent.frustration import ANGRY, COMPLAINT, PROFANITY
from models.schemas import PolicyEvaluation, ServiceFeedback, SessionMemory

FEEDBACK_PROMPT = (
    "Is everything resolved on this case? Tell me if you still need help."
)
ALREADY_ESCALATED = (
    "A supervisor already has your case — they can see the delay and what I arranged. "
    "I'm still here if you want me to add a note for them."
)

_SKIP_OFFERED = {"status", "priority_rebooking", "general_help", "booking_assist", "help_question"}

_WANT_MORE = re.compile(
    r"\b(want more|more compensation|additional compensation|extra compensation|"
    r"not enough|that(?:'s| is) not enough|deserve more|beyond (?:the )?policy|"
    r"(?:give|pay|send|owe)\s+me\s+(?:₹|rs\.?|inr)?\s*\d|"
    r"(?:₹|rs\.?|inr)\s*\d{3,}|\d{3,}\s*(?:₹|rs\.?|inr|rupees))\b",
    re.I,
)
_GREETING = re.compile(
    r"^\s*(hi|hello|hey|yo|(?:thanks|thank you)(?:\s+a\s+lot)?|ok|okay|hmm|hm)+\s*[!.]*\s*$",
    re.I,
)
_THANKS = re.compile(
    r"^\s*(?:thanks|thank you|thx)(?:\s+a\s+lot)?\s*[!.]*\s*$",
    re.I,
)
_STILL_WRONG = re.compile(
    r"\b(not resolved|still (?:broken|wrong|open|unresolved)|this isn'?t (?:done|resolved|over)|"
    r"reopen(?: the)?(?: this)? case)\b",
    re.I,
)
_ESCALATE = re.compile(
    r"\b(escalate|supervisor|speak to (?:a )?(?:manager|human|person|someone)|"
    r"talk to (?:a )?(?:manager|human|person|someone)|manager please)\b",
    re.I,
)
_SUPERVISOR_OFFER = re.compile(
    r"supervisor case|escalate|supervisor|a person should take over",
    re.I,
)
_AFFIRM = re.compile(
    r"^\s*(yes|yeah|yep|yup|ok|okay|sure|please(?: do)?|go ahead|do it|proceed)\b",
    re.I,
)
_RESOLVED = re.compile(
    r"\b(that(?:'s| is) all|that(?:'s| is) it|that(?:'s| is) everything|"
    r"i(?:'?m)? (?:all )?done|all set|nothing else|no further|"
    r"everything(?:'s| is) (?:fine|resolved|sorted|ok|okay)|"
    r"this (?:is|case is) resolved|issue is resolved|"
    r"(?:it(?:'s| is)|its) resolved|"
    r"(?:the )?(?:case|issue) (?:is )?resolved|"
    r"no(?:thing)? more(?: help)? needed|that will do|i(?:'?m) good)\b",
    re.I,
)
_CLOSE_CASE = re.compile(
    r"^\s*(?:please\s+|can you\s+|could you\s+|i want to\s+|i(?:'?d) like to\s+)?"
    r"close(?:\s+(?:the|this|my))?\s+case(?:\s+please)?\s*[!.]*\s*$",
    re.I,
)
_ASKED_TO_CLOSE = re.compile(
    r"everything(?:\s+is)?\s+resolved|how was (?:this|the) service|"
    r"rate (?:this|the|your) (?:service|experience)|from 1 to 5|on a scale of|"
    r"still need help|need anything else",
    re.I,
)
_ASKED_IF_RESOLVED = re.compile(
    r"everything(?:\s+is)?\s+resolved|how was (?:this|the) service|"
    r"rate (?:this|the|your) (?:service|experience)|from 1 to 5|on a scale of|"
    r"still need help",
    re.I,
)
_RATING = re.compile(
    r"\b([1-5])\s*(?:/|out of)?\s*5\b|\b([1-5])\s*stars?\b|"
    r"(?:rate|rating|score)\s*(?:(?:is|of|as)\s*)?([1-5])\b",
    re.I,
)
_POSITIVE = re.compile(
    r"\b(great|excellent|amazing|perfect|helpful|satisfied|wonderful|"
    r"good (?:service|job|help)|thank you that(?:'s| is) all)\b",
    re.I,
)
_NEGATIVE = re.compile(
    r"\b(terrible|awful|unhelpful|poor(?: service)?|unsatisfied|not happy|"
    r"bad service|worst|horrible|this is not resolved)\b",
    re.I,
)
_LONE_RATING = re.compile(r"^\s*([1-5])\s*[!.]*\s*$")


def last_assistant_text(session: SessionMemory) -> str:
    for message in reversed(session.messages[:-1]):
        if message.get("role") == "assistant":
            return message.get("content") or ""
    return ""


def offered_supervisor(session: SessionMemory) -> bool:
    return bool(_SUPERVISOR_OFFER.search(last_assistant_text(session)))


def wants_more(message: str) -> bool:
    return bool(_WANT_MORE.search(message or ""))


def is_greeting(message: str) -> bool:
    return bool(_GREETING.match(message or ""))


def is_thanks(message: str) -> bool:
    return bool(_THANKS.match(message or ""))


def asks_to_close_case(message: str) -> bool:
    text = message or ""
    return bool(_CLOSE_CASE.match(text) or _RESOLVED.search(text))


def reopens_resolution(message: str) -> bool:
    """True when a later turn undoes a spoken close — hostility, not a 3★ rating."""
    text = message or ""
    if not text.strip() or is_greeting(text):
        return False
    if parse_feedback(text) and not _STILL_WRONG.search(text) and not PROFANITY.search(text):
        return False
    return bool(
        PROFANITY.search(text)
        or COMPLAINT.search(text)
        or ANGRY.search(text)
        or _STILL_WRONG.search(text)
        or _NEGATIVE.search(text)
    )


def wants_escalation(message: str, session: SessionMemory | None = None) -> bool:
    text = message or ""
    if session and session.escalated_to_human and is_greeting(text):
        return False
    if _ESCALATE.search(text) or wants_more(text):
        return True
    if session and session.escalated_to_human:
        return False
    if session and offered_supervisor(session) and _AFFIRM.search(text):
        return True
    return False


def remaining_offered(evaluation: PolicyEvaluation | None, session: SessionMemory) -> list[str]:
    offered = list(evaluation.offered_actions) if evaluation else []
    if not offered and session.last_evaluation:
        offered = list(session.last_evaluation.offered_actions)
    return [action for action in offered if action not in session.executed_actions and action not in _SKIP_OFFERED]


def parse_feedback(message: str, session: SessionMemory | None = None) -> ServiceFeedback | None:
    text = message or ""
    rating = None
    match = _RATING.search(text)
    if match:
        rating = int(next(group for group in match.groups() if group))
    elif session and (session.awaiting_feedback or session.resolved_by_customer):
        lone = _LONE_RATING.match(text)
        if lone:
            rating = int(lone.group(1))

    positive = bool(_POSITIVE.search(text))
    negative = bool(_NEGATIVE.search(text))
    if rating is None and not positive and not negative:
        return None

    if rating is not None:
        sentiment = "positive" if rating >= 4 else "negative" if rating <= 2 else "mixed"
    elif positive and not negative:
        sentiment = "positive"
    elif negative and not positive:
        sentiment = "negative"
    else:
        sentiment = "mixed"

    comment = text.strip()
    return ServiceFeedback(rating=rating, comment=comment or None, sentiment=sentiment, source="chat")


def confirms_resolution(message: str, session: SessionMemory) -> bool:
    text = message or ""
    if wants_escalation(text, session) or reopens_resolution(text):
        return False
    if _CLOSE_CASE.match(text) or _RESOLVED.search(text):
        return True
    asked_if_resolved = _ASKED_IF_RESOLVED.search(last_assistant_text(session))
    if session.awaiting_feedback or asked_if_resolved:
        if re.search(
            r"^\s*(that(?:'s| is) all|thats all|all (?:set|done)|yes.*resolved|"
            r"(?:it(?:'s| is)|its)\s+resolved)\b",
            text,
            re.I,
        ):
            return True
        if (
            asked_if_resolved
            and _AFFIRM.search(text)
            and not wants_more(text)
            and not re.search(r"^\s*no\b", text, re.I)
        ):
            return True
    feedback = parse_feedback(text, session)
    return bool(feedback and feedback.sentiment == "positive")


def thread_declares_resolved(session: SessionMemory | None, messages: list[dict[str, Any]] | None = None) -> bool:
    """True when the passenger already said the case is closed, later chatter included."""
    rows = list(messages if messages is not None else (session.messages if session else []))
    declared = False
    for row in rows:
        if row.get("role") != "user":
            continue
        text = row.get("content") or ""
        if wants_escalation(text, session):
            return False
        if _CLOSE_CASE.match(text) or _RESOLVED.search(text):
            declared = True
        elif reopens_resolution(text):
            declared = False
    return declared


def should_prompt_feedback(
    *,
    session: SessionMemory,
    evaluation: PolicyEvaluation | None,
    escalating: bool,
) -> bool:
    if escalating or session.escalated_to_human or session.feedback or session.resolved_by_customer:
        return False
    if not session.executed_actions:
        return False
    if remaining_offered(evaluation, session):
        return False
    if evaluation and any(
        decision.action in {"booking_assist", "help_question"} for decision in evaluation.decisions
    ):
        return False
    return True


def should_show_feedback_popup(*, case_status: str | None, session: SessionMemory) -> bool:
    """CSAT is a post-close popup, not a card that closes the case."""
    if case_status != "resolved":
        return False
    if session.feedback and session.feedback.rating is not None:
        return False
    return True


def already_asked_feedback(reply: str) -> bool:
    return bool(_ASKED_TO_CLOSE.search(reply or ""))


def asked_if_resolved(reply: str) -> bool:
    return bool(_ASKED_IF_RESOLVED.search(reply or ""))


def reconcile_open_case(case: dict[str, Any]) -> dict[str, Any]:
    """Keep the ops card aligned with the transcript: close or reopen."""
    status = (case or {}).get("status")
    if status == "escalated":
        return case
    messages = (case or {}).get("transcript") or []
    declared = thread_declares_resolved(None, messages)
    if status == "open" and declared:
        updated = dict(case)
        updated["status"] = "resolved"
        updated["resolved_by"] = updated.get("resolved_by") or "customer"
        return updated
    later_hostility = any(
        row.get("role") == "user" and reopens_resolution(row.get("content") or "")
        for row in messages
    )
    if status == "resolved" and messages and not declared and later_hostility:
        updated = dict(case)
        updated["status"] = "open"
        updated["resolved_at"] = None
        updated["resolved_by"] = None
        return updated
    return case


def case_status(
    *,
    evaluation: PolicyEvaluation | None,
    session: SessionMemory,
    distress: Any = None,
    existing: dict[str, Any] | None = None,
) -> str:
    """Sticky case state for this conversation. Executed actions never close it."""
    del existing
    previously_escalated = session.escalated_to_human or bool(session.escalations)
    currently_escalating = bool(evaluation and evaluation.escalate) or bool(distress)
    if previously_escalated or currently_escalating:
        return "escalated"

    if session.resolved_by_customer:
        return "resolved"
    return "open"
