"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { AppFrame, Panel, PrimaryButton, TopNav } from "@aero/ui";
import { createPlatform } from "@aero/ui";
import { api, setToken, resetChatSession } from "../../lib/auth";

const factory = createPlatform("customer");

type Member = { name: string; email: string; loyalty_tier: string; pnr: string };

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [members, setMembers] = useState<Member[]>([]);
  const [hint, setHint] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    fetch("/api/auth/members")
      .then((r) => r.json())
      .then((data) => {
        setMembers(data.members || []);
        setHint(data.seed_password_hint || "");
      })
      .catch(() => undefined);
  }, []);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const session = await api<{ token: string }>("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      setToken(session.token);
      resetChatSession();
      window.location.href = "/";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not sign in");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppFrame>
      <TopNav factory={factory} activeHref="/login" LinkComponent={Link} />
      <div className="grid gap-4 px-5 py-6 md:grid-cols-[1.1fr_0.9fr]">
        <Panel className="p-8">
          <div className="text-[11px] font-bold uppercase tracking-wide text-slate-400">Passenger sign in</div>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight text-slate-900">Welcome back to AERO</h1>
          <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
            Resolution is tied to your passenger account. Sign in to load your booking — we do not switch you into someone else&apos;s disruption.
          </p>
          <form className="mt-6 space-y-3" onSubmit={onSubmit}>
            <label className="block text-[11px] font-semibold uppercase tracking-wide text-slate-400">
              Email
              <input
                className="mt-1 w-full rounded-full border border-slate-200 px-4 py-2.5 text-sm text-slate-800 outline-none focus:border-[#2f6bff]"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </label>
            <label className="block text-[11px] font-semibold uppercase tracking-wide text-slate-400">
              Password
              <input
                className="mt-1 w-full rounded-full border border-slate-200 px-4 py-2.5 text-sm text-slate-800 outline-none focus:border-[#2f6bff]"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </label>
            {error && <p className="text-sm text-rose-600">{error}</p>}
            <PrimaryButton type="submit" disabled={busy}>
              {busy ? "Signing in…" : "Sign in"}
            </PrimaryButton>
          </form>
          <p className="mt-4 text-sm text-slate-500">
            New to AERO?{" "}
            <Link href="/signup" className="font-semibold text-[#2f6bff]">
              Open an account
            </Link>
          </p>
        </Panel>
        <Panel>
          <div className="text-[11px] font-bold uppercase tracking-wide text-slate-400">Members already on file</div>
          <p className="mt-2 text-[12px] leading-5 text-slate-500">
            Assignment passenger profiles are enrolled accounts, not demo shortcuts. Select a member to fill the email field, then sign in.
          </p>
          <div className="mt-4 space-y-2">
            {members.map((m) => (
              <button
                type="button"
                key={m.email}
                onClick={() => {
                  setEmail(m.email);
                  if (hint) setPassword(hint);
                }}
                className="w-full rounded-xl border border-slate-100 px-3 py-2 text-left hover:border-[#2f6bff]"
              >
                <div className="text-sm font-semibold text-slate-800">{m.name}</div>
                <div className="text-[11px] text-slate-500">
                  {m.loyalty_tier} · {m.email}
                </div>
              </button>
            ))}
          </div>
          {hint && <p className="mt-3 text-[11px] text-slate-400">Enrolled-member password for this prototype: {hint}</p>}
        </Panel>
      </div>
    </AppFrame>
  );
}
