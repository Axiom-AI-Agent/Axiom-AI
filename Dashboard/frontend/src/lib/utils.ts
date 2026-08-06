// src/lib/utils.ts
/**
 * Simple classNames (cn) utility – joins truthy strings.
 */
export function cn(...classes: (string | undefined | null | false)[]) {
  return classes.filter(Boolean).join(' ');
}
