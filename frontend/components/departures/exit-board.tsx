"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ArrowLeft, Plane } from "lucide-react";

import { Wordmark } from "@/components/brand";
import { InlineCard } from "@/components/chat/inline-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FALLBACK_FLIGHTS, type SuggestedFlight } from "@/lib/flights";
import { flightStatusCopy } from "@/lib/labels";

function clockLabel(now: Date) {
  return now.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" });
}

export function ExitBoard() {
  const router = useRouter();
  const params = useSearchParams();
  const highlight = (params.get("flight") || "").toUpperCase();
  const from = params.get("from");
  const to = params.get("to");
  const [now, setNow] = useState(() => new Date());
  const [flights, setFlights] = useState<SuggestedFlight[]>(FALLBACK_FLIGHTS);

  useEffect(() => {
    const timer = window.setInterval(() => setNow(new Date()), 1000);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/flights/upcoming")
      .then((response) => (response.ok ? response.json() : null))
      .then((body: { flights?: SuggestedFlight[] } | null) => {
        if (!cancelled && body?.flights?.length) setFlights(body.flights);
      })
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, []);

  const rows = useMemo(() => {
    const picked = [...flights];
    if (highlight && !picked.some((row) => row.flight.toUpperCase() === highlight)) {
      picked.unshift({
        flight: highlight,
        origin: from || "—",
        destination: to || "—",
        scheduled_departure: "--:--",
        status: "NOT FOUND",
        source: "random",
        href: "/exit",
      });
    }
    return picked;
  }, [flights, highlight, from, to]);

  const opened = rows.find((row) => highlight && row.flight.toUpperCase() === highlight) ?? rows[0];
  const openedStatus = opened ? flightStatusCopy(opened.status) : null;

  return (
    <div className="flex h-dvh flex-col bg-canvas">
      <header className="border-b border-line bg-white/95 px-4 py-3 backdrop-blur sm:px-6">
        <div className="mx-auto flex max-w-thread items-center justify-between gap-3">
          <Wordmark compact />
          <div className="flex min-w-0 items-center gap-2">
            <div className="hidden rounded-full bg-ice px-3 py-1.5 sm:block">
              <span className="text-xs font-medium tabular text-ink-soft">{clockLabel(now)}</span>
            </div>
            <Button variant="secondary" size="sm" onClick={() => router.push("/")}>
              <ArrowLeft className="h-3.5 w-3.5" strokeWidth={2} />
              Return to chat
            </Button>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto scroll-slim px-4 py-5 sm:px-6">
        <div className="mx-auto flex max-w-thread flex-col gap-4">
          <section className="hero-sky relative overflow-hidden rounded-card px-5 py-6 text-white shadow-card">
            <Plane className="suggested-plane pointer-events-none absolute right-5 top-5 h-5 w-5 text-white/70" strokeWidth={2} />
            <p className="text-2xs font-semibold uppercase tracking-[0.16em] text-white/70">404</p>
            <h1 className="mt-2 text-2xl font-bold tracking-tight">Exiting customer service</h1>
            <p className="mt-2 max-w-[42ch] text-sm leading-6 text-white/80">
              This chat cannot ticket a seat. Upcoming departures are look-only
              {highlight ? (
                <>
                  {" "}
                  — <span className="font-semibold text-white">{highlight}</span> is the flight you opened.
                </>
              ) : null}
            </p>
          </section>

          {opened && (
            <div className="hero-sky relative overflow-hidden rounded-card px-4 py-4 text-white shadow-card">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-2xs font-semibold uppercase tracking-[0.16em] text-white/70">Opened departure</p>
                  <p className="mt-1 text-lg font-bold tracking-tight">{opened.flight}</p>
                </div>
                {openedStatus && (
                  <span className="rounded-full bg-white/15 px-2.5 py-1 text-2xs font-semibold">{openedStatus.label}</span>
                )}
              </div>
              <p className="mt-3 flex items-center gap-2 text-sm font-medium">
                <Plane className="h-3.5 w-3.5 text-white/80" strokeWidth={2} />
                {opened.origin} → {opened.destination}
              </p>
              <p className="mt-1.5 text-xs text-white/75">
                {opened.date_label || opened.date || "Open date"} · {opened.scheduled_departure}
                {opened.scheduled_arrival ? ` · ${opened.scheduled_arrival}` : ""}
                {opened.gate ? ` · Gate ${opened.gate}` : ""}
              </p>
            </div>
          )}

          <InlineCard title="Upcoming flights">
            <ul className="space-y-1.5">
              {rows.map((row, index) => {
                const status = flightStatusCopy(row.status);
                const active = highlight && row.flight.toUpperCase() === highlight;
                return (
                  <li
                    key={`${row.flight}-${row.origin}-${index}`}
                    className={`departures-row flex items-center justify-between gap-3 rounded-full border px-3 py-2 ${
                      active ? "border-brand-line bg-brand-ice" : "border-line bg-ice"
                    }`}
                    style={{ animationDelay: `${index * 70}ms` }}
                  >
                    <div className="min-w-0">
                      <p className="truncate text-xs font-semibold text-ink">
                        {row.flight}
                        <span className="font-medium text-ink-muted">
                          {" "}
                          · {row.origin} → {row.destination}
                        </span>
                      </p>
                      <p className="text-2xs tabular text-ink-faint">
                        {row.scheduled_departure}
                        {row.gate ? ` · Gate ${row.gate}` : ""}
                      </p>
                    </div>
                    <Badge tone={status.tone}>{status.label}</Badge>
                  </li>
                );
              })}
            </ul>
            <p className="mt-2.5 text-2xs text-ink-muted">This is a prototype. No real booking, refund, or hotel was changed.</p>
          </InlineCard>
        </div>
      </div>

      <div className="bg-white px-4 py-3 shadow-composer sm:px-6">
        <div className="mx-auto flex max-w-thread items-center justify-between gap-3">
          <p className="text-xs text-ink-muted">You left the resolution chat.</p>
          <Button variant="primary" size="sm" onClick={() => router.push("/")}>
            Return to chat
          </Button>
        </div>
      </div>
    </div>
  );
}
