import { Suspense } from "react";

import { ExitBoard } from "@/components/departures/exit-board";

export default function NotFound() {
  return (
    <Suspense fallback={<div className="grid min-h-dvh place-items-center bg-canvas text-sm text-ink-muted">Loading…</div>}>
      <ExitBoard />
    </Suspense>
  );
}
