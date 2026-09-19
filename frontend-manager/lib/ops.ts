export type CaseStatus = "open" | "resolved" | "escalated" | string;

export interface Operations {
  total_cases: number;
  resolved_cases: number;
  escalated_cases: number;
  open_cases: number;
  resolution_rate: number;
  average_resolution_seconds: number | null;
}

export interface PolicyDecision {
  action: string;
  status: string;
  reason: string;
  source: string;
  scope?: string | null;
  eligible?: boolean;
  escalation_reason?: string | null;
}

export interface PolicyRule {
  clause_id: string;
  title: string;
  text: string;
  for_action: string | null;
  kind: string;
}

export interface TimelineEvent {
  id?: string;
  ts?: string;
  kind: string;
  action?: string;
  tool?: string;
  status?: string;
  reason?: string;
  source?: string;
  message?: string;
  reply?: string;
}

export interface CaseSummary {
  id: string;
  status: CaseStatus;
  customer: string;
  customer_id?: string;
  loyalty_tier?: string;
  email?: string;
  pnr: string;
  flight?: string | null;
  issue?: string;
  action_taken?: string[];
  escalation_status?: boolean;
  escalation_reasons?: string[];
  escalation_reason_codes?: string[];
  updated_at?: string;
  created_at?: string;
  resolved_at?: string | null;
  feedback?: {
    rating?: number | null;
    comment?: string | null;
    sentiment?: string;
  } | null;
}

export interface CaseDetail extends CaseSummary {
  booking?: {
    flight?: string | null;
    origin?: string;
    destination?: string;
    date_label?: string;
    scheduled_departure?: string;
    new_departure?: string | null;
    status?: string;
    status_reason?: string | null;
    delay_hours?: number | null;
    pnr?: string;
  } | null;
  policy_decisions?: PolicyDecision[];
  policy_rules?: PolicyRule[];
  transcript?: { role: string; content: string }[];
  timeline?: TimelineEvent[];
  recommended_human_question?: string | null;
}

export interface ContainmentByCategory {
  turns: number;
  contained_turns: number;
  escalated_turns: number;
  containment_rate: number;
}

/** GET /api/analytics/frustration.
 *
 * `by_category` counts only observations at or above the store confidence
 * threshold. `low_confidence_by_category` is deliberately a separate field
 * rather than a subset flag: an unconfirmed regex guess must never be summed
 * into a number someone staffs a shift from.
 */
export interface Frustration {
  observations: number;
  counted_observations?: number;
  by_category?: Record<string, number>;
  low_confidence_observations?: number;
  low_confidence_by_category?: Record<string, number>;
  escalation_recommended?: number;
  containment_by_category?: Record<string, ContainmentByCategory>;
  graph?: {
    edge: string;
    edges: number;
    counted_edges: number;
    low_confidence_edges: number;
    passengers: number;
    top_signals_by_category?: Record<string, Record<string, number>>;
  };
  note?: string;
}

export interface Containment {
  turns: number;
  contained_turns?: number;
  containment_rate?: number;
  escalated_turns?: number;
  escalations_by_reason?: Record<string, number>;
  distress_escalations?: number;
  authority_escalations?: number;
  grounding_coverage?: number | null;
  p50_latency_ms?: number | null;
  p95_latency_ms?: number | null;
  llm_calls?: number;
  est_spend_usd?: number;
  est_cost_per_turn_usd?: number;
  est_cost_per_contained_turn_usd?: number | null;
  degraded_turns?: number;
  note?: string;
}

export interface Analytics {
  operations?: Operations;
  containment?: Containment;
  frustration?: Frustration;
  passengers?: number;
  events?: number;
  cases?: number;
  escalations?: number;
  kb_backend?: string;
}

export interface GraphNode {
  id: string;
  type: string;
  label: string;
}

export interface GraphEdge {
  id?: string;
  from_id: string;
  to_id: string;
  rel: string;
  reason?: string;
  source?: string;
  customer_id?: string;
  status?: string;
  action?: string;
  writes?: number;
  ts?: string;
  low_confidence?: boolean;
}

export interface KnowledgeGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
  writes?: number;
  unique_edges?: number;
  types?: Record<string, number>;
  relations?: Record<string, number>;
  kb_backend?: string;
  note?: string;
}

/** GET /api/kb/pending — low-confidence writes waiting for a supervisor. */
export interface PendingKbEntry {
  id: string;
  tag: string;
  message_excerpt: string;
  frustration_score: number;
  proposed_direction: string;
}

/** Mildest to most severe, so the panel never reshuffles between refreshes. */
export const FRUSTRATION_ORDER = ["neutral", "annoyed", "frustrated", "distressed", "hostile"];

export function frustrationTone(category: string): "good" | "warn" | "stop" | "neutral" {
  if (category === "hostile" || category === "distressed") return "stop";
  if (category === "frustrated" || category === "annoyed") return "warn";
  if (category === "neutral") return "good";
  return "neutral";
}

/** Categories present in any of the supplied buckets, in severity order. */
export function orderedCategories(...buckets: (Record<string, unknown> | undefined)[]): string[] {
  const present = new Set<string>();
  for (const bucket of buckets) {
    for (const key of Object.keys(bucket || {})) present.add(key);
  }
  const known = FRUSTRATION_ORDER.filter((category) => present.has(category));
  const extra = [...present].filter((category) => !FRUSTRATION_ORDER.includes(category)).sort();
  return [...known, ...extra];
}

export const CUSTOMER_URL = process.env.NEXT_PUBLIC_CUSTOMER_URL || "http://localhost:3000";

export class OpsAuthError extends Error {
  constructor() {
    super("unauthorized");
    this.name = "OpsAuthError";
  }
}

export async function fetchJson<T>(path: string, token: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { Authorization: `Bearer ${token}`, ...(init?.headers || {}) },
  });
  if (response.status === 401) throw new OpsAuthError();
  if (!response.ok) throw new Error("Request failed");
  return response.json() as Promise<T>;
}

export function humanise(value: string | null | undefined): string {
  if (!value) return "—";
  return value.replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase());
}

export function formatDuration(seconds: number | null | undefined): string {
  if (seconds == null) return "—";
  if (seconds < 60) return `${Math.round(seconds)}s`;
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  const rest = minutes % 60;
  return rest ? `${hours}h ${rest}m` : `${hours}h`;
}

export function formatRate(value: number | null | undefined): string {
  if (typeof value !== "number") return "—";
  return `${Math.round(value * 100)}%`;
}

export function statusTone(status: string): "good" | "warn" | "stop" | "neutral" {
  if (status === "resolved") return "good";
  if (status === "escalated") return "warn";
  if (status === "open") return "neutral";
  return "neutral";
}

export function initials(name?: string | null): string {
  if (!name) return "?";
  const parts = name.trim().split(/\s+/).filter(Boolean);
  return parts
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || "")
    .join("");
}

const AVATARS = ["#7c6cff", "#60a5fa", "#34d399", "#f472b6", "#fbbf24", "#fb7185"];

export function avatarColor(seed?: string | null): string {
  const value = seed || "?";
  let hash = 0;
  for (let i = 0; i < value.length; i += 1) hash = (hash * 31 + value.charCodeAt(i)) >>> 0;
  return AVATARS[hash % AVATARS.length];
}

export function formatUsd(value: number | null | undefined): string {
  if (typeof value !== "number") return "—";
  if (value === 0) return "$0";
  if (value < 0.01) return `$${value.toFixed(4)}`;
  return `$${value.toFixed(2)}`;
}

export function formatDay(iso?: string | null): string {
  if (!iso) return "—";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}
