from models.schemas import (
    CustomerAgentContext,
    DecisionStatus,
    RequestType,
)
from products.replies.base import ReplyRenderer


def _name(ctx: CustomerAgentContext) -> str:
    if ctx.identity and ctx.identity.name:
        return ctx.identity.name.split()[0]
    return "there"


def _asked(ctx: CustomerAgentContext) -> set[str]:
    return {request.type.value for request in ctx.requests_this_turn}


def _has_spoken(ctx: CustomerAgentContext) -> bool:
    return any(message.get("role") == "assistant" for message in ctx.session_memory.messages)


ACKNOWLEDGEMENT = {
    "angry": "I hear you — this delay is a mess.",
    "frustrated": "I know this has been frustrating.",
    "confused": "Let me keep this simple.",
}

OFFER_LABEL = {
    "meal_voucher": "a meal voucher",
    "lounge": "lounge access",
    "hotel_delayed_hours": "hotel cover for the delayed hours",
    "rebook_24h": "free rebooking within 24 hours",
    "refund_original": "a refund to the original payment method",
}


class TemplateReplyRenderer(ReplyRenderer):
    def render(self, ctx: CustomerAgentContext, utterance: str) -> str:
        from agent.closure import (
            ALREADY_ESCALATED,
            asks_to_close_case,
            is_greeting,
            is_thanks,
            reopens_resolution,
            wants_more,
        )
        from agent.router import missing_slots, parse_notes, SLOT_KEYS

        ack = ACKNOWLEDGEMENT.get(ctx.emotion or "")
        first = _name(ctx)
        asked = _asked(ctx)
        spoken = _has_spoken(ctx)
        executed = set(ctx.session_memory.executed_actions)
        ev = ctx.policy_decision

        if ctx.unidentified:
            return " ".join(
                part
                for part in [
                    ack,
                    "Please sign in so I can load your booking. New travellers can open an account from Join.",
                ]
                if part
            )

        if is_thanks(utterance):
            if ctx.session_memory.escalated_to_human:
                return ALREADY_ESCALATED
            if ctx.session_memory.resolved_by_customer:
                return "You're welcome — this case is closed. Safe travels."
            return "You're welcome! If anything else comes up, I'm here. Safe travels."

        if is_greeting(utterance):
            if ctx.session_memory.escalated_to_human:
                return ALREADY_ESCALATED
            if spoken:
                return f"Hi {first} — I'm here. What do you need?"
            if ctx.booking and ctx.booking.status == "DELAYED":
                return (
                    f"Hi {first} — I can see {ctx.booking.flight or 'your flight'} is delayed "
                    f"{ctx.booking.delay_hours} hours. What can I help with?"
                )
            return f"Hi {first} — I'm here. What can I help with?"

        if asks_to_close_case(utterance) and ctx.session_memory.resolved_by_customer:
            return "All set — case closed. Safe travels!"

        if reopens_resolution(utterance):
            heard = ack or "I hear you."
            if ctx.booking:
                return f"{heard} I've reopened this case. What's still unresolved?"
            return (
                f"{heard} I've reopened this case. Tell me what's still wrong "
                "and I'll stay on it."
            )

        escalating = bool(ev and ev.escalate) or bool(
            any(d.status == DecisionStatus.ESCALATE for d in (ev.decisions if ev else []))
        )

        if "booking_assist" in asked and not escalating:
            notes = next((request.notes for request in ctx.requests_this_turn if request.type == RequestType.BOOKING_ASSIST), "")
            filled = parse_notes(notes)
            missing = missing_slots({key: str(filled.get(key) or "") for key in SLOT_KEYS})
            if missing:
                need = ", ".join(missing)
                return f"Sure — I can help sketch a new trip. I still need {need}. I can't invent a flight number or fare."
            summary = (
                f"{filled.get('origin')} to {filled.get('destination')} on {filled.get('date')} "
                f"for {filled.get('passengers')} passenger(s)"
            )
            return (
                f"Got it — {summary}. This chat has no ticketing inventory, so I will not invent a "
                "flight number or fare. There's a look-only departure on the card if you want the board."
            )

        if "help_question" in asked and not escalating:
            help_hits = [hit for hit in (ctx.retrieval.rules if ctx.retrieval else []) if hit.kind == "help"]
            if help_hits:
                return help_hits[0].text
            return "I can help with check-in, baggage, seats, or planning a new trip. What do you want to know?"

        if not ctx.booking:
            return " ".join(
                part
                for part in [
                    ack,
                    f"{first}, you're signed in but I don't have a booking on this account yet. "
                    "Add your trip under Account — I will not invent a flight number.",
                ]
                if part
            )

        if not ev:
            return f"I've got your booking, {first}. What do you need help with?"

        if escalating or wants_more(utterance):
            if ctx.session_memory.escalated_to_human:
                return (
                    "A supervisor already has this — I can't add extra compensation from here. "
                    "Want me to leave them a note?"
                )
            return (
                "I can't approve extra compensation — that's outside the delay policy. "
                "I've sent this to a supervisor with your booking so you don't have to repeat it."
            )

        issued = [action for action in ev.execute if action in asked]
        leftover = [
            action
            for action in ev.offered_actions
            if action not in executed
            and action not in issued
            and action in OFFER_LABEL
        ]

        if issued:
            names = ", ".join(OFFER_LABEL.get(action, action.replace("_", " ")) for action in issued)
            extra = f" {OFFER_LABEL[leftover[0]].capitalize()} is still available if you want it." if leftover else ""
            return f"Done — I've issued {names} (simulated).{extra}"

        if asked & {"meal_voucher", "lounge", "hotel_delayed_hours"} and asked & executed:
            extra = f" {OFFER_LABEL[leftover[0]].capitalize()} is still available." if leftover else ""
            return f"That's already on the booking.{extra}"

        denies = [d for d in ev.decisions if d.status == DecisionStatus.DENY and d.action in asked]
        if denies:
            hotel = next((d for d in denies if "hotel" in d.action), None)
            if hotel and ctx.booking and ctx.booking.delay_hours is not None:
                body = (
                    f"A hotel only applies after more than 5 hours. Yours is {ctx.booking.delay_hours}, "
                    "so I can't book one. A meal voucher and lounge access are still available."
                )
            else:
                body = denies[0].reason
            return f"{ack} {body}".strip() if ack else body

        if asked & {"rebook_24h", "refund_original"} or "rebook_or_refund_choice" in (ev.missing_slots + ctx.missing_slots):
            if ctx.booking and ctx.booking.status == "CANCELLED":
                return (
                    f"{first}, {ctx.booking.flight or 'your flight'} {ctx.booking.route} was cancelled. "
                    "You can rebook free within 24 hours or take a full refund to the original payment method. Which do you want?"
                )
            return "You can rebook free within 24 hours or take a full refund. Which do you want?"

        if not spoken or asked == {"status"}:
            parts = [ack] if ack else []
            if ctx.booking.status == "CANCELLED":
                parts.append(
                    f"{first}, {ctx.booking.flight or 'your flight'} {ctx.booking.route} was cancelled"
                    + (f" ({ctx.booking.status_reason})" if ctx.booking.status_reason else "")
                    + ". You can rebook free within 24 hours or take a full refund. Which do you want?"
                )
            elif ctx.booking.status == "DELAYED":
                hours = ctx.booking.delay_hours
                parts.append(
                    f"Sorry about the wait, {first}. {ctx.booking.flight or 'Your flight'} is delayed "
                    f"{hours} hours"
                    + (f" — now leaving at {ctx.booking.new_departure}" if ctx.booking.new_departure else "")
                    + ". I can issue a meal voucher and lounge access."
                )
                if hours is not None and hours <= 5:
                    parts.append("A hotel only applies after more than 5 hours, so I can't do that for this delay.")
                parts.append("What would you like?")
            else:
                parts.append(f"{first}, I've loaded your booking. What do you need?")
            return " ".join(part for part in parts if part)

        leftover_text = ""
        if leftover:
            leftover_text = " I can still arrange " + " or ".join(OFFER_LABEL[a] for a in leftover[:2]) + "."
        return f"I'm here, {first}.{leftover_text} What do you need next?"
