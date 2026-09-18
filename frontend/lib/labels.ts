import type { DecisionStatus, EscalationReason } from "./types";

/**
 * Wording, and only wording.
 *
 * The backend speaks in action codes (`hotel_delayed_hours`). A passenger
 * should not have to. These maps translate the code into a phrase and nothing
 * more: no entitlement is added, removed or softened here, and any code
 * without an entry falls back to its own words rather than being hidden.
 */

const ACTION_LABELS: Record<string, string> = {
  status: "Flight status",
  rebook_24h: "Free rebooking within 24 hours",
  refund_original: "Full refund to your original payment method",
  refund_other_method: "Refund to a different payment method",
  meal_voucher: "Meal voucher",
  lounge: "Lounge access",
  hotel_delayed_hours: "Hotel for the delayed hours",
  hotel_full_night: "Full night's hotel stay",
  business_upgrade: "Business-class upgrade",
  higher_fare_rebook: "Rebooking onto a higher-fare flight",
  fare_waiver: "Waiver of the fare difference",
  priority_rebooking: "Priority rebooking",
  compensation_beyond_policy: "Additional compensation",
  legal_or_formal: "Formal complaint",
  non_airline_exception: "Exception for a non-airline cause",
  general_help: "General help",
  booking_assist: "New booking",
  help_question: "Travel help",
};

const ACTION_ACTIONS: Record<string, string> = {
  rebook_24h: "Rebook next available flight",
  refund_original: "Request full refund",
  meal_voucher: "Meal voucher",
  lounge: "Lounge access",
  hotel_delayed_hours: "Arrange hotel",
  priority_rebooking: "Priority rebooking",
};

export function actionLabel(action: string): string {
  return ACTION_LABELS[action] ?? humanise(action);
}

export function actionButtonLabel(action: string): string {
  return ACTION_ACTIONS[action] ?? actionLabel(action);
}

export function actionRequestPhrase(action: string): string {
  const phrases: Record<string, string> = {
    rebook_24h: "Please rebook me on the next available flight.",
    refund_original: "Please issue a full refund to my original payment method.",
    meal_voucher: "Can I have the meal voucher?",
    lounge: "Can I have lounge access?",
    hotel_delayed_hours: "Please arrange the hotel for the delayed hours.",
  };
  return phrases[action] ?? `I would like: ${actionLabel(action).toLowerCase()}.`;
}

function humanise(code: string): string {
  return code.replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase());
}

export const STATUS_COPY: Record<DecisionStatus, { label: string; tone: "good" | "stop" | "warn" | "info" }> = {
  ALLOW: { label: "Approved", tone: "good" },
  DENY: { label: "Not available", tone: "stop" },
  ESCALATE: { label: "Sent to a supervisor", tone: "warn" },
  ASK: { label: "Your choice", tone: "info" },
  INFORM: { label: "Good to know", tone: "info" },
};

export const ESCALATION_COPY: Record<EscalationReason, string> = {
  fare_waiver_above_limit: "The fare difference is above what an agent can waive on their own.",
  legal_or_formal: "You have raised a formal complaint, which a person must handle.",
  compensation_beyond_policy: "You have asked for something the airline's policy does not cover.",
  // Deliberately says nothing about a category, a score, or the signals that
  // triggered it. The passenger is told a person is taking over, which is the
  // only part that concerns them.
  severe_customer_distress: "We have brought a colleague in so you can speak with a person directly.",
  refund_alternate_method: "A refund to a different payment method needs approval.",
  non_airline_cause: "This was not caused by the airline, so an exception needs approval.",
  unknown_entitlement: "This request is not covered by the policy the agent can apply.",
};

export function flightStatusCopy(status: string): { label: string; tone: "good" | "stop" | "warn" | "info" | "neutral" } {
  switch (status.toUpperCase()) {
    case "CANCELLED":
    case "NOT FOUND":
      return { label: status.toUpperCase() === "NOT FOUND" ? "Not found" : "Cancelled", tone: "stop" };
    case "DELAYED":
      return { label: "Delayed", tone: "warn" };
    case "BOARDING":
      return { label: "Boarding", tone: "good" };
    case "GATE OPEN":
      return { label: "Gate open", tone: "info" };
    case "SCHEDULED":
      return { label: "Scheduled", tone: "info" };
    case "UNAFFECTED":
    case "ON_TIME":
    case "ON TIME":
      return { label: "On time", tone: "good" };
    default:
      return { label: humanise(status.toLowerCase()), tone: "neutral" };
  }
}

export function initialsOf(name: string | undefined | null): string {
  if (!name) return "You";
  return name
    .split(" ")
    .filter(Boolean)
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}
