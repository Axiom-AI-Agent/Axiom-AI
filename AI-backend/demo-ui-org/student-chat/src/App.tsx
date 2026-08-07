import { useCallback, useState } from "react";
import { RotateCcw } from "lucide-react";
import { ChatPage, emptyLifecycle } from "@/pages/ChatPage";
import { DemoProgress } from "@/components/DemoProgress";
import { useDemoSession } from "@/hooks/useDemoSession";
import { TENANT_NAME } from "@/shared/constants";
import type { LifecycleState } from "@/shared/lifecycle";

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
    <div className="h-dvh flex flex-col overflow-hidden bg-slate-100 lg:bg-[#e8edf2]">
      <header className="bg-white border-b border-slate-200 px-3 py-2.5 sm:px-4 flex items-center justify-between gap-3 shrink-0 safe-top">
        <div className="min-w-0">
          <h1 className="text-sm sm:text-base font-semibold text-slate-900 truncate">{TENANT_NAME}</h1>
          <p className="text-[11px] sm:text-xs text-slate-500 truncate">
            Student portal — WhatsApp demo
          </p>
        </div>
        <button
          type="button"
          onClick={handleReset}
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 sm:px-3 text-xs font-medium text-slate-700 hover:bg-slate-50 shrink-0"
          aria-label="Reset demo"
        >
          <RotateCcw size={14} />
          <span className="hidden sm:inline">Reset demo</span>
        </button>
      </header>

      <div className="lg:hidden shrink-0 border-b border-slate-200 bg-white shadow-sm">
        <DemoProgress state={lifecycle} variant="strip" />
      </div>

      <main className="flex-1 min-h-0 flex flex-col lg:p-4 lg:max-w-5xl lg:mx-auto lg:w-full">
        <div className="flex-1 min-h-0 lg:h-[calc(100dvh-88px)] lg:min-h-[520px]">
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
