import { actionButtonLabel, actionRequestPhrase } from "./labels";
import type { Booking, PolicyDecision, QuickReply, Turn } from "./types";

const CHOICE_STATUSES = new Set(["ASK", "ALLOW"]);

export function previousExecuted(turns: Turn[], index: number): Set<string> {
  for (let i = index - 1; i >= 0; i -= 1) {
    const executed = turns[i].executedActions;
    if (executed?.length) return new Set(executed);
  }
  return new Set();
}

export function newActions(turn: Turn, already: Set<string>): string[] {
  return (turn.executedActions ?? []).filter((action) => !already.has(action));
}

export function choiceDecisions(turn: Turn): PolicyDecision[] {
  const executed = new Set(turn.executedActions ?? []);
  return (turn.decisions ?? []).filter((decision) => {
    if (!CHOICE_STATUSES.has(decision.status)) return false;
    if (!decision.eligible && decision.status !== "ASK") return false;
    if (executed.has(decision.action)) return false;
    if (decision.requires_customer_choice) return true;
    return decision.status === "ALLOW" && decision.eligible;
  });
}

export function repliesForTurn(turn: Turn | undefined): QuickReply[] {
  if (!turn) return [];
  return choiceDecisions(turn).map((decision, index) => ({
    id: `${turn.id}-${decision.action}`,
    label: actionButtonLabel(decision.action),
    message: actionRequestPhrase(decision.action),
    tone: index === 0 ? "primary" : "neutral",
  }));
}

export function starterReplies(booking: Booking | null): QuickReply[] {
  if (!booking) {
    return [
      {
        id: "start-help",
        label: "I need help with my trip",
        message: "I need help with my trip.",
        tone: "primary",
      },
    ];
  }

  const status = booking.status.toUpperCase();
  if (status === "CANCELLED") {
    return [
      {
        id: "start-cancel",
        label: "Help me with this cancellation",
        message: "My flight has been cancelled. Please tell me what you can do.",
        tone: "primary",
      },
    ];
  }
  if (status === "DELAYED") {
    return [
      {
        id: "start-delay",
        label: "Help me with this delay",
        message: "My flight is delayed. Please tell me what I'm entitled to.",
        tone: "primary",
      },
    ];
  }
  return [
    {
      id: "start-status",
      label: "What's happening with my flight?",
      message: "What's the status of my flight?",
      tone: "primary",
    },
  ];
}
