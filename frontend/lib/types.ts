/**
 * Mirrors of `backend/models/schemas.py`.
 *
 * Nothing here is invented for the UI: every field is something the API
 * actually returns, so the conversation can only show what the policy engine
 * decided. Passengers, bookings and policy text all arrive over the wire —
 * none of it is baked into this app.
 */

export type DecisionStatus = "ALLOW" | "DENY" | "ASK" | "ESCALATE" | "INFORM";

export type EscalationReason =
  | "fare_waiver_above_limit"
  | "legal_or_formal"
  | "compensation_beyond_policy"
  | "severe_customer_distress"
  | "refund_alternate_method"
  | "non_airline_cause"
  | "unknown_entitlement";

export interface Passenger {
  id: string;
  name: string;
  email: string;
  loyalty_tier: string;
  pnr: string;
  phone?: string;
  account_origin?: "seeded" | "self_service";
}

export interface SuggestedFlight {
  flight: string;
  origin: string;
  destination: string;
  date?: string;
  date_label?: string;
  scheduled_departure: string;
  scheduled_arrival?: string | null;
  gate?: string | null;
  status: string;
  aircraft?: string | null;
  source: "scheduled" | "random";
  passengers?: string | null;
  href: string;
}

export interface Booking {
  id: string;
  customer_id: string;
  customer_name: string;
  pnr: string;
  flight: string | null;
  leg: string;
  route: string;
  origin: string;
  destination: string;
  date: string;
  date_label: string;
  scheduled_departure: string;
  status: string;
  status_reason: string | null;
  delay_hours: number | null;
  new_departure: string | null;
  airline_caused: boolean;
  quoted_fare_difference_inr: number | null;
}

export interface Eligibility {
  action: string;
  status: DecisionStatus;
  reason: string;
  source: string;
  scope: string | null;
  eligible: boolean;
}

export interface PolicyDecision extends Eligibility {
  simulated?: boolean;
  amount_inr?: number | null;
  requires_customer_choice?: boolean;
  authority_limit_inr?: number | null;
  escalation_reason?: EscalationReason | null;
}

export interface RuleHit {
  clause_id: string;
  rule_id: string;
  title: string;
  text: string;
  kind: "rule" | "allowed_action" | "must_escalate" | "assumption";
  score: number;
  for_action: string | null;
}

export interface ServiceFeedback {
  rating?: number | null;
  comment?: string | null;
  sentiment: "positive" | "negative" | "mixed";
  source?: string;
  ts?: string | null;
}

export interface ContextPacket {
  unidentified: boolean;
  identity: { id: string; name: string; tier: string; pnr: string; email: string } | null;
  booking: Booking | null;
  disruption: Record<string, unknown> | null;
  emotion: string | null;
  policy_decision: {
    disruption_type: string | null;
    delay_hours: number | null;
    entitlements: string[];
    decisions: PolicyDecision[];
    missing_slots: string[];
    execute: string[];
    deny: string[];
    escalate: string[];
    ask: string[];
  } | null;
  retrieved_facts: string[];
  forbidden_notes: string[];
  retrieved: { backend: string; rules: RuleHit[] } | null;
  missing_slots: string[];
  authority: Record<string, unknown>;
  executed_actions: string[];
  recalled_turns?: { ts: string; message: string; reply: string }[];
  known_facts?: { fact: string; source: string; ts: string }[];
  kb_backend: string;
  case_status?: "open" | "resolved" | "escalated" | string;
  feedback_prompt?: boolean;
  feedback_popup?: boolean;
  feedback?: ServiceFeedback | null;
  suggested_flight?: SuggestedFlight | null;
}

export interface Escalation {
  id: string;
  status: string;
  customer: string;
  pnr: string;
  flight: string | null;
  escalation_reasons: string[];
  escalation_reason_codes: EscalationReason[];
  recommended_human_question?: string;
}

export interface ChatResponse {
  reply: string;
  context_packet: ContextPacket;
  trace: { step: string; detail: string; status: string }[];
  eligibility: Eligibility[];
  audit_event: Record<string, unknown>;
  escalation: Escalation | null;
  case_status?: string | null;
  feedback_prompt?: boolean;
  feedback_popup?: boolean;
  feedback?: ServiceFeedback | null;
  session: {
    session_id: string;
    identified: boolean;
    customer_id: string | null;
    executed_actions: string[];
    denied: string[];
    escalations: string[];
    escalated_to_human?: boolean;
    resolved_by_customer?: boolean;
    open_question: string | null;
    agent_mode?: "llm" | "fallback";
  };
}

export interface LlmHealth {
  enabled: boolean;
  provider: string;
  model: string;
  agent_mode: "llm" | "fallback";
  key_present: boolean;
  fallback: string;
}

export interface ChatMessage {
  role: "user" | "assistant" | string;
  content: string;
}

export interface Conversation {
  session_id: string | null;
  messages: ChatMessage[];
  executed_actions?: string[];
  escalated_to_human?: boolean;
  resolved_by_customer?: boolean;
  feedback?: ServiceFeedback | null;
}

export interface MeResponse {
  passenger: Passenger | null;
  bookings: Booking[];
  affected_booking: Booking | null;
  eligibility: Eligibility[];
  kb_backend: string;
  conversation?: Conversation;
}

export interface AuthResult {
  token: string;
  passenger: Passenger;
}

export interface MembersResponse {
  members: Passenger[];
  seed_password_hint: string;
  note: string;
}

export interface SignupPayload {
  name: string;
  email: string;
  phone: string;
  password: string;
  pnr?: string;
}

export interface QuickReply {
  id: string;
  label: string;
  message: string;
  tone?: "primary" | "neutral";
}

export interface Turn {
  id: string;
  role: "passenger" | "agent";
  text: string;
  at: number;
  eligibility?: Eligibility[];
  decisions?: PolicyDecision[];
  clauses?: RuleHit[];
  executedActions?: string[];
  escalation?: Escalation | null;
  booking?: Booking | null;
  packet?: ContextPacket | null;
  failed?: boolean;
  caseStatus?: string | null;
  feedbackPrompt?: boolean;
  feedbackPopup?: boolean;
  suggestedFlight?: SuggestedFlight | null;
}
