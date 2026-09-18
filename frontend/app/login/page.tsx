"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { SignIn } from "@/components/sign-in";
import { useReady } from "@/lib/ready";
import { useConversation } from "@/lib/store";

export default function LoginPage() {
  const router = useRouter();
  const ready = useReady();
  const token = useConversation((state) => state.token);

  useEffect(() => {
    if (ready && token) router.replace("/");
  }, [ready, token, router]);

  if (!ready) {
    return (
      <div className="grid min-h-dvh place-items-center text-sm text-ink-muted">
        Loading…
      </div>
    );
  }

  if (token) return null;

  return <SignIn />;
}
