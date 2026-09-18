"use client";

import { useEffect, useState } from "react";

import { useConversation } from "./store";

/** Client-only gate so persist can read localStorage without blocking forever. */
export function useReady() {
  const hydrated = useConversation((state) => state.hydrated);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const finish = () => useConversation.setState({ hydrated: true });
    const unsub = useConversation.persist.onFinishHydration(finish);
    if (useConversation.persist.hasHydrated()) finish();
    const timer = window.setTimeout(finish, 50);
    return () => {
      unsub();
      window.clearTimeout(timer);
    };
  }, []);

  return mounted && hydrated;
}
