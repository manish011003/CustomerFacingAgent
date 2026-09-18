"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { AppFrame, Panel, PrimaryButton, Stepper, TopNav } from "@aero/ui";
import { createDecisionChrome, createPlatform, toIata } from "@aero/ui";
import { api, chatSessionId, clearSession, getToken, initials } from "../lib/auth";

const factory = createPlatform("customer");

type Msg = { role: "user" | "assistant"; text: string };
type Tab = "options" | "conversation" | "record";

export default function ResolvePage() {
  const [sessionId, setSessionId] = useState("");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Msg[]>([]);
  const [packet, setPacket] = useState<any>(null);
  const [trace, setTrace] = useState<any[]>([]);
  const [eligibility, setEligibility] = useState<any[]>([]);
  const [busy, setBusy] = useState(false);
  const [tab, setTab] = useState<Tab>("options");
  const [timelineOpen, setTimelineOpen] = useState(true);
  const [ready, setReady] = useState(false);

  const identity = packet?.identity;
  const booking = packet?.booking;
  const origin = toIata(booking?.origin);
  const dest = toIata(booking?.destination);

  const currentStep = factory.stepIndex({
    identified: Boolean(identity),
    hasDecision: eligibility.length > 0,
    executed: (packet?.executed_actions || []).length > 0,
    escalated: eligibility.some((e) => e.status === "ESCALATE"),
  });

  useEffect(() => {
    if (!getToken()) {
      window.location.href = "/login";
      return;
    }
    setSessionId(chatSessionId());
    api<any>("/api/me")
      .then((data) => {
        setPacket({
          identity: data.passenger,
          booking: data.affected_booking,
          retrieved_facts: data.affected_booking
            ? [`${data.passenger.name} / ${data.passenger.loyalty_tier} / PNR ${data.passenger.pnr}`]
            : ["Signed in. No disrupted booking on this account yet."],
          missing_slots: data.affected_booking ? [] : ["booking"],
          kb_backend: data.kb_backend,
          executed_actions: [],
        });
        setEligibility(data.eligibility || []);
        setReady(true);
      })
      .catch(() => {
        window.location.href = "/login";
      });
  }, []);

  async function send(text: string) {
    const content = text.trim();
    if (!content || !sessionId) return;
    setBusy(true);
    setMessages((m) => [...m, { role: "user", text: content }]);
    setInput("");
    try {
      const data = await api<any>("/api/chat", {
        method: "POST",
        body: JSON.stringify({ session_id: sessionId, message: content }),
      });
      setMessages((m) => [...m, { role: "assistant", text: data.reply }]);
      setPacket(data.context_packet);
      setTrace(data.trace || []);
      setEligibility(data.eligibility || []);
      setTab("options");
    } catch {
      setMessages((m) => [...m, { role: "assistant", text: "Resolution service is offline. Start the API on port 8000." }]);
    } finally {
      setBusy(false);
    }
  }

  const grouped = useMemo(() => {
    const allow = eligibility.filter((e) => e.status === "ALLOW");
    const rest = eligibility.filter((e) => e.status !== "ALLOW");
    return { allow, rest };
  }, [eligibility]);

  if (!ready) {
    return (
      <AppFrame>
        <TopNav factory={factory} activeHref="/" LinkComponent={Link} />
        <div className="p-10 text-sm text-slate-500">Loading your passenger record…</div>
      </AppFrame>
    );
  }

  return (
    <AppFrame>
      <TopNav
        factory={factory}
        activeHref="/"
        LinkComponent={Link}
        account={identity ? { name: identity.name, initials: initials(identity.name) } : null}
        onSignOut={() => {
          api("/api/auth/logout", { method: "POST" }).catch(() => undefined);
          clearSession();
          window.location.href = "/login";
        }}
      />
      <Stepper steps={factory.steps} current={currentStep} />

      <div className="grid min-w-[1080px] grid-cols-[240px_minmax(420px,1fr)_270px] gap-4 px-5 pb-6">
        <aside className="space-y-3">
          <Panel>
            {booking ? (
              <>
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-[28px] font-extrabold tracking-tight text-slate-900">{origin}</div>
                    <div className="text-[11px] uppercase tracking-wide text-slate-400">{booking.origin}</div>
                    <div className="mt-3 text-[11px] text-slate-500">{booking.date_label}</div>
                    <div className="text-sm font-semibold">{booking.scheduled_departure}</div>
                  </div>
                  <div className="pt-2 text-slate-300">↔</div>
                  <div className="text-right">
                    <div className="text-[28px] font-extrabold tracking-tight text-slate-900">{dest}</div>
                    <div className="text-[11px] uppercase tracking-wide text-slate-400">{booking.destination}</div>
                    <div className="mt-3 text-[11px] text-slate-500">{booking.status}</div>
                    <div className="text-sm font-semibold">{booking.new_departure || "—"}</div>
                  </div>
                </div>
                <div className="mt-4 flex flex-wrap gap-2 text-[11px] text-slate-500">
                  <Meta icon="✈" label={booking.flight || booking.leg} />
                  <Meta icon="⏱" label={booking.delay_hours != null ? `${booking.delay_hours}h delay` : booking.status} />
                </div>
                <p className="mt-3 text-[12px] leading-5 text-slate-500">{booking.status_reason || "Status from this passenger's booking only."}</p>
              </>
            ) : (
              <div>
                <div className="text-[22px] font-extrabold text-slate-400">— → —</div>
                <p className="mt-2 text-sm text-slate-500">
                  No disrupted trip on this account. Add a booking under Account.
                </p>
              </div>
            )}
          </Panel>

          <Panel>
            {identity ? (
              <div className="flex items-center gap-3">
                <div className="grid h-10 w-10 place-items-center rounded-full bg-slate-800 text-xs font-bold text-white">
                  {initials(identity.name)}
                </div>
                <div>
                  <div className="text-sm font-semibold">{identity.name}</div>
                  <div className="text-[11px] text-slate-500">
                    {identity.loyalty_tier || identity.tier} · {identity.pnr || "No PNR yet"}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-sm text-slate-500">Not signed in.</p>
            )}
            {identity && <div className="mt-3 text-[11px] text-slate-400">{identity.email}</div>}
            <Link href="/account" className="mt-3 inline-block text-[11px] font-semibold uppercase tracking-wide text-[#2f6bff]">
              Manage account
            </Link>
          </Panel>
        </aside>

        <section>
          <Panel className="min-h-[560px]">
            <div className="flex items-end gap-6 border-b border-slate-100">
              <TabBtn active={tab === "options"} onClick={() => setTab("options")} count={eligibility.length} label="Options" />
              <TabBtn active={tab === "conversation"} onClick={() => setTab("conversation")} count={messages.length} label="Conversation" />
              <TabBtn active={tab === "record"} onClick={() => setTab("record")} count={trace.length} label="Record" />
            </div>

            <div className="mt-4 flex flex-wrap items-center gap-4 text-[12px] text-slate-500">
              <span className="font-semibold text-rose-500">Allowed {grouped.allow.length}</span>
              <span>All decisions {eligibility.length}</span>
            </div>

            {tab === "options" && (
              <div className="mt-4">
                <div className="mb-2 grid grid-cols-[1.4fr_90px_90px_90px] gap-2 px-2 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                  <span>Action</span>
                  <span>Status</span>
                  <span>Source</span>
                  <span className="text-right">Apply</span>
                </div>
                {eligibility.length === 0 && (
                  <div className="rounded-xl border border-dashed border-slate-200 p-8 text-center text-sm text-slate-500">
                    Policy options appear from this passenger&apos;s booking. Ask Resolve if you need a specific action.
                  </div>
                )}
                {eligibility.map((row) => {
                  const chrome = createDecisionChrome(row.status);
                  return (
                    <div key={row.action + row.status} className="grid grid-cols-[1.4fr_90px_90px_90px] items-center gap-2 border-b border-slate-50 px-2 py-3 text-sm">
                      <label className="flex items-start gap-3">
                        <input type="checkbox" readOnly checked={row.status === "ALLOW"} className="mt-1 accent-[#2f6bff]" />
                        <span>
                          <div className="font-semibold capitalize text-slate-800">{row.action.replaceAll("_", " ")}</div>
                          <div className="text-[12px] leading-5 text-slate-500">{row.reason}</div>
                        </span>
                      </label>
                      <span className={`w-fit rounded-full border px-2 py-0.5 text-[11px] font-semibold ${chrome.pill}`}>{chrome.label}</span>
                      <span className="truncate text-[11px] text-slate-400">{row.source}</span>
                      <div className="text-right">
                        {row.status === "ALLOW" ? (
                          <PrimaryButton onClick={() => send(`Please apply ${row.action.replaceAll("_", " ")}.`)}>Apply</PrimaryButton>
                        ) : (
                          <span className="text-[11px] text-slate-300">—</span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {tab === "conversation" && (
              <div className="mt-4 flex min-h-[380px] flex-col">
                <div className="flex-1 space-y-3 overflow-y-auto">
                  {messages.length === 0 && (
                    <p className="text-sm text-slate-500">Tell Resolve what you need for this disruption. It cannot add benefits that policy does not allow.</p>
                  )}
                  {messages.map((m, i) => (
                    <div
                      key={i}
                      className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-6 ${
                        m.role === "user" ? "ml-auto bg-[#2f6bff] text-white" : "bg-slate-50 text-slate-700 ring-1 ring-slate-100"
                      }`}
                    >
                      {m.text}
                    </div>
                  ))}
                </div>
                <form
                  className="mt-4 flex gap-2"
                  onSubmit={(e: FormEvent) => {
                    e.preventDefault();
                    send(input);
                  }}
                >
                  <input
                    className="flex-1 rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm outline-none focus:border-[#2f6bff]"
                    placeholder="Message Resolve…"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                  />
                  <PrimaryButton type="submit" disabled={busy}>
                    Send
                  </PrimaryButton>
                </form>
              </div>
            )}

            {tab === "record" && (
              <ol className="mt-4 space-y-2 text-sm">
                {trace.map((t, i) => (
                  <li key={i} className="flex gap-3 rounded-xl bg-slate-50 px-3 py-2">
                    <span className="w-20 shrink-0 text-[11px] font-bold uppercase text-[#2f6bff]">{t.step}</span>
                    <span className="text-slate-600">{t.detail}</span>
                  </li>
                ))}
              </ol>
            )}
          </Panel>
        </section>

        <aside className="space-y-3">
          {timelineOpen && (
            <Panel className="relative">
              <button type="button" className="absolute right-3 top-3 text-slate-400" onClick={() => setTimelineOpen(false)}>
                ×
              </button>
              <div className="text-sm font-semibold text-[#2f6bff]">This turn context</div>
              <div className="mt-3 space-y-2 text-[12px] text-slate-500">
                {(packet?.retrieved_facts || ["No passenger retrieved yet."]).map((f: string) => (
                  <div key={f} className="flex gap-2">
                    <span className="w-16 shrink-0 text-[10px] font-semibold uppercase text-slate-400">Fact</span>
                    {f}
                  </div>
                ))}
                {packet?.missing_slots?.length > 0 && (
                  <div className="rounded-lg bg-amber-50 px-2 py-1 text-amber-700">Missing: {packet.missing_slots.join(", ")}</div>
                )}
                {packet?.retrieved?.rules?.length > 0 && (
                  <div className="space-y-1 border-t border-slate-100 pt-2">
                    <div className="text-[10px] font-semibold uppercase text-slate-400">
                      Retrieved policy ({packet.retrieved.rules.length})
                    </div>
                    {packet.retrieved.rules.map((r: any, i: number) => (
                      <div key={`${r.clause_id}-${r.for_action}-${i}`} className="rounded-lg bg-slate-50 px-2 py-1">
                        <span className="font-semibold text-slate-600">{r.for_action || r.kind}</span>
                        <span className="ml-1 text-[10px] text-slate-400">{r.clause_id}</span>
                        <div className="text-slate-500">&ldquo;{r.text}&rdquo;</div>
                      </div>
                    ))}
                  </div>
                )}
                {packet?.retrieved?.recalled_turns?.length > 0 && (
                  <div className="space-y-1 border-t border-slate-100 pt-2">
                    <div className="text-[10px] font-semibold uppercase text-slate-400">Recalled turns</div>
                    {packet.retrieved.recalled_turns.map((t: any, i: number) => (
                      <div key={i} className="text-slate-500">&ldquo;{t.message}&rdquo;</div>
                    ))}
                  </div>
                )}
                {packet?.retrieved?.known_facts?.length > 0 && (
                  <div className="space-y-1 border-t border-slate-100 pt-2">
                    <div className="text-[10px] font-semibold uppercase text-slate-400">Remembered</div>
                    {packet.retrieved.known_facts.map((f: any, i: number) => (
                      <div key={i} className="text-slate-500">{f.fact}</div>
                    ))}
                  </div>
                )}
                <div className="pt-1 text-[11px] text-slate-400">KB {packet?.kb_backend || "—"} · LLM never decides policy</div>
              </div>
            </Panel>
          )}
          <Panel>
            <div className="text-[11px] font-bold uppercase tracking-wide text-slate-400">Authority</div>
            <p className="mt-2 text-[12px] leading-5 text-slate-500">
              ALLOW is simulated. DENY stays denied. ESCALATE opens a supervisor case on AERO OPS — a separate CRM, not this passenger app.
            </p>
          </Panel>
        </aside>
      </div>
    </AppFrame>
  );
}

function TabBtn({ active, onClick, label, count }: { active: boolean; onClick: () => void; label: string; count: number }) {
  return (
    <button type="button" onClick={onClick} className={`-mb-px border-b-2 pb-3 text-sm font-semibold ${active ? "border-slate-800 text-slate-900" : "border-transparent text-slate-400"}`}>
      {label} <span className={`ml-1 text-[11px] ${active ? "text-rose-500" : "text-slate-400"}`}>{count}</span>
    </button>
  );
}

function Meta({ icon, label }: { icon: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-slate-50 px-2 py-1">
      {icon} {label}
    </span>
  );
}
