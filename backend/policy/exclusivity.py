"""Which already-eligible actions may be offered together, and in what order.

Two separate jobs, deliberately in one place because they are easy to confuse:

1. **Exclusivity** — a resolution track can make a goodwill action incoherent
   even when the delay rule allows it. Offering lounge access to someone whose
   money is being refunded and whose journey is over is not generous, it is
   noise. This is policy shape, so it lives here in code rather than in a
   prompt.

2. **Ordering** — when the passenger is distressed, the fastest resolution goes
   first. Order is presentation only.

The contract that makes this safe to add and safe to delete: the returned list
is always a subset of the actions already present in `evaluation.decisions`
with status ALLOW or ASK. This module can remove and reorder. It can never add.
Eligibility is decided entirely by `policy/engine.py` and its handlers before
anything here runs.
"""

from __future__ import annotations

from models.schemas import DecisionStatus, FrustrationCategory, PolicyEvaluation

# Actions that identify a resolution track once the engine has allowed or
# offered them. A track is the passenger's route out of the disruption.
TRACK_MARKERS: dict[str, frozenset[str]] = {
    "refund": frozenset({"refund_original", "refund_other_method"}),
    "cancellation": frozenset({"rebook_24h"}),
}

# Goodwill actions that stop making sense on a given track. Both tracks end the
# passenger's time in the terminal, which is exactly what lounge access and a
# meal voucher are for.
EXCLUDED_BY_TRACK: dict[str, frozenset[str]] = {
    "refund": frozenset({"lounge", "meal_voucher"}),
    "cancellation": frozenset({"lounge", "meal_voucher"}),
}

# Fastest route to a resolved passenger, first. Used only when frustration is
# high; otherwise the engine's own declaration order is preserved.
URGENCY_ORDER: tuple[str, ...] = (
    "refund_original",
    "rebook_24h",
    "hotel_delayed_hours",
    "meal_voucher",
    "lounge",
    "priority_rebooking",
)

# Categories that reorder the offer. Anything calmer keeps engine order, so a
# neutral turn and a today's-build turn read identically.
URGENT_CATEGORIES = frozenset({FrustrationCategory.DISTRESSED, FrustrationCategory.HOSTILE})

# Statuses that represent something the agent can put on the table. DENY,
# ESCALATE and INFORM are not offers, so they are never in the offered set —
# they stay in `decisions`, where the reply layer still explains them.
OFFERABLE = (DecisionStatus.ALLOW, DecisionStatus.ASK)


def resolution_track(evaluation: PolicyEvaluation) -> str | None:
    """Which track the engine has actually put on the table, if any."""
    offered = {d.action for d in evaluation.decisions if d.status in OFFERABLE}
    for track, markers in TRACK_MARKERS.items():
        if offered & markers:
            return track
    return None


def excluded_actions(evaluation: PolicyEvaluation) -> set[str]:
    """Goodwill actions the active track rules out. Empty when there is no track."""
    track = resolution_track(evaluation)
    if track is None:
        return set()
    return set(EXCLUDED_BY_TRACK.get(track, frozenset()))


def offered_actions(
    evaluation: PolicyEvaluation,
    frustration_category: FrustrationCategory | None = None,
) -> list[str]:
    """The ordered, exclusivity-filtered subset of what the engine allowed.

    Exclusion runs before ordering, so no frustration category can reintroduce
    a filtered action by any route.
    """
    seen: list[str] = []
    for decision in evaluation.decisions:
        if decision.status in OFFERABLE and decision.action not in seen:
            seen.append(decision.action)

    excluded = excluded_actions(evaluation)
    eligible = [action for action in seen if action not in excluded]

    if frustration_category not in URGENT_CATEGORIES:
        return eligible

    def rank(action: str) -> tuple[int, int]:
        if action in URGENCY_ORDER:
            return (0, URGENCY_ORDER.index(action))
        # Unranked actions keep their relative engine order, behind ranked ones.
        return (1, eligible.index(action))

    return sorted(eligible, key=rank)
