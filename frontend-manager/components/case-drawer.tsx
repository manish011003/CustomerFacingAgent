"use client";

import type { ReactNode } from "react";

import { type CaseDetail, humanise, statusTone } from "@/lib/ops";

export function CaseDrawer({
  caseData,
  onClose,
}: {
  caseData: CaseDetail | null;
  onClose: () => void;
}) {
  if (!caseData) return null;

  const booking = caseData.booking;
  const actions = caseData.action_taken || [];
  const rules = caseData.policy_rules || [];
  const decisions = caseData.policy_decisions || [];
  const transcript = caseData.transcript || [];
  const timeline = caseData.timeline || [];

  return (
    <div className="fixed inset-0 z-40 flex justify-end">
      <button type="button" className="absolute inset-0 bg-black/50" onClick={onClose} aria-label="Close case" />
      <aside className="relative flex h-full w-full max-w-lg flex-col border-l border-line bg-surface shadow-card">
        <div className="flex items-start justify-between gap-3 border-b border-line px-5 py-4">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink-faint">Case</p>
            <h2 className="mt-1 text-xl font-semibold tracking-tight">{caseData.customer}</h2>
            <p className="mt-1 text-sm text-ink-muted">
              {caseData.pnr} · {caseData.flight || "No flight"} · {caseData.loyalty_tier || "—"}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <StatusPill status={caseData.status} />
            <button type="button" onClick={onClose} className="text-sm text-ink-muted hover:text-ink">
              Close
            </button>
          </div>
        </div>

        <div className="scroll-slim flex-1 space-y-5 overflow-y-auto px-5 py-5">
          <Section title="Customer and booking">
            {booking ? (
              <p className="text-sm leading-6 text-ink-soft">
                {booking.flight || "Flight"} · {booking.origin} → {booking.destination}
                <br />
                {booking.date_label} · {booking.scheduled_departure}
                {booking.new_departure ? ` · now ${booking.new_departure}` : ""}
                {booking.delay_hours != null ? ` · delayed ${booking.delay_hours}h` : ""}
                <br />
                {booking.status_reason || booking.status}
              </p>
            ) : (
              <p className="text-sm text-ink-muted">No disrupted booking on this case.</p>
            )}
          </Section>

          <Section title="Conversation">
            <div className="max-h-56 space-y-2 overflow-y-auto rounded-xl bg-canvas p-3">
              {transcript.map((message, index) => (
                <p key={`${message.role}-${index}`} className="text-xs leading-5 text-ink-soft">
                  <span className="font-semibold capitalize text-ink">
                    {message.role === "assistant" ? "Agent" : "Customer"}
                  </span>
                  {": "}
                  {message.content}
                </p>
              ))}
              {!transcript.length && <p className="text-xs text-ink-muted">No transcript yet.</p>}
            </div>
          </Section>

          <Section title="Policy used">
            <div className="space-y-2">
              {decisions.map((decision, index) => (
                <div key={`${decision.action}-${index}`} className="rounded-xl border border-line px-3 py-2">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-sm font-medium">{humanise(decision.action)}</span>
                    <StatusPill status={decision.status.toLowerCase()} />
                  </div>
                  <p className="mt-1 text-xs leading-5 text-ink-muted">{decision.reason}</p>
                  <p className="mt-1 text-[11px] text-ink-faint">{decision.source}</p>
                </div>
              ))}
              {!decisions.length && <p className="text-sm text-ink-muted">No policy decision on this case yet.</p>}
            </div>
            {rules.length > 0 && (
              <div className="mt-3 space-y-2">
                {rules.map((rule) => (
                  <p key={rule.clause_id} className="text-xs leading-5 text-ink-muted">
                    <span className="font-semibold text-ink-soft">{rule.clause_id}</span> — {rule.text}
                  </p>
                ))}
              </div>
            )}
          </Section>

          <Section title="Actions performed">
            {actions.length ? (
              <ul className="list-disc space-y-1 pl-5 text-sm text-ink-soft">
                {actions.map((action) => (
                  <li key={action}>{humanise(action)} (simulated)</li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-ink-muted">No action was taken.</p>
            )}
          </Section>

          {caseData.feedback && (
            <Section title="Passenger feedback">
              <p className="text-sm leading-6 text-ink-soft">
                {caseData.feedback.rating != null ? `${caseData.feedback.rating}/5` : "No rating"}
                {caseData.feedback.sentiment ? ` · ${humanise(caseData.feedback.sentiment)}` : ""}
              </p>
              {caseData.feedback.comment && (
                <p className="mt-1 text-xs leading-5 text-ink-muted">{caseData.feedback.comment}</p>
              )}
            </Section>
          )}

          {(caseData.escalation_status || caseData.escalation_reasons?.length) && (
            <Section title="Escalation">
              <p className="text-sm leading-6 text-ink-soft">{(caseData.escalation_reasons || []).join(" ")}</p>
              {!!caseData.escalation_reason_codes?.length && (
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {caseData.escalation_reason_codes.map((code) => (
                    <span key={code} className="rounded-full bg-canvas px-2 py-0.5 text-[11px] font-semibold text-ink-muted">
                      {humanise(code)}
                    </span>
                  ))}
                </div>
              )}
              {caseData.recommended_human_question && (
                <p className="mt-2 text-xs text-ink-muted">{caseData.recommended_human_question}</p>
              )}
            </Section>
          )}

          <Section title="Audit timeline">
            <ol className="space-y-2">
              {timeline.map((event, index) => (
                <li key={event.id || `${event.kind}-${index}`} className="flex gap-3 text-xs text-ink-soft">
                  <span className="w-24 shrink-0 font-semibold uppercase tracking-wide text-ink-faint">{event.kind}</span>
                  <span>
                    {event.tool
                      ? event.tool
                      : event.action
                        ? humanise(event.action)
                        : event.message || event.reason || event.reply || "Recorded"}
                    {event.status ? ` · ${event.status}` : ""}
                  </span>
                </li>
              ))}
              {!timeline.length && <p className="text-sm text-ink-muted">No events recorded.</p>}
            </ol>
          </Section>
        </div>
      </aside>
    </div>
  );
}

function StatusPill({ status }: { status: string }) {
  const tone = statusTone(status);
  const classes = {
    good: "bg-good-bg text-good-fg",
    warn: "bg-warn-bg text-warn-fg",
    stop: "bg-stop-bg text-stop-fg",
    neutral: "bg-white/5 text-ink-muted",
  }[tone];
  return <span className={`rounded-full px-2 py-0.5 text-[11px] font-semibold capitalize ${classes}`}>{status}</span>;
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section>
      <h3 className="text-[11px] font-semibold uppercase tracking-wide text-ink-faint">{title}</h3>
      <div className="mt-2">{children}</div>
    </section>
  );
}
