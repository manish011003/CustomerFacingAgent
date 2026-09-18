from models.schemas import (
    CustomerAgentContext,
    DecisionStatus,
    FrustrationCategory,
    PolicyDecision,
)
from products.replies.base import ReplyRenderer


def _line(decision: PolicyDecision) -> str:
    label = {
        "meal_voucher": "a meal voucher" + (f" of ₹{decision.amount_inr}" if decision.amount_inr else ""),
        "lounge": "lounge access",
        "hotel_delayed_hours": decision.scope or "hotel covering delayed hours only",
        "rebook_24h": "free rebooking on the next available flight within 24 hours (no specific flight number is in our records)",
        "refund_original": "a full refund to the original payment method within 7 business days",
        "priority_rebooking": "priority rebooking, not extra compensation",
    }.get(decision.action, decision.action.replace("_", " "))
    return label


# One short line, never an entitlement. Acknowledging tone must not imply approval.
ACKNOWLEDGEMENT = {
    "angry": "I hear you, and I'm sorry — this is a real disruption.",
    "frustrated": "I hear you, and I'm sorry this has been frustrating.",
    "confused": "Let me lay out exactly where things stand.",
}


class TemplateReplyRenderer(ReplyRenderer):
    def render(self, ctx: CustomerAgentContext, utterance: str) -> str:
        ack = ACKNOWLEDGEMENT.get(ctx.emotion or "")

        if ctx.unidentified:
            return " ".join(
                p for p in [
                    ack,
                    "Please sign in to AERO Resolve so I can load your passenger record. "
                    "New travellers can open an account from Join.",
                ] if p
            )
        if not ctx.booking:
            first = (ctx.identity.name.split()[0] if ctx.identity else "there")
            return " ".join(
                p for p in [
                    ack,
                    f"{first}, you are signed in but I don't have a booking on this account yet. "
                    "Add your trip under Account — I will not invent a flight number.",
                ] if p
            )

        name = ctx.identity.name if ctx.identity else "there"
        first = name.split()[0]
        parts: list[str] = []
        if ack:
            parts.append(ack)

        if ctx.disruption and ctx.booking:
            if ctx.disruption.get("type") == "cancellation":
                parts.append(
                    f"{first}, flight {ctx.booking.flight} {ctx.booking.route} is cancelled "
                    f"({ctx.booking.status_reason})."
                )
            elif ctx.disruption.get("type") == "delay":
                parts.append(
                    f"{first}, flight {ctx.booking.flight} {ctx.booking.route} is delayed "
                    f"{ctx.booking.delay_hours} hours (new departure {ctx.booking.new_departure})."
                )

        ev = ctx.policy_decision
        if not ev:
            parts.append("I don't have an established policy decision for this request.")
            return " ".join(parts)

        # Presentation only: offered_actions is the exclusivity-filtered, possibly
        # reordered subset. Membership never changes what is ALLOW/ASK — it only
        # decides what is put in front of the passenger, and in which order.
        offered = list(ev.offered_actions)
        by_action = {d.action: d for d in ev.decisions}
        allows = [by_action[a] for a in offered if by_action.get(a) and by_action[a].status == DecisionStatus.ALLOW]
        asks = [by_action[a] for a in offered if by_action.get(a) and by_action[a].status == DecisionStatus.ASK]
        denies = [d for d in ev.decisions if d.status == DecisionStatus.DENY]
        escalations = [d for d in ev.decisions if d.status == DecisionStatus.ESCALATE]
        informs = [d for d in ev.decisions if d.status == DecisionStatus.INFORM]
        urgent = bool(
            ctx.frustration
            and ctx.frustration.category
            in {FrustrationCategory.DISTRESSED, FrustrationCategory.HOSTILE}
        )

        if allows:
            executed = [a for a in allows if a.action in (ctx.session_memory.executed_actions or []) or a.action in ev.execute]
            unique = []
            seen = set()
            for d in executed or allows:
                if d.action in seen:
                    continue
                seen.add(d.action)
                unique.append(d)
            actionable = [d for d in unique if d.action not in {"priority_rebooking", "status"}]
            if actionable and ev.execute:
                parts.append(
                    "I can arrange " + ", ".join(_line(d) for d in actionable if d.action in ev.execute) + " now (simulated)."
                )
            elif asks:
                pass
            elif actionable:
                parts.append("You qualify for " + ", ".join(_line(d) for d in actionable) + ".")

        if asks and "rebook_or_refund_choice" in (ev.missing_slots + ctx.missing_slots):
            if offered and offered[0] == "refund_original":
                parts.append(
                    "You can choose a full refund to the original payment method or free rebooking within 24 hours. Which do you want?"
                )
            else:
                parts.append(
                    "You can choose free rebooking within 24 hours or a full refund to the original payment method. Which do you want?"
                )
        elif asks:
            for d in asks:
                parts.append(d.reason if not urgent else _line(d).capitalize() + " is available.")

        for d in informs:
            if d.action == "priority_rebooking" and not urgent:
                parts.append(d.reason)

        for d in denies:
            parts.append(d.reason)

        for d in escalations:
            parts.append(d.reason + " I'm sending this to a supervisor with your case context so you don't have to repeat it.")

        related = [b for b in ctx.related_bookings if ctx.booking and b.id != ctx.booking.id]
        for b in related:
            if b.status == "UNAFFECTED":
                parts.append(f"Your {b.leg} {b.route} on {b.date_label} is unaffected.")

        if ctx.session_memory.executed_actions:
            parts.append("Already on this case (simulated): " + ", ".join(ctx.session_memory.executed_actions) + ".")

        text = " ".join(p for p in parts if p)
        return text or "I've logged your message against this booking. Tell me what you'd like me to do next."
