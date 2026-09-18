"use client";

import { useEffect, useState } from "react";

import { ChatHeader } from "@/components/chat/header";
import { Composer } from "@/components/chat/composer";
import { ContextPanel } from "@/components/chat/context-panel";
import { FeedbackPopup } from "@/components/chat/feedback-popup";
import { QuickReplies } from "@/components/chat/quick-replies";
import { Thread } from "@/components/chat/thread";
import { api } from "@/lib/api";
import { starterReplies, resolvedReplies } from "@/lib/cards";
import { refreshTrip, useConversation } from "@/lib/store";
import type { LlmHealth } from "@/lib/types";

export function ChatShell() {
  const passenger = useConversation((state) => state.passenger);
  const booking = useConversation((state) => state.booking);
  const turns = useConversation((state) => state.turns);
  const sending = useConversation((state) => state.sending);
  const packet = useConversation((state) => state.packet);
  const csatDismissed = useConversation((state) => state.csatDismissed);
  const send = useConversation((state) => state.send);
  const submitFeedback = useConversation((state) => state.submitFeedback);
  const dismissCsat = useConversation((state) => state.dismissCsat);
  const signOut = useConversation((state) => state.signOut);
  const restart = useConversation((state) => state.restart);
  const [llm, setLlm] = useState<LlmHealth | null>(null);

  useEffect(() => {
    void refreshTrip();
    void api.llmHealth().then(setLlm).catch(() => setLlm(null));
  }, []);

  if (!passenger) return null;

  const onlyGreeting = turns.length === 1 && turns[0]?.role === "agent";
  const latest = [...turns].reverse().find((turn) => turn.role === "agent");
  const replies = onlyGreeting ? starterReplies(booking) : latest?.feedbackPrompt ? resolvedReplies() : [];
  const showCsat =
    !csatDismissed &&
    (latest?.feedbackPopup || packet?.feedback_popup) &&
    !packet?.feedback?.rating;

  return (
    <div className="flex h-dvh flex-col bg-canvas">
      <ChatHeader passenger={passenger} booking={booking} llm={llm} onSignOut={() => void signOut()} onRestart={() => void restart()} />
      <div className="flex min-h-0 flex-1">
        <Thread turns={turns} sending={sending} onChoose={(message) => void send(message)} />
        <ContextPanel />
      </div>
      <div className="bg-white px-4 py-3 shadow-composer sm:px-6">
        <div className="mx-auto max-w-thread">
          <QuickReplies replies={replies} disabled={sending} onPick={(reply) => void send(reply.message)} />
          <Composer disabled={sending} onSend={(text) => void send(text)} />
        </div>
      </div>
      <FeedbackPopup
        open={Boolean(showCsat)}
        sending={sending}
        onRate={(rating) => void submitFeedback(rating)}
        onDismiss={dismissCsat}
      />
    </div>
  );
}
