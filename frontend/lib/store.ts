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

  markHydrated: () => void;
  signIn: (email: string, password: string) => Promise<void>;
  join: (payload: SignupPayload) => Promise<void>;
  signOut: () => Promise<void>;
  send: (text: string) => Promise<void>;
  restart: () => Promise<void>;
  clearAuthError: () => void;
}

function greeting(passenger: Passenger, booking: Booking | null): Turn {
  const firstName = passenger.name.split(" ")[0];
  const text = booking
    ? `Hi ${firstName} — I'm the resolution agent. I can see your booking ${booking.pnr}, and I'm here to sort out whatever has gone wrong with it. Tell me what you need and I'll check it against the airline's policy.`
    : `Hi ${firstName} — I'm the resolution agent. I can't see a disrupted flight on your account yet. If you tell me your booking reference and what has happened, I'll take a look.`;

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
                decisions: packet.policy_decision?.decisions ?? [],
                clauses: packet.retrieved?.rules ?? [],
                executedActions: response.session.executed_actions,
                escalation: response.escalation,
                booking: state.turns.some((turn) => turn.booking) ? undefined : packet.booking,
                packet,
              },
            ],
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

      restart: async () => {
        const { token, sessionId, passenger, booking } = get();
        if (token && sessionId) await api.resetSession(token, sessionId).catch(() => undefined);
        set({
          sessionId: newSessionId(),
          turns: passenger ? [greeting(passenger, booking)] : [],
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

async function openConversation(
  set: (partial: Partial<State>) => void,
  token: string,
  passenger: Passenger,
) {
  const me = await api.me(token).catch(() => null);
  const booking = me?.affected_booking ?? null;

  set({
    token,
    passenger: me?.passenger ?? passenger,
    sessionId: newSessionId(),
    booking,
    baseline: me?.eligibility ?? [],
    packet: null,
    turns: [greeting(me?.passenger ?? passenger, booking)],
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
