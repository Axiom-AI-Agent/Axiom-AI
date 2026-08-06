"use client";

import { MoonIcon, SunIcon, Menu } from "lucide-react";
import { useState, useEffect } from "react";

import TenantSelector from "@/components/TenantSelector";

interface HeaderProps {
  onMenuClick?: () => void;
}

export default function Header({ onMenuClick }: HeaderProps) {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const isDark = document.documentElement.classList.contains("dark");
    setDark(isDark);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    document.body.classList.toggle("dark", dark);
    localStorage.setItem("theme", dark ? "dark" : "light");
  }, [dark]);

  return (
    <header className="flex items-center justify-between gap-4 bg-white dark:bg-slate-900 px-6 py-3 shadow-sm border-b border-slate-200 dark:border-slate-800">
      {onMenuClick && (
        <button
          className="lg:hidden p-2 rounded-md text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
          onClick={onMenuClick}
          aria-label="Open sidebar"
          type="button"
        >
          <Menu className="h-6 w-6" />
        </button>
      )}

      <h1 className="text-xl font-semibold text-slate-900 dark:text-white flex-1 text-center lg:text-left">
        Staff Dashboard
      </h1>

      <div className="flex items-center gap-3">
        <TenantSelector />

        <button
          onClick={() => setDark(!dark)}
          className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          aria-label="Toggle dark mode"
          type="button"
        >
          <SunIcon className="h-5 w-5 text-slate-600 dark:hidden" />
          <MoonIcon className="h-5 w-5 text-slate-300 hidden dark:inline-block" />
        </button>
      </div>
    </header>
  );
}
