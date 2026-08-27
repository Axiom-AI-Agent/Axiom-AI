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
    <header className="flex items-center justify-between gap-4 border-b border-border bg-surface/90 px-6 py-3 backdrop-blur-sm">
      {onMenuClick ? (
        <button
          onClick={onMenuClick}
          className="rounded-lg p-2 text-muted transition-colors hover:bg-hover hover:text-fg lg:hidden"
          aria-label="Open sidebar"
          type="button"
        >
          <Menu className="h-6 w-6" />
        </button>
      ) : null}

      <div className="flex-1">
        <h1 className="font-display text-lg font-medium tracking-tight text-heading">
          Staff Dashboard
        </h1>
        {user ? (
          <p className="hidden text-sm text-muted sm:block">
            {user.institution_name}
          </p>
        ) : null}
      </div>

      <div className="flex items-center gap-3">
        {user ? (
          <div className="hidden items-center gap-2 rounded-lg border border-border bg-bg/60 px-3 py-1.5 sm:flex">
            <User className="h-4 w-4 text-muted" />
            <div className="text-xs">
              <p className="font-medium text-fg">{user.name}</p>
              <p className="capitalize text-muted">{user.role}</p>
            </div>
          </div>
        ) : null}

        <motion.button
          type="button"
          onClick={toggleTheme}
          whileTap={{ scale: 0.98 }}
          className="rounded-lg p-2 text-muted transition-colors hover:bg-hover hover:text-fg"
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
          whileTap={{ scale: 0.98 }}
          className="rounded-lg p-2 text-muted transition-colors hover:bg-hover hover:text-fg"
          aria-label="Logout"
          title="Logout"
        >
          <LogOut className="h-5 w-5" />
        </motion.button>
      </div>
    </header>
  );
}
