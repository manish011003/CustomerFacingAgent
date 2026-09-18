"use client";

import { useEffect, useRef } from "react";

import { AgentCards } from "@/components/chat/cards";
import { TypingIndicator } from "@/components/chat/typing-indicator";
import { previousExecuted } from "@/lib/cards";
import { formatTime } from "@/lib/utils";
import type { Turn } from "@/lib/types";
import { cn } from "@/lib/utils";

export function Thread({
  turns,
  sending,
  onChoose,
}: {
  turns: Turn[];
  sending: boolean;
  onChoose: (message: string) => void;
}) {
  const bottom = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth" });
  }, [turns.length, sending]);

  const latestAgentId = [...turns].reverse().find((turn) => turn.role === "agent")?.id;

  return (
    <div className="flex-1 overflow-y-auto scroll-slim px-4 py-5 sm:px-6">
      <div className="mx-auto flex max-w-thread flex-col gap-4">
        {turns.map((turn, index) => {
          const mine = turn.role === "passenger";
          return (
            <div key={turn.id} className={cn("flex flex-col", mine ? "items-end" : "items-start")}>
              <div
                className={cn(
                  "max-w-[92%] animate-bubble-in whitespace-pre-wrap rounded-bubble px-4 py-3 text-sm leading-6 sm:max-w-[85%]",
                  mine
                    ? "rounded-br-md bg-brand text-white"
                    : turn.failed
                      ? "border border-stop-line bg-stop-bg text-stop-fg"
                      : "rounded-bl-md bg-white text-ink shadow-card",
                )}
              >
                {turn.text}
              </div>
              <span className="mt-1 text-2xs text-ink-faint">{formatTime(turn.at)}</span>
              {!mine && (
                <div className="mt-0 w-full max-w-[92%] sm:max-w-[85%]">
                  <AgentCards
                    turn={turn}
                    previousExecuted={previousExecuted(turns, index)}
                    isLatest={turn.id === latestAgentId}
                    sending={sending}
                    onChoose={onChoose}
                    showHandover={
                      Boolean(turn.escalation) &&
                      !turns.slice(0, index).some((prior) => prior.role === "agent" && prior.escalation)
                    }
                  />
                </div>
              )}
            </div>
          );
        })}
        {sending && <TypingIndicator />}
        <div ref={bottom} />
      </div>
    </div>
  );
}
