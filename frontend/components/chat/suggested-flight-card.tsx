"use client";

import Link from "next/link";
import { ArrowUpRight, Plane } from "lucide-react";

import { flightStatusCopy } from "@/lib/labels";
import type { SuggestedFlight } from "@/lib/flights";

export function SuggestedFlightCard({ flight }: { flight: SuggestedFlight }) {
  const scheduled = flight.source === "scheduled";
  const status = flightStatusCopy(flight.status);

  return (
    <Link
      href={flight.href || "/exit"}
      className="hero-sky group relative mt-2 block overflow-hidden rounded-card px-4 py-4 text-white shadow-card transition duration-200 ease-swift hover:shadow-lift"
    >
      <span className="suggested-plane pointer-events-none absolute right-4 top-5 text-white/70">
        <Plane className="h-5 w-5" strokeWidth={2} />
      </span>
      <div className="relative flex items-start justify-between gap-3">
        <div>
          <p className="text-2xs font-semibold uppercase tracking-[0.16em] text-white/70">
            {scheduled ? "Scheduled departure" : "Sample departure"}
          </p>
          <p className="mt-1 text-lg font-bold tracking-tight">{flight.flight}</p>
        </div>
        <span className="rounded-full bg-white/15 px-2.5 py-1 text-2xs font-semibold">{status.label}</span>
      </div>
      <p className="relative mt-3 flex items-center gap-2 text-sm font-medium">
        <Plane className="h-3.5 w-3.5 text-white/80" strokeWidth={2} />
        {flight.origin} → {flight.destination}
      </p>
      <p className="relative mt-1.5 text-xs text-white/75">
        {flight.date_label || flight.date || "Open date"} · {flight.scheduled_departure}
        {flight.scheduled_arrival ? ` · ${flight.scheduled_arrival}` : ""}
        {flight.gate ? ` · Gate ${flight.gate}` : ""}
      </p>
      <p className="relative mt-3 flex items-center gap-1 text-2xs text-white/55">
        Look-only · tap to leave this chat
        <ArrowUpRight className="h-3.5 w-3.5 text-white/80 transition group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
      </p>
    </Link>
  );
}
