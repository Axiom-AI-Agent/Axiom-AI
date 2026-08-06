import { useCallback, useState } from "react";
import { RotateCcw } from "lucide-react";
import { ChatPage, emptyLifecycle } from "@/pages/ChatPage";
import { useDemoSession } from "@/hooks/useDemoSession";
import { TENANT_NAME } from "@shared/constants";
import type { LifecycleState } from "@shared/lifecycle";

export default function App() {
  const { session, resetDemo, useEnrolledStudent } = useDemoSession();
  const [lifecycle, setLifecycle] = useState<LifecycleState>(emptyLifecycle());
  const [resetKey, setResetKey] = useState(0);
  const [autoSendText, setAutoSendText] = useState<string | null>(null);

  const handleReset = useCallback(() => {
    resetDemo();
    setLifecycle(emptyLifecycle());
    setAutoSendText(null);
    setResetKey((k) => k + 1);
  }, [resetDemo]);

  const handleUseEnrolledStudent = useCallback(
    (message?: string) => {
      useEnrolledStudent();
      setLifecycle(emptyLifecycle());
      setAutoSendText(message ?? null);
      setResetKey((k) => k + 1);
    },
    [useEnrolledStudent],
  );

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white border-b border-slate-200 px-4 py-3 flex items-center justify-between gap-4 shrink-0">
        <div>
          <h1 className="text-sm font-semibold text-slate-900">{TENANT_NAME}</h1>
          <p className="text-xs text-slate-500">Student portal — WhatsApp chat demo</p>
        </div>
        <button
          type="button"
          onClick={handleReset}
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
        >
          <RotateCcw size={14} />
          Reset demo
        </button>
      </header>

      <main className="flex-1 p-4 max-w-5xl mx-auto w-full min-h-0">
        <div className="h-[calc(100vh-88px)] min-h-[520px]">
          <ChatPage
            key={`${session.phone}-${resetKey}`}
            session={session}
            lifecycle={lifecycle}
            onLifecycle={setLifecycle}
            autoSendText={autoSendText}
            onAutoSendConsumed={() => setAutoSendText(null)}
            onUseEnrolledStudent={handleUseEnrolledStudent}
          />
        </div>
      </main>
    </div>
  );
}
