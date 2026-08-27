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
    icon: <LayoutDashboard className="h-4 w-4" />,
  },
  {
    href: "/dashboard/analytics",
    label: "Analytics",
    icon: <BarChart3 className="h-4 w-4" />,
  },
  {
    href: "/dashboard/analytics/classes",
    label: "Class Analytics",
    icon: <School className="h-4 w-4" />,
  },
  {
    href: "/dashboard/inbox",
    label: "Escalation Inbox",
    icon: <Inbox className="h-4 w-4" />,
  },
  {
    href: "/dashboard/messages",
    label: "Messages",
    icon: <MessageSquare className="h-4 w-4" />,
  },
  {
    href: "/dashboard/classes",
    label: "Classes",
    icon: <BookOpen className="h-4 w-4" />,
  },
  {
    href: "/dashboard/schedules",
    label: "Schedules",
    icon: <Calendar className="h-4 w-4" />,
  },
  {
    href: "/dashboard/students",
    label: "Students",
    icon: <Users className="h-4 w-4" />,
  },
  {
    href: "/dashboard/staff",
    label: "Staff",
    icon: <UserCog className="h-4 w-4" />,
  },
  {
    href: "/dashboard/faqs",
    label: "FAQ Intelligence",
    icon: <HelpCircle className="h-4 w-4" />,
  },
  {
    href: "/dashboard/logs",
    label: "Logs",
    icon: <ScrollText className="h-4 w-4" />,
  },
  {
    href: "/dashboard/ingest",
    label: "Ingest",
    icon: <FileUp className="h-4 w-4" />,
  },
];

const settingsNavItem: NavItem = {
  href: "/dashboard/settings",
  label: "Settings",
  icon: <Settings className="h-4 w-4" />,
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
        "flex items-center gap-2.5 rounded-md px-2 py-1.5 text-[13px] transition-colors duration-150",
        active
          ? "bg-blue/20 font-medium text-white shadow-[inset_2px_0_0_0_var(--blue)]"
          : "text-white/70 hover:bg-white/10 hover:text-white",
      )}
    >
      <span
        className={cn(
          "flex h-7 w-7 shrink-0 items-center justify-center rounded-md",
          active ? "bg-blue/25 text-white" : "text-white/55",
        )}
      >
        {item.icon}
      </span>
      <span className="truncate leading-tight">{item.label}</span>
    </Link>
  );
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-50 flex min-h-screen w-56 flex-col border-r border-white/10 bg-[linear-gradient(180deg,#152238_0%,#1b2a4a_55%,#152033_100%)] p-2 text-white transition-transform duration-300 ease-in-out lg:relative lg:shadow-none",
        isOpen ? "translate-x-0" : "-translate-x-full",
        "lg:flex lg:translate-x-0",
      )}
    >
      <div className="mb-3 flex items-center justify-between px-1.5 pt-1 lg:justify-start">
        <div className="flex min-w-0 items-center gap-2">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/logo.png" alt="Axiom AI Logo" className="h-7 w-auto shrink-0" />
          <div className="min-w-0">
            <h2 className="font-display truncate text-sm font-semibold tracking-tight text-white">
              Axiom AI
            </h2>
            <p className="text-[10px] tracking-wide text-white/45">
              Staff Console
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="rounded-md p-1.5 text-white/65 hover:bg-white/10 hover:text-white lg:hidden"
          aria-label="Close sidebar"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <nav className="flex-1 space-y-0.5 overflow-y-auto">
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

      <nav className="mt-auto border-t border-white/10 pt-2">
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
