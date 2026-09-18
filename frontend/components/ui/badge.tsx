import * as React from "react";

import { cn } from "@/lib/utils";

export type Tone = "good" | "warn" | "stop" | "info" | "neutral";

const TONES: Record<Tone, string> = {
  good: "bg-good-bg text-good-fg border-good-line",
  warn: "bg-warn-bg text-warn-fg border-warn-line",
  stop: "bg-stop-bg text-stop-fg border-stop-line",
  info: "bg-brand-ice text-brand-deep border-brand-line",
  neutral: "bg-canvas text-ink-muted border-line",
};

export function Badge({
  tone = "neutral",
  className,
  children,
}: {
  tone?: Tone;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-2xs font-semibold",
        TONES[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}
