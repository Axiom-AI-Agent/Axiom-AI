"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import {
  BookOpen,
  FileUp,
  Inbox,
  LayoutDashboard,
  MessageSquare,
  ScrollText,
  Settings,
  Users,
  X,
} from "lucide-react";

import { cn } from "@/lib/utils";

interface NavItem {
  href: string;
  label: string;
  icon: ReactNode;
}

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const mainNavItems: NavItem[] = [
  {
    href: "/dashboard/overview",
    label: "Overview",
    icon: <LayoutDashboard className="h-5 w-5" />,
  },
  {
    href: "/dashboard/inbox",
    label: "Inbox",
    icon: <Inbox className="h-5 w-5" />,
  },
  {
    href: "/dashboard/messages",
    label: "Messages",
    icon: <MessageSquare className="h-5 w-5" />,
  },
  {
    href: "/dashboard/classes",
    label: "Classes",
    icon: <BookOpen className="h-5 w-5" />,
  },
  {
    href: "/dashboard/students",
    label: "Students",
    icon: <Users className="h-5 w-5" />,
  },
  {
    href: "/dashboard/logs",
    label: "Logs",
    icon: <ScrollText className="h-5 w-5" />,
  },
  {
    href: "/dashboard/ingest",
    label: "Ingest",
    icon: <FileUp className="h-5 w-5" />,
  },
];

const settingsNavItem: NavItem = {
  href: "/dashboard/settings",
  label: "Settings",
  icon: <Settings className="h-5 w-5" />,
};

export default function Sidebar({
  isOpen,
  onClose,
}: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-50 flex min-h-screen w-64 flex-col border-r border-slate-200 bg-white p-4 text-slate-700 transition-transform duration-300 ease-in-out dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 lg:relative",
        isOpen ? "translate-x-0" : "-translate-x-full",
        "lg:flex lg:translate-x-0",
      )}
    >
      <div className="mb-6 flex items-center justify-between px-2 lg:justify-start">
        <div className="flex items-center gap-3">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/logo.png"
            alt="Axiom AI Logo"
            className="h-8 w-auto"
          />

          <h2 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">
            Axiom AI
          </h2>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-900 dark:hover:bg-slate-800 dark:hover:text-white lg:hidden"
          aria-label="Close sidebar"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <nav className="flex-1 space-y-2">
        {mainNavItems.map((item) => {
          const active =
            pathname === item.href ||
            pathname?.startsWith(`${item.href}/`);

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onClose}
              className={cn(
                "flex items-center space-x-3 rounded-lg px-3 py-2 transition-all duration-200 ease-in-out",
                active
                  ? "bg-blue-50 font-medium text-blue-700 dark:bg-blue-500/10 dark:text-blue-400"
                  : "hover:bg-slate-50 hover:text-slate-900 dark:hover:bg-slate-800/50 dark:hover:text-white",
              )}
            >
              {item.icon}
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <nav className="mt-auto border-t border-slate-200 pt-4 dark:border-slate-800">
        <Link
          href={settingsNavItem.href}
          onClick={onClose}
          className={cn(
            "flex items-center space-x-3 rounded-lg px-3 py-2 transition-all duration-200 ease-in-out",
            pathname === settingsNavItem.href ||
              pathname?.startsWith(`${settingsNavItem.href}/`)
              ? "bg-blue-50 font-medium text-blue-700 dark:bg-blue-500/10 dark:text-blue-400"
              : "hover:bg-slate-50 hover:text-slate-900 dark:hover:bg-slate-800/50 dark:hover:text-white",
          )}
        >
          {settingsNavItem.icon}
          <span>{settingsNavItem.label}</span>
        </Link>
      </nav>
    </aside>
  );
}