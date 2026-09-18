"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AppFrame, Panel, PrimaryButton, Stepper, TopNav } from "@aero/ui";
import { createDecisionChrome, createPlatform } from "@aero/ui";

const factory = createPlatform("manager");

export default function QueuePage() {
  const [cases, setCases] = useState<any[]>([]);
  const [selected, setSelected] = useState<any>(null);
  const [note, setNote] = useState("");
  const [filter, setFilter] = useState<"all" | "escalated" | "open">("all");

  async function load() {
    const c = await fetch("/api/cases").then((r) => r.json());
    setCases(c);
  }

  useEffect(() => {
    load().catch(() => undefined);
  }, []);

  async function openCase(item: any) {
    const full = await fetch(`/api/cases/${item.id}`).then((r) => r.json());
    setSelected(full);
  }

  async function assess() {
    if (!selected) return;
    const updated = await fetch(`/api/cases/${selected.id}/assess`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "assessed", note }),
    }).then((r) => r.json());
    setSelected(updated);
    setNote("");
    load();
  }

  const visible = cases.filter((c) => (filter === "all" ? true : c.status === filter));
  const currentStep = factory.stepIndex({
    identified: Boolean(selected),
    hasDecision: Boolean(selected?.policy_decisions?.length),
    executed: selected?.status === "assessed",
    escalated: selected?.status === "escalated",
  });

  return (
    <AppFrame>
      <TopNav factory={factory} activeHref="/" LinkComponent={Link} />
      <Stepper steps={factory.steps} current={currentStep} />

      <div className="grid min-w-[1080px] grid-cols-[280px_minmax(420px,1fr)] gap-4 px-5 pb-6">
        <aside className="space-y-3">
          <Panel>
            <div className="flex items-center justify-between">
              <div className="text-[11px] font-bold uppercase tracking-wide text-slate-400">Queue</div>
              <select
                className="rounded-full border border-slate-200 bg-white px-2 py-1 text-[11px]"
                value={filter}
                onChange={(e) => setFilter(e.target.value as any)}
              >
                <option value="all">All</option>
                <option value="escalated">Escalated</option>
                <option value="open">Open</option>
              </select>
            </div>
            <div className="mt-3 space-y-2">
              {visible.map((c) => (
                <button
                  type="button"
                  key={c.id}
                  onClick={() => openCase(c)}
                  className={`w-full rounded-xl border px-3 py-2 text-left text-sm ${
                    selected?.id === c.id ? "border-[#2f6bff] bg-blue-50" : "border-slate-100 hover:border-slate-300"
                  }`}
                >
                  <div className="font-semibold">{c.customer || "Unknown"}</div>
                  <div className="text-[11px] text-slate-500">
                    {c.pnr} · {c.status}
                  </div>
                </button>
              ))}
              {!visible.length && <p className="text-sm text-slate-500">No cases yet. Run AERO Resolve first.</p>}
            </div>
          </Panel>
        </aside>

        <Panel className="min-h-[560px]">
          {!selected && <p className="p-8 text-center text-sm text-slate-500">Select a case. This CRM never invents extra compensation.</p>}
          {selected && (
            <>
              <div className="flex items-start justify-between gap-4 border-b border-slate-100 pb-4">
                <div>
                  <div className="text-2xl font-extrabold">{selected.customer}</div>
                  <div className="text-sm text-slate-500">
                    {selected.pnr} · {selected.flight}
                  </div>
                </div>
                <span className="rounded-full bg-amber-50 px-3 py-1 text-[11px] font-bold uppercase text-amber-700">{selected.status}</span>
              </div>

              {selected.escalation_reasons && (
                <div className="mt-4 rounded-xl bg-amber-50 px-4 py-3 text-sm text-amber-800">{selected.escalation_reasons.join(" ")}</div>
              )}

              <div className="mt-5 mb-2 grid grid-cols-[1.5fr_110px_1fr] gap-2 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                <span>Decision</span>
                <span>Status</span>
                <span>Source</span>
              </div>
              {(selected.policy_decisions || []).map((d: any, i: number) => {
                const chrome = createDecisionChrome(d.status);
                return (
                  <div key={i} className="grid grid-cols-[1.5fr_110px_1fr] items-start gap-2 border-b border-slate-50 py-3 text-sm">
                    <div>
                      <div className="font-semibold capitalize">{d.action.replaceAll("_", " ")}</div>
                      <div className="text-[12px] text-slate-500">{d.reason}</div>
                    </div>
                    <span className={`h-fit w-fit rounded-full border px-2 py-0.5 text-[11px] font-semibold ${chrome.pill}`}>{chrome.label}</span>
                    <span className="text-[11px] text-slate-400">{d.source}</span>
                  </div>
                );
              })}

              <div className="mt-5">
                <div className="text-[11px] font-bold uppercase tracking-wide text-slate-400">Transcript</div>
                <div className="mt-2 max-h-40 overflow-y-auto rounded-xl bg-slate-50 p-3 text-[12px] text-slate-600">
                  {(selected.transcript || []).map((m: any, i: number) => (
                    <div key={i} className="mb-2">
                      <b>{m.role}:</b> {m.content}
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-4">
                <textarea
                  className="w-full rounded-xl border border-slate-200 p-3 text-sm"
                  rows={3}
                  placeholder="Supervisor note — logged as human, not agent authority"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                />
                <div className="mt-2">
                  <PrimaryButton onClick={assess}>Assess case</PrimaryButton>
                </div>
                {selected.manager_assessment && (
                  <p className="mt-2 text-xs text-emerald-700">
                    Logged: {selected.manager_assessment.status} — {selected.manager_assessment.note}
                  </p>
                )}
              </div>
            </>
          )}
        </Panel>
      </div>
    </AppFrame>
  );
}
