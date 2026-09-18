import * as React from "react";

import { cn } from "@/lib/utils";

type Variant = "primary" | "secondary" | "quiet" | "chip";
type Size = "sm" | "md" | "lg";

const VARIANTS: Record<Variant, string> = {
  primary: "bg-brand text-white shadow-card hover:bg-brand-hover active:bg-brand-deep",
  secondary: "border border-line bg-white text-ink-soft hover:border-brand-line hover:text-brand",
  quiet: "text-ink-muted hover:bg-brand-ice hover:text-brand",
  chip: "border border-brand-line bg-brand-ice text-brand hover:bg-white",
};

const SIZES: Record<Size, string> = {
  sm: "h-9 gap-1.5 rounded-full px-3.5 text-xs",
  md: "h-11 gap-2 rounded-full px-5 text-sm",
  lg: "h-12 gap-2 rounded-full px-6 text-base",
};

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", type = "button", ...props }, ref) => (
    <button
      ref={ref}
      type={type}
      className={cn(
        "inline-flex select-none items-center justify-center whitespace-nowrap font-semibold transition-colors duration-200 ease-swift focus-ring",
        "disabled:pointer-events-none disabled:opacity-50",
        VARIANTS[variant],
        SIZES[size],
        className,
      )}
      {...props}
    />
  ),
);
Button.displayName = "Button";
