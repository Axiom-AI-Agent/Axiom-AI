"use client";

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
  icon: React.ReactNode;
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

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 min-h-screen flex flex-col p-4 border-r border-slate-200 dark:border-slate-800",
        "fixed lg:relative inset-y-0 left-0 w-64 transform transition-transform duration-300 ease-in-out z-50",
        isOpen ? "translate-x-0" : "-translate-x-full",
        "lg:translate-x-0 lg:flex",
      )}
    >
      <button
        className="absolute top-4 right-4 lg:hidden text-slate-400 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
        onClick={onClose}
        aria-label="Close sidebar"
        type="button"
      >
        <X className="h-6 w-6" />
      </button>

      <div className="flex items-center gap-3 mb-6 px-2">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/logo.png" alt="Axiom AI Logo" className="h-8 w-auto" />
        <h2 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">Axiom AI</h2>
      </div>

      <nav className="flex-1 space-y-2">
        {mainNavItems.map((item) => {
          const active = pathname?.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onClose}
              className={cn(
                "flex items-center space-x-3 rounded-lg px-3 py-2 transition-all duration-200 ease-in-out",
                active 
                  ? "bg-blue-50 dark:bg-blue-500/10 text-blue-700 dark:text-blue-400 font-medium" 
                  : "hover:bg-slate-50 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white",
              )}
            >
              {item.icon}
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <nav className="mt-auto border-t border-slate-200 dark:border-slate-800 pt-4">
        <Link
          href={settingsNavItem.href}
          onClick={onClose}
          className={cn(
            "flex items-center space-x-3 rounded-lg px-3 py-2 transition-all duration-200 ease-in-out",
            pathname?.startsWith(settingsNavItem.href)
              ? "bg-blue-50 dark:bg-blue-500/10 text-blue-700 dark:text-blue-400 font-medium"
              : "hover:bg-slate-50 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white",
          )}
        >
          {settingsNavItem.icon}
          <span>{settingsNavItem.label}</span>
        </Link>
      </nav>
    </aside>
  );
}
