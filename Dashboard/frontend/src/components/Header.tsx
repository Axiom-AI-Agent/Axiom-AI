"use client";

import {
  Menu,
  MoonIcon,
  LogOut,
  SunIcon,
  User,
} from "lucide-react";

import {
  useRouter,
} from "next/navigation";

import {
  useAuth,
} from "@/context/AuthContext";


interface HeaderProps {
  onMenuClick?: () => void;
}


export default function Header({
  onMenuClick,
}: HeaderProps) {
  const router =
    useRouter();

  const {
    user,
    logout,
  } = useAuth();


  function toggleTheme() {
    const next = !document.documentElement.classList.contains("dark");

    document.documentElement.classList.toggle("dark", next);
    localStorage.setItem("theme", next ? "dark" : "light");
  }


  function handleLogout() {
    logout();

    router.replace(
      "/login",
    );
  }


  return (
    <header className="flex items-center justify-between gap-4 border-b border-slate-200 bg-white px-6 py-3 shadow-sm dark:border-slate-800 dark:bg-slate-900">

      {onMenuClick && (
        <button
          onClick={
            onMenuClick
          }
          className="rounded-md p-2 text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white lg:hidden"
          aria-label="Open sidebar"
          type="button"
        >
          <Menu className="h-6 w-6" />
        </button>
      )}


      <div className="min-w-0 flex-1">
        {user?.institution_name ? (
          <>
            <h1 className="truncate text-lg font-semibold tracking-tight text-slate-900 dark:text-white">
              {user.institution_name}
            </h1>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400">
              Staff Dashboard
            </p>
          </>
        ) : (
          <h1 className="text-lg font-semibold tracking-tight text-slate-900 dark:text-white">
            Staff Dashboard
          </h1>
        )}
      </div>


      <div className="flex items-center gap-3">

        {user && (
          <div className="hidden items-center gap-2 rounded-lg border border-slate-200 px-3 py-1.5 dark:border-slate-700 sm:flex">

            <User className="h-4 w-4 text-slate-500" />

            <div className="text-xs">

              <p className="font-medium text-slate-800 dark:text-slate-200">
                {user.name}
              </p>

              <p className="capitalize text-slate-500">
                {user.role}
              </p>

            </div>

          </div>
        )}


        <button
          onClick={toggleTheme}
          className="rounded-full p-2 hover:bg-slate-100 dark:hover:bg-slate-800"
          aria-label="Toggle dark mode"
          type="button"
        >
          <SunIcon className="h-5 w-5 text-slate-600 dark:hidden" />

          <MoonIcon className="hidden h-5 w-5 text-slate-300 dark:inline-block" />
        </button>


        <button
          onClick={
            handleLogout
          }
          className="rounded-full p-2 text-slate-500 hover:bg-red-500/10 hover:text-red-500"
          aria-label="Logout"
          title="Logout"
          type="button"
        >
          <LogOut className="h-5 w-5" />
        </button>

      </div>

    </header>
  );
}