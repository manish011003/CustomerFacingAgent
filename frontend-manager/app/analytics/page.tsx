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

  const cards = [
    { label: "Passengers", value: data?.passengers ?? "—", hint: "Live directory" },
    { label: "Events", value: data?.events ?? "—", hint: "Audit trail" },
    { label: "Escalations", value: data?.escalations ?? "—", hint: "Human backup" },
    { label: "KB", value: data?.kb_backend ?? "—", hint: "elasticsearch or json" },
  ];

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
      <div className="px-5 pb-6">
        <Panel>
          <p className="text-sm text-slate-500">{data?.note || "Live passenger directory and audit metrics."}</p>
        </Panel>
      </div>
    </AppFrame>
  );
}
