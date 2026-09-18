import { cn } from "@/lib/utils";

export function InlineCard({
  title,
  aside,
  children,
  footer,
  className,
}: {
  title?: string;
  aside?: React.ReactNode;
  children: React.ReactNode;
  footer?: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("w-full overflow-hidden rounded-card border border-line bg-white shadow-card", className)}>
      {(title || aside) && (
        <div className="flex items-center justify-between gap-2 px-4 pb-2 pt-3.5">
          {title && <h3 className="text-sm font-semibold leading-none text-ink">{title}</h3>}
          {aside}
        </div>
      )}
      <div className="px-4 pb-4 pt-0.5">{children}</div>
      {footer && <div className="border-t border-line px-4 py-3">{footer}</div>}
    </div>
  );
}
