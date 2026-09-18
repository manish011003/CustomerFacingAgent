"use client";

import { useState } from "react";
import { X } from "lucide-react";

import { Button } from "@/components/ui/button";

export function FeedbackPopup({
  open,
  sending,
  onRate,
  onDismiss,
}: {
  open: boolean;
  sending?: boolean;
  onRate: (rating: number) => void;
  onDismiss: () => void;
}) {
  const [picked, setPicked] = useState<number | null>(null);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-ink/40 p-4 sm:items-center">
      <div
        role="dialog"
        aria-labelledby="csat-title"
        className="w-full max-w-sm rounded-3xl border border-line bg-white p-5 shadow-card"
      >
        <div className="flex items-start justify-between gap-3">
          <div>
            <p id="csat-title" className="text-sm font-semibold text-ink">
              How was this service?
            </p>
            <p className="mt-1 text-xs leading-5 text-ink-muted">
              This case is resolved. A rating helps Operations — it does not change what was already arranged.
            </p>
          </div>
          <button
            type="button"
            aria-label="Dismiss feedback"
            className="rounded-full p-1 text-ink-faint hover:bg-canvas hover:text-ink"
            onClick={onDismiss}
          >
            <X className="h-4 w-4" strokeWidth={2.2} />
          </button>
        </div>
        <div className="mt-4 flex justify-between gap-1.5">
          {[1, 2, 3, 4, 5].map((rating) => (
            <Button
              key={rating}
              variant={picked === rating ? "chip" : "secondary"}
              size="sm"
              disabled={sending}
              className="min-w-0 flex-1 px-0"
              onClick={() => {
                setPicked(rating);
                onRate(rating);
              }}
            >
              {rating}
            </Button>
          ))}
        </div>
        <p className="mt-3 text-2xs text-ink-faint">1 is poor · 5 is excellent</p>
      </div>
    </div>
  );
}
