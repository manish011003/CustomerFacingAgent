"use client";

import { LogOut, RotateCcw } from "lucide-react";

import { Wordmark } from "@/components/brand";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { flightStatusCopy, initialsOf } from "@/lib/labels";
import type { Booking, LlmHealth, Passenger } from "@/lib/types";

export function ChatHeader({
  passenger,
  booking,
  llm,
  onSignOut,
  onRestart,
}: {
  passenger: Passenger;
  booking: Booking | null;
  llm: LlmHealth | null;
  onSignOut: () => void;
  onRestart: () => void;
}) {
  const status = booking ? flightStatusCopy(booking.status) : null;

  return (
    <header className="border-b border-line bg-white/95 px-4 py-3 backdrop-blur sm:px-6">
      <div className="mx-auto flex max-w-thread items-center justify-between gap-3">
        <Wordmark compact />
        <div className="flex min-w-0 items-center gap-2">
          {llm && (
            <Badge tone={llm.enabled ? "good" : "neutral"} className="hidden sm:inline-flex">
              {llm.enabled ? `Live agent · ${llm.provider}` : "Demo mode"}
            </Badge>
          )}
          {booking && status && (
            <div className="hidden min-w-0 items-center gap-2 rounded-full bg-ice px-3 py-1.5 sm:flex">
              <span className="truncate text-xs font-medium text-ink-soft">
                {booking.flight || booking.leg} · {booking.origin} → {booking.destination}
              </span>
              <Badge tone={status.tone}>{status.label}</Badge>
            </div>
          )}
          <div className="hidden text-right sm:block">
            <div className="text-xs font-semibold text-ink">{passenger.name}</div>
            <div className="text-2xs text-ink-muted">{passenger.loyalty_tier}</div>
          </div>
          <span className="grid h-9 w-9 place-items-center rounded-full bg-brand text-2xs font-bold text-white">
            {initialsOf(passenger.name)}
          </span>
          <Button variant="quiet" size="sm" onClick={onRestart} aria-label="New conversation">
            <RotateCcw className="h-3.5 w-3.5" strokeWidth={2} />
          </Button>
          <Button variant="quiet" size="sm" onClick={onSignOut} aria-label="Sign out">
            <LogOut className="h-3.5 w-3.5" strokeWidth={2} />
          </Button>
        </div>
      </div>
    </header>
  );
}
