import { cn } from "@/lib/utils";

export function BrandMark({ className }: { className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center justify-center rounded-full bg-brand text-white shadow-card",
        className,
      )}
      aria-hidden
    >
      <svg viewBox="0 0 24 24" fill="none" className="h-[54%] w-[54%]">
        <path
          d="M20.8 4.2 3.4 11.6c-.7.3-.6 1.3.2 1.5l5.2 1.2 1.3 5.3c.2.8 1.2.8 1.5.1L20.8 4.2Z"
          fill="currentColor"
        />
        <path d="M20.8 4.2 10.2 14.6" stroke="#001A80" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    </span>
  );
}

export function Wordmark({ compact = false }: { compact?: boolean }) {
  return (
    <span className="flex items-center gap-2.5">
      <BrandMark className={compact ? "h-9 w-9" : "h-11 w-11"} />
      <span className="leading-none">
        <span
          className={cn(
            "block font-bold tracking-tight text-brand",
            compact ? "text-lg" : "text-2xl",
          )}
        >
          AeroResolve
        </span>
        {!compact && (
          <span className="mt-1 block text-2xs font-medium text-ink-muted">Passenger support</span>
        )}
      </span>
    </span>
  );
}
