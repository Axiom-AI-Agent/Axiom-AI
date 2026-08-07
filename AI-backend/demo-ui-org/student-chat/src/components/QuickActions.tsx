import { ImageIcon } from "lucide-react";
import { QUICK_ACTIONS, ENROLLED_DEMO_PHONE } from "@/shared/constants";

interface Props {
  disabled?: boolean;
  onPick: (text: string) => void;
  onAttachSlip: () => void;
  onUseEnrolledStudent: (message?: string) => void;
  currentPhone: string;
}

export function QuickActions({
  disabled,
  onPick,
  onAttachSlip,
  onUseEnrolledStudent,
  currentPhone,
}: Props) {
  const handleAction = (id: string, text: string) => {
    if (id === "enrolled") {
      if (currentPhone !== ENROLLED_DEMO_PHONE) {
        onUseEnrolledStudent(text);
        return;
      }
      onPick(text);
      return;
    }
    onPick(text);
  };

  return (
    <div className="px-2 py-1.5 bg-wa-input/80 border-t border-slate-200/80 flex gap-1.5 overflow-x-auto shrink-0 scrollbar-thin touch-pan-x">
      <button
        type="button"
        disabled={disabled}
        onClick={onAttachSlip}
        className="shrink-0 inline-flex items-center gap-1 rounded-full bg-white border border-slate-200 px-2.5 py-1.5 text-[11px] text-slate-700 hover:bg-slate-50 disabled:opacity-50 min-h-[32px]"
      >
        <ImageIcon size={12} />
        Payment slip
      </button>
      {QUICK_ACTIONS.map((a) => (
        <button
          key={a.id}
          type="button"
          disabled={disabled}
          onClick={() => handleAction(a.id, a.text)}
          className="shrink-0 rounded-full bg-white border border-slate-200 px-2.5 py-1.5 text-[11px] text-slate-700 hover:bg-slate-50 disabled:opacity-50 whitespace-nowrap min-h-[32px]"
        >
          {a.label}
        </button>
      ))}
    </div>
  );
}
