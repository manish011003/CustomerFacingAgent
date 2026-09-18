"use client";

import { AnimatePresence, motion } from "framer-motion";
import { AlertCircle, ArrowRight, Loader2 } from "lucide-react";
import { useState } from "react";

import { Wordmark } from "@/components/brand";
import { Button } from "@/components/ui/button";
import { Field, Input } from "@/components/ui/field";
import { api, resolveOpsUrl } from "@/lib/api";
import { useConversation } from "@/lib/store";
import { cn } from "@/lib/utils";

type Mode = "signin" | "join" | "staff";

export function SignIn() {
  const [mode, setMode] = useState<Mode>("signin");
  const { signIn, join, loading, authError, clearAuthError } = useConversation();
  const [staffError, setStaffError] = useState<string | null>(null);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [pnr, setPnr] = useState("");
  const [staffBusy, setStaffBusy] = useState(false);

  const busy = mode === "staff" ? staffBusy : loading;

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      if (mode === "staff") {
        setStaffBusy(true);
        setStaffError(null);
        const session = await api.staffLogin(email, password);
        window.location.assign(`${resolveOpsUrl()}/#st=${encodeURIComponent(session.token)}`);
        return;
      }
      if (mode === "signin") await signIn(email, password);
      else await join({ name, email, phone, password, pnr: pnr || undefined });
    } catch (error) {
      if (mode === "staff") {
        setStaffError(error instanceof Error ? error.message : "Email or password is incorrect.");
      }
    } finally {
      if (mode === "staff") setStaffBusy(false);
    }
  };

  return (
    <main className="flex min-h-dvh items-center justify-center px-4 py-8">
      <div className="w-full max-w-phone">
        <div className="mb-7 flex justify-center">
          <Wordmark />
        </div>

        <section className="hero-sky relative overflow-hidden rounded-sheet px-6 py-7 text-white shadow-lift">
          <PlaneWatermark />
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-white/70">Support</p>
          <h1 className="mt-2 max-w-[14ch] text-3xl font-bold leading-tight tracking-tight">
            We&apos;re here anytime.
          </h1>
          <p className="mt-3 max-w-[32ch] text-sm leading-6 text-white/80">
            Tell us what happened with your flight. We check your booking and the policy, then resolve
            what we can in this chat.
          </p>
        </section>

        <section className="mt-5 rounded-sheet bg-white p-5 shadow-card">
          {mode !== "staff" && (
            <div className="flex rounded-full bg-ice p-1">
              {(["signin", "join"] as const).map((value) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => {
                    setMode(value);
                    clearAuthError();
                    setStaffError(null);
                  }}
                  className={cn(
                    "h-9 flex-1 rounded-full text-xs font-semibold transition-colors duration-200 ease-swift focus-ring",
                    mode === value ? "bg-white text-brand shadow-sm" : "text-ink-muted hover:text-ink",
                  )}
                >
                  {value === "signin" ? "Sign in" : "Join"}
                </button>
              ))}
            </div>
          )}

          {mode === "staff" && (
            <p className="text-xs font-semibold text-ink-muted">Operations</p>
          )}

          <form onSubmit={submit} className={cn("space-y-3.5", mode === "staff" ? "mt-4" : "mt-5")}>
            {mode === "join" && (
              <>
                <Field label="Full name">
                  <Input value={name} onChange={(e) => setName(e.target.value)} required autoComplete="name" />
                </Field>
                <Field label="Phone">
                  <Input value={phone} onChange={(e) => setPhone(e.target.value)} required autoComplete="tel" />
                </Field>
              </>
            )}

            <Field label="Email">
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </Field>

            <Field label="Password">
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete={mode === "join" ? "new-password" : "current-password"}
              />
            </Field>

            {mode === "join" && (
              <Field label="Booking reference" hint="Optional — add it now or tell the agent later.">
                <Input value={pnr} onChange={(e) => setPnr(e.target.value.toUpperCase())} placeholder="Booking reference" />
              </Field>
            )}

            <AnimatePresence>
              {(mode === "staff" ? staffError : authError) && (
                <motion.p
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="flex items-start gap-2 rounded-field bg-stop-bg px-3 py-2 text-xs text-stop-fg"
                >
                  <AlertCircle className="mt-px h-3.5 w-3.5 shrink-0" strokeWidth={2} />
                  {mode === "staff" ? staffError : authError}
                </motion.p>
              )}
            </AnimatePresence>

            <Button type="submit" size="lg" className="w-full" disabled={busy}>
              {busy ? (
                <Loader2 className="h-4 w-4 animate-spin" strokeWidth={2} />
              ) : (
                <>
                  {mode === "join" ? "Create account" : mode === "staff" ? "Continue" : "Continue"}
                  <ArrowRight className="h-4 w-4" strokeWidth={2} />
                </>
              )}
            </Button>
          </form>
        </section>

        <div className="mt-4 flex justify-center">
          <button
            type="button"
            onClick={() => {
              setMode(mode === "staff" ? "signin" : "staff");
              clearAuthError();
              setStaffError(null);
            }}
            className="text-[11px] font-medium text-mist transition-colors hover:text-ink-muted"
          >
            {mode === "staff" ? "Passenger sign-in" : "Staff"}
          </button>
        </div>
      </div>
    </main>
  );
}

function PlaneWatermark() {
  return (
    <svg
      viewBox="0 0 180 90"
      className="pointer-events-none absolute -right-6 top-2 h-28 w-44 text-white/20"
      fill="none"
      aria-hidden
    >
      <path
        d="M12 62c28-18 58-30 92-34 18-2 36 2 48 14"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path d="M118 18 168 42 132 58 118 18Z" fill="currentColor" />
      <circle cx="28" cy="66" r="3" fill="currentColor" />
    </svg>
  );
}
