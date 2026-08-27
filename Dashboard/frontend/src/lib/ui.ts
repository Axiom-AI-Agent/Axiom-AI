export const pageTitle =
  "font-display text-2xl font-semibold tracking-tight text-heading";

export const pageSubtitle = "mt-1.5 max-w-2xl text-sm leading-relaxed text-muted";

/** Keeps page title/actions clear of content cards below. */
export const pageHeader =
  "mb-6 flex shrink-0 flex-wrap items-start justify-between gap-4";

export const pageToolbar =
  "flex shrink-0 flex-wrap items-center justify-end gap-2.5";

export const surfaceCard =
  "rounded-xl border border-border bg-surface shadow-[var(--shadow-card)]";

export const btnPrimary =
  "inline-flex items-center justify-center gap-2 rounded-lg bg-blue px-4 py-2 text-sm font-medium text-paper shadow-sm transition-all hover:bg-blue/90 hover:shadow-md disabled:cursor-not-allowed disabled:opacity-50";

export const btnQuiet =
  "inline-flex shrink-0 items-center justify-center gap-2 rounded-lg border border-border bg-surface px-3.5 py-2 text-sm font-medium text-fg shadow-sm transition-colors hover:bg-hover hover:border-blue/25 disabled:cursor-not-allowed disabled:opacity-50";

export const btnGhost =
  "inline-flex items-center justify-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-muted transition-colors hover:bg-hover hover:text-fg disabled:opacity-50";

export const btnDanger =
  "inline-flex items-center justify-center gap-2 rounded-lg border border-border bg-surface px-3 py-1.5 text-sm font-medium text-fg transition-colors hover:bg-hover disabled:cursor-not-allowed disabled:opacity-50";

export const inputClass =
  "w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-fg outline-none transition-colors placeholder:text-muted focus:border-blue/55 focus:ring-2 focus:ring-[var(--ring)]";

/** Compact control for page toolbars — never stretches full width. */
export const toolbarSelect =
  "h-10 w-auto min-w-[11.5rem] shrink-0 rounded-lg border border-border bg-surface px-3 text-sm text-fg outline-none transition-colors focus:border-blue/55 focus:ring-2 focus:ring-[var(--ring)]";

export const selectClass = inputClass;

export const errorBanner =
  "flex items-start gap-2 rounded-xl border border-border bg-surface p-4 text-sm text-fg shadow-[var(--shadow-card)]";

export const emptyState =
  "rounded-xl border border-dashed border-border bg-surface/70 p-10 text-center text-muted";
