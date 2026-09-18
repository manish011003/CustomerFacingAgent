"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { AppFrame, Panel, PrimaryButton, Stepper, TopNav } from "@aero/ui";
import { createPlatform } from "@aero/ui";
import { api, clearSession, initials } from "../../lib/auth";

const factory = createPlatform("customer");

type Me = {
  passenger: { name: string; email: string; phone: string; loyalty_tier: string; pnr: string; account_origin: string };
  bookings: Array<{ id: string; flight?: string; route: string; status: string; date_label: string; pnr: string }>;
};

export default function AccountPage() {
  const [me, setMe] = useState<Me | null>(null);
  const [form, setForm] = useState({
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

  async function load() {
    const data = await api<Me>("/api/me");
    setMe(data);
  }

  useEffect(() => {
    load().catch(() => undefined);
  }, []);

  async function addBooking(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api("/api/me/bookings", {
        method: "POST",
        body: JSON.stringify({
          ...form,
          delay_hours: form.delay_hours ? Number(form.delay_hours) : null,
          airline_caused: true,
        }),
      });
      setForm((current) => ({ ...current, pnr: "", flight: "", origin: "", destination: "" }));
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not add booking");
    } finally {
      setBusy(false);
    }
  }

  const field = "mt-1 w-full rounded-full border border-slate-200 px-4 py-2.5 text-sm outline-none focus:border-[#2f6bff]";
  const passenger = me?.passenger;

  return (
    <AppFrame>
      <TopNav
        factory={factory}
        activeHref="/account"
        LinkComponent={Link}
        account={passenger ? { name: passenger.name, initials: initials(passenger.name) } : null}
        onSignOut={() => {
          api("/api/auth/logout", { method: "POST" }).catch(() => undefined);
          clearSession();
          window.location.href = "/login";
        }}
      />
      <Stepper steps={factory.steps} current={0} />
      <div className="grid gap-4 px-5 pb-6 lg:grid-cols-[0.9fr_1.1fr]">
        <Panel>
          <div className="text-[11px] font-bold uppercase tracking-wide text-slate-400">Passenger profile</div>
          {passenger ? (
            <div className="mt-4 space-y-2 text-sm">
              <div className="text-2xl font-extrabold">{passenger.name}</div>
              <div className="text-slate-500">
                {passenger.loyalty_tier} · {passenger.email}
              </div>
              <div className="text-slate-500">{passenger.phone}</div>
              <div className="text-[12px] text-slate-400">
                {passenger.account_origin === "seeded" ? "Enrolled from airline record" : "Self-service account"} · PNR {passenger.pnr || "—"}
              </div>
            </div>
          ) : (
            <p className="mt-4 text-sm text-slate-500">Loading account…</p>
          )}
        </Panel>
        <Panel>
          <div className="text-[11px] font-bold uppercase tracking-wide text-slate-400">Bookings</div>
          <div className="mt-3 space-y-2">
            {(me?.bookings || []).map((b) => (
              <div key={b.id} className="rounded-xl border border-slate-100 px-3 py-2 text-sm">
                <div className="font-semibold">
                  {b.flight || "Trip"} · {b.route}
                </div>
                <div className="text-[11px] text-slate-500">
                  {b.status} · {b.pnr} · {b.date_label}
                </div>
              </div>
            ))}
            {!me?.bookings?.length && <p className="text-sm text-slate-500">No trips on this account yet.</p>}
          </div>
          <form className="mt-5 grid gap-3 md:grid-cols-2" onSubmit={addBooking}>
            <div className="md:col-span-2 text-[11px] font-bold uppercase tracking-wide text-slate-400">Add a trip</div>
            <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
              PNR
              <input className={field} value={form.pnr} onChange={(e) => setForm({ ...form, pnr: e.target.value })} required />
            </label>
            <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
              Flight
              <input className={field} value={form.flight} onChange={(e) => setForm({ ...form, flight: e.target.value })} />
            </label>
            <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
              Origin
              <input className={field} value={form.origin} onChange={(e) => setForm({ ...form, origin: e.target.value })} required />
            </label>
            <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
              Destination
              <input className={field} value={form.destination} onChange={(e) => setForm({ ...form, destination: e.target.value })} required />
            </label>
            <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
              Date
              <input className={field} type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} required />
            </label>
            <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
              Status
              <select className={field} value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
                <option value="ON_TIME">On time</option>
                <option value="DELAYED">Delayed</option>
                <option value="CANCELLED">Cancelled</option>
              </select>
            </label>
            {form.status === "DELAYED" && (
              <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                Delay hours
                <input className={field} type="number" min={1} value={form.delay_hours} onChange={(e) => setForm({ ...form, delay_hours: e.target.value })} />
              </label>
            )}
            {error && <p className="md:col-span-2 text-sm text-rose-600">{error}</p>}
            <div className="md:col-span-2">
              <PrimaryButton type="submit" disabled={busy}>
                Save trip
              </PrimaryButton>
            </div>
          </form>
        </Panel>
      </div>
    </AppFrame>
  );
}
