import { useEffect, useRef } from "react";
import type { UIMessage } from "@/types";
import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";
import { WELCOME_HINT } from "@/shared/constants";

interface Props {
  messages: UIMessage[];
  loading: boolean;
  loadingHistory?: boolean;
  error: string | null;
}

export function ChatWindow({ messages, loading, loadingHistory, error }: Props) {
  const end = useRef<HTMLDivElement>(null);

  useEffect(() => {
    end.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages.length, loading]);

  return (
    <div className="flex-1 overflow-y-auto px-3 py-3 wa-wallpaper">
      {loadingHistory && messages.length === 0 && (
        <p className="text-center text-xs text-slate-600 py-6">Loading chat…</p>
      )}

      {!loadingHistory && messages.length === 0 && !loading && (
        <div className="mx-auto max-w-sm text-center py-10 px-4">
          <div className="inline-flex size-14 items-center justify-center rounded-full bg-wa-header text-white text-lg font-bold mb-3">
            DPA
          </div>
          <p className="text-sm text-slate-700 font-medium">Demo Physics Academy</p>
          <p className="text-xs text-slate-600 mt-2 leading-relaxed">{WELCOME_HINT}</p>
        </div>
      )}

      <div className="space-y-1.5 max-w-lg mx-auto w-full">
        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
        {loading && <TypingIndicator />}
        {error && (
          <div className="text-xs text-red-700 bg-red-50 border border-red-200 rounded-md px-3 py-2">
            {error}
          </div>
        )}
        <div ref={end} />
      </div>
    </div>
  );
}
