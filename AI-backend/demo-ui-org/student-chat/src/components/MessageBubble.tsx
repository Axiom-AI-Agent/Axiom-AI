import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { motion } from "framer-motion";
import clsx from "clsx";
import type { UIMessage } from "@/types";

interface Props {
  message: UIMessage;
}

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
}

export function MessageBubble({ message }: Props) {
  const isStudent = message.sender === "student";
  const isStaff = message.sender === "staff";

  return (
    <motion.div
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.15 }}
      className={clsx("flex w-full", isStudent ? "justify-end" : "justify-start")}
    >
      <div
        className={clsx(
          "relative max-w-[85%] rounded-lg px-2.5 py-1.5 shadow-bubble text-[13.5px] leading-snug",
          isStudent && "bg-wa-user text-slate-900 rounded-tr-none",
          !isStudent && !isStaff && "bg-wa-bot text-slate-900 rounded-tl-none",
          isStaff && "bg-amber-50 border border-amber-200 text-slate-900 rounded-tl-none",
          message.error && "opacity-70 ring-1 ring-red-400",
          message.pending && "opacity-80",
        )}
      >
        {isStaff && (
          <div className="text-[11px] font-semibold text-amber-700 mb-0.5">Staff</div>
        )}
        {message.mediaUrl && (
          <a
            href={message.mediaUrl}
            target="_blank"
            rel="noreferrer"
            className="block mb-1 rounded overflow-hidden border border-black/5"
          >
            <img
              src={message.mediaUrl}
              alt="Attached media"
              className="max-h-40 w-auto object-contain bg-white"
            />
          </a>
        )}
        {isStudent ? (
          <p className="m-0 whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="prose-wa prose-sm max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content || "…"}
            </ReactMarkdown>
          </div>
        )}
        <div
          className={clsx(
            "mt-0.5 flex items-center justify-end gap-1 text-[10px]",
            "text-slate-500",
          )}
        >
          <span>{formatTime(message.createdAt)}</span>
          {message.pending && <span>· sending</span>}
          {message.error && <span className="text-red-500">· failed</span>}
        </div>
      </div>
    </motion.div>
  );
}
