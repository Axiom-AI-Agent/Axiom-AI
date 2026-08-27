"use client";

import { FormEvent, useState } from "react";
import { Loader2, MessageCircle, Send, Sparkles, X } from "lucide-react";

import { queryDashboardAgent } from "@/lib/api";
import { useTenant } from "@/context/TenantContext";

interface ChatTurn {
  role: "user" | "assistant";
  content: string;
}

export default function FloatingChat() {
  const { tenantId } = useTenant();
  const [isOpen, setIsOpen] = useState(false);
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = draft.trim();
    if (!message || sending) {
      return;
    }

    setDraft("");
    setError(null);
    setSending(true);
    setTurns((current) => [...current, { role: "user", content: message }]);

    try {
      const result = await queryDashboardAgent(message, tenantId);
      setTurns((current) => [
        ...current,
        { role: "assistant", content: result.reply },
      ]);
    } catch (requestError) {
      console.error(requestError);
      setError("Could not reach the dashboard agent.");
    } finally {
      setSending(false);
    }
  }

  return (
    <>
      {/* Floating trigger button */}
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg transition-all hover:bg-blue-500 hover:shadow-xl"
        aria-label="Toggle AI assistant"
      >
        {isOpen ? (
          <X className="h-6 w-6" />
        ) : (
          <Sparkles className="h-6 w-6" />
        )}
      </button>

      {/* Chat panel */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-50 flex w-[360px] flex-col rounded-2xl border border-slate-200 bg-white shadow-2xl dark:border-slate-700 dark:bg-slate-900">
          {/* Header */}
          <div className="flex items-center gap-3 border-b border-slate-200 px-4 py-3 dark:border-slate-700">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/10 text-blue-500">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-900 dark:text-white">
                AI Assistant
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Ask about your dashboard
              </p>
            </div>
          </div>

          {/* Messages */}
          <div className="max-h-80 space-y-3 overflow-y-auto p-4">
            {turns.length === 0 ? (
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Try &ldquo;How many open escalations?&rdquo; or &ldquo;What&apos;s
                the deflection rate?&rdquo;
              </p>
            ) : (
              turns.map((turn, index) => (
                <div
                  key={`${turn.role}-${index}`}
                  className={
                    turn.role === "user"
                      ? "ml-8 rounded-lg bg-blue-600 px-3 py-2 text-sm text-white"
                      : "mr-8 whitespace-pre-wrap rounded-lg bg-slate-100 px-3 py-2 text-sm text-slate-800 dark:bg-slate-800 dark:text-slate-100"
                  }
                >
                  {turn.content}
                </div>
              ))
            )}
            {sending && (
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <Loader2 className="h-4 w-4 animate-spin" />
                Thinking...
              </div>
            )}
          </div>

          {/* Error */}
          {error && (
            <p className="px-4 pb-2 text-xs text-red-500">{error}</p>
          )}

          {/* Input */}
          <form
            onSubmit={handleSubmit}
            className="flex gap-2 border-t border-slate-200 px-4 py-3 dark:border-slate-700"
          >
            <input
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Ask a question..."
              className="flex-1 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white"
            />
            <button
              type="submit"
              disabled={sending || !draft.trim()}
              className="inline-flex items-center rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      )}
    </>
  );
}
