"use client";

import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

import { ApiError, api } from "./api";
import type { Booking, ContextPacket, Eligibility, Passenger, SignupPayload, Turn } from "./types";

function turnId() {
  return `t-${Math.random().toString(36).slice(2, 10)}`;
}

function newSessionId() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) return crypto.randomUUID();
  return `sess-${Math.random().toString(36).slice(2)}`;
}

interface Persisted {
  token: string | null;
  passenger: Passenger | null;
  sessionId: string | null;
  turns: Turn[];
}

interface State extends Persisted {
  booking: Booking | null;
  baseline: Eligibility[];
  packet: ContextPacket | null;
  sending: boolean;
  loading: boolean;
  authError: string | null;
  hydrated: boolean;
  csatDismissed: boolean;

  markHydrated: () => void;
  signIn: (email: string, password: string) => Promise<void>;
  join: (payload: SignupPayload) => Promise<void>;
  signOut: () => Promise<void>;
  send: (text: string) => Promise<void>;
  submitFeedback: (rating: number, comment?: string) => Promise<void>;
  dismissCsat: () => void;
  restart: () => Promise<void>;
  clearAuthError: () => void;
}

function greeting(passenger: Passenger, booking: Booking | null): Turn {
  const firstName = passenger.name.split(" ")[0];
  const status = booking?.status?.toUpperCase();
  let text = `Hi ${firstName} — I'm here. What can I help with?`;
  if (status === "DELAYED") {
    const hours = booking?.delay_hours != null ? ` ${booking.delay_hours} hours` : "";
    text = `Hi ${firstName} — I can see ${booking?.flight || "your flight"} is delayed${hours}. What can I help with?`;
  } else if (status === "CANCELLED") {
    text = `Hi ${firstName} — ${booking?.flight || "Your flight"} was cancelled. I can rebook you or refund the original payment. What do you want to do?`;
  } else if (booking) {
    text = `Hi ${firstName} — I've got ${booking.flight || "your booking"}. What do you need?`;
  }

  return {
    id: turnId(),
    role: "agent",
    text,
    at: Date.now(),
    booking,
  };
}

export const useConversation = create<State>()(
  persist(
    (set, get) => ({
      token: null,
      passenger: null,
      sessionId: null,
      turns: [],

      booking: null,
      baseline: [],
      packet: null,
      sending: false,
      loading: false,
      authError: null,
      hydrated: false,
      csatDismissed: false,

      markHydrated: () => set({ hydrated: true }),
      clearAuthError: () => set({ authError: null }),

      signIn: async (email, password) => {
        set({ loading: true, authError: null });
        try {
          const { token, passenger } = await api.login(email, password);
          await openConversation(set, token, passenger);
        } catch (error) {
          set({ loading: false, authError: messageFor(error) });
          throw error;
        }
      },

      join: async (payload) => {
        set({ loading: true, authError: null });
        try {
          const { token, passenger } = await api.signup(payload);
          await openConversation(set, token, passenger);
        } catch (error) {
          set({ loading: false, authError: messageFor(error) });
          throw error;
        }
      },

      signOut: async () => {
        const { token } = get();
        if (token) await api.logout(token).catch(() => undefined);
        set({
          token: null,
          passenger: null,
          sessionId: null,
          turns: [],
          booking: null,
          baseline: [],
          packet: null,
          authError: null,
        });
      },

      send: async (text) => {
        const body = text.trim();
        const { token, sessionId, sending } = get();
        if (!body || !token || !sessionId || sending) return;

        set((state) => ({
          sending: true,
          turns: [...state.turns, { id: turnId(), role: "passenger", text: body, at: Date.now() }],
        }));

        try {
          const response = await api.chat(token, sessionId, body);
          const packet = response.context_packet;
          const decisions = packet.policy_decision?.decisions ?? [];
          const missing = packet.missing_slots ?? [];
          const bookingReady =
            decisions.some((decision: { action?: string }) => decision.action === "booking_assist") &&
            Boolean(packet.suggested_flight) &&
            !["origin", "destination", "date", "passengers"].some((slot) => missing.includes(slot));

          set((state) => ({
            sending: false,
            booking: packet.booking ?? state.booking,
            packet,
            turns: [
              ...state.turns,
              {
                id: turnId(),
                role: "agent",
                text: response.reply,
                at: Date.now(),
                eligibility: response.eligibility,
                decisions,
                clauses: packet.retrieved?.rules ?? [],
                executedActions: response.session.executed_actions,
                escalation: response.escalation,
                booking: state.turns.some((turn) => turn.booking) ? undefined : packet.booking,
                packet,
                caseStatus: response.case_status ?? packet.case_status,
                feedbackPrompt: Boolean(response.feedback_prompt ?? packet.feedback_prompt),
                feedbackPopup: Boolean(response.feedback_popup ?? packet.feedback_popup),
                suggestedFlight: bookingReady ? packet.suggested_flight ?? null : null,
              },
            ],
            csatDismissed: Boolean(response.feedback_popup ?? packet.feedback_popup)
              ? false
              : state.csatDismissed,
          }));
        } catch (error) {
          set((state) => ({
            sending: false,
            turns: [
              ...state.turns,
              {
                id: turnId(),
                role: "agent",
                text: messageFor(error),
                at: Date.now(),
                failed: true,
              },
            ],
          }));
        }
      },

      submitFeedback: async (rating, comment) => {
        const { token, sessionId, sending } = get();
        if (!token || !sessionId || sending) return;

        set((state) => ({
          sending: true,
          turns: [
            ...state.turns,
            {
              id: turnId(),
              role: "passenger",
              text: `I'd rate this service ${rating}/5.${comment ? ` ${comment}` : ""}`,
              at: Date.now(),
            },
          ],
        }));

        try {
          const response = await api.feedback(token, sessionId, rating, comment);
          set((state) => ({
            sending: false,
            packet: state.packet
              ? {
                  ...state.packet,
                  case_status: response.case_status,
                  feedback_prompt: false,
                  feedback: {
                    rating,
                    comment: comment ?? null,
                    sentiment: response.feedback.sentiment as "positive" | "negative" | "mixed",
                    source: "card",
                  },
                }
              : state.packet,
            turns: [
              ...state.turns,
              {
                id: turnId(),
                role: "agent",
                text: response.reply,
                at: Date.now(),
                caseStatus: response.case_status,
                feedbackPrompt: false,
                feedbackPopup: false,
              },
            ],
            csatDismissed: true,
          }));
        } catch (error) {
          set((state) => ({
            sending: false,
            turns: [
              ...state.turns,
              {
                id: turnId(),
                role: "agent",
                text: messageFor(error),
                at: Date.now(),
                failed: true,
              },
            ],
          }));
        }
      },

      dismissCsat: () => set({ csatDismissed: true }),

      restart: async () => {
        const { token, sessionId, passenger, booking } = get();
        if (token && sessionId) await api.resetSession(token, sessionId).catch(() => undefined);
        set({
          sessionId: newSessionId(),
          turns: passenger ? [greeting(passenger, booking)] : [],
          csatDismissed: false,
          packet: null,
        });
      },
    }),
    {
      name: "aeroresolve.customer.v1",
      storage: createJSONStorage(() => localStorage),
      partialize: (state): Persisted => ({
        token: state.token,
        passenger: state.passenger,
        sessionId: state.sessionId,
        turns: state.turns,
      }),
      onRehydrateStorage: () => () => {
        useConversation.setState({ hydrated: true });
      },
    },
  ),
);

function turnsFromMessages(messages: { role?: string; content?: string }[] | undefined, booking: Booking | null): Turn[] {
  const rows = (messages || []).filter((message) => message.role === "user" || message.role === "assistant");
  if (!rows.length) return [];
  return rows.map((message, index) => ({
    id: `hist-${index}`,
    role: message.role === "user" ? "passenger" : "agent",
    text: message.content || "",
    at: Date.now() - (rows.length - index) * 1000,
    booking: index === 0 && message.role === "assistant" ? booking : undefined,
  }));
}

async function openConversation(
  set: (partial: Partial<State>) => void,
  token: string,
  passenger: Passenger,
) {
  const me = await api.me(token).catch(() => null);
  const booking = me?.affected_booking ?? null;
  const restored = turnsFromMessages(me?.conversation?.messages, booking);

  set({
    token,
    passenger: me?.passenger ?? passenger,
    sessionId: me?.conversation?.session_id || newSessionId(),
    booking,
    baseline: me?.eligibility ?? [],
    packet: null,
    turns: restored.length ? restored : [greeting(me?.passenger ?? passenger, booking)],
    loading: false,
    authError: null,
  });
}

function messageFor(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  return "I couldn't reach the airline's systems just now. Please try again.";
}

export async function refreshTrip() {
  const { token } = useConversation.getState();
  if (!token) return;
  try {
    const me = await api.me(token);
    useConversation.setState({
      passenger: me.passenger ?? undefined,
      booking: me.affected_booking,
      baseline: me.eligibility,
    });
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      useConversation.setState({ token: null, passenger: null, turns: [], sessionId: null });
    }
  }
}
