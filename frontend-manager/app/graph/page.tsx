"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AppFrame, Panel, Stepper, TopNav } from "@aero/ui";
import { createPlatform } from "@aero/ui";

const factory = createPlatform("manager");

type Passenger = { id: string; name: string; loyalty_tier?: string };

export default function GraphPage() {
  const [people, setPeople] = useState<Passenger[]>([]);
  const [customerId, setCustomerId] = useState("");
  const [graph, setGraph] = useState<any>(null);

  useEffect(() => {
    fetch("/api/passengers")
      .then((r) => r.json())
      .then((rows: Passenger[]) => {
        setPeople(rows);
        if (rows[0]) setCustomerId(rows[0].id);
      })
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    if (!customerId) return;
    fetch(`/api/passengers/${customerId}/graph`)
      .then((r) => r.json())
      .then(setGraph)
      .catch(() => undefined);
  }, [customerId]);

  return (
    <AppFrame>
      <TopNav factory={factory} activeHref="/graph" LinkComponent={Link} />
      <Stepper steps={factory.steps} current={1} />
      <div className="px-5 pb-6">
        <Panel>
          <div className="flex flex-wrap gap-2">
            {people.map((p) => (
              <button
                type="button"
                key={p.id}
                onClick={() => setCustomerId(p.id)}
                className={`rounded-full px-3 py-1 text-[12px] font-semibold ${customerId === p.id ? "bg-[#2f6bff] text-white" : "bg-slate-100 text-slate-600"}`}
              >
                {p.name}
              </button>
            ))}
          </div>
          <p className="mt-3 text-[12px] text-slate-500">Edges are written by the policy engine. This is not a vector graph and not extra policy.</p>
          <div className="mt-4 grid gap-2 md:grid-cols-2">
            {(graph?.edges || []).map((e: any) => (
              <div key={e.id} className="rounded-xl border border-slate-100 p-3">
                <div className="text-[11px] font-bold uppercase tracking-wide text-[#2f6bff]">{e.rel}</div>
                <div className="mt-1 text-sm text-slate-700">
                  {e.from_id} → {e.to_id}
                </div>
                <div className="mt-1 text-[12px] text-slate-500">{e.reason}</div>
              </div>
            ))}
            {!graph?.edges?.length && <p className="text-sm text-slate-500">No edges yet. Resolve a passenger case first.</p>}
          </div>
        </Panel>
      </div>
    </AppFrame>
  );
}
