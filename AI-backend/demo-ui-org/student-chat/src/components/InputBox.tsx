import { useRef, useState, type KeyboardEvent } from "react";
import { Paperclip, SendHorizontal } from "lucide-react";
import clsx from "clsx";

interface Props {
  disabled?: boolean;
  onSend: (text: string) => void;
  onAttachSlip?: () => void;
  placeholder?: string;
  draft?: string;
  onDraftChange?: (text: string) => void;
}

export function InputBox({
  disabled,
  onSend,
  onAttachSlip,
  placeholder,
  draft,
  onDraftChange,
}: Props) {
  const [local, setLocal] = useState("");
  const text = draft !== undefined ? draft : local;
  const setText = onDraftChange ?? setLocal;
  const ta = useRef<HTMLTextAreaElement>(null);

  const submit = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText("");
    ta.current?.focus();
  };

  const onKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  return (
    <div className="bg-wa-input px-2 py-2 flex items-end gap-1.5">
      {onAttachSlip && (
        <button
          type="button"
          className="shrink-0 size-10 rounded-full flex items-center justify-center text-slate-600 hover:bg-black/5 disabled:opacity-50"
          onClick={onAttachSlip}
          disabled={disabled}
          title="Attach sample payment slip"
        >
          <Paperclip size={20} />
        </button>
      )}
      <div className="flex-1 bg-white rounded-2xl border border-slate-200 px-3 py-1.5 flex items-end">
        <textarea
          ref={ta}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={onKey}
          disabled={disabled}
          rows={1}
          placeholder={placeholder || "Type a message"}
          className="flex-1 resize-none bg-transparent outline-none text-sm text-slate-800 placeholder-slate-400 py-1.5 min-h-[36px] max-h-[120px]"
          style={{ fieldSizing: "content" } as React.CSSProperties}
        />
      </div>
      <button
        type="button"
        onClick={submit}
        disabled={disabled || !text.trim()}
        title="Send"
        className={clsx(
          "shrink-0 size-10 rounded-full flex items-center justify-center text-white transition-colors",
          disabled || !text.trim()
            ? "bg-slate-300 cursor-not-allowed"
            : "bg-wa-header hover:bg-wa-headerDark",
        )}
      >
        <SendHorizontal size={18} />
      </button>
    </div>
  );
}
