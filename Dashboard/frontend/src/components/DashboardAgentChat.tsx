"use client";

import { FormEvent, useState } from "react";
import { Loader2, Send, Sparkles } from "lucide-react";

import { queryDashboardAgent } from "@/lib/api";
import { useTenant } from "@/context/TenantContext";

interface ChatTurn {
  role: "user" | "assistant";
  content: string;
}

export default function DashboardAgentChat() {
  const { tenantId } = useTenant();
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
      setError("Could not reach the dashboard agent. Confirm the AI backend is running.");
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <div className="mb-4 flex items-start gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400">
          <Sparkles className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
            Ask the dashboard
          </h2>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Query this institute&apos;s metrics in plain language. The same
            assistant is available on Telegram after you link your account in
            Settings.
          </p>
        </div>
      </div>

      <div className="mb-4 max-h-72 space-y-3 overflow-y-auto rounded-lg bg-slate-50 p-3 dark:bg-slate-950/60">
        {turns.length === 0 ? (
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Try &ldquo;How many open escalations?&rdquo; or &ldquo;What&apos;s
            this week&apos;s deflection rate?&rdquo;
          </p>
        ) : (
          turns.map((turn, index) => (
            <div
              key={`${turn.role}-${index}`}
              className={
                turn.role === "user"
                  ? "ml-8 rounded-lg bg-blue-600 px-3 py-2 text-sm text-white"
                  : "mr-8 whitespace-pre-wrap rounded-lg bg-white px-3 py-2 text-sm text-slate-800 dark:bg-slate-800 dark:text-slate-100"
              }
            >
              {turn.content}
            </div>
          ))
        )}
        {sending ? (
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Loader2 className="h-4 w-4 animate-spin" />
            Looking up your dashboard…
          </div>
        ) : null}
      </div>

      {error ? (
        <p className="mb-3 text-sm text-red-400">{error}</p>
      ) : null}

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Ask about escalations, deflection, classes…"
          className="flex-1 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white"
        />
        <button
          type="submit"
          disabled={sending || !draft.trim()}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50"
        >
          <Send className="h-4 w-4" />
          Ask
        </button>
      </form>
    </div>
  );
}
