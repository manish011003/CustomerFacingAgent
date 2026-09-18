export function TypingIndicator() {
  return (
    <div className="flex max-w-[85%] items-center gap-1 rounded-bubble rounded-bl-md bg-white px-4 py-3 shadow-card">
      <span className="h-1.5 w-1.5 animate-dot-bounce rounded-full bg-brand/40" />
      <span className="h-1.5 w-1.5 animate-dot-bounce rounded-full bg-brand/40 [animation-delay:120ms]" />
      <span className="h-1.5 w-1.5 animate-dot-bounce rounded-full bg-brand/40 [animation-delay:240ms]" />
    </div>
  );
}
