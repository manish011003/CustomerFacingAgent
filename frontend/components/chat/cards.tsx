"use client";

import { ArrowUpRight, CheckCircle2, Plane } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { InlineCard } from "@/components/chat/inline-card";
import { SuggestedFlightCard } from "@/components/chat/suggested-flight-card";
import { choiceDecisions, newActions } from "@/lib/cards";
import { ESCALATION_COPY, actionButtonLabel, actionLabel, actionRequestPhrase, flightStatusCopy } from "@/lib/labels";
import type { Booking, Escalation, PolicyDecision, Turn } from "@/lib/types";

export function BookingCard({ booking }: { booking: Booking }) {
  const status = flightStatusCopy(booking.status);
  const delay =
    booking.status.toUpperCase() === "DELAYED" && booking.delay_hours != null
      ? `${booking.delay_hours}h delay`
      : null;

  return (
    <div className="hero-sky relative mt-2 overflow-hidden rounded-card px-4 py-4 text-white shadow-card">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-2xs font-semibold uppercase tracking-[0.16em] text-white/70">Your flight</p>
          <p className="mt-1 text-lg font-bold tracking-tight">{booking.flight || booking.leg}</p>
        </div>
        <span className="rounded-full bg-white/15 px-2.5 py-1 text-2xs font-semibold">{status.label}</span>
      </div>
      <p className="mt-3 flex items-center gap-2 text-sm font-medium">
        <Plane className="h-3.5 w-3.5 text-white/80" strokeWidth={2} />
        {booking.origin} → {booking.destination}
      </p>
      <p className="mt-1.5 text-xs text-white/75">
        {booking.date_label} · {booking.scheduled_departure}
        {booking.new_departure ? ` · now ${booking.new_departure}` : ""}
        {delay ? ` · ${delay}` : ""}
      </p>
      {booking.status_reason && <p className="mt-2 text-xs leading-5 text-white/80">{booking.status_reason}</p>}
      <p className="mt-3 text-2xs text-white/55">Booking {booking.pnr}</p>
    </div>
  );
}

export function ChoiceCard({
  decisions,
  disabled,
  onChoose,
}: {
  decisions: PolicyDecision[];
  disabled?: boolean;
  onChoose: (message: string) => void;
}) {
  if (!decisions.length) return null;

  return (
    <InlineCard title="I can help with">
      <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
        {decisions.map((decision) => (
          <Button
            key={decision.action}
            variant="chip"
            size="sm"
            disabled={disabled}
            onClick={() => onChoose(actionRequestPhrase(decision.action))}
            className="justify-start rounded-full sm:justify-center"
          >
            {actionButtonLabel(decision.action)}
          </Button>
        ))}
      </div>
    </InlineCard>
  );
}

export function ConfirmationCard({ actions }: { actions: string[] }) {
  if (!actions.length) return null;

  return (
    <InlineCard
      className="border-good-line bg-good-bg/40"
      title="Arranged for you"
      aside={
        <span className="flex h-6 w-6 items-center justify-center rounded-full bg-good-bg">
          <CheckCircle2 className="h-3.5 w-3.5 text-good-fg" strokeWidth={2.2} />
        </span>
      }
    >
      <ul className="space-y-1.5">
        {actions.map((action) => (
          <li
            key={action}
            className="flex items-center justify-between gap-3 rounded-full border border-line bg-ice px-3 py-2"
          >
            <span className="text-xs font-medium text-ink">{actionLabel(action)}</span>
            <Badge tone="good">Simulated</Badge>
          </li>
        ))}
      </ul>
      <p className="mt-2.5 text-2xs text-ink-muted">This is a prototype. No real booking, refund, or hotel was changed.</p>
    </InlineCard>
  );
}

export function EscalationCard({ escalation }: { escalation: Escalation }) {
  const code = escalation.escalation_reason_codes[0];
  const reason = (code && ESCALATION_COPY[code]) || escalation.escalation_reasons[0] || "A supervisor needs to review this.";

  return (
    <InlineCard
      className="border-warn-line"
      title="Handed to a supervisor"
      aside={
        <span className="flex h-6 w-6 items-center justify-center rounded-full bg-warn-bg">
          <ArrowUpRight className="h-3.5 w-3.5 text-warn-fg" strokeWidth={2.4} />
        </span>
      }
    >
      <p className="text-xs leading-5 text-ink-soft">{reason}</p>
      {escalation.escalation_reasons.length > 1 && (
        <ul className="mt-2 space-y-1 text-xs text-ink-muted">
          {escalation.escalation_reasons.slice(1).map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
      )}
      <p className="mt-2.5 text-2xs text-ink-faint">Case {escalation.id} stays with a supervisor until they close it.</p>
    </InlineCard>
  );
}

export function AgentCards({
  turn,
  previousExecuted,
  isLatest,
  sending,
  onChoose,
  showHandover,
}: {
  turn: Turn;
  previousExecuted: Set<string>;
  isLatest: boolean;
  sending: boolean;
  onChoose: (message: string) => void;
  showHandover?: boolean;
}) {
  const choices = isLatest ? choiceDecisions(turn) : [];
  const confirmed = newActions(turn, previousExecuted);

  return (
    <div className="mt-2 space-y-2">
      {turn.booking && <BookingCard booking={turn.booking} />}
      {turn.suggestedFlight && <SuggestedFlightCard flight={turn.suggestedFlight} />}
      {choices.length > 0 && <ChoiceCard decisions={choices} disabled={sending} onChoose={onChoose} />}
      {confirmed.length > 0 && <ConfirmationCard actions={confirmed} />}
      {showHandover && turn.escalation && <EscalationCard escalation={turn.escalation} />}
    </div>
  );
}
