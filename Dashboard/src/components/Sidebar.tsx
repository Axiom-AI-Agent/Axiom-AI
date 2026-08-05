// src/components/Sidebar.tsx
"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { X } from "lucide-react";

interface NavItem {
  href: string;
  label: string;
  icon: React.ReactNode;
}

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const navItems: NavItem[] = [
  {
    href: "/dashboard/overview",
    label: "Overview",
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M13 5v6h6" />
      </svg>
    ),
  },
  {
    href: "/dashboard/classes",
    label: "Classes",
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m2 0a2 2 0 100-4 2 2 0 000 4zm-8 0a2 2 0 100-4 2 2 0 000 4z" />
      </svg>
    ),
  },
  {
    href: "/dashboard/payments",
    label: "Payments",
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-3.866 0-7 1.79-7 4s3.134 4 7 4 7-1.79 7-4-3.134-4-7-4z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 12v4" />
      </svg>
    ),
  },
  {
    href: "/dashboard/chats",
    label: "Chats",
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16h6" />
      </svg>
    ),
  },
  {
    href: "/dashboard/logs",
    label: "Logs",
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v4a1 1 0 001 1h3l3 3 3-3h3a1 1 0 001-1V7" />
      </svg>
    ),
  },
];

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "bg-gradient-to-b from-gray-800 to-gray-900 text-gray-100 min-h-screen flex flex-col p-4",
        "fixed lg:relative inset-y-0 left-0 w-64 transform transition-transform duration-300 ease-in-out z-50",
        isOpen ? "translate-x-0" : "-translate-x-full",
        "lg:translate-x-0 lg:flex"
      )}
    >
      {/* Close button only visible on mobile */}
      <button
        className="absolute top-4 right-4 lg:hidden text-gray-300 hover:text-white"
        onClick={onClose}
        aria-label="Close sidebar"
      >
        <X className="h-6 w-6" />
      </button>
      <h2 className="text-xl font-semibold mb-6">Axiom AI</h2>
      <nav className="flex-1 space-y-2">
        {navItems.map((item) => {
          const active = pathname?.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center space-x-3 rounded-md p-2 hover:bg-gray-700 transition-colors",
                active && "bg-gray-700 font-medium"
              )}
            >
              {item.icon}
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
