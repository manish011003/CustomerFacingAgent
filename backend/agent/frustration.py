"""Frustration detection: a signal, never an authority.

This module owns the text detectors the rest of the agent shares — the
legal/formal threat regex and the tone buckets previously copied into both
`agent/tools.py` and `products/extractors/heuristic.py` — plus the
deterministic frustration classifier.

`classify()` is pure: same utterance and same prior turns produce the same
category, confidence and signal order, with no model call and no clock.
`classify_llm()` asks a model for the same schema when a live client is
present. That is what lets the fallback path (zero LLM key) and the
orchestrator path write to one schema, so nothing downstream has to branch
on `agent_mode`.

Nothing here decides eligibility. The output can change tone, ordering, and
whether a supervisor is brought in. It cannot grant, deny, or override anything
`check_eligibility` / `evaluate_policy` returned.
"""

from __future__ import annotations

import json
import os
import re

from llm.client import LlmClient
from models.schemas import FrustrationAssessment, FrustrationCategory, SessionMemory

# The one copy of the legal/formal detector. `tools.py` and the heuristic
# extractor both import this rather than carrying their own regex, so the
# "legal language -> immediate escalation" rule and the `legal_language`
# frustration signal can never disagree about what counts.
LEGAL = re.compile(
    r"\b(legal action|lawsuit|sue|lawyer|formal complaint|file a complaint)\b",
    re.I,
)

ANGRY = re.compile(r"\b(furious|angry|frustrated|upset|unacceptable|ruined)\b", re.I)
ANGRY_STRONG = re.compile(r"furious|angry|unacceptable", re.I)
CONFUSED = re.compile(
    r"(don'?t understand|do not understand|confus|what does that mean|not sure what"
    r"|no ?one told me|nobody told me|makes no sense|what happened)",
    re.I,
)

# --- frustration signal buckets --------------------------------------------

COMPLAINT = re.compile(
    r"\b(unacceptable|appalling|disgraceful|outrageous|ridiculous|pathetic|useless"
    r"|worst|terrible|awful|incompeten\w*|disgusted|fed up|sick of|frustrated|upset)\b",
    re.I,
)
PROFANITY = re.compile(
    r"\b(damn|damn\w+|hell|bloody|crap|bullshit|wtf|fuck(?:ing|ed|er)?|shit|asshole|piss(?:ed)?)\b",
    re.I,
)
ABANDONMENT = re.compile(
    r"(never fly\w*|never book\w*|never using|cancel my account|close my account"
    r"|switch\w* to|take my business|social media|twitter|tell everyone)",
    re.I,
)
# Distress that is about the person, not the transaction. These are the words
# that should reach a human even when every entitlement has already been given.
DISTRESS = re.compile(
    r"(stranded|stuck at the airport|no ?where to go|nowhere to go|my (?:child|kid|baby|son|daughter)"
    r"|medical|medicine|insulin|wheelchair|elderly|pregnan\w*|funeral|hospital"
    r"|crying|desperate|(?:please help|help me)(?!\s+(?:book|check|with|plan))"
    r"|scared|panic\w*|can'?t afford|no money)",
    re.I,
)
HELPLESS = re.compile(
    r"(no ?one (?:is )?help\w*|nobody (?:is )?help\w*|been waiting|still waiting"
    r"|hours? (?:on|in) (?:the )?(?:phone|hold|queue)|third time|fourth time|again and again)",
    re.I,
)

# Signals are emitted in this order, always. A stable order makes the stored
# event byte-comparable across turns and keeps CI free of set-ordering flake.
SIGNAL_ORDER: tuple[str, ...] = (
    "repeated_request",
    "explicit_complaint",
    "caps_lock",
    "punctuation_escalation",
    "profanity",
    "helplessness",
    "abandonment_threat",
    "vulnerability_disclosed",
    "legal_language",
)

# What each signal contributes to the severity score. Fixed table, no tuning at
# runtime, so the classifier cannot drift between turns.
SIGNAL_WEIGHT: dict[str, int] = {
    "repeated_request": 2,
    "explicit_complaint": 2,
    "caps_lock": 1,
    "punctuation_escalation": 1,
    "profanity": 2,
    "helplessness": 2,
    "abandonment_threat": 3,
    "vulnerability_disclosed": 3,
    "legal_language": 3,
}

# Signals that mean "this person needs a human", as opposed to "this person is
# annoyed with us". Hostility alone does not buy a handover; distress does.
DISTRESS_SIGNALS = frozenset({"vulnerability_disclosed", "helplessness", "repeated_request"})
HOSTILE_SIGNALS = frozenset({"profanity", "abandonment_threat", "legal_language"})

# Score bands. Read as: at or above this score, the category applies.
CATEGORY_BANDS: tuple[tuple[int, FrustrationCategory], ...] = (
    (6, FrustrationCategory.DISTRESSED),
    (4, FrustrationCategory.FRUSTRATED),
    (2, FrustrationCategory.ANNOYED),
)

# Confidence per category, plus a small bump per corroborating signal. Capped at
# 0.95: a regex is never certain, and pretending otherwise would let the gate
# below auto-store something a human should have confirmed.
CATEGORY_CONFIDENCE: dict[FrustrationCategory, float] = {
    FrustrationCategory.NEUTRAL: 0.9,
    FrustrationCategory.ANNOYED: 0.6,
    FrustrationCategory.FRUSTRATED: 0.72,
    FrustrationCategory.DISTRESSED: 0.8,
    FrustrationCategory.HOSTILE: 0.8,
}
CONFIDENCE_PER_SIGNAL = 0.05
CONFIDENCE_CEILING = 0.95

CAPS_MIN_LETTERS = 12
CAPS_RATIO = 0.6

# Read at import so tests can monkeypatch the module attribute directly.
KB_AUTO_STORE_THRESHOLD = float(os.getenv("KB_AUTO_STORE_THRESHOLD", "0.75"))
FRUSTRATION_ESCALATION_THRESHOLD = float(os.getenv("FRUSTRATION_ESCALATION_THRESHOLD", "0.85"))
FRUSTRATION_CLASSIFIER = os.getenv("FRUSTRATION_CLASSIFIER", "auto")

ESCALATING_CATEGORIES = frozenset({FrustrationCategory.DISTRESSED, FrustrationCategory.HOSTILE})


def detect_emotion(message: str) -> str | None:
    """The existing tone axis: angry / frustrated / confused, or nothing.

    Kept deliberately separate from `classify()`. This drives one
    acknowledgement line of reply copy; the frustration category drives audit,
    escalation and analytics. Collapsing them would tie a UI string to a
    supervisor handover.
    """
    text = message or ""
    if PROFANITY.search(text):
        return "angry"
    if ANGRY.search(text):
        return "angry" if ANGRY_STRONG.search(text) else "frustrated"
    if CONFUSED.search(text):
        return "confused"
    return None


def detect_legal_or_formal(message: str) -> bool:
    return bool(LEGAL.search(message or ""))


def _caps_lock(message: str) -> bool:
    """Shouting, not acronyms. Needs enough letters to mean something."""
    letters = [c for c in message if c.isalpha()]
    if len(letters) < CAPS_MIN_LETTERS:
        return False
    upper = sum(1 for c in letters if c.isupper())
    return upper / len(letters) >= CAPS_RATIO


def _punctuation_escalation(message: str) -> bool:
    return bool(re.search(r"[!?]{2,}", message or ""))


def _intents(message: str) -> set[str]:
    """Request types this message asks for, via the existing heuristic extractor.

    Imported lazily: the extractor imports the detectors above, so a
    module-level import here would be a cycle. Constructed with no directory,
    because name/PNR matching is irrelevant to whether an ask repeated.
    """
    from products.extractors.heuristic import HeuristicExtractor

    extraction = HeuristicExtractor().extract(message or "")
    return {
        request.type.value
        for request in extraction.requests
        if request.type.value not in {"general_help", "status", "booking_assist", "help_question"}
    }


def _repeated_request(message: str, session: SessionMemory | None) -> bool:
    """The same ask, already made earlier in this conversation.

    Asking twice is the clearest non-lexical frustration signal there is: it
    means the last answer did not land, whatever words were used.
    """
    if session is None:
        return False
    current = _intents(message)
    if not current:
        return False
    for entry in session.messages:
        if entry.get("role") != "user":
            continue
        earlier = entry.get("content") or ""
        if earlier.strip() == (message or "").strip():
            # The live turn is appended to `messages` before the agent runs, so
            # the utterance under assessment is in there. It is not a repeat of
            # itself.
            continue
        if current & _intents(earlier):
            return True
    return False


def _signals(message: str, session: SessionMemory | None) -> list[str]:
    text = message or ""
    found = {
        "repeated_request": _repeated_request(text, session),
        "explicit_complaint": bool(COMPLAINT.search(text)),
        "caps_lock": _caps_lock(text),
        "punctuation_escalation": _punctuation_escalation(text),
        "profanity": bool(PROFANITY.search(text)),
        "helplessness": bool(HELPLESS.search(text)),
        "abandonment_threat": bool(ABANDONMENT.search(text)),
        "vulnerability_disclosed": bool(DISTRESS.search(text)),
        "legal_language": detect_legal_or_formal(text),
    }
    return [name for name in SIGNAL_ORDER if found[name]]


def _category(signals: list[str]) -> FrustrationCategory:
    if not signals:
        return FrustrationCategory.NEUTRAL
    score = sum(SIGNAL_WEIGHT[name] for name in signals)
    present = set(signals)

    # Hostility is aimed outward and needs no care package; distress is aimed
    # inward and does. Distress wins the tie, because the cost of missing a
    # stranded passenger is higher than the cost of over-reading an angry one.
    if score >= 6 and present & DISTRESS_SIGNALS:
        return FrustrationCategory.DISTRESSED
    if score >= 5 and present & HOSTILE_SIGNALS:
        return FrustrationCategory.HOSTILE
    for floor, category in CATEGORY_BANDS:
        if score >= floor:
            return category
    return FrustrationCategory.ANNOYED


def _confidence(category: FrustrationCategory, signals: list[str]) -> float:
    base = CATEGORY_CONFIDENCE[category]
    if category is FrustrationCategory.NEUTRAL:
        return round(base, 4)
    bump = CONFIDENCE_PER_SIGNAL * max(0, len(signals) - 1)
    return round(min(CONFIDENCE_CEILING, base + bump), 4)


CLASSIFY_LLM_SYSTEM = """Assess how this passenger is holding up. Return JSON only.

Weigh these as psychological signals of state, not as keyword matches:
- swearing or hostile language
- shouting in caps
- punctuation escalation (!!, ???)
- repeating a request already made in this conversation
- disclosing vulnerability (stranded, a dependent, medical need, no money)
- legal or formal-complaint language

Return an object with exactly these keys:
- category: one of neutral, annoyed, frustrated, distressed, hostile
- confidence: a number from 0 to 1
- signals: an array drawn only from repeated_request, explicit_complaint, caps_lock, punctuation_escalation, profanity, helplessness, abandonment_threat, vulnerability_disclosed, legal_language
- escalation_recommended: boolean
- low_confidence: boolean
- source: "llm_dynamic"

This assessment is a signal. It cannot grant, deny, or override eligibility.
"""


def classify(
    message: str,
    session: SessionMemory | None = None,
    *,
    source: str = "heuristic",
) -> FrustrationAssessment:
    """Assess one turn. Deterministic, offline, and safe to call every turn."""
    signals = _signals(message, session)
    category = _category(signals)
    confidence = _confidence(category, signals)
    return FrustrationAssessment(
        category=category,
        confidence=confidence,
        signals=signals,
        escalation_recommended=should_escalate(category, confidence),
        low_confidence=is_low_confidence(confidence),
        source=source,  # type: ignore[arg-type]
    )


def _latest_user(memory: SessionMemory) -> str:
    for entry in reversed(memory.messages):
        if entry.get("role") == "user":
            return entry.get("content") or ""
    return ""


def _classify_llm_user(memory: SessionMemory, message: str) -> str:
    recent = [
        f"{entry.get('role')}: {entry.get('content') or ''}"
        for entry in memory.messages[-12:]
        if entry.get("role") in {"user", "assistant"}
    ]
    transcript = "\n".join(recent) or f"user: {message}"
    return f"Latest utterance:\n{message}\n\nConversation so far:\n{transcript}"


def _assessment_from_llm(data: dict) -> FrustrationAssessment | None:
    raw_category = str(data.get("category") or "").strip().lower()
    try:
        category = FrustrationCategory(raw_category)
    except ValueError:
        return None
    try:
        confidence = float(data.get("confidence", 0.0))
    except (TypeError, ValueError):
        return None
    confidence = round(min(1.0, max(0.0, confidence)), 4)
    raw_signals = data.get("signals") if isinstance(data.get("signals"), list) else []
    found = {str(name) for name in raw_signals if str(name) in SIGNAL_ORDER}
    signals = [name for name in SIGNAL_ORDER if name in found]
    return FrustrationAssessment(
        category=category,
        confidence=confidence,
        signals=signals,
        escalation_recommended=should_escalate(category, confidence),
        low_confidence=is_low_confidence(confidence),
        source="llm_dynamic",
    )


def classify_llm(memory: SessionMemory, llm: LlmClient) -> FrustrationAssessment:
    """Assess one turn via the model. Same schema as classify(); never an authority."""
    message = _latest_user(memory)
    mode = str(FRUSTRATION_CLASSIFIER or "auto").strip().lower()
    if mode == "heuristic":
        return classify(message, memory)
    turn = llm.chat(
        purpose="frustration",
        messages=[
            {"role": "system", "content": CLASSIFY_LLM_SYSTEM},
            {"role": "user", "content": _classify_llm_user(memory, message)},
        ],
        session_id=memory.session_id,
        json_mode=True,
    )
    if turn is None:
        return classify(message, memory)
    try:
        data = json.loads(turn.text or "{}")
    except (TypeError, ValueError, json.JSONDecodeError):
        return classify(message, memory)
    if not isinstance(data, dict):
        return classify(message, memory)
    assessment = _assessment_from_llm(data)
    return assessment if assessment is not None else classify(message, memory)


def should_escalate(category: FrustrationCategory, confidence: float) -> bool:
    """Both gates, or neither. A hostile guess is not a reason to fetch a human."""
    return category in ESCALATING_CATEGORIES and confidence >= FRUSTRATION_ESCALATION_THRESHOLD


def is_low_confidence(confidence: float) -> bool:
    """Below the store threshold the observation is logged but not aggregated."""
    return confidence < KB_AUTO_STORE_THRESHOLD


ESCALATION_NOTE = (
    "The passenger is in severe distress. A supervisor case is already open for "
    "duty of care. This grants no entitlement on its own."
)
