"use client";

// src/components/Header.tsx
import { MoonIcon, SunIcon, Menu } from "lucide-react";
import { useState, useEffect } from "react";

interface HeaderProps {
  onMenuClick?: () => void;
}

/**
 * Header with dark mode toggle and responsive hamburger menu.
 * Theme preference is persisted in localStorage under "theme".
 */
export default function Header({ onMenuClick }: HeaderProps) {
  const [dark, setDark] = useState(false);

  // Initialize state from the current class on first client render
  useEffect(() => {
    const isDark = document.documentElement.classList.contains("dark");
    setDark(isDark);
  }, []);

  // Apply theme classes and persist when toggled
  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    document.body.classList.toggle("dark", dark);
    localStorage.setItem("theme", dark ? "dark" : "light");
  }, [dark]);


  return (
    <header className="flex items-center justify-between bg-gray-800 px-4 py-2 shadow-md">
      {onMenuClick && (
        <button
          className="lg:hidden p-2 rounded-md text-gray-300 hover:text-white"
          onClick={onMenuClick}
          aria-label="Open sidebar"
        >
          <Menu className="h-6 w-6" />
        </button>
      )}
      <h1 className="text-xl font-semibold text-white flex-1 text-center lg:text-left">
        Staff Dashboard
      </h1>
      <button
        onClick={() => setDark(!dark)}
        className="p-2 rounded-full hover:bg-gray-700 transition-colors"
        aria-label="Toggle dark mode"
      >
        <SunIcon className="h-5 w-5 text-yellow-400 dark:hidden" />
        <MoonIcon className="h-5 w-5 text-gray-200 hidden dark:inline-block" />
      </button>
    </header>
  );
}
