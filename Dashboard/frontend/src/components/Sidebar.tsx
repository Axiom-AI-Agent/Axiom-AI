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
        "bg-gradient-to-b from-gray-800 to-gray-900 text-gray-100 min-h-screen flex flex-col p-4",
        "fixed lg:relative inset-y-0 left-0 w-64 transform transition-transform duration-300 ease-in-out z-50",
        isOpen ? "translate-x-0" : "-translate-x-full",
        "lg:translate-x-0 lg:flex",
      )}
    >
      <button
        className="absolute top-4 right-4 lg:hidden text-gray-300 hover:text-white"
        onClick={onClose}
        aria-label="Close sidebar"
        type="button"
      >
        <X className="h-6 w-6" />
      </button>

      <h2 className="text-xl font-semibold mb-6">Axiom AI</h2>

      <nav className="flex-1 space-y-2">
        {mainNavItems.map((item) => {
          const active = pathname?.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onClose}
              className={cn(
                "flex items-center space-x-3 rounded-md p-2 hover:bg-gray-700 transition-colors",
                active && "bg-gray-700 font-medium",
              )}
            >
              {item.icon}
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <nav className="mt-auto border-t border-gray-700 pt-4">
        <Link
          href={settingsNavItem.href}
          onClick={onClose}
          className={cn(
            "flex items-center space-x-3 rounded-md p-2 hover:bg-gray-700 transition-colors",
            pathname?.startsWith(settingsNavItem.href) &&
              "bg-gray-700 font-medium",
          )}
        >
          {settingsNavItem.icon}
          <span>{settingsNavItem.label}</span>
        </Link>
      </nav>
    </aside>
  );
}
