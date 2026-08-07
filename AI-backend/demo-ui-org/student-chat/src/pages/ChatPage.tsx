import { useEffect, useState } from "react";
import { ChatWindow } from "@/components/ChatWindow";
import { DemoProgress } from "@/components/DemoProgress";
import { InputBox } from "@/components/InputBox";
import { QuickActions } from "@/components/QuickActions";
import { WhatsAppShell } from "@/components/WhatsAppShell";
import { useChat } from "@/hooks/useChat";
import type { DemoSession } from "@/types";
import { PAYMENT_SLIP_PATH } from "@/shared/constants";
import {
  detectLifecycleProgress,
  emptyLifecycle,
  type LifecycleState,
} from "@/shared/lifecycle";

interface Props {
  session: DemoSession;
  lifecycle: LifecycleState;
  onLifecycle: (next: LifecycleState) => void;
  onUseEnrolledStudent: (message?: string) => void;
  autoSendText?: string | null;
  onAutoSendConsumed?: () => void;
}

function paymentSlipUrl(): string {
  return `${window.location.origin}${PAYMENT_SLIP_PATH}`;
}

export function ChatPage({
  session,
  lifecycle,
  onLifecycle,
  onUseEnrolledStudent,
  autoSendText,
  onAutoSendConsumed,
}: Props) {
  const chat = useChat(session);
  const [draft, setDraft] = useState("");

  useEffect(() => {
    if (!autoSendText) return;
    void (async () => {
      const result = await chat.send(autoSendText);
      onAutoSendConsumed?.();
      if (!result) return;
      onLifecycle(
        detectLifecycleProgress(lifecycle, {
          studentText: result.studentText,
          botText: result.botText,
          sentMedia: Boolean(result.mediaUrl),
        }),
      );
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- one-shot auto-send after enrolled switch
  }, [autoSendText]);

  const afterSend = (
    result: { studentText: string; botText: string; mediaUrl?: string | null } | null,
  ) => {
    if (!result) return;
    onLifecycle(
      detectLifecycleProgress(lifecycle, {
        studentText: result.studentText,
        botText: result.botText,
        sentMedia: Boolean(result.mediaUrl),
      }),
    );
  };

  const sendText = async (text: string) => {
    const result = await chat.send(text);
    afterSend(result);
  };

  const attachSlip = async () => {
    const result = await chat.send(
      "Please find my payment slip attached.",
      paymentSlipUrl(),
    );
    afterSend(result);
  };

  return (
    <div className="grid lg:grid-cols-[minmax(0,1fr)_220px] gap-4 h-full min-h-0">
      <WhatsAppShell
        phone={session.phone}
        backendOk={chat.backendOk}
        fullBleedMobile
        footer={
          <>
            <QuickActions
              disabled={chat.loading}
              currentPhone={session.phone}
              onPick={setDraft}
              onAttachSlip={() => void attachSlip()}
              onUseEnrolledStudent={onUseEnrolledStudent}
            />
            <InputBox
              disabled={chat.loading}
              draft={draft}
              onDraftChange={setDraft}
              onSend={(t) => void sendText(t)}
              onAttachSlip={() => void attachSlip()}
            />
          </>
        }
      >
        <ChatWindow
          messages={chat.messages}
          loading={chat.loading}
          loadingHistory={chat.loadingHistory}
          error={chat.error}
        />
      </WhatsAppShell>
      <div className="hidden lg:block min-h-0">
        <DemoProgress state={lifecycle} variant="sidebar" />
      </div>
    </div>
  );
}

export { emptyLifecycle };
