export function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-wa-bot rounded-lg rounded-tl-none px-3 py-2.5 shadow-bubble flex gap-1 items-center">
        <span className="size-1.5 rounded-full bg-slate-400 animate-bounce [animation-delay:-0.3s]" />
        <span className="size-1.5 rounded-full bg-slate-400 animate-bounce [animation-delay:-0.15s]" />
        <span className="size-1.5 rounded-full bg-slate-400 animate-bounce" />
      </div>
    </div>
  );
}
