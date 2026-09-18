"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AppFrame, Panel, Stepper, TopNav } from "@aero/ui";
import { createPlatform } from "@aero/ui";

const factory = createPlatform("manager");

export default function PassengersPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [selected, setSelected] = useState<any>(null);

  useEffect(() => {
    fetch("/api/passengers")
      .then((r) => r.json())
      .then(setRows)
      .catch(() => undefined);
  }, []);

  async function open(id: string) {
    const data = await fetch(`/api/passengers/${id}`).then((r) => r.json());
    setSelected(data);
  }

  return (
    <AppFrame>
      <TopNav factory={factory} activeHref="/passengers" LinkComponent={Link} />
      <Stepper steps={factory.steps} current={0} />
      <div className="grid gap-4 px-5 pb-6 lg:grid-cols-[320px_1fr]">
        <Panel>
          <div className="text-[11px] font-bold uppercase tracking-wide text-slate-400">Passenger 360</div>
          <div className="mt-3 space-y-2">
            {rows.map((p) => (
              <button
                type="button"
                key={p.id}
                onClick={() => open(p.id)}
                className="w-full rounded-xl border border-slate-100 px-3 py-2 text-left hover:border-[#2f6bff]"
              >
                <div className="font-semibold">{p.name}</div>
                <div className="text-[11px] text-slate-500">
                  {p.loyalty_tier} · {p.pnr || "No PNR"} · {p.account_origin === "seeded" ? "Enrolled" : "New"}
                </div>
              </button>
            ))}
          </div>
        </Panel>
        <Panel>
          {!selected && <p className="p-8 text-center text-sm text-slate-500">Select a passenger. Enrolled members and newly onboarded accounts both appear here.</p>}
          {selected && (
            <div className="space-y-4">
              <div>
                <div className="text-2xl font-extrabold">{selected.passenger?.name}</div>
                <div className="text-sm text-slate-500">
                  {selected.passenger?.loyalty_tier} · {selected.passenger?.pnr} · {selected.passenger?.email}
                </div>
              </div>
              <div>
                <div className="text-[11px] font-bold uppercase tracking-wide text-slate-400">Bookings</div>
                {(selected.bookings || []).map((b: any) => (
                  <div key={b.id} className="mt-2 rounded-xl border border-slate-100 px-3 py-2 text-sm">
                    {b.flight || b.leg} · {b.route} · {b.status}
                  </div>
                ))}
              </div>
              <div>
                <div className="text-[11px] font-bold uppercase tracking-wide text-slate-400">Events {selected.events?.length || 0}</div>
                <div className="mt-2 max-h-64 overflow-auto text-[12px] text-slate-600">
                  {(selected.events || []).slice(-12).map((e: any) => (
                    <div key={e.id} className="border-b border-slate-50 py-1">
                      {e.kind} {e.action || ""} {e.status || ""}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </Panel>
      </div>
    </AppFrame>
  );
}
