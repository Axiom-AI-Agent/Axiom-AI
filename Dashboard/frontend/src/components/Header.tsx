"use client";

import {
  Menu,
  MoonIcon,
  LogOut,
  SunIcon,
  User,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

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

  const [
    dark,
    setDark,
  ] = useState(false);


  useEffect(() => {
    const isDark =
      document
        .documentElement
        .classList
        .contains(
          "dark",
        );

    setDark(
      isDark,
    );
  }, []);


  useEffect(() => {
    document
      .documentElement
      .classList
      .toggle(
        "dark",
        dark,
      );

    document
      .body
      .classList
      .toggle(
        "dark",
        dark,
      );

    localStorage.setItem(
      "theme",
      dark
        ? "dark"
        : "light",
    );
  }, [
    dark,
  ]);


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


      <div className="flex-1">

        <h1 className="text-xl font-semibold text-slate-900 dark:text-white">
          Staff Dashboard
        </h1>

        {user && (
          <p className="hidden text-xs text-slate-500 sm:block">
            {user.institution_name}
          </p>
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
          onClick={() =>
            setDark(
              !dark,
            )
          }
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