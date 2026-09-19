"use client";

import {
  type PendingKbEntry,
  formatRate,
  frustrationTone,
  humanise,
} from "@/lib/ops";

export function KbReviewQueue({
  entries,
  onApprove,
  onReject,
}: {
  entries: PendingKbEntry[] | null;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
}) {
  if (!entries?.length) {
    return (
      <section className="grid min-h-[280px] place-items-center rounded-2xl border border-line bg-surface text-sm text-ink-faint">
        No pending knowledge-base entries. Low-confidence writes land here for review.
      </section>
    );
  }

  return (
    <section className="space-y-3">
      {entries.map((entry) => (
        <article key={entry.id} className="rounded-2xl border border-line bg-surface p-4 shadow-card">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <TagPill tag={entry.tag} />
                <span className="text-[11px] text-ink-faint">
                  Score {formatRate(entry.frustration_score)}
                </span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink-soft">{entry.message_excerpt}</p>
              <p className="mt-1 text-xs text-ink-muted">
                Proposed direction:{" "}
                <span className="text-ink-soft">{entry.proposed_direction || "—"}</span>
              </p>
            </div>
            <div className="flex shrink-0 items-center gap-2">
              <button
                type="button"
                onClick={() => onApprove(entry.id)}
                className="rounded-xl bg-good-bg px-3 py-1.5 text-xs font-semibold text-good-fg hover:bg-good-bg/80"
              >
                Approve
              </button>
              <button
                type="button"
                onClick={() => onReject(entry.id)}
                className="rounded-xl bg-stop-bg px-3 py-1.5 text-xs font-semibold text-stop-fg hover:bg-stop-bg/80"
              >
                Reject
              </button>
            </div>
          </div>
        </article>
      ))}
    </section>
  );
}

function TagPill({ tag }: { tag: string }) {
  const tone = frustrationTone(tag);
  const classes = {
    good: "bg-good-bg text-good-fg",
    warn: "bg-warn-bg text-warn-fg",
    stop: "bg-stop-bg text-stop-fg",
    neutral: "bg-white/5 text-ink-muted",
  }[tone];
  return <span className={`rounded-full px-2 py-0.5 text-[11px] font-semibold capitalize ${classes}`}>{humanise(tag)}</span>;
}
