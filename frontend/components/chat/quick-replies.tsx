"use client";

import { Button } from "@/components/ui/button";
import type { QuickReply } from "@/lib/types";

export function QuickReplies({
  replies,
  disabled,
  onPick,
}: {
  replies: QuickReply[];
  disabled?: boolean;
  onPick: (reply: QuickReply) => void;
}) {
  if (!replies.length) return null;

  return (
    <div className="flex flex-wrap gap-1.5 px-1 pb-2">
      {replies.map((reply) => (
        <Button
          key={reply.id}
          variant={reply.tone === "primary" ? "chip" : "secondary"}
          size="sm"
          disabled={disabled}
          onClick={() => onPick(reply)}
          className="max-w-full"
        >
          <span className="truncate">{reply.label}</span>
        </Button>
      ))}
    </div>
  );
}
