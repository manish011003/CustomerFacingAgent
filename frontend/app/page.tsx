"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { ChatShell } from "@/components/chat/chat-shell";
import { useReady } from "@/lib/ready";
import { useConversation } from "@/lib/store";

export default function ResolvePage() {
  const router = useRouter();
  const ready = useReady();
  const token = useConversation((state) => state.token);

  useEffect(() => {
    if (ready && !token) router.replace("/login");
  }, [ready, token, router]);

  if (!ready || !token) {
    return (
      <div className="grid min-h-dvh place-items-center text-sm text-ink-muted">
        Loading…
      </div>
    );
  }

  return <ChatShell />;
}
