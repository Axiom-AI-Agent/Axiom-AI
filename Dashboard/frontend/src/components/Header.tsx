"use client";

import { LogOut, Menu, MoonIcon, SunIcon, User } from "lucide-react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";

import { useAuth } from "@/context/AuthContext";
import { useTheme } from "@/context/ThemeContext";

interface HeaderProps {
  onMenuClick?: () => void;
}

export default function Header({ onMenuClick }: HeaderProps) {
  const router = useRouter();
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  function handleLogout() {
    logout();
    router.replace("/login");
  }

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between gap-4 border-b border-border/70 bg-surface/75 px-5 py-3.5 shadow-[0_8px_24px_rgba(10,18,32,0.04)] backdrop-blur-xl supports-[backdrop-filter]:bg-surface/65 dark:shadow-[0_10px_28px_rgba(0,0,0,0.28)]">
      {onMenuClick ? (
        <button
          onClick={onMenuClick}
          className="rounded-xl p-2 text-muted transition-colors hover:bg-hover hover:text-fg lg:hidden"
          aria-label="Open sidebar"
          type="button"
        >
          <Menu className="h-6 w-6" />
        </button>
      ) : null}

      <div className="min-w-0 flex-1">
        <h1 className="font-display text-lg font-semibold tracking-tight text-heading">
          Staff Dashboard
        </h1>
        {user ? (
          <p className="hidden truncate text-sm text-muted sm:block">
            {user.institution_name}
          </p>
        ) : null}
      </div>

      <div className="flex items-center gap-2 sm:gap-3">
        {user ? (
          <div className="hidden items-center gap-2.5 rounded-2xl border border-border bg-bg/80 px-3 py-1.5 shadow-sm sm:flex">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-blue/12 text-blue">
              <User className="h-4 w-4" />
            </div>
            <div className="text-xs">
              <p className="font-medium text-fg">{user.name}</p>
              <p className="capitalize text-muted">{user.role}</p>
            </div>
          </div>
        ) : null}

        <motion.button
          type="button"
          onClick={toggleTheme}
          whileTap={{ scale: 0.97 }}
          className="rounded-xl border border-border bg-surface p-2.5 text-muted shadow-sm transition-colors hover:border-blue/30 hover:bg-hover hover:text-fg"
          aria-label="Toggle dark mode"
        >
          {theme === "dark" ? (
            <SunIcon className="h-5 w-5" />
          ) : (
            <MoonIcon className="h-5 w-5" />
          )}
        </motion.button>

        <motion.button
          type="button"
          onClick={handleLogout}
          whileTap={{ scale: 0.97 }}
          className="rounded-xl border border-border bg-surface p-2.5 text-muted shadow-sm transition-colors hover:border-blue/30 hover:bg-hover hover:text-fg"
          aria-label="Logout"
          title="Logout"
        >
          <LogOut className="h-5 w-5" />
        </motion.button>
      </div>
    </header>
  );
}
