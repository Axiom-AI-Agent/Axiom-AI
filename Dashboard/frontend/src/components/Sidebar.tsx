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
        "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-all duration-200",
        active
          ? "bg-blue/20 font-medium text-white shadow-[inset_3px_0_0_0_var(--blue)]"
          : "text-white/70 hover:bg-white/10 hover:text-white",
      )}
    >
      <span
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-md transition-colors",
          active ? "bg-blue/25 text-white" : "text-white/55",
        )}
      >
        {item.icon}
      </span>
      <span>{item.label}</span>
    </Link>
  );
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-50 flex min-h-screen w-64 flex-col border-r border-white/10 bg-[linear-gradient(175deg,#0f1a2e_0%,#15233b_48%,#101b2d_100%)] p-3 text-white shadow-[var(--shadow-soft)] transition-transform duration-300 ease-in-out lg:relative lg:shadow-none",
        isOpen ? "translate-x-0" : "-translate-x-full",
        "lg:flex lg:translate-x-0",
      )}
    >
      <div className="mb-5 flex items-center justify-between px-2 pt-1 lg:justify-start">
        <div className="flex items-center gap-3">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/logo.png" alt="Axiom AI Logo" className="h-8 w-auto" />
          <div>
            <h2 className="font-display text-base font-semibold tracking-tight text-white">
              Axiom AI
            </h2>
            <p className="text-[11px] tracking-wide text-white/45">
              Staff Console
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="rounded-lg p-2 text-white/65 hover:bg-white/10 hover:text-white lg:hidden"
          aria-label="Close sidebar"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <nav className="flex-1 space-y-0.5 overflow-y-auto px-0.5">
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

      <nav className="mt-auto border-t border-white/10 pt-3">
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
