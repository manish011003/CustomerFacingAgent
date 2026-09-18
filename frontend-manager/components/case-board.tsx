"use client";

import {
  type CaseSummary,
  avatarColor,
  formatDay,
  humanise,
  initials,
  statusTone,
} from "@/lib/ops";

const COLUMNS = [
  { id: "open", title: "Open", hint: "Still with the agent" },
  { id: "escalated", title: "Escalated", hint: "Needs a person" },
  { id: "resolved", title: "Resolved", hint: "Closed in the thread" },
] as const;

export function CaseBoard({
  cases,
  selectedId,
  onSelect,
}: {
  cases: CaseSummary[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}) {
  return (
    <section className="grid gap-4 md:grid-cols-3">
      {COLUMNS.map((column) => {
        const items = cases.filter((item) => item.status === column.id);
        return (
          <div key={column.id} className="min-h-[280px] rounded-2xl border border-line bg-surface/80 p-3">
            <div className="mb-3 flex items-baseline justify-between px-1">
              <div>
                <h3 className="text-sm font-semibold">{column.title}</h3>
                <p className="text-[11px] text-ink-faint">{column.hint}</p>
              </div>
              <span className="rounded-full bg-white/5 px-2 py-0.5 text-[11px] text-ink-muted">{items.length}</span>
            </div>
            <div className="space-y-2">
              {items.map((item) => (
                <CaseCard
                  key={item.id}
                  item={item}
                  selected={selectedId === item.id}
                  onSelect={() => onSelect(item.id)}
                />
              ))}
              {!items.length && (
                <p className="rounded-xl border border-dashed border-line px-3 py-8 text-center text-xs text-ink-faint">
                  Nothing in this column yet.
                </p>
              )}
            </div>
          </div>
        );
      })}
    </section>
  );
}

function CaseCard({
  item,
  selected,
  onSelect,
}: {
  item: CaseSummary;
  selected: boolean;
  onSelect: () => void;
}) {
  const distressed = (item.escalation_reason_codes || []).includes("severe_customer_distress");
  const tone = statusTone(item.status);
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`w-full rounded-2xl border p-3 text-left transition ${
        distressed
          ? "border-transparent bg-gradient-to-br from-[#7c6cff] to-[#f472b6] text-white"
          : selected
            ? "border-brand bg-brand-tint"
            : "border-line bg-lift hover:border-line-strong"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <span
          className={`rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${
            distressed
              ? "bg-white/20 text-white"
              : {
                  good: "bg-good-bg text-good-fg",
                  warn: "bg-warn-bg text-warn-fg",
                  stop: "bg-stop-bg text-stop-fg",
                  neutral: "bg-white/5 text-ink-muted",
                }[tone]
          }`}
        >
          {distressed ? "Priority" : item.loyalty_tier || item.status}
        </span>
      </div>
      <div className="mt-3 text-sm font-semibold">{item.customer || "Unknown"}</div>
      <p className={`mt-1 line-clamp-2 text-xs leading-5 ${distressed ? "text-white/80" : "text-ink-muted"}`}>
        {item.issue || "Support request"}
      </p>
      <div className="mt-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span
            className="grid h-6 w-6 place-items-center rounded-full text-[10px] font-semibold text-white"
            style={{ background: distressed ? "rgba(255,255,255,0.25)" : avatarColor(item.customer) }}
          >
            {initials(item.customer)}
          </span>
          <span className={`text-[11px] ${distressed ? "text-white/80" : "text-ink-faint"}`}>
            {item.pnr || "—"} · {formatDay(item.updated_at || item.created_at)}
          </span>
        </div>
        <span className={`text-[11px] ${distressed ? "text-white/80" : "text-ink-faint"}`}>
          {item.action_taken?.length ? `${item.action_taken.length} act` : humanise(item.flight)}
        </span>
      </div>
    </button>
  );
}
