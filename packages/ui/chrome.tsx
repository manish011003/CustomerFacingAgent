"use client";

import type { ReactNode } from "react";
import type { PlatformChrome } from "./products/platform";

export function AppFrame({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-[#d5dee8] px-3 py-4 md:px-8 md:py-8">
      <div className="mx-auto max-w-[1280px] overflow-x-auto rounded-[28px] bg-[#f3f6fa] shadow-[0_30px_80px_rgba(15,35,70,0.18)] ring-1 ring-white/70">
        {children}
      </div>
    </div>
  );
}

export function TopNav({
  factory,
  activeHref,
  LinkComponent,
  account,
  onSignOut,
}: {
  factory: PlatformChrome;
  activeHref: string;
  LinkComponent: (props: { href: string; className?: string; children: ReactNode }) => ReactNode;
  account?: { name: string; initials: string } | null;
  onSignOut?: () => void;
}) {
  return (
    <header className="flex items-center justify-between border-b border-[#e6edf5] bg-white/80 px-6 py-3.5">
      <div className="flex items-center gap-8">
        <div className="flex items-center gap-2">
          <span className={`grid h-7 w-7 place-items-center rounded-full border border-current text-[11px] font-bold ${factory.brand.accentClass}`}>
            {factory.brand.mark}
          </span>
          <span className={`text-[15px] font-extrabold tracking-[0.18em] ${factory.brand.accentClass}`}>{factory.brand.name}</span>
        </div>
        <nav className="hidden items-center gap-6 text-[13px] font-semibold tracking-wide text-slate-400 md:flex">
          {factory.navItems.map((item) => {
            const active = activeHref === item.href || (item.href !== "/" && activeHref.startsWith(item.href));
            return (
              <LinkComponent
                key={item.href}
                href={item.href}
                className={active ? "text-[#3b82f6] relative after:absolute after:-bottom-3.5 after:left-0 after:h-[3px] after:w-full after:rounded-full after:bg-[#3b82f6]" : "hover:text-slate-600"}
              >
                {item.label.toUpperCase()}
              </LinkComponent>
            );
          })}
        </nav>
      </div>
      <div className="flex items-center gap-3 text-right">
        <div className="hidden text-xs text-slate-400 sm:block">
          <div className="font-semibold text-slate-700">{account?.name || factory.brand.product}</div>
          <div>{account ? "Signed in" : factory.brand.tagline}</div>
        </div>
        {onSignOut ? (
          <button type="button" onClick={onSignOut} className="text-[11px] font-semibold uppercase tracking-wide text-slate-400 hover:text-slate-700">
            Sign out
          </button>
        ) : null}
        <div className="grid h-9 w-9 place-items-center rounded-full bg-slate-800 text-[11px] font-bold text-white">
          {account?.initials || (factory.id === "customer" ? "PX" : "OP")}
        </div>
      </div>
    </header>
  );
}

export function Stepper({ steps, current }: { steps: string[]; current: number }) {
  return (
    <div className="flex items-center gap-3 px-6 py-4">
      <span className="grid h-8 w-8 place-items-center rounded-full border border-slate-200 bg-white text-slate-400">←</span>
      <div className="flex min-w-0 flex-1 overflow-hidden rounded-full bg-white shadow-sm ring-1 ring-slate-100">
        {steps.map((step, i) => {
          const done = i < current;
          const active = i === current;
          return (
            <div
              key={step}
              className={`relative flex flex-1 items-center justify-center px-3 py-2 text-[12px] font-semibold ${
                active ? "bg-[#22c55e] text-white" : done ? "bg-white text-slate-500" : "bg-white text-slate-400"
              }`}
            >
              {i > 0 && (
                <span
                  className={`absolute left-0 top-0 h-full w-3 -translate-x-1/2 ${active ? "bg-[#22c55e]" : "bg-white"}`}
                  style={{ clipPath: "polygon(0 0, 100% 50%, 0 100%)" }}
                />
              )}
              {step}
            </div>
          );
        })}
      </div>
      <span className="grid h-8 w-8 place-items-center rounded-full border border-slate-200 bg-white text-slate-400">⋯</span>
    </div>
  );
}

export function Panel({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-100 ${className}`}>{children}</section>;
}

export function PrimaryButton({
  children,
  onClick,
  disabled,
  type = "button",
}: {
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  type?: "button" | "submit";
}) {
  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className="rounded-full bg-[#2f6bff] px-4 py-1.5 text-[11px] font-bold uppercase tracking-wide text-white shadow-sm hover:bg-[#2458d6] disabled:opacity-50"
    >
      {children}
    </button>
  );
}
