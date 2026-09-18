"""When a passenger conversation is still open, handed over, or actually closed.

Issuing a meal voucher is not a resolution. A case is resolved only when the
passenger says so, or leaves good feedback. Escalation, once opened, stays
opened: later chatter such as "NO!" must not flip the operations board back
to resolved.
"""

from __future__ import annotations

import re
from typing import Any

from models.schemas import PolicyEvaluation, ServiceFeedback, SessionMemory

FEEDBACK_PROMPT = (
    "Is everything resolved on this case? Tell me if you still need help."
)

_SKIP_OFFERED = {"status", "priority_rebooking", "general_help", "booking_assist", "help_question"}

_WANT_MORE = re.compile(
    r"\b(want more|more compensation|additional compensation|extra compensation|"
    r"not enough|that(?:'s| is) not enough|deserve more|beyond (?:the )?policy)\b",
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
    r"no(?:thing)? more(?: help)? needed|that will do|i(?:'?m) good)\b",
    re.I,
)
_ASKED_TO_CLOSE = re.compile(
    r"everything resolved|how was (?:this|the) service|"
    r"rate (?:this|the) service|from 1 to 5|still need help",
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


def wants_escalation(message: str, session: SessionMemory | None = None) -> bool:
    text = message or ""
    if _ESCALATE.search(text) or wants_more(text):
        return True
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
    elif session and session.awaiting_feedback:
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
    if wants_escalation(text, session):
        return False
    if _RESOLVED.search(text):
        return True
    if session.awaiting_feedback and _ASKED_TO_CLOSE.search(last_assistant_text(session)):
        if re.search(r"^\s*(that(?:'s| is) all|thats all|all (?:set|done)|yes.*resolved)\b", text, re.I):
            return True
        if _AFFIRM.search(text) and not wants_more(text) and not re.search(r"^\s*no\b", text, re.I):
            return True
    feedback = parse_feedback(text, session)
    return bool(feedback and feedback.sentiment == "positive")


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

    good_feedback = bool(session.feedback and session.feedback.sentiment == "positive")
    if session.resolved_by_customer or good_feedback:
        return "resolved"
    return "open"
