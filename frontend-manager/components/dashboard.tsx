"use client";

import { useMemo } from "react";

import { Donut, HorizontalBars, StackedBars } from "@/components/charts";
import {
  type Analytics,
  type CaseSummary,
  type Frustration,
  formatDuration,
  formatRate,
  formatUsd,
  humanise,
  orderedCategories,
} from "@/lib/ops";

const STATUS_SERIES = [
  { key: "open", label: "Open", color: "#60a5fa" },
  { key: "escalated", label: "Escalated", color: "#fbbf24" },
  { key: "resolved", label: "Resolved", color: "#34d399" },
];

const FRUSTRATION_SERIES = [
  { key: "counted", label: "Counted", color: "#7c6cff" },
  { key: "low", label: "Low confidence", color: "#475569" },
];

export function OpsDashboard({
  analytics,
  cases,
  frustration,
}: {
  analytics: Analytics | null;
  cases: CaseSummary[];
  frustration: Frustration | null;
}) {
  const ops = analytics?.operations;
  const containment = analytics?.containment;
  const pipeline = useMemo(() => lastSevenDays(cases), [cases]);
  const mix = useMemo(() => frustrationMix(frustration), [frustration]);
  const reasons = Object.entries(containment?.escalations_by_reason || {}).map(([label, value]) => ({
    label: humanise(label),
    value,
  }));

  const kpis = [
    {
      label: "Open cases",
      value: ops ? String(ops.open_cases) : "—",
      hint: `${ops?.total_cases ?? 0} total`,
    },
    {
      label: "Resolution rate",
      value: formatRate(ops?.resolution_rate),
      hint: `${ops?.resolved_cases ?? 0} resolved · ${formatDuration(ops?.average_resolution_seconds)} avg`,
    },
    {
      label: "Containment",
      value: formatRate(containment?.containment_rate),
      hint: `${containment?.contained_turns ?? 0} of ${containment?.turns ?? 0} turns needed no human`,
    },
    {
      label: "Distress handovers",
      value: String(containment?.distress_escalations ?? 0),
      hint: `${containment?.authority_escalations ?? 0} authority · ${formatUsd(containment?.est_spend_usd)} spend`,
    },
  ];

  return (
    <div className="space-y-5">
      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {kpis.map((kpi) => (
          <div key={kpi.label} className="rounded-2xl border border-line bg-surface px-4 py-4 shadow-card">
            <div className="text-[11px] font-semibold uppercase tracking-wide text-ink-faint">{kpi.label}</div>
            <div className="mt-2 text-3xl font-semibold tracking-tight">{kpi.value}</div>
            <p className="mt-1 text-xs text-ink-muted">{kpi.hint}</p>
          </div>
        ))}
      </section>

      <section className="grid gap-4 xl:grid-cols-[minmax(0,1.4fr)_minmax(280px,0.9fr)]">
        <div className="rounded-2xl border border-line bg-surface p-5 shadow-card">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h2 className="text-sm font-semibold">Cases opened</h2>
              <p className="mt-1 text-xs text-ink-muted">Last 7 days, stacked by status. Same store the board reads.</p>
            </div>
            <Legend items={STATUS_SERIES} />
          </div>
          <div className="mt-4 h-[240px]">
            <StackedBars categories={pipeline.labels} series={STATUS_SERIES} values={pipeline.values} />
          </div>
        </div>

        <div className="grid gap-4">
          <div className="rounded-2xl border border-line bg-surface p-5 shadow-card">
            <h2 className="text-sm font-semibold">Containment</h2>
            <p className="mt-1 text-xs text-ink-muted">Share of measured turns that never needed a person.</p>
            <div className="mt-4">
              <Donut
                value={containment?.containment_rate || 0}
                label={formatRate(containment?.containment_rate)}
                caption={
                  containment?.p95_latency_ms
                    ? `p95 ${containment.p95_latency_ms}ms · grounding ${formatRate(containment.grounding_coverage ?? undefined)}`
                    : "Run a passenger turn to populate this."
                }
              />
            </div>
          </div>
          <div className="rounded-2xl border border-line bg-surface p-5 shadow-card">
            <h2 className="text-sm font-semibold">Why humans were needed</h2>
            <p className="mt-1 text-xs text-ink-muted">Escalation reasons on measured turns.</p>
            <div className="mt-4">
              <HorizontalBars items={reasons} color="#fbbf24" />
            </div>
          </div>
        </div>
      </section>

      <section className="rounded-2xl border border-line bg-surface p-5 shadow-card">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold">Frustration signal</h2>
            <p className="mt-1 text-xs text-ink-muted">
              Counted observations only. Low-confidence guesses stay in the grey stack and never move a staffing number.
            </p>
          </div>
          <Legend items={FRUSTRATION_SERIES} />
        </div>
        {mix.labels.length ? (
          <div className="mt-4 h-[200px]">
            <StackedBars categories={mix.labels} series={FRUSTRATION_SERIES} values={mix.values} />
          </div>
        ) : (
          <p className="mt-6 text-sm text-ink-muted">No frustration observations yet.</p>
        )}
        {frustration?.observations ? (
          <div className="mt-4 flex flex-wrap gap-x-5 gap-y-1 text-[11px] text-ink-faint">
            <span>{frustration.counted_observations ?? 0} counted</span>
            <span>{frustration.low_confidence_observations ?? 0} held back</span>
            <span>{frustration.escalation_recommended ?? 0} recommended a supervisor</span>
            <span>
              {frustration.graph?.counted_edges ?? 0} {frustration.graph?.edge || "EXHIBITS_FRUSTRATION"} edges
            </span>
          </div>
        ) : null}
      </section>
    </div>
  );
}

function Legend({ items }: { items: { label: string; color: string }[] }) {
  return (
    <div className="flex flex-wrap gap-3 text-[11px] text-ink-muted">
      {items.map((item) => (
        <span key={item.label} className="inline-flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-sm" style={{ background: item.color }} />
          {item.label}
        </span>
      ))}
    </div>
  );
}

function dayKey(date: Date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function lastSevenDays(cases: CaseSummary[]) {
  const days: { key: string; label: string }[] = [];
  const now = new Date();
  for (let i = 6; i >= 0; i -= 1) {
    const date = new Date(now);
    date.setHours(0, 0, 0, 0);
    date.setDate(date.getDate() - i);
    days.push({
      key: dayKey(date),
      label: date.toLocaleDateString(undefined, { month: "short", day: "numeric" }),
    });
  }
  const values: Record<string, Record<string, number>> = {};
  for (const day of days) values[day.label] = { open: 0, escalated: 0, resolved: 0 };
  for (const item of cases) {
    const stamp = item.created_at || item.updated_at;
    if (!stamp) continue;
    const parsed = new Date(stamp);
    if (Number.isNaN(parsed.getTime())) continue;
    const day = days.find((entry) => entry.key === dayKey(parsed));
    if (!day) continue;
    const status = item.status === "escalated" || item.status === "resolved" ? item.status : "open";
    values[day.label][status] += 1;
  }
  return { labels: days.map((day) => day.label), values };
}

function frustrationMix(data: Frustration | null) {
  if (!data?.observations) return { labels: [] as string[], values: {} as Record<string, Record<string, number>> };
  const counted = data.by_category || {};
  const unconfirmed = data.low_confidence_by_category || {};
  const labels = orderedCategories(counted, unconfirmed);
  const values: Record<string, Record<string, number>> = {};
  for (const label of labels) {
    values[label] = { counted: counted[label] || 0, low: unconfirmed[label] || 0 };
  }
  return { labels, values };
}
