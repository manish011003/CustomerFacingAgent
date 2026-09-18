"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { AppFrame, Panel, PrimaryButton, TopNav } from "@aero/ui";
import { createPlatform } from "@aero/ui";
import { api, resetChatSession, setToken } from "../../lib/auth";

const factory = createPlatform("customer");

export default function SignupPage() {
  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    password: "",
    pnr: "",
    flight: "",
    origin: "",
    destination: "",
    date: "2026-09-23",
    scheduled_departure: "10:00",
    status: "ON_TIME",
    delay_hours: "",
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function set<K extends keyof typeof form>(key: K, value: string) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const payload: Record<string, unknown> = {
        name: form.name,
        email: form.email,
        phone: form.phone,
        password: form.password,
        pnr: form.pnr || null,
        airline_caused: true,
      };
      if (form.origin && form.destination && form.pnr) {
        payload.flight = form.flight || null;
        payload.origin = form.origin;
        payload.destination = form.destination;
        payload.date = form.date;
        payload.scheduled_departure = form.scheduled_departure;
        payload.status = form.status;
        payload.delay_hours = form.delay_hours ? Number(form.delay_hours) : null;
      }
      const session = await api<{ token: string }>("/api/auth/signup", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setToken(session.token);
      resetChatSession();
      window.location.href = "/";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not open account");
    } finally {
      setBusy(false);
    }
  }

  const field = "mt-1 w-full rounded-full border border-slate-200 px-4 py-2.5 text-sm outline-none focus:border-[#2f6bff]";

  return (
    <AppFrame>
      <TopNav factory={factory} activeHref="/signup" LinkComponent={Link} />
      <div className="px-5 py-6">
        <Panel className="mx-auto max-w-3xl p-8">
          <div className="text-[11px] font-bold uppercase tracking-wide text-slate-400">Join AERO</div>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight">Create a passenger account</h1>
          <p className="mt-2 text-sm text-slate-500">
            New members start as Standard. Loyalty benefits from the data pack apply only when that tier is on the passenger record. We never invent a flight number for you.
          </p>
          <form className="mt-6 grid gap-3 md:grid-cols-2" onSubmit={onSubmit}>
            <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
              Full name
              <input className={field} value={form.name} onChange={(e) => set("name", e.target.value)} required />
            </label>
            <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
              Email
              <input className={field} type="email" value={form.email} onChange={(e) => set("email", e.target.value)} required />
            </label>
            <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
              Phone
              <input className={field} value={form.phone} onChange={(e) => set("phone", e.target.value)} required />
            </label>
            <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
              Password
              <input className={field} type="password" value={form.password} onChange={(e) => set("password", e.target.value)} required />
            </label>
            <div className="md:col-span-2 pt-2 text-[11px] font-bold uppercase tracking-wide text-slate-400">Optional first trip</div>
            <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
              PNR
              <input className={field} value={form.pnr} onChange={(e) => set("pnr", e.target.value)} />
            </label>
            <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
              Flight
              <input className={field} value={form.flight} onChange={(e) => set("flight", e.target.value)} placeholder="Only if you have it" />
            </label>
            <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
              Origin
              <input className={field} value={form.origin} onChange={(e) => set("origin", e.target.value)} />
            </label>
            <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
              Destination
              <input className={field} value={form.destination} onChange={(e) => set("destination", e.target.value)} />
            </label>
            <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
              Date
              <input className={field} type="date" value={form.date} onChange={(e) => set("date", e.target.value)} />
            </label>
            <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
              Status
              <select className={field} value={form.status} onChange={(e) => set("status", e.target.value)}>
                <option value="ON_TIME">On time</option>
                <option value="DELAYED">Delayed</option>
                <option value="CANCELLED">Cancelled</option>
              </select>
            </label>
            {form.status === "DELAYED" && (
              <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                Delay hours
                <input className={field} type="number" min={1} value={form.delay_hours} onChange={(e) => set("delay_hours", e.target.value)} />
              </label>
            )}
            {error && <p className="md:col-span-2 text-sm text-rose-600">{error}</p>}
            <div className="md:col-span-2 flex items-center gap-4">
              <PrimaryButton type="submit" disabled={busy}>
                {busy ? "Creating…" : "Create account"}
              </PrimaryButton>
              <Link href="/login" className="text-sm font-semibold text-slate-500">
                I already have an account
              </Link>
            </div>
          </form>
        </Panel>
      </div>
    </AppFrame>
  );
}
