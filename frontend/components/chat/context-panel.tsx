"use client";

import { Badge } from "@/components/ui/badge";
import { useConversation } from "@/lib/store";
import type { PolicyDecision } from "@/lib/types";

function toneFor(status: string): "good" | "stop" | "warn" | "info" | "neutral" {
  if (status === "ALLOW") return "good";
  if (status === "DENY") return "stop";
  if (status === "ESCALATE") return "warn";
  if (status === "ASK") return "info";
  return "neutral";
}

function DecisionRow({ decision }: { decision: PolicyDecision }) {
  return (
    <div className="rounded-2xl border border-line bg-canvas/80 px-3 py-2">
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-semibold capitalize text-ink">{decision.action.replaceAll("_", " ")}</span>
        <Badge tone={toneFor(decision.status)}>{decision.status}</Badge>
      </div>
      <p className="mt-1 text-2xs leading-4 text-ink-muted">{decision.reason}</p>
      <p className="mt-1 text-2xs text-ink-faint">{decision.source}</p>
    </div>
  );
}

export function ContextPanel() {
  const packet = useConversation((state) => state.packet);
  const passenger = useConversation((state) => state.passenger);
  const booking = useConversation((state) => state.booking);
  const baseline = useConversation((state) => state.baseline);

  const identity = packet?.identity ?? (passenger
    ? { name: passenger.name, tier: passenger.loyalty_tier, pnr: passenger.pnr, email: passenger.email }
    : null);
  const facts = packet?.retrieved_facts?.length
    ? packet.retrieved_facts
    : booking
      ? [`${identity?.name} / ${identity?.tier} / PNR ${identity?.pnr}`, `${booking.flight || booking.leg} ${booking.route} ${booking.status}`]
      : ["No passenger retrieved yet."];
  const decisions = packet?.policy_decision?.decisions ?? baseline;
  const missing = packet?.missing_slots ?? [];

  return (
    <aside className="hidden w-[300px] shrink-0 overflow-y-auto scroll-slim border-l border-line bg-white/90 p-4 lg:block">
      <div className="text-xs font-semibold text-brand">This turn&apos;s context</div>
      <p className="mt-1 text-2xs leading-4 text-ink-faint">
        Retrieved this passenger. Policy is computed in code. Other customers and raw policy stay out of the model.
      </p>

      <section className="mt-4">
        <div className="text-2xs font-bold uppercase tracking-wide text-ink-faint">Identity</div>
        {identity ? (
          <p className="mt-1 text-sm font-semibold text-ink">
            {identity.name}
            <span className="block text-2xs font-medium text-ink-muted">
              {identity.tier} · {identity.pnr}
            </span>
          </p>
        ) : (
          <p className="mt-1 text-2xs text-ink-muted">Not identified.</p>
        )}
      </section>

      <section className="mt-4">
        <div className="text-2xs font-bold uppercase tracking-wide text-ink-faint">Retrieved facts</div>
        <ul className="mt-1 space-y-1">
          {facts.map((fact) => (
            <li key={fact} className="text-2xs leading-4 text-ink-soft">
              {fact}
            </li>
          ))}
        </ul>
      </section>

      {missing.length > 0 && (
        <div className="mt-3 rounded-xl bg-warn-bg px-2 py-1.5 text-2xs text-warn-fg">Missing: {missing.join(", ")}</div>
      )}

      <section className="mt-4 space-y-2">
        <div className="text-2xs font-bold uppercase tracking-wide text-ink-faint">Decision JSON</div>
        {decisions.length === 0 && <p className="text-2xs text-ink-muted">No engine decision on this turn yet.</p>}
        {decisions.map((decision) => (
          <DecisionRow key={decision.action + decision.status} decision={decision} />
        ))}
      </section>
    </aside>
  );
}
