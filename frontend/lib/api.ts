import type {
  AuthResult,
  ChatResponse,
  LlmHealth,
  MeResponse,
  MembersResponse,
  SignupPayload,
} from "./types";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init: RequestInit & { token?: string | null } = {}): Promise<T> {
  const { token, ...rest } = init;

  const response = await fetch(path, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...rest.headers,
    },
  });

  const body = await response.json().catch(() => ({}));

  if (!response.ok) {
    const detail = (body as { detail?: unknown }).detail;
    throw new ApiError(
      typeof detail === "string" ? detail : "Something went wrong. Please try again.",
      response.status,
    );
  }

  return body as T;
}

export interface StaffAuthResult {
  token: string;
  role: "staff";
  name: string;
}

export const api = {
  members: () => request<MembersResponse>("/api/auth/members"),

  login: (email: string, password: string) =>
    request<AuthResult>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  staffLogin: (email: string, password: string) =>
    request<StaffAuthResult>("/api/auth/staff/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  signup: (payload: SignupPayload) =>
    request<AuthResult>("/api/auth/signup", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  logout: (token: string) => request<{ ok: boolean }>("/api/auth/logout", { method: "POST", token }),

  me: (token: string) => request<MeResponse>("/api/me", { token }),

  llmHealth: () => request<LlmHealth>("/api/llm/health"),

  chat: (token: string, sessionId: string, message: string) =>
    request<ChatResponse>("/api/chat", {
      method: "POST",
      token,
      body: JSON.stringify({ session_id: sessionId, message }),
    }),

  feedback: (token: string, sessionId: string, rating: number, comment?: string) =>
    request<{ ok: boolean; reply: string; case_status: string; feedback: { rating: number; sentiment: string } }>(
      "/api/feedback",
      {
        method: "POST",
        token,
        body: JSON.stringify({ session_id: sessionId, rating, comment, resolved: rating >= 4 }),
      },
    ),

  resetSession: (token: string, sessionId: string) =>
    request<{ ok: boolean }>(`/api/session/${sessionId}/reset`, { method: "POST", token }),
};

export const OPS_URL = process.env.NEXT_PUBLIC_OPS_URL || "http://localhost:3001";

export function resolveOpsUrl() {
  const base = OPS_URL;
  if (typeof window === "undefined") return base.replace(/\/$/, "");
  try {
    const url = new URL(base, window.location.origin);
    if (url.hostname === "localhost" || url.hostname === "127.0.0.1") {
      url.hostname = window.location.hostname;
    }
    return url.toString().replace(/\/$/, "");
  } catch {
    return base.replace(/\/$/, "");
  }
}
