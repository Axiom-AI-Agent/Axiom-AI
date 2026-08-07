import { MoreVertical, Phone, Wifi, WifiOff } from "lucide-react";
import clsx from "clsx";
import { TENANT_NAME, TENANT_SHORT } from "@/shared/constants";
import type { ReactNode } from "react";

interface Props {
  phone: string;
  backendOk: boolean | null;
  children: ReactNode;
  footer?: ReactNode;
  /** Full viewport width/height on mobile (no phone-frame chrome). */
  fullBleedMobile?: boolean;
}

export function WhatsAppShell({
  phone,
  backendOk,
  children,
  footer,
  fullBleedMobile = false,
}: Props) {
  return (
    <div
      className={clsx(
        "flex flex-col h-full min-h-0 bg-white overflow-hidden w-full mx-auto",
        fullBleedMobile
          ? "max-w-none rounded-none border-0 shadow-none lg:max-w-[420px] lg:rounded-xl lg:border lg:border-slate-200 lg:shadow-sm"
          : "max-w-[420px] rounded-xl border border-slate-200 shadow-sm",
      )}
    >
      <header className="bg-wa-header text-white px-3 py-2.5 flex items-center gap-3 shrink-0">
        <div className="size-10 rounded-full bg-white/15 flex items-center justify-center text-sm font-bold tracking-wide">
          {TENANT_SHORT}
        </div>
        <div className="flex-1 min-w-0">
          <div className="font-semibold text-[15px] truncate">{TENANT_NAME}</div>
          <div className="text-[11px] text-white/80 flex items-center gap-1.5">
            <span>online</span>
            <span className="text-white/40">·</span>
            <span className="truncate font-mono">{phone}</span>
          </div>
        </div>
        <div className="flex items-center gap-2 text-white/90">
          {backendOk === false ? (
            <WifiOff size={16} className="text-amber-300" aria-label="API unreachable" />
          ) : (
            <Wifi
              size={16}
              className={clsx(backendOk ? "text-emerald-300" : "text-white/50")}
              aria-label={backendOk ? "API ok" : "Checking API"}
            />
          )}
          <Phone size={16} className="opacity-70" />
          <MoreVertical size={16} className="opacity-70" />
        </div>
      </header>
      <div className="flex-1 min-h-0 flex flex-col">{children}</div>
      {footer && <div className="shrink-0 safe-bottom">{footer}</div>}
    </div>
  );
}
