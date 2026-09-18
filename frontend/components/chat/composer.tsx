"use client";

import { FormEvent, useState } from "react";
import { ArrowUp } from "lucide-react";

export function Composer({
  disabled,
  onSend,
}: {
  disabled?: boolean;
  onSend: (text: string) => void;
}) {
  const [value, setValue] = useState("");

  const submit = (event: FormEvent) => {
    event.preventDefault();
    const text = value.trim();
    if (!text || disabled) return;
    onSend(text);
    setValue("");
  };

  return (
    <form onSubmit={submit} className="flex items-center gap-2">
      <label className="sr-only" htmlFor="message">
        Message
      </label>
      <textarea
        id="message"
        rows={1}
        value={value}
        disabled={disabled}
        placeholder="Tell us what you need…"
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            submit(event);
          }
        }}
        className="max-h-32 min-h-12 flex-1 resize-none rounded-full border-0 bg-ice px-5 py-3 text-base text-ink placeholder:text-ink-faint focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand/20"
      />
      <button
        type="submit"
        disabled={disabled || !value.trim()}
        aria-label="Send"
        className="grid h-12 w-12 shrink-0 place-items-center rounded-full bg-brand text-white shadow-card transition-colors hover:bg-brand-hover disabled:pointer-events-none disabled:opacity-40"
      >
        <ArrowUp className="h-4 w-4" strokeWidth={2.4} />
      </button>
    </form>
  );
}
