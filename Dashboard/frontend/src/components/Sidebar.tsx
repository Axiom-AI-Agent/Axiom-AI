"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  BookOpen,
  Calendar,
  FileUp,
  HelpCircle,
  Inbox,
  LayoutDashboard,
  MessageSquare,
  School,
  ScrollText,
  Settings,
  UserCog,
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
    href: "/dashboard/analytics",
    label: "Analytics",
    icon: <BarChart3 className="h-5 w-5" />,
  },
  {
    href: "/dashboard/analytics/classes",
    label: "Class Analytics",
    icon: <School className="h-5 w-5" />,
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
    href: "/dashboard/schedules",
    label: "Schedules",
    icon: <Calendar className="h-5 w-5" />,
  },
  {
    href: "/dashboard/students",
    label: "Students",
    icon: <Users className="h-5 w-5" />,
  },
  {
    href: "/dashboard/staff",
    label: "Staff",
    icon: <UserCog className="h-5 w-5" />,
  },
  {
    href: "/dashboard/faqs",
    label: "FAQ Intelligence",
    icon: <HelpCircle className="h-5 w-5" />,
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

function NavLink({
  item,
  active,
  onClose,
}: {
  item: NavItem;
  active: boolean;
  onClose: () => void;
}) {
  return (
    <Link
      href={item.href}
      onClick={onClose}
      className={cn(
        "flex items-center space-x-3 rounded-lg px-3 py-2 text-sm transition-colors",
        active
          ? "bg-blue/20 font-medium text-paper shadow-[inset_2px_0_0_0_var(--blue)]"
          : "text-paper/70 hover:bg-white/10 hover:text-paper",
      )}
    >
      {item.icon}
      <span>{item.label}</span>
    </Link>
  );
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-50 flex min-h-screen w-64 flex-col border-r border-white/10 bg-[linear-gradient(180deg,#152238_0%,#1a2744_55%,#152033_100%)] p-4 text-paper transition-transform duration-300 ease-in-out lg:relative",
        isOpen ? "translate-x-0" : "-translate-x-full",
        "lg:flex lg:translate-x-0",
      )}
    >
      <div className="mb-6 flex items-center justify-between px-2 lg:justify-start">
        <div className="flex items-center gap-3">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/logo.png" alt="Axiom AI Logo" className="h-8 w-auto" />
          <h2 className="font-display text-base font-semibold tracking-tight text-paper">
            Axiom AI
          </h2>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="rounded-md p-2 text-paper/70 hover:bg-indigo-soft hover:text-paper lg:hidden"
          aria-label="Close sidebar"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <nav className="flex-1 space-y-1">
        {mainNavItems.map((item) => {
          const active =
            item.href === "/dashboard/analytics"
              ? pathname === item.href
              : pathname === item.href ||
                Boolean(pathname?.startsWith(`${item.href}/`));

          return (
            <NavLink
              key={item.href}
              item={item}
              active={active}
              onClose={onClose}
            />
          );
        })}
      </nav>

      <nav className="mt-auto border-t border-white/10 pt-4">
        <NavLink
          item={settingsNavItem}
          active={
            pathname === settingsNavItem.href ||
            Boolean(pathname?.startsWith(`${settingsNavItem.href}/`))
          }
          onClose={onClose}
        />
      </nav>
    </aside>
  );
}
