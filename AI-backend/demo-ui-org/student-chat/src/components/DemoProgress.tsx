import clsx from "clsx";
import { Check } from "lucide-react";
import { LIFECYCLE_STEPS, type LifecycleState } from "@/shared/lifecycle";

interface Props {
  state: LifecycleState;
  variant?: "sidebar" | "strip";
}

export function DemoProgress({ state, variant = "sidebar" }: Props) {
  const done = LIFECYCLE_STEPS.filter((s) => state[s.id]).length;

  if (variant === "strip") {
    return (
      <div className="bg-white px-2 py-2">
        <div className="flex items-center justify-between gap-2 mb-1.5 px-1">
          <span className="text-[10px] font-semibold uppercase tracking-wide text-slate-600">
            Lifecycle
          </span>
          <span className="text-[10px] font-medium text-wa-header tabular-nums">
            {done}/{LIFECYCLE_STEPS.length}
          </span>
        </div>
        <ol className="flex gap-1.5 overflow-x-auto pb-0.5 snap-x snap-mandatory scrollbar-thin">
          {LIFECYCLE_STEPS.map((step, i) => {
            const ok = state[step.id];
            return (
              <li
                key={step.id}
                className={clsx(
                  "snap-start shrink-0 flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[10px] font-medium whitespace-nowrap",
                  ok
                    ? "border-wa-accent/40 bg-emerald-50 text-emerald-900"
                    : "border-slate-200 bg-slate-50 text-slate-600",
                )}
                title={step.hint}
              >
                <span
                  className={clsx(
                    "size-4 rounded-full flex items-center justify-center shrink-0 border text-[9px]",
                    ok
                      ? "bg-wa-accent border-wa-accent text-white"
                      : "bg-white border-slate-300 text-slate-400",
                  )}
                >
                  {ok ? <Check size={9} strokeWidth={3} /> : i + 1}
                </span>
                {step.label}
              </li>
            );
          })}
        </ol>
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-3 shadow-sm">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-xs font-semibold text-slate-800 uppercase tracking-wide">
          Lifecycle
        </h3>
        <span className="text-[11px] text-slate-500">
          {done}/{LIFECYCLE_STEPS.length}
        </span>
      </div>
      <ol className="space-y-1.5">
        {LIFECYCLE_STEPS.map((step, i) => {
          const ok = state[step.id];
          return (
            <li key={step.id} className="flex items-start gap-2 text-xs">
              <span
                className={clsx(
                  "mt-0.5 size-4 rounded-full flex items-center justify-center shrink-0 border",
                  ok
                    ? "bg-wa-accent border-wa-accent text-white"
                    : "bg-white border-slate-300 text-slate-400",
                )}
              >
                {ok ? <Check size={10} strokeWidth={3} /> : <span className="text-[9px]">{i + 1}</span>}
              </span>
              <span className="min-w-0">
                <span className={clsx("font-medium", ok ? "text-slate-800" : "text-slate-600")}>
                  {step.label}
                </span>
                <span className="block text-[10px] text-slate-400 truncate">{step.hint}</span>
              </span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
