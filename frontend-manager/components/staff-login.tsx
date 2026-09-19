"use client";

import { FormEvent, useState } from "react";

import { staffLogin } from "@/lib/auth";

export function StaffLogin({ onSignedIn }: { onSignedIn: (token: string) => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const token = await staffLogin(email, password);
      onSignedIn(token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Email or password is incorrect.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="relative grid min-h-dvh place-items-center overflow-hidden px-5">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(80%_60%_at_10%_-10%,rgba(124,108,255,0.28),transparent_55%),radial-gradient(70%_50%_at_110%_10%,rgba(244,114,182,0.18),transparent_50%)]" />
      <form
        onSubmit={submit}
        className="relative w-full max-w-sm rounded-3xl border border-line bg-surface/90 p-7 shadow-card backdrop-blur"
      >
        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-brand-accent">AeroResolve</p>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight">Operations</h1>
        <p className="mt-2 text-sm text-ink-muted">Staff sign-in to audit cases, containment, and the live knowledge graph.</p>

        <label className="mt-6 block text-xs font-semibold text-ink-soft">
          Email
          <input
            type="email"
            required
            autoComplete="username"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="ops@aeroresolve.local"
            className="mt-1.5 h-11 w-full rounded-xl border border-line bg-canvas px-3 text-sm text-ink outline-none placeholder:text-ink-faint focus:border-brand"
          />
        </label>
        <label className="mt-3 block text-xs font-semibold text-ink-soft">
          Password
          <input
            type="password"
            required
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="mt-1.5 h-11 w-full rounded-xl border border-line bg-canvas px-3 text-sm text-ink outline-none focus:border-brand"
          />
        </label>

        {error && <p className="mt-3 text-xs text-stop-fg">{error}</p>}

        <button
          type="submit"
          disabled={busy}
          className="mt-6 h-11 w-full rounded-xl bg-brand text-sm font-semibold text-white disabled:opacity-50"
        >
          {busy ? "Signing in…" : "Sign in"}
        </button>

        <button
          type="button"
          onClick={() => {
            setEmail("ops@aeroresolve.local");
            setPassword("AeroOps2026!");
            setError("");
          }}
          className="mt-4 w-full rounded-xl px-2 py-2 text-left transition-colors hover:bg-canvas"
        >
          <span className="block text-[10px] font-semibold uppercase tracking-[0.16em] text-ink-faint">
            Reviewer account
          </span>
          <span className="mt-1 block text-[12px] font-medium text-ink-soft">Operations</span>
          <span className="mt-0.5 block text-[11px] text-ink-muted">
            ops@aeroresolve.local · AeroOps2026!
          </span>
        </button>
      </form>
    </main>
  );
}
