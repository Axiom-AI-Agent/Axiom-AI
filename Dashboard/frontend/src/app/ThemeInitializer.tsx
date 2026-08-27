"use client";

import { useEffect } from "react";

/**
 * Reads the persisted theme from localStorage (or defaults to "dark")
 * and applies the appropriate class to the <html> element before the UI renders.
 */
export default function ThemeInitializer() {
  useEffect(() => {
    const stored = typeof window !== "undefined" ? localStorage.getItem("theme") : null;
    const isDark = stored ? stored === "dark" : true; // default to dark if no preference
    document.documentElement.classList.toggle("dark", isDark);
  }, []);
  return null;
}
