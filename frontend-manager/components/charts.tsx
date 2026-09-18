"use client";

type Series = { key: string; label: string; color: string };

export function StackedBars({
  categories,
  series,
  values,
}: {
  categories: string[];
  series: Series[];
  values: Record<string, Record<string, number>>;
}) {
  const totals = categories.map((category) => series.reduce((sum, item) => sum + (values[category]?.[item.key] || 0), 0));
  const max = Math.max(1, ...totals);
  const ticks = [0, 0.5, 1].map((part) => Math.round(max * part));

  return (
    <div className="flex h-full min-h-[220px] flex-col">
      <div className="relative flex-1">
        <div className="absolute inset-x-0 top-0 flex h-full flex-col justify-between pb-6">
          {ticks
            .slice()
            .reverse()
            .map((tick) => (
              <div key={tick} className="flex items-center gap-2">
                <span className="w-6 text-right text-[10px] text-ink-faint">{tick}</span>
                <div className="h-px flex-1 bg-line" />
              </div>
            ))}
        </div>
        <div className="absolute inset-x-8 bottom-6 top-1 flex items-end justify-around gap-3">
          {categories.map((category, index) => {
            const total = totals[index];
            const height = `${Math.max(total ? 8 : 0, (total / max) * 100)}%`;
            return (
              <div key={category} className="flex h-full w-full max-w-[52px] flex-col items-center justify-end">
                <div className="flex w-8 flex-col-reverse overflow-hidden rounded-md" style={{ height }}>
                  {series.map((item) => {
                    const count = values[category]?.[item.key] || 0;
                    if (!count) return null;
                    return (
                      <div
                        key={item.key}
                        title={`${item.label}: ${count}`}
                        style={{ height: `${(count / total) * 100}%`, background: item.color }}
                      />
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>
      <div className="mt-1 flex justify-around pl-8">
        {categories.map((category) => (
          <div key={category} className="w-full max-w-[52px] text-center text-[10px] text-ink-muted">
            {category}
          </div>
        ))}
      </div>
    </div>
  );
}

export function Donut({
  value,
  label,
  caption,
}: {
  value: number;
  label: string;
  caption?: string;
}) {
  const clamped = Math.max(0, Math.min(1, value || 0));
  const r = 36;
  const c = 2 * Math.PI * r;
  const dash = c * clamped;
  return (
    <div className="flex items-center gap-4">
      <svg width="96" height="96" viewBox="0 0 96 96" className="-rotate-90">
        <circle cx="48" cy="48" r={r} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="10" />
        <circle
          cx="48"
          cy="48"
          r={r}
          fill="none"
          stroke="#7c6cff"
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={`${dash} ${c - dash}`}
        />
      </svg>
      <div>
        <div className="text-3xl font-semibold tracking-tight">{label}</div>
        {caption ? <p className="mt-1 text-xs text-ink-muted">{caption}</p> : null}
      </div>
    </div>
  );
}

export function HorizontalBars({
  items,
  color = "#7c6cff",
}: {
  items: { label: string; value: number }[];
  color?: string;
}) {
  const max = Math.max(1, ...items.map((item) => item.value));
  if (!items.length) {
    return <p className="text-sm text-ink-muted">No breakdown yet.</p>;
  }
  return (
    <div className="space-y-2.5">
      {items.map((item) => (
        <div key={item.label}>
          <div className="mb-1 flex items-center justify-between text-[11px]">
            <span className="truncate text-ink-soft">{item.label}</span>
            <span className="tabular-nums text-ink-muted">{item.value}</span>
          </div>
          <div className="h-1.5 overflow-hidden rounded-full bg-white/5">
            <div className="h-full rounded-full" style={{ width: `${(item.value / max) * 100}%`, background: color }} />
          </div>
        </div>
      ))}
    </div>
  );
}
