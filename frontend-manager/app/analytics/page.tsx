"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AppFrame, Panel, Stepper, TopNav } from "@aero/ui";
import { createPlatform } from "@aero/ui";

const factory = createPlatform("manager");

export default function AnalyticsPage() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetch("/api/analytics/summary")
      .then((r) => r.json())
      .then(setData)
      .catch(() => undefined);
  }, []);

  const c = data?.containment;
  const pct = (value: number | null | undefined) =>
    typeof value === "number" ? `${Math.round(value * 100)}%` : "—";

  const cards = [
    {
      label: "Containment",
      value: pct(c?.containment_rate),
      hint: c?.turns ? `${c.contained_turns}/${c.turns} turns needed no human` : "No measured turns yet",
    },
    {
      label: "Grounding",
      value: pct(c?.grounding_coverage),
      hint: c?.decisions_claimed ? `${c.decisions_cited}/${c.decisions_claimed} claims cited` : "Claims with a clause",
    },
    { label: "p95 latency", value: c?.p95_latency_ms ? `${c.p95_latency_ms}ms` : "—", hint: "Slowest 1 in 20 turns" },
    {
      label: "Spend",
      value: typeof c?.est_spend_usd === "number" ? `$${c.est_spend_usd.toFixed(4)}` : "—",
      hint: c?.llm_calls ? `${c.llm_calls} model calls` : "No model calls made",
    },
    { label: "Passengers", value: data?.passengers ?? "—", hint: "Live directory" },
    { label: "Events", value: data?.events ?? "—", hint: "Audit trail" },
    { label: "Escalations", value: data?.escalations ?? "—", hint: "Human backup" },
    { label: "KB", value: data?.kb_backend ?? "—", hint: "elasticsearch or json" },
  ];

  const byReason: [string, number][] = Object.entries(c?.escalations_by_reason ?? {}) as [string, number][];

  return (
    <AppFrame>
      <TopNav factory={factory} activeHref="/analytics" LinkComponent={Link} />
      <Stepper steps={factory.steps} current={2} />
      <div className="grid gap-4 px-5 pb-6 md:grid-cols-4">
        {cards.map((c) => (
          <Panel key={c.label}>
            <div className="text-[11px] font-bold uppercase tracking-wide text-slate-400">{c.label}</div>
            <div className="mt-2 text-3xl font-extrabold">{c.value}</div>
            <div className="mt-1 text-[12px] text-slate-500">{c.hint}</div>
          </Panel>
        ))}
      </div>
      {byReason.length > 0 && (
        <div className="px-5 pb-6">
          <Panel>
            <div className="text-[11px] font-bold uppercase tracking-wide text-slate-400">
              Why authority ran out
            </div>
            <div className="mt-3 space-y-2">
              {byReason.map(([reason, count]) => (
                <div key={reason} className="flex items-center justify-between text-sm">
                  <span className="text-slate-600">{reason.replace(/_/g, " ")}</span>
                  <span className="font-bold">{count}</span>
                </div>
              ))}
            </div>
            <p className="mt-3 text-[12px] text-slate-500">
              Each of these is a policy limit on agent authority, not a failure to understand the passenger.
            </p>
          </Panel>
        </div>
      )}
      <div className="px-5 pb-6">
        <Panel>
          <p className="text-sm text-slate-500">{data?.note || "Live passenger directory and audit metrics."}</p>
        </Panel>
      </div>
    </AppFrame>
  );
}
